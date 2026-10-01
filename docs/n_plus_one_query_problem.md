# P95 performance issue: summary

## N+1 Sql Query Problem

The N+1 problem happens when an application fetches a list of records with one query, then runs one more query for each record to load related data.

- `1` query fetches the parent records.
- `N` queries fetch related data, one query per parent record.

If a request returns 20 products and loads each product's inventory separately, the endpoint runs 1 product query plus 20 inventory queries. In this project, the endpoint also runs a count query, so the total is about 22 queries.

## Example from the product list

`GET /api/v1/products?page=1&page_size=20`

The target from your Phase 0 foundation is:

`P95 ≤ 300 ms`

P95 means 95 out of 100 requests should finish within the target time. It focuses on slow user experiences that an average response time can hide.

## What we observed

| Test stage | P50 | P95 | Throughput | Finding |
|---|---:|---:|---:|---|
| Before query fix | 620 ms | 2,300 ms | 5.46 req/s | Product-list endpoint was slow. |
| After query fix | 50 ms | 520 ms | 8.22 req/s | Most requests became fast; a few slow requests still affect P95. |

The product query fetches one page:

At higher load we will also observe

`QueuePool limit of size 5 overflow 10 reached`

This means the FastAPI process had at most 15 concurrent database connections available. When all were busy, later requests waited; after 30 seconds, they failed to get a connection.


## Root cause found
The original product-list code loaded products first:

```python
rows = db.exec(
    select(models.Product)
    .where(*filters)
    .order_by(models.Product.created_at.desc())
    .offset((page - 1) * page_size)
    .limit(page_size)
).all()
```

When response-building code then accesses:

```python
product.inventory.quantity
```

SQLAlchemy may lazily query inventory for each product. For a page of 20, the pattern is:

```text
1 query: count matching products
1 query: fetch 20 products
20 queries: fetch inventory, once per product
```

That is the N+1 problem. Each query may be small, but the repeated database round trips add latency and multiply under concurrent traffic.

## How we diagnosed it

1. Locust showed high P95 latency and low request throughput.
2. Server errors showed database connection-pool saturation at high load.
3. SQLAlchemy SQL logging showed repeated inventory queries for every product.
3. We changed one thing: eager-load inventory using selectinload.
4. We reran the same Locust scenario and compared P50, P95, throughput, and failures.

Measure with Locust
    ↓
Find slow or failing request
    ↓
Inspect logs, SQL count, database activity, CPU, and memory
    ↓
Identify one likely bottleneck
    ↓
Apply one focused change
    ↓
Run the identical test again
    ↓
Compare evidence

## How to confirm it

Enable SQLAlchemy SQL logging temporarily and make one product-list request. Repeated queries shaped like this, with a different product ID each time, indicate the issue:

```sql
SELECT ... FROM inventory WHERE inventory.product_id = ...;
```

The phrase `cached since ...` in SQLAlchemy's log means the compiled SQL statement was reused. It does not mean the database returned cached inventory data; each statement still runs.

## Fix with `selectinload`

Tell SQLAlchemy to fetch the related inventory for the page in one grouped query:

```python
from sqlalchemy.orm import selectinload

rows = db.exec(
    select(models.Product)
    .options(selectinload(models.Product.inventory))
    .where(*filters)
    .order_by(models.Product.created_at.desc())
    .offset((page - 1) * page_size)
    .limit(page_size)
).all()
```

The query pattern becomes:

```text
1 query: count matching products
1 query: fetch the product page
1 query: fetch inventory for all product IDs in the page
```

The inventory query uses an `IN (...)` condition with the page's product IDs. For 20 products, this changes roughly 22 queries into 3.

## When to use relationship loading

It is not needed just because an endpoint uses two tables. Ask instead:

> Will response or business logic access this relationship for many fetched records?

If yes, eager-load it to avoid one relationship query per record. `selectinload` is often a good fit for collections or list endpoints. `joinedload` can be useful for a single record or a many-to-one relationship. Choose based on the relationship and verify the generated SQL.

## How to measure the improvement

1. Capture SQL for one request and count the repeated queries.
2. Add relationship loading.
3. Confirm the repeated per-product inventory queries became one grouped query.
4. Turn SQL echo back off; verbose SQL logging affects performance.
5. Rerun the same Locust test and compare P50, P95, throughput, and failures.

In the ecommerce test, adding `selectinload` reduced product-list median latency from about 620 ms to 50 ms in one observed run. P95 fell from about 2,300 ms to 520 ms. Those measurements are specific to that run; repeat the same workload and setup to compare future changes fairly.
