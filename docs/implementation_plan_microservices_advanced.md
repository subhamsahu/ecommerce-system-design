# Advanced Microservices Development: A Practical E-commerce Handbook

**From a FastAPI monolith to a measured, resilient distributed system**  
**Edition:** 2 — implementation and learning handbook  
**Prepared:** 30 September 2026  
**Companion:** `roadmap_microservice(1).md`  
**Format reference:** `IMPLEMENTATION_GUIDE_v2.md`

---

## How to use this book

This handbook expands the roadmap into a development guide. Work through it with your e-commerce repository open. Each chapter explains a problem, introduces the concept that solves it, names the relevant tools, provides implementation details, and finishes with experiments and completion criteria.

Your attached Test Management Platform guide supplies the presentation format: numbered steps, file locations, responsibilities, API contracts, and verification checkpoints. The application here remains your e-commerce learning project. Its domain is customers, products, inventory, orders, and payments.

The guide is an implementation specification with focused executable labs, rather than a complete generated application. Blocks labelled **complete lab file** can be saved at the indicated path and run after their prerequisites. Blocks labelled **implementation pattern** illustrate code to integrate into your application. SQL and infrastructure examples specify where they run. Do not assume an illustrative function or module already exists in your repository. SQL containing `:named_parameters` is a driver/SQLAlchemy binding pattern, not a command to paste unchanged into `psql`. Kubernetes and service-extraction templates list dependencies that you must implement or provision first.

The commands use Bash on Linux, macOS, or WSL. If using Windows, WSL2 is a useful consistent environment for the later Celery and container labs. Start with your working Python installation; record its exact version and verify the selected packages install successfully. The examples use modern FastAPI, Pydantic 2, SQLAlchemy 2, and PostgreSQL APIs. Dependency versions must be locked after the initial installation. Whenever a later chapter adds a package, update the appropriate lock file and rebuild affected images. Keep the Python minor version used for that lock compatible with the container runtime. Image tags below are teaching baselines, not claims about the newest or recommended production patch.

No performance figures in this handbook are results measured on your application. Numerical tables marked **illustrative** are learning examples. Replace them with your own measurements.

## Detailed contents

- [Chapter 0 — Establish the laboratory](#chapter-0--establish-the-laboratory)
- [Chapter 1 — Build a monolith whose behavior you understand](#chapter-1--build-a-monolith-whose-behavior-you-understand)
- [Chapter 2 — Create a modular monolith](#chapter-2--create-a-modular-monolith)
- [Chapter 3 — Query plans, transactions, and concurrent purchases](#chapter-3--query-plans-transactions-and-concurrent-purchases)
- [Chapter 4 — Measure P50, P95, and P99 with Locust](#chapter-4--measure-p50-p95-and-p99-with-locust)
- [Chapter 5 — Scale the monolith horizontally](#chapter-5--scale-the-monolith-horizontally)
- [Chapter 6 — Redis caching with failure behavior](#chapter-6--redis-caching-with-failure-behavior)
- [Chapter 7 — Background jobs with Celery and RabbitMQ](#chapter-7--background-jobs-with-celery-and-rabbitmq)
- [Chapter 8 — Extract Notification as the first service](#chapter-8--extract-notification-as-the-first-service)
- [Chapter 9 — Extract core services without hiding the cost](#chapter-9--extract-core-services-without-hiding-the-cost)
- [Chapter 10 — Distributed checkout, Saga, and payment uncertainty](#chapter-10--distributed-checkout-saga-and-payment-uncertainty)
- [Chapter 11 — Reliable events with Outbox and Inbox](#chapter-11--reliable-events-with-outbox-and-inbox)
- [Chapter 12 — API gateway, identity, and edge behavior](#chapter-12--api-gateway-identity-and-edge-behavior)
- [Chapter 13 — Search projections and eventual consistency](#chapter-13--search-projections-and-eventual-consistency)
- [Chapter 14 — Logs, metrics, tracing, and P99 in operation](#chapter-14--logs-metrics-tracing-and-p99-in-operation)
- [Chapter 15 — Resilience and bounded failure](#chapter-15--resilience-and-bounded-failure)
- [Chapter 16 — Distributed rate limits and overload control](#chapter-16--distributed-rate-limits-and-overload-control)
- [Chapter 17 — Database scaling, retention, and recovery](#chapter-17--database-scaling-retention-and-recovery)
- [Chapter 18 — Product media, object storage, and CDN](#chapter-18--product-media-object-storage-and-cdn)
- [Chapter 19 — Kubernetes and safe deployment](#chapter-19--kubernetes-and-safe-deployment)
- [Chapter 20 — Autoscaling and backpressure](#chapter-20--autoscaling-and-backpressure)
- [Chapter 21 — Flash-sale laboratory](#chapter-21--flash-sale-laboratory)
- [Chapter 22 — Build a defensible million-user design](#chapter-22--build-a-defensible-million-user-design)
- [Appendix A — Turn the handbook into a weekly development routine](#appendix-a--turn-the-handbook-into-a-weekly-development-routine)
- [Appendix B — Testing and CI as the system grows](#appendix-b--testing-and-ci-as-the-system-grows)
- [Appendix C — Reusable experiment and incident templates](#appendix-c--reusable-experiment-and-incident-templates)
- [Appendix D — Diagnostic reference](#appendix-d--diagnostic-reference)
- [Appendix E — Learning checks and transfer to your test platform](#appendix-e--learning-checks-and-transfer-to-your-test-platform)
- [Appendix F — Official technical references and version policy](#appendix-f--official-technical-references-and-version-policy)

### The chapter method

For each chapter, follow this order:

1. Explain the problem in your own words.
2. Build the smallest feature that exposes it.
3. Run a normal test and a failure test.
4. Measure the relevant behavior.
5. Implement the proposed improvement.
6. Repeat the same experiment.
7. Record what improved, what became harder, and what remains unknown.

Do not skip correctness work because a benchmark looks good. An endpoint that responds quickly while overselling inventory is incorrect.

### Reading map

| Part | Chapters | Result |
|---|---|---|
| Foundation | 0–2 | Working, modular monolith |
| Measurement and scaling | 3–6 | Correct concurrency, understood P99, horizontally scaled application, cache |
| Distributed workflows | 7–11 | Workers, service extraction, Saga, reliable events |
| Operating services | 12–16 | Gateway, search, observability, resilience, rate limits |
| Advanced scale | 17–22 | Data scaling, media delivery, Kubernetes, autoscaling, flash sale, capacity model |
| Reference | Appendices A–F | Delivery sequence, templates, troubleshooting, learning checks, sources |

### When to introduce each tool

| Question you are trying to answer | Tool or technique | First use |
|---|---|---|
| Is the business rule correct? | pytest and PostgreSQL integration tests | Chapter 1 |
| Why does a query become slow? | PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` | Chapter 3 |
| What are P95/P99 under traffic? | Locust | Small baseline in Chapter 1; full lab in Chapter 4 |
| Which component consumes latency? | Request timing, SQL timing, profiler, later traces | Chapters 1, 3, 14 |
| Is one API process saturated? | Process/container metrics, repeated load test | Chapters 4–5 |
| Can caching reduce database reads? | Redis and cache metrics | Chapter 6 |
| Can work continue after the HTTP response? | Celery with RabbitMQ | Chapter 7 |
| How do independent services exchange facts reliably? | RabbitMQ, Outbox, Inbox | Chapters 8–11 |
| What happens across the whole order journey? | OpenTelemetry, Prometheus, Grafana | Chapter 14 |
| How do I deploy and scale replicas? | Docker first; Kubernetes later | Chapters 5, 19–20 |

P99 is a statistical measurement. Locust is a load generator and measurement tool; it does not improve P99 by itself. The fix depends on the cause: slow SQL, queueing, CPU work, connection limits, large responses, or a slow dependency.

---

# Chapter 0 — Establish the laboratory

## 0.1 The system you are building

The first version has one API deployment and one database. A request travels through an HTTP route, an application function, database queries, and response serialization. Separate Python folders do not make it a microservice system. Separate deployments introduce network failure and data ownership questions that you will study later.

Start with these capabilities:

- Customer registration and login.
- Product listing, filtering, detail, and admin maintenance.
- Inventory adjustments and reservations.
- A persistent cart.
- Checkout, simulated payment, order history, cancellation.

Defer coupons, shipping integrations, recommendations, and real-money transactions. You need a small complete order flow on which to run experiments.

## 0.2 Establish assumptions and success criteria

Create `docs/requirements/mvp.md`. Record functional requirements, invariants, workload assumptions, and initial performance targets separately.

**Illustrative local targets, to calibrate after your first baseline:**

| Operation | Workload | Initial target |
|---|---|---|
| Product list | 100 virtual users, 20 items/page | P95 < 300 ms; P99 < 800 ms |
| Product detail | Same mixed browse run | P99 < 500 ms |
| Checkout acceptance | Controlled stock and valid buyers | P99 < 1.5 s; no duplicate orders |
| Correctness | 100 buyers compete for one unit | At most one active reservation |
| Reliability | Replay one payment event 20 times | One business transition |

A target without a workload and environment is ambiguous. Include CPU, RAM, deployment topology, dataset, duration, and traffic mix. Monthly availability SLOs need a real observation window; a ten-minute local test cannot prove them.

## 0.3 Prepare directories and dependencies

From the repository root, create:

```bash
mkdir -p server/app scripts load-tests docs/benchmarks docs/adr
mkdir -p docs/runbooks tests/integration tests/concurrency infrastructure
touch server/__init__.py server/app/__init__.py scripts/__init__.py
```

Retain your existing layout where practical. The following examples assume that `server` and `server/app` contain `__init__.py`, enabling imports such as `server.app.db` from the repository root.

Create an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install fastapi 'uvicorn[standard]' 'sqlalchemy[asyncio]' asyncpg alembic pydantic-settings
python -m pip install pytest pytest-asyncio httpx locust
python -m pip freeze > requirements.lock.txt
```

Use a separate environment/lock file for load generation when it moves to a different machine. Record `python --version`, `locust --version`, and `docker version` with benchmark results. Do not keep upgrading dependencies between comparison runs.

## 0.4 Start only PostgreSQL

**Complete lab file: `compose.lab.yml`**

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: shop
      POSTGRES_PASSWORD: local_lab_password
      POSTGRES_DB: shop
    ports:
      - '127.0.0.1:5432:5432'
    volumes:
      - shop_pg:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U shop -d shop']
      interval: 5s
      timeout: 3s
      retries: 10
volumes:
  shop_pg:
```

The fixed password is solely for this loopback-bound local lab. Shared environments need managed secrets and appropriate network access.

```bash
docker compose -f compose.lab.yml up -d
docker compose -f compose.lab.yml ps
docker compose -f compose.lab.yml exec postgres psql -U shop -d shop -c 'SELECT version();'
export DATABASE_URL='postgresql+asyncpg://shop:local_lab_password@127.0.0.1:5432/shop'
```

A healthy PostgreSQL container means the database process accepts connections. It does not prove your schema or application migrations are correct.

## 0.5 Make experiments repeatable

Maintain separate development and disposable test databases. Mark data created by experiments with a run identifier. Seed deterministic product prices, product IDs, and inventory amounts so comparisons have the same input.

For every benchmark, save:

- Git commit and dependency lock.
- Hardware/container limits and worker count.
- Data volume, popularity distribution, and cache state.
- Locust script, users, spawn rate, duration, and think time.
- Raw CSV output, server logs, and resource measurements.

**Checkpoint:** You can explain the MVP, start PostgreSQL, connect to it, and state which assumptions a later benchmark will test.

---

# Chapter 1 — Build a monolith whose behavior you understand

## 1.1 Define a request's responsibilities

An HTTP route translates input and output. An application service performs a use case such as placing an order. Database access reads and writes records. Domain rules decide whether a purchase, cancellation, or state transition is allowed.

For the initial monolith, one database transaction may update inventory, order, payment-attempt, and idempotency records together. That is useful atomicity. Do not replace it with messaging until you have a real reason to split ownership.

Suggested folders:

```text
server/app/
  main.py
  db.py
  core/             # settings, errors, security, logging
  auth/             # routes, schemas, application logic
  catalog/
  inventory/
  cart/
  orders/
  payments/
```

Start with readable routes and application functions. Introduce repositories where they clarify ownership or testing; do not add multiple pass-through layers for every CRUD call.

## 1.2 Design the relational model

| Table | Important fields and constraints | Purpose |
|---|---|---|
| users | UUID PK, normalized email UNIQUE, password hash, role | Identity |
| products | UUID PK, SKU UNIQUE, name, price_minor, currency, active | Current commercial offer |
| inventory | product_id PK/FK, on_hand, reserved, version | Stock ownership |
| carts/cart_items | user/cart relationship, UNIQUE(cart_id, product_id), positive quantity | Purchase intent |
| orders | UUID PK, user_id, status, total_minor, currency, timestamps | Purchase lifecycle |
| order_items | order_id, product_id, SKU/name/price snapshots, quantity | Immutable purchase details |
| reservations | order_id, product_id, quantity, status, expires_at | Temporary stock claims |
| payment_attempts | order_id, provider key, amount, status | Payment lifecycle |
| idempotency_records | UNIQUE(user_id, operation, key), request hash, result | Safe client retries |

Use integer minor units for money in this course: ₹199.50 becomes `19950` paise with currency `INR`. Never use binary floating-point arithmetic for money. Define rounding when discounts/tax are introduced.

The core stock model is:

```text
available = on_hand - reserved
0 <= reserved <= on_hand
```

Reservation increases `reserved`. A successful purchase consumes both `on_hand` and `reserved`. Cancellation/expiry releases `reserved` only. Add check constraints and test both the application and database boundaries.

## 1.3 Create a small runnable read lab first

The following files create a product-list endpoint so you can learn performance measurement while building the rest of the monolith. They do not implement the entire shop.

**Complete lab file: `scripts/catalog_lab.sql`**

```sql
CREATE TABLE IF NOT EXISTS products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    price_minor BIGINT NOT NULL CHECK (price_minor >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO products (sku, name, category_id, price_minor)
SELECT 'LAB-' || n, 'Product ' || n, 1 + n % 20, 10000 + n % 50000
FROM generate_series(1, 10000) AS n
ON CONFLICT (sku) DO NOTHING;
ANALYZE products;
```

This isolated catalog lab uses numeric IDs to keep the scripts short. The full domain can use UUIDs consistently; adjust Locust's ID source accordingly. Apply the lab schema to a disposable lab database, not over a conflicting existing `products` table:

```bash
docker compose -f compose.lab.yml exec -T postgres psql -U shop -d shop < scripts/catalog_lab.sql
```

For your application, express equivalent changes as Alembic migrations, inspect the generated SQL, and apply migrations once per deployment. Do not run `create_all()` or migrations independently in every web worker.

**Complete lab file: `server/app/db.py`**

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    os.environ['DATABASE_URL'],
    pool_size=5,
    max_overflow=5,
    pool_timeout=3,
    pool_pre_ping=True,
)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with SessionFactory() as session:
        yield session
```

Create the engine once per application process, and a session for each request/use case. A SQLAlchemy session contains transaction state; concurrent tasks need separate sessions. A larger pool is not automatically faster. It increases how much work can reach PostgreSQL simultaneously. See [SQLAlchemy's async session guidance](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks).

**Complete lab file: `server/app/main.py`**

```python
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.db import engine, get_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get('/health/live')
async def live():
    return {'status': 'ok'}

@app.get('/api/v1/products')
async def products(
    db: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
):
    rows = await db.execute(
        text('''
            SELECT id, sku, name, price_minor, currency
            FROM products
            WHERE active = TRUE
            ORDER BY id
            LIMIT :limit OFFSET :offset
        '''),
        {'limit': page_size, 'offset': (page - 1) * page_size},
    )
    return {'items': [dict(row) for row in rows.mappings()],
            'page': page, 'page_size': page_size}

@app.get('/api/v1/products/{product_id}')
async def product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    result = await db.execute(
        text('''
            SELECT id, sku, name, price_minor, currency
            FROM products WHERE id = :id AND active = TRUE
        '''),
        {'id': product_id},
    )
    row = result.mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail='Product not found')
    return dict(row)
```

Start from the repository root:

```bash
python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
curl -f 'http://127.0.0.1:8000/api/v1/products?page=1&page_size=20'
```

Read the response before load testing it. Confirm the number of items and field names. This sample omits authentication because catalog browsing is public. It also omits a total-count query intentionally: an exact total is a separate database cost and should be added when the API contract requires it.

## 1.4 Understand async execution before increasing users

`async def` permits cooperative waiting; it does not automatically parallelize CPU work. An awaited async database query lets the event loop serve other requests while waiting. Calling a synchronous network client or doing heavy hashing directly inside an async route can block that loop.

Use these rules:

- Async driver/client: `await` it from an async function.
- Blocking library: use a synchronous FastAPI route/dependency or explicitly offload appropriately.
- CPU-heavy work: bound concurrency; consider a separate process/worker when justified.
- Never share one `AsyncSession` across `asyncio.gather()` tasks.

FastAPI's [concurrency explanation](https://fastapi.tiangolo.com/async/) describes how it treats sync and async route functions. Add an experiment later: introduce a blocking 100 ms operation in an isolated lab route, compare it with an async wait, and inspect throughput under concurrency. Remove the fault route afterward.

## 1.5 Implement identity and authorization

Add registration, login, and current-user endpoints before cart/order APIs. Use a maintained password-hashing library with Argon2 support and a JWT library; lock their versions and follow the [FastAPI security tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

The implementation order is:

1. Normalize and uniquely constrain email addresses according to your chosen policy.
2. Hash passwords; never store or log the original.
3. Validate login and issue a token containing a stable subject and expiration.
4. On every protected request, verify signature, allowed algorithm, expiry, issuer/audience where configured, and whether the identity is allowed to act.
5. Resolve permissions server-side. The client cannot promote itself by sending `role=admin`.
6. Add ownership filters to order/cart queries using the authenticated identity.
7. Add refresh rotation/revocation only when you define the session lifecycle; test reuse and logout behavior.

Do not include an order owner supplied by the client without comparing it with the authenticated user. An order API returning another customer's order is a correctness and authorization failure even if the JWT is valid.

## 1.6 Define checkout and payment contracts

| Endpoint | Behavior |
|---|---|
| `PUT /api/v1/cart/items/{product_id}` | Set positive quantity; return server-calculated cart |
| `POST /api/v1/orders` | Accept cart snapshot/version and idempotency key; create pending order/reservation |
| `GET /api/v1/orders/{id}` | Return caller-owned order and payment status |
| `POST /api/v1/orders/{id}/cancel` | Request allowed cancellation; repeated request is safe |
| `POST /api/v1/payments/webhooks/{provider}` | Verify provider event, deduplicate, persist transition |

A useful first policy is reserve inventory at order creation, confirm only after payment succeeds, and expire unpaid reservations after a documented interval. A payment timeout is an unknown outcome; it is not proof that no money was taken.

Keep separate status fields:

| Aggregate | Example states |
|---|---|
| Order | PENDING_PAYMENT, CONFIRMED, CANCEL_PENDING, CANCELLED, EXPIRED, REVIEW_REQUIRED |
| Reservation | ACTIVE, CONSUMED, RELEASED, EXPIRED |
| Payment attempt | CREATED, PENDING, SUCCEEDED, FAILED, UNKNOWN, REFUND_PENDING, REFUNDED |

For a real provider, authorization and capture can be separate states. Specify whether your chosen integration captures automatically. Do not casually translate every authorized payment into a fulfilled order.

## 1.7 The monolithic checkout transaction

**Implementation pattern; application functions are to be written by you:**

```python
async def create_order(command, authenticated_user_id):
    async with SessionFactory() as db:
        async with db.begin():
            # 1. Claim a unique (user, operation, key) idempotency record.
            # 2. If already completed, compare request hash and return its result.
            # 3. Validate the cart/version and read server-owned price snapshots.
            # 4. Reserve stock with conditional updates in stable product-ID order.
            # 5. Insert order, items, reservation rows, and payment attempt.
            # 6. Persist the idempotency result in this same transaction.
            pass
    # A real provider call happens after commit, with a stable provider key.
```

A `SELECT` to check whether an idempotency key exists followed by an unprotected `INSERT` is racy. Use a unique constraint plus conflict handling. The claim and successful business writes should commit together. Retrying the same key with different payload must return a conflict, not a previous unrelated result.

If an HTTP response is lost after commit, the client retries with the same key. The service returns the existing order. If the transaction rolled back, the retry can create it. Do not let an indefinitely stuck `IN_PROGRESS` record block recovery without an explicit lease/reconciliation policy.

## 1.8 Add tests and an early performance baseline

Unit-test state transitions and totals. Integration-test checkout against PostgreSQL, not SQLite. The database's locking and type semantics are part of the behavior under study.

Test invalid quantities, changed prices, duplicate keys, insufficient inventory, ownership checks, payment decline, unknown payment, and repeated cancellation. Add concurrent final-unit tests in Chapter 3.

As soon as the product API works, run the Chapter 4 Locust lab with 10 users. Save that baseline even though the application is still a monolith. You should not wait for microservices to begin measuring.

**Checkpoint:** A buyer completes the whole flow; database constraints protect key invariants; retries are safe; you have a small, reproducible latency baseline.

**Explain aloud:** Why is a payment timeout different from a decline? What commits together during order creation? Why might an async route block every other request in its worker?

---

# Chapter 2 — Create a modular monolith

## 2.1 Recognize the coupling you will eventually remove

If ordering imports the inventory ORM class, edits its columns, and depends on its indexes, the modules share implementation knowledge. Extracting inventory later then requires changes in many places.

Define an application interface around business operations: `reserve`, `consume`, `release`, and `availability`. Return small result objects, not live ORM instances. Keep inventory queries and invariants inside the inventory module.

An interface does not have to mean an abstract class for everything. A well-defined Python function with typed parameters can be enough until there are multiple implementations.

## 2.2 Separate ownership from transaction boundaries

In a monolith, the caller can provide a shared unit of work so several modules participate in one PostgreSQL transaction. This does not grant ordering permission to write inventory tables directly; it allows inventory's own function to use the existing transaction.

After extraction that local transaction disappears. You must redesign it as a workflow; replacing a Python function with HTTP does not preserve atomicity.

## 2.3 Refactor one use case

Move `reserve_inventory` out of the order route. Give it inputs `(order_id, product_quantities)` and a supplied transaction. Return explicit outcomes such as `Reserved` or `InsufficientStock`. Map these to HTTP at the outer boundary.

Then refactor notifications behind an interface. An internal adapter can store a notification request locally today, and later publish an event without rewriting order-domain rules.

## 2.4 Enforce useful boundaries

Create `docs/architecture/module-ownership.md` listing owner, tables, public application methods, and allowed dependencies. Search cross-module imports with `rg` during review, and add an import-boundary test if violations recur.

Share technical utilities such as request-ID propagation sparingly. A shared package containing every service's ORM model recreates a shared data model and forces coordinated releases.

**Lab:** Change inventory's implementation from one table to balance plus movement history while retaining its interface. Record which callers changed and why.

**Checkpoint:** Routes are thin, module ownership is visible, and the full customer flow still passes. Tag this state `v2-modular-monolith`.

---

# Chapter 3 — Query plans, transactions, and concurrent purchases

## 3.1 Generate data that can reveal a problem

Ten products cannot demonstrate how a million-row query behaves. Increase the catalog lab to 100,000 rows, then 500,000 if your machine permits. Introduce uneven popularity: many users view a small number of products while most products receive few reads.

Generate order history separately. Use a small number of customers with many orders and many customers with few orders. Uniform random data often hides the hot customers and products that cause contention.

Record dataset size before each experiment. Run `ANALYZE` after a large seed so the planner has useful statistics.

## 3.2 Read a query plan instead of guessing

Suppose customer order history executes:

```sql
SELECT id, status, total_minor, created_at
FROM orders
WHERE user_id = '11111111-1111-4111-8111-111111111111'
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

In a disposable dataset, inspect:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, status, total_minor, created_at
FROM orders
WHERE user_id = '11111111-1111-4111-8111-111111111111'
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

`ANALYZE` executes the statement. Do not use it casually on mutating production queries. Inspect estimated versus actual rows, sequential/index scans, sort work, and buffer hits/reads. A sequential scan can be the correct plan for a small table or a query returning much of it.

Now create a candidate index:

```sql
CREATE INDEX idx_orders_user_created_id
ON orders (user_id, created_at DESC, id DESC);
```

Repeat the same query. Explain why the leading equality filter and subsequent order columns match this access pattern. Also measure an insert workload: every index adds write work and storage.

**Record:** SQL, row count, plan before/after, execution duration, buffers, index size, and effect on writes. Avoid clearing production caches to manufacture a benchmark.

## 3.3 Replace deep offsets with stable cursors

An offset of 200,000 asks the database to walk past many rows. A cursor identifies where to continue using an indexed ordering.

```sql
SELECT id, status, total_minor, created_at
FROM orders
WHERE user_id = :user_id
  AND (created_at, id) < (:cursor_time, :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT :page_size;
```

Include a unique tie-breaker (`id`) because timestamps may match. Encode the cursor safely and validate it. Apply the same filters and sorting on every page. A cursor does not create a frozen snapshot across independent requests; concurrent changes can still affect the result set. Explain those semantics in the API contract.

## 3.4 Learn the last-unit race

The unsafe sequence is: read available stock as one; another transaction reads one; both independently decide the item is available. Application checks alone cannot serialize the decision.

A conditional update combines the decision and mutation:

```sql
UPDATE inventory
SET reserved = reserved + :quantity,
    version = version + 1
WHERE product_id = :product_id
  AND :quantity > 0
  AND on_hand - reserved >= :quantity
RETURNING product_id, on_hand, reserved;
```

If no row returns, reservation did not succeed. At PostgreSQL's default Read Committed isolation, a concurrent update to the same row is waited on and the update predicate is checked against the updated version. This is why the condition belongs in the update. See [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html).

For a multi-product order, use one transaction and process product IDs in a stable order. If any reservation fails, roll back all reservations. Stable ordering reduces deadlock opportunities, though it does not eliminate every deadlock in a larger application.

Alternative: `SELECT ... FOR UPDATE`, inspect the locked row, then update. Compare the two approaches. Locking is useful when a rule needs several values, but do not hold the lock during a payment-provider call.

## 3.5 Complete concurrency laboratory

This deliberately small experiment bypasses HTTP to isolate PostgreSQL correctness. It creates its own `inventory_lab` table and does not touch real inventory.

**Complete lab file: `scripts/race_inventory.py`**

```python
import asyncio
from sqlalchemy import text
from server.app.db import engine, SessionFactory

async def attempt(start):
    await start.wait()
    async with SessionFactory() as db:
        async with db.begin():
            result = await db.execute(text('''
                UPDATE inventory_lab
                SET reserved = reserved + 1
                WHERE product_id = 1 AND on_hand - reserved >= 1
                RETURNING product_id
            '''))
            return result.scalar_one_or_none() is not None

async def main():
    async with engine.begin() as conn:
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS inventory_lab (
                product_id BIGINT PRIMARY KEY,
                on_hand INTEGER NOT NULL CHECK (on_hand >= 0),
                reserved INTEGER NOT NULL CHECK (
                    reserved >= 0 AND reserved <= on_hand
                )
            )
        '''))
        await conn.execute(text('''
            INSERT INTO inventory_lab VALUES (1, 1, 0)
            ON CONFLICT (product_id) DO UPDATE
            SET on_hand = 1, reserved = 0
        '''))
    start = asyncio.Event()
    tasks = [asyncio.create_task(attempt(start)) for _ in range(100)]
    start.set()
    outcomes = await asyncio.gather(*tasks)
    async with SessionFactory() as db:
        row = (await db.execute(text(
            'SELECT on_hand, reserved FROM inventory_lab WHERE product_id=1'
        ))).one()
    print({'successes': sum(outcomes), 'balance': tuple(row)})
    assert sum(outcomes) == 1
    assert tuple(row) == (1, 1)
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
```

Run it from the repository root using module syntax:

```bash
python -m scripts.race_inventory
```

The expected outcome is one successful reservation. Pool limits mean not all 100 transactions run at exactly the same instant; that is realistic bounded concurrency. Later run an API-level race with distinct authenticated buyers and compare database state with returned orders. This database lab alone cannot prove checkout idempotency or authorization.

## 3.6 Diagnose waits, pool exhaustion, and deadlocks

Useful PostgreSQL inspection query in your lab:

```sql
SELECT pid, state, wait_event_type, wait_event,
       now() - query_start AS duration, left(query, 120) AS query
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY query_start;
```

`pg_blocking_pids(pid)` helps identify blocking sessions. Long transactions can retain locks even when they are not actively executing SQL. Inspect transaction age, not just individual query duration.

Retry deadlocks or serialization failures only by rerunning the entire transaction with a bounded count, fresh transaction state, and jitter. Do not retry arbitrary integrity violations such as duplicate email.

**Checkpoint:** You can show a query improvement with evidence, explain why inventory cannot oversell in your implementation, and locate a blocking database session.

---

# Chapter 4 — Measure P50, P95, and P99 with Locust

## 4.1 What a percentile tells you

Sort measured request durations from fastest to slowest. P50 is the median; P95 and P99 describe the slow tail. A P99 near 800 ms means approximately 99% of the recorded durations were at or below 800 ms. It does not mean every user experiences 800 ms, and it does not bound the remaining 1%.

For 10,000 completed requests, roughly 100 fall above the 99th-percentile boundary, subject to the percentile definition and repeated values. With 100 requests, the tail is represented by about one observation: that is weak evidence. Locust groups/buckets durations internally, so its percentile values are estimates, not a list of exact raw timings.

Averages conceal the tail. If 99 requests take 20 ms and one takes 5 seconds, the average is 69.8 ms. The average can look acceptable while a user encounters a multi-second delay.

Also report failures and timeouts. A service can show lower latency because it rejects requests immediately. That is not an improvement in successful throughput.

## 4.2 Distinguish client timing from server timing

Locust measures HTTP behavior from its load-generator location. Application timing measures a narrower server interval. Browser page rendering, JavaScript execution, and all follow-on resource requests are not automatically included by `HttpUser`.

Use three complementary views:

| View | What it helps answer |
|---|---|
| Locust | What does the API client experience under this workload? |
| Server metrics | Which routes are slow and how does latency change over time? |
| Traces/query timing | Which component or wait contributes to the slow request? |

Do not expect client and server percentiles to match exactly. Their populations, aggregation windows, and measurement boundaries can differ.

## 4.3 Write a complete browsing workload

Prerequisites: Chapter 1's catalog lab is running on port 8000 with 10,000 seeded products. If adapting to your existing backend, change the endpoint and response contract explicitly.

**Complete lab file: `load-tests/locustfile.py`**

```python
import random
from locust import HttpUser, between, task

class CatalogUser(HttpUser):
    wait_time = between(1, 3)

    @task(4)
    def product_list(self):
        page = random.randint(1, 20)
        with self.client.get(
            '/api/v1/products',
            params={'page': page, 'page_size': 20},
            name='GET products page_size=20',
            timeout=5,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f'HTTP {response.status_code}')
                return
            try:
                payload = response.json()
                if not isinstance(payload.get('items'), list) or not payload['items']:
                    response.failure('Expected a non-empty items list')
            except ValueError:
                response.failure('Invalid JSON')

    @task(1)
    def product_detail(self):
        product_id = random.randint(1, 10000)
        with self.client.get(
            f'/api/v1/products/{product_id}',
            name='GET products/{id}',
            timeout=5,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f'HTTP {response.status_code}')
                return
            try:
                if response.json().get('id') != product_id:
                    response.failure('Incorrect product returned')
            except ValueError:
                response.failure('Invalid JSON')
```

This workload chooses the listing task approximately four times as often as detail. Since each task sends one request, it also approximates an 80/20 request mix. In a workflow with several requests per task, task weights do not directly equal endpoint traffic percentages.

The stable `name` groups detail URLs instead of creating thousands of statistics rows. Response validation catches successful HTTP responses containing the wrong data. `wait_time` represents user think time after a task.

The [Locust user guide](https://docs.locust.io/en/stable/writing-a-locustfile.html) documents `HttpUser`, task weights, naming, and response validation. The workload choices above are course examples; adapt them to observed or stated user behavior.

## 4.4 Run a smoke test and learn the UI

```bash
locust -f load-tests/locustfile.py --host http://127.0.0.1:8000
```

Open `http://localhost:8089` and start with 10 users, spawning 2 users per second. Let the run continue for several minutes. Inspect request count, failures, requests/sec, median, and percentile statistics. Depending on the installed Locust release, use the statistics table, HTML report, or exported CSV for P99.

Do not begin by spawning 1,000 users in one second. First establish that every scripted request succeeds at low traffic. Authentication mistakes or nonexistent product IDs will otherwise dominate the result.

## 4.5 Run a repeatable headless test

Keep the API and Locust in separate terminals. Run the API without `--reload`, initially with one worker. The same-machine test is useful for learning but CPU contention between client and server limits capacity claims.

```bash
mkdir -p artifacts/locust
locust -f load-tests/locustfile.py \
  --host http://127.0.0.1:8000 \
  --headless --users 100 --spawn-rate 5 --run-time 10m \
  --csv artifacts/locust/baseline_100 \
  --csv-full-history --html artifacts/locust/baseline_100.html
```

`--users 100` is a virtual-user population. `--spawn-rate 5` means five users are started per second. It is not five HTTP requests per second. The run contains about 20 seconds of ramp-up, plus the remaining steady period. The final summary includes that ramp unless you deliberately reset or select a stable measurement window. For cache experiments, warm the cache in a separate run and label warm/cold results accurately.

Read your installed `locust --help` and [configuration reference](https://docs.locust.io/en/stable/configuration.html) when checking flags. The key output is `baseline_100_stats.csv`; the history file shows changes over time. Save failure/exception reports when produced by your version.

## 4.6 Read the CSV and define an initial gate

**Complete lab file: `scripts/check_locust.py`**

```python
import csv
import sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: python scripts/check_locust.py PATH_stats.csv')

# Illustrative local budgets. Recalibrate from requirements and a stable baseline.
budgets_ms = {
    'GET products page_size=20': 800,
    'GET products/{id}': 500,
}
with open(sys.argv[1], newline='', encoding='utf-8') as handle:
    rows = {row['Name']: row for row in csv.DictReader(handle)}

problems = []
for name, budget in budgets_ms.items():
    if name not in rows:
        problems.append(f'Missing statistics: {name}')
        continue
    row = rows[name]
    count = int(row['Request Count'])
    failures = int(row['Failure Count'])
    failure_ratio = failures / count if count else 1.0
    raw_p99 = row.get('99%', '')
    if not raw_p99:
        problems.append(f'Missing 99% column/value for {name}')
        continue
    p99 = float(raw_p99)
    print(f'{name}: n={count}, P99={p99:.0f} ms, failures={failure_ratio:.2%}')
    if count < 1000:
        problems.append(f'{name}: insufficient samples for this lab gate')
    if failure_ratio > 0.01:
        problems.append(f'{name}: failure ratio exceeds 1%')
    if p99 > budget:
        problems.append(f'{name}: P99 exceeds {budget} ms')

if problems:
    raise SystemExit('\n'.join(problems))
print('Lab thresholds passed')
```

```bash
python scripts/check_locust.py artifacts/locust/baseline_100_stats.csv
```

Inspect the CSV headers before using this gate with a different Locust version. A 1,000-sample minimum is a teaching safeguard, not a statistical confidence guarantee. Repeat runs, longer windows, and tail confidence analysis are needed for stronger claims. CI performance gates belong on reasonably stable resources; a shared overloaded runner can create false regressions.

Do not average P99 from two workers or endpoints to get the overall P99. Combine the underlying distributions, or use Locust's aggregated statistics. Also keep endpoint-specific results: an overall percentile can hide a slow but rarely used checkout path.

## 4.7 Concurrency is not requests per second

A rough estimate for a closed workload with one request per iteration is:

```text
RPS ≈ virtual users / (mean response time + mean think time)
```

With 100 users, 100 ms response time, and 2 s think time, the rough rate is `100 / 2.1 ≈ 47.6 RPS`. With zero think time it could be much higher, until another limit is reached.

Locust's normal user model waits for requests to complete. When the server slows, those users send fewer new requests. This can conceal the queue pressure from a real workload whose arrivals continue independently. Record achieved throughput and consider an open-arrival tool/profile in advanced overload experiments. Do not claim a strict fixed arrival rate merely from a Locust user count or pacing function.

## 4.8 Choose experiments deliberately

| Test | Example lab setup | What to learn |
|---|---|---|
| Smoke | 10 users for 2 minutes | Script and API contract work |
| Baseline | 50 users for 10 minutes | Stable reference |
| Load | 100, 200, 400 users in separate runs | How latency grows with demand |
| Stress | Increase until a stated stop condition | First saturation/failure point |
| Spike | Rapid jump after a stable period | Burst behavior and recovery |
| Soak | Sustainable load for 1–2 hours locally | Leaks, connection retention, backlog growth |

Stop a lab when error rate, resource use, or queue backlog exceeds its predefined safe bound. Increasing users indefinitely while the server is already failing produces less useful evidence than diagnosing the first failure.

## 4.9 Explain a benchmark result

**Illustrative results, not measurements:**

| Run | RPS | P50 | P99 | Failures | Observation |
|---|---:|---:|---:|---:|---|
| 50 users | 24 | 35 ms | 160 ms | 0% | Healthy baseline |
| 200 users | 89 | 60 ms | 700 ms | 0% | Tail grows |
| 500 users | 95 | 900 ms | 4,800 ms | 3% | Throughput plateaus; queues build |

The important clue is the plateau: more concurrency adds waiting rather than useful throughput. Investigate the saturated resource. You have not yet shown that Redis or microservices is the correct fix.

## 4.10 Diagnose your 1,000-user run

A traceback beginning in `asyncio` or `SpawnProcess` does not identify the root cause. Preserve the final exception lines, preceding log messages, exact server command, Python version, and resource state. A reload supervisor or interrupted process can also produce such frames.

Use this sequence:

1. Reproduce with the normal server command, without `--reload`.
2. Confirm 10 users work and no scripted request repeatedly returns 401/404/422.
3. Run 50, 100, 200 users with a controlled ramp.
4. Capture application and PostgreSQL logs at the first failure.
5. Inspect pool timeouts, event-loop blocking, memory growth, connections, and generator CPU.
6. Change one variable and rerun the same workload.

| Symptom | Hypothesis | Next evidence |
|---|---|---|
| Pool timeout | Too much concurrent DB work or leaked sessions | Pool checkout wait; long transactions |
| High CPU, low DB load | Serialization, hashing, CPU code, generator saturation | Profile API and generator separately |
| Many DB lock waits | Hot rows or long transactions | Blocking sessions and transaction ages |
| Fast 401/422 responses | Invalid test/auth data | Inspect a single request/response |
| Increasing memory | Accumulated results, sessions, logs, backlog | Memory over time; allocation profiling |
| Connection/handle errors | OS/process limits or connection churn | Full error, connection counts, keep-alive behavior |
| Large page size worsens P99 | More SQL work, objects, JSON, and bytes | Compare page_size 20 and 200 separately |

Increasing the pool, worker count, OS limits, or switching framework before finding the failing layer can move the symptom and obscure its cause.

## 4.11 Expand from browsing to checkout

Allocate a distinct seeded account/cart per virtual shopper. Load credentials from a local test dataset; do not register a new user for every product read. Use `on_start` for login where appropriate, and decide whether login latency belongs in the measurement.

For each new order attempt generate a new idempotency key. For the retry experiment reuse the same key and same body. Mixing these two behaviors invalidates duplicate-order testing.

Track separate business counters for checkout accepted, out of stock, payment declined, payment unknown, and order confirmed. A deliberate out-of-stock response may be expected in a flash-sale test, but it is a failed assumption in a benchmark that promises stock to every buyer. Never mark every 409 response as a success without distinguishing the scenario.

Measure two latencies: HTTP checkout acceptance, and time until the order reaches its terminal business state. An asynchronous 202 response can be fast while orders remain stuck for minutes.

**Checkpoint:** You can run a repeatable test, interpret P99 with sample counts and errors, explain users versus RPS, and identify evidence needed to diagnose the first bottleneck.

**Deliverable:** `docs/benchmarks/001-monolith-baseline.md` plus raw CSV, workload, commit, configuration, and a written bottleneck hypothesis.

---

# Chapter 5 — Scale the monolith horizontally

## 5.1 What another process changes

A process has its own Python memory, event loop, clients, and connection pools. Adding a second process can use another CPU core and isolate some failures. It cannot make a saturated database faster, and it does not share an in-memory cart or lock with the first process.

First compare one versus two Uvicorn workers:

```bash
python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000 --workers 2
```

Keep the dataset and Locust scenario unchanged. Compare useful throughput, P99, errors, and total CPU. Do not compare a two-worker warm-cache run against a one-worker cold-cache run and credit the entire gain to process scaling.

## 5.2 Calculate the connection budget

With SQLAlchemy `pool_size=5` and `max_overflow=5`, a process can potentially use ten database connections. Three containers with two processes each can use sixty. Add workers, migrations, monitoring, and administration connections before comparing with PostgreSQL's configured limit.

```text
possible API connections = containers × processes per container × (pool size + overflow)
```

This is an upper bound, not a promise that all connections are active. Reducing pools may improve stability by limiting admitted database work. A connection pool is a queueing/control mechanism as well as a reuse optimization.

## 5.3 Put two containers behind a proxy

Create `server/Dockerfile` from the repository root build context:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.lock.txt /app/requirements.lock.txt
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY server /app/server
RUN useradd --create-home appuser
USER appuser
CMD ["python", "-m", "uvicorn", "server.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

For the first lab the combined lock is acceptable. Later split runtime and developer dependencies so load-test/test packages are not in the API image. Add a `.dockerignore` that excludes secrets, virtual environments, local artifacts, and Git metadata.

**Complete extension: `compose.scale.yml`**

```yaml
services:
  api1:
    build:
      context: .
      dockerfile: server/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://shop:local_lab_password@postgres:5432/shop
    depends_on:
      postgres:
        condition: service_healthy
  api2:
    build:
      context: .
      dockerfile: server/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://shop:local_lab_password@postgres:5432/shop
    depends_on:
      postgres:
        condition: service_healthy
  proxy:
    image: nginx:stable-alpine
    ports:
      - '127.0.0.1:8080:80'
    volumes:
      - ./infrastructure/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api1
      - api2
```

**Complete lab file: `infrastructure/nginx.conf`**

```nginx
 events { worker_connections 1024; }
 http {
   upstream shop_api {
     server api1:8000 max_fails=1 fail_timeout=5s;
     server api2:8000 max_fails=1 fail_timeout=5s;
     keepalive 32;
   }
   server {
     listen 80;
     location / {
       proxy_pass http://shop_api;
       proxy_http_version 1.1;
       proxy_set_header Connection "";
       proxy_set_header Host $host;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_connect_timeout 1s;
       proxy_read_timeout 5s;
     }
   }
 }
```

```bash
docker compose -f compose.lab.yml -f compose.scale.yml up -d --build
curl -f 'http://127.0.0.1:8080/api/v1/products?page_size=20'
```

Point Locust at port 8080. These upstreams use simple static container names; after container replacement, proxy DNS/address refresh behavior matters. For this lab restart/reload the proxy when upstream addresses change. Production discovery should handle that explicitly. Proxy read timeouts are not the same as a strict end-to-end request deadline.

## 5.4 Practice failure and shutdown

While a controlled browsing test runs:

```bash
docker compose -f compose.lab.yml -f compose.scale.yml stop api1
docker compose -f compose.lab.yml -f compose.scale.yml start api1
```

Record transient errors and recovery. A passive health check can send some traffic to a failed upstream before marking it unavailable. Do not promise zero errors from this configuration.

Separate probe meanings:

- Liveness: the process can make progress; a shared database outage should not necessarily trigger restart loops.
- Readiness: this instance can serve its required workload; a required database dependency can make it unready.
- Startup: initialization is still in progress; later used with Kubernetes.

**Checkpoint:** Any instance can serve any valid request; local state does not determine correctness; scaling measurements account for multiplied pools and proxy behavior.

---

# Chapter 6 — Redis caching with failure behavior

## 6.1 Decide whether a cache is the next useful change

Suppose traces show product-detail reads repeatedly query unchanged rows and database reads consume substantial capacity. Cache-aside can help: check Redis, fetch from PostgreSQL on a miss, then save the result briefly.

Caching shifts the problem from only query performance to freshness, invalidation, memory limits, and outage behavior. A single indexed query already taking 2 ms may not justify this complexity.

## 6.2 Add Redis to the lab

Install `redis`, update your lock, and add a service to a Compose extension:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - '127.0.0.1:6379:6379'
    command: ['redis-server', '--maxmemory', '128mb', '--maxmemory-policy', 'allkeys-lru']
```

This is a disposable cache. Do not put payment records or the only copy of a cart into a cache configured to evict arbitrary keys. Persistence and eviction requirements depend on the data's role.

Create one async Redis client in application lifespan and close it at shutdown. Configure short connect/read timeouts and bound its pool. A cache outage should not leave every request waiting seconds before falling back to the database.

## 6.3 Implement one cached read

**Implementation pattern: integrate into the catalog module.** `read_product` below is a supplied async function that reads PostgreSQL and returns a JSON-serializable dictionary or `None`.

```python
import json
import random
from redis.asyncio import Redis
from redis.exceptions import RedisError

redis_client = Redis.from_url(
    'redis://127.0.0.1:6379/0',
    decode_responses=True,
    socket_connect_timeout=0.1,
    socket_timeout=0.1,
    max_connections=20,
)

async def cached_product(product_id, read_product):
    key = f'catalog:product:v1:{product_id}'
    try:
        cached = await redis_client.get(key)
        if cached is not None:
            try:
                return json.loads(cached)
            except (ValueError, TypeError):
                # Bad cache data must not become the authoritative answer.
                pass
    except RedisError:
        # Count cache errors and fall back. Do not print one log per request.
        pass

    value = await read_product(product_id)
    if value is not None:
        try:
            await redis_client.set(key, json.dumps(value), ex=random.randint(45, 60))
        except RedisError:
            pass
    return value
```

The socket deadlines are lab settings, not universal budgets. Tune from local network behavior and your total request deadline. JSON values must use serializable money/timestamp representations.

Instrument cache hits, misses, errors, and duration. If PostgreSQL is close to capacity, a Redis outage can cause a fallback stampede. Add admission limits or a defined degradation policy instead of assuming fallback is always harmless.

## 6.4 Understand invalidation races

After a successful product update commits, delete its cache key. If invalidation happens before commit, another reader may repopulate the old value. Even deleting after commit can race with an earlier slow reader that later writes stale data into Redis.

For browsing, a bounded stale period may be acceptable; state that policy. For stronger freshness, study versioned keys, version-aware writes, or event-driven invalidation. None of these should make cached price or stock authoritative during checkout. The purchase transaction validates current price/version and durable availability.

## 6.5 Create a stampede experiment

1. Choose one popular product and set a short TTL.
2. Send many concurrent reads as its key expires.
3. Measure how many database reads happen for one expiration.
4. Add per-process request coalescing as the first experiment.
5. Compare with a distributed single-flight lease if multiple replicas still overload the database.

A Redis lease needs a unique token, expiry, and token-checked release. A lease can expire while its owner is still running, so it does not by itself guarantee safe inventory mutation. Never replace transactional stock constraints with a cache lock just because it worked in one run.

## 6.6 Measure warm, cold, and unavailable states

Run the same Locust workload in three conditions: cache empty, cache warm, Redis stopped. Record P99, hit ratio, database queries/sec, failures, and memory. A fast warm-cache benchmark alone is insufficient.

**Checkpoint:** You can state maximum acceptable staleness, demonstrate invalidation, and explain what happens when Redis fails. See [Redis SET options](https://redis.io/docs/latest/commands/set/) for expiry/conditional writes.

---

# Chapter 7 — Background jobs with Celery and RabbitMQ

## 7.1 Separate job execution from business events

RabbitMQ is a broker that routes and buffers messages. Celery is a task-execution framework with task names, arguments, retries, and workers. A Celery message has a protocol; arbitrary JSON published to a RabbitMQ queue is not automatically a valid Celery task.

Use Celery for commands such as generating a receipt. Use explicit domain events such as `order.confirmed.v1` for facts that multiple services may consume. Later an event consumer can enqueue a Celery task. Give these pathways different queues and contracts.

## 7.2 Understand what becomes faster

Moving receipt generation out of checkout reduces synchronous response work. It does not make generation itself faster. Record queue wait plus processing time, and expose the receipt's status. Returning 202 means accepted for processing, not completed.

FastAPI's in-process background tasks can be useful for short best-effort work, but they are not a durable queue across process death. Financial or fulfillment work needs a durable intent and recovery mechanism.

## 7.3 Start a broker and a worker

Add this local-only Compose service:

```yaml
services:
  rabbitmq:
    image: rabbitmq:4-management
    environment:
      RABBITMQ_DEFAULT_USER: shop
      RABBITMQ_DEFAULT_PASS: local_broker_password
    ports:
      - '127.0.0.1:5672:5672'
      - '127.0.0.1:15672:15672'
    volumes:
      - shop_rabbit:/var/lib/rabbitmq
volumes:
  shop_rabbit:
```

A single broker node with a volume is not a highly available broker cluster. Explore quorum queues and multi-node behavior later, with deliberate node-loss tests.

```bash
python -m pip install celery
export CELERY_BROKER_URL='amqp://shop:local_broker_password@127.0.0.1:5672//'
```

**Complete lab file: `server/app/jobs.py`**

```python
import json
import os
from pathlib import Path
from uuid import UUID, uuid4
from celery import Celery

celery_app = Celery('shop', broker=os.environ['CELERY_BROKER_URL'])
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    task_ignore_result=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_delivery_mode='persistent',
    broker_transport_options={'confirm_publish': True},
)

@celery_app.task(name='shop.write_receipt')
def write_receipt(order_id, amount_minor):
    safe_id = str(UUID(order_id))
    if not isinstance(amount_minor, int) or amount_minor < 0:
        raise ValueError('amount_minor must be a non-negative integer')
    root = Path('artifacts/receipts')
    root.mkdir(parents=True, exist_ok=True)
    target = root / f'{safe_id}.json'
    temporary = root / f'{safe_id}.{uuid4().hex}.tmp'
    # The input is an immutable order snapshot for this laboratory.
    payload = {'order_id': safe_id, 'amount_minor': amount_minor, 'currency': 'INR'}
    temporary.write_text(json.dumps(payload, sort_keys=True), encoding='utf-8')
    os.replace(temporary, target)
```

Run a worker on Linux/WSL, from the repository root:

```bash
celery -A server.app.jobs:celery_app worker --loglevel=INFO --concurrency=2
```

Submit the same task twice from a second terminal with the same broker environment:

```bash
python -c "from server.app.jobs import write_receipt; write_receipt.delay('11111111-1111-4111-8111-111111111111', 19950)"
```

Inspect the one resulting JSON receipt. Atomic replacement makes repeated writes of the same snapshot converge on the same file content. This is a single-machine filesystem lab. Distributed workers need an appropriate shared/object-storage design, job status in a database, cleanup for abandoned temporary files, and protection against the same order ID being submitted with conflicting snapshots.

## 7.4 Acknowledge only what you mean

Publisher confirms tell the publisher that the broker accepted a publish according to its guarantees. Consumer acknowledgements tell the broker that a delivery can be removed. Neither means a customer received an email or an order was paid. See [RabbitMQ acknowledgement guidance](https://www.rabbitmq.com/docs/confirms).

Celery late acknowledgement changes when a task is acknowledged, but worker-child termination has important exceptions. `task_reject_on_worker_lost` can request redelivery in those cases; repeatedly crashing work can then loop. Introduce it only with poison-work detection and operational bounds. Python task exceptions should use explicit retry logic where appropriate. See [Celery task behavior](https://docs.celeryq.dev/en/stable/userguide/tasks.html).

Do not configure automatic retry for every exception. Retry transient network/availability errors with limits and jitter. Reject invalid schemas and impossible business operations for inspection.

## 7.5 The difficult side effect: sending email

A processed-task table alone cannot make an external email atomic:

- Mark done first, then crash before sending: email lost.
- Send first, then crash before marking done: retry may send twice.

Use the provider's idempotency support where available, a stable dispatch key, a delivery-status record, and reconciliation. If the provider cannot deduplicate, document that duplicate notification is possible. Do not advertise exactly-once delivery.

## 7.6 Worker capacity and backlog

If one job takes a mean 0.5 s, a two-slot worker's theoretical throughput is about four jobs/sec before other overhead. Run below saturation to preserve headroom. Inspect queue depth, oldest message age, running tasks, retries, and end-to-end completion time.

Prefetch controls how much work a worker reserves, not merely how many tasks it executes. With mixed long/short jobs, one queue can cause head-of-line effects; separate queues and worker pools when measurements justify it.

**Lab:** Enqueue a backlog, stop a worker, restart it, and inspect recovered work. Inject a transient failure and an invalid payload; verify they have different handling. Until Outbox is implemented, explicitly record the DB-commit/enqueue gap as a known limitation.

**Checkpoint:** Background work is observable and repeatable, retries have limits, duplicate delivery is safe for the chosen operation, and you can explain the remaining external-side-effect risk.

---

# Chapter 8 — Extract Notification as the first service

## 8.1 Why this boundary is a useful first experiment

Notification can be unavailable without making the durable order itself disappear. Extracting it teaches contracts, independent deployment, duplicate delivery, and failure isolation before you split the transactional inventory/order core.

It is still legitimate to leave notifications in the monolith if independent deployment adds no benefit. For this course, extraction is a controlled learning experiment with its own ADR.

## 8.2 Define ownership and a contract

The notification service owns preferences, delivery attempts, provider adapters, and delivery status. Ordering owns whether an order was confirmed. The notification service must not query or update the order database directly.

Create `docs/event-contracts/order-confirmed-v1.json` with an envelope such as:

```json
{
  "event_id": "0a034029-a816-416f-a870-2af7d94c1a73",
  "type": "order.confirmed.v1",
  "schema_version": 1,
  "aggregate_id": "11111111-1111-4111-8111-111111111111",
  "aggregate_version": 3,
  "occurred_at": "2026-09-29T18:00:00Z",
  "correlation_id": "checkout-7c85",
  "data": {
    "customer_id": "22222222-2222-4222-8222-222222222222",
    "total_minor": 19950,
    "currency": "INR"
  }
}
```

Choose how contact details are supplied: minimal event snapshot or an authenticated identity lookup. Document privacy, freshness, availability, and coupling. Do not copy entire customer or ORM objects into every event.

## 8.3 Scaffold the service

```text
services/notification/
  app/main.py
  app/consumer.py
  app/application.py
  app/providers.py
  app/db.py
  migrations/
  tests/
  Dockerfile
```

Use a separate database/user, even if the local database server is shared. Code has exclusive access to its own schema/data. Reusing a PostgreSQL server is not the same as sharing write ownership.

## 8.4 Migrate deliberately

1. Freeze and test the contract against producer and consumer fixtures.
2. Implement the consumer and a fake notification provider that records attempts.
3. Start in shadow mode if useful: consume and validate without actually sending.
4. Enable one real dispatch path, with a stable idempotency key across migration.
5. Stop the old dispatcher, reconcile pending work, and remove the temporary adapter.

Do not run two active email paths and assume subscribers will deduplicate one another.

## 8.5 Test independent operation

Stop Notification while confirming orders. Orders should reach their defined state; queued notifications should accumulate and recover. Restart with an older compatible consumer. Send a duplicate and an unknown optional field. An unknown incompatible event should be quarantined, not discarded silently.

**Checkpoint:** Independent deployment works, ownership is explicit, and Notification failure has a bounded business impact.

---

# Chapter 9 — Extract core services without hiding the cost

## 9.1 Define data ownership before moving code

| Service | Owns | May keep a projection of |
|---|---|---|
| Catalog | Product definition, current offer | Search metadata |
| Inventory | Stock, reservations, stock movements | Product identifier/SKU |
| Ordering | Order and item snapshots, checkout workflow | Payment/reservation outcomes |
| Payment | Provider attempts, verified events, refund records | Order amount/currency snapshot |
| Notification | Delivery/preferences | Notification content snapshot |

An order's item snapshot is intentional duplication, not a foreign service editing catalog data. The snapshot explains what the customer purchased even if a product name changes.

## 9.2 Choose synchronous versus asynchronous interaction

Use synchronous HTTP when a caller needs an immediate answer and can handle timeout/failure. Use events for durable facts and independent reactions. Use commands for requests directed at one responsible owner. RabbitMQ RPC is still a request/reply dependency and needs deadlines, correlation, and unknown-outcome handling.

There is no rule that all service communication must be HTTP or all must be events. Decide from business semantics. A network call cannot replace a local function without changing latency and failure behavior.

## 9.3 Implement an authenticated, bounded client

**Implementation pattern:** create this client at service startup, reuse it, and close it at shutdown.

```python
import httpx

inventory_http = httpx.AsyncClient(
    base_url='http://inventory:8000',
    timeout=httpx.Timeout(connect=0.3, read=0.8, write=0.5, pool=0.2),
    limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
)
```

HTTPX timeouts apply to phases of I/O; they are not a complete business deadline. Add an outer deadline, propagate remaining budget, authenticate the caller, and carry a stable command ID for mutations. Retry only when the operation supports it. See [HTTPX timeout semantics](https://www.python-httpx.org/advanced/timeouts/).

## 9.4 Move existing data safely

For a small learning database, a short documented maintenance window is a valid migration strategy: stop relevant writes, export/import owned data, validate counts/totals, switch the caller, and remove old write access.

For the advanced exercise, study snapshot plus change capture/backfill, a catch-up barrier, read verification, and a single-writer cutover. Uncoordinated dual writes create divergent copies. Rollback after new writes requires reconciliation, not merely pointing at the old database.

## 9.5 Add contract compatibility tests

Store representative requests/events in version control. Test old consumer against new producer output before rollout. Prefer additive optional fields when semantics are compatible; use a new event/API version for incompatible changes. Never silently change money units or the meaning of `confirmed`.

**Checkpoint:** Each service can deploy and migrate independently, calls have deadlines and identity, and cross-service workflows are ready to be expressed explicitly in Chapter 10.

---

# Chapter 10 — Distributed checkout, Saga, and payment uncertainty

## 10.1 The transaction you no longer have

In the monolith, reserving inventory and creating an order shared one PostgreSQL commit. After extraction, Ordering cannot commit Inventory's database. A process may crash between two successful service actions. A network timeout may hide a successful action.

A Saga models the business workflow as durable local transactions and compensating actions. Compensation is a new business operation, not a database rollback across the network. Refunding a captured payment leaves an audit trail and can itself fail.

For this course, use orchestration: Ordering persists workflow state and sends commands to Inventory and Payment. This makes the sequence and recovery behavior visible in one place. Choreography is a later comparison exercise.

## 10.2 Implement a durable workflow record

Create a Saga table in Ordering with `saga_id`, `order_id`, state, version, pending command ID, deadline, next retry time, and last failure category. Store a transition history with event/command IDs and timestamps.

| Current state | Input | Local transaction and next action |
|---|---|---|
| NEW | Checkout accepted | Save order; enqueue ReserveInventory |
| RESERVING | InventoryReserved | Save reservation token; enqueue CreatePayment |
| RESERVING | InventoryRejected | Mark order rejected |
| PAYING | PaymentSucceeded | Record payment evidence; enqueue ConsumeReservation |
| PAYING | PaymentDeclined | Enqueue ReleaseReservation |
| PAYING | PaymentTimeout | Mark uncertainty; enqueue status reconciliation |
| COMMITTING_STOCK | ReservationConsumed | Confirm order; emit OrderConfirmed |
| COMPENSATING | ReservationReleased | Complete failed/cancelled order |
| Any active state | Deadline exceeded | Reconcile actual state; compensate or escalate |

The table defines a teaching workflow. Real fulfillment may require additional capture/authorization and shipping steps.

Persist each state change and its next outgoing command in one local transaction using the Outbox from Chapter 11. Study the Saga first, but implement reliable publication before calling the distributed workflow complete.

## 10.3 Use identifiers for different jobs

| Identifier | Meaning |
|---|---|
| Request ID | One HTTP interaction |
| Trace ID | Distributed diagnostic trace |
| Correlation/Saga ID | One business workflow across attempts |
| Idempotency key | One logical client operation |
| Command ID | One logical action requested of a service |
| Event ID | One immutable event; reused on redelivery |
| Aggregate version | Sequence/version of a domain entity |

A retry creates a new network attempt, but should retain the logical command/idempotency identity. Do not use the changing request ID as the deduplication key for payment creation.

## 10.4 Handle late replies and cancellation races

A payment success may arrive after the reservation expired. Do not automatically recreate inventory or confirm an unavailable item. Reconcile whether stock can be reacquired safely; otherwise initiate refund or manual resolution according to policy.

A cancellation command can arrive before a delayed reservation command. If `release` simply does nothing when no reservation exists, the late `reserve` can create an orphan reservation. Inventory needs a durable terminal intent/tombstone or compatible command ordering/version rule that rejects the stale reserve.

Every participant therefore validates command identity, allowed state, and workflow version. Deduplicating only by transport message ID is insufficient when two different commands contradict each other.

## 10.5 Model the payment adapter

Expose an internal interface:

```text
create_attempt(order_id, amount_minor, currency, provider_idempotency_key)
lookup_attempt(provider_reference)
request_refund(payment_reference, amount_minor, refund_idempotency_key)
verify_and_parse_webhook(raw_body, headers)
```

First implement a fake provider whose outcome can be selected per test: success, decline, slow response, success with lost response, delayed webhook, duplicate webhook, and refund failure. Persist its attempt state so restarting the API does not change the meaning of an earlier payment.

Then add Razorpay **Test Mode** as an optional adapter exercise. Keep the order total server-owned, map local attempts to provider orders/payments, verify signatures on the backend, deduplicate events, and reconcile through provider lookup. A frontend success screen is not authoritative payment evidence. Use provider documentation for the exact signature input and webhook raw-body rules; do not reuse checkout-signature validation as webhook validation.

See [Razorpay Standard Checkout integration](https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/integration-steps/) and the provider's linked webhook/verification documentation. This chapter is a test integration exercise, not a real-money deployment procedure.

## 10.6 Make transition updates race-safe

Use an optimistic version check or row lock around each local state transition:

```sql
UPDATE order_sagas
SET state = :next_state, version = version + 1, updated_at = now()
WHERE saga_id = :saga_id
  AND state = :expected_state
  AND version = :expected_version
RETURNING saga_id;
```

No returned row means another transition may have won. Reload state and classify the incoming event as duplicate, stale, conflicting, or still applicable. Do not blindly retry the same invalid transition forever.

## 10.7 Build a reconciliation loop

A periodic worker selects workflows whose next action/deadline is due, claims them safely, and checks their authoritative participant states. It records findings, emits idempotent corrective commands, and reschedules with limits. A timer firing late must still be safe.

Expose an operator view with order, reservation, payment, outstanding command, retries, and timeline. Manual recovery actions should be audited and idempotent. Avoid direct database edits as the normal support workflow.

## 10.8 Failure matrix

| Injection point | Required recovery |
|---|---|
| Crash after order commit, before publish | Outbox later publishes reserve command |
| Inventory reserves, reply is lost | Retry returns existing reservation |
| Payment succeeds, HTTP response is lost | Lookup/webhook confirms existing attempt; no new charge |
| Cancellation races payment success | State policy chooses fulfillment or refund; no silent ambiguity |
| Refund request times out | Reconcile existing refund using stable identity |
| Consumer receives duplicate success | One state transition and one next command |

**Checkpoint:** Restarting any participant does not erase workflow state. Every unknown outcome has a reconciliation path, and every compensation has its own failure behavior.

---

# Chapter 11 — Reliable events with Outbox and Inbox

## 11.1 Reproduce the dual-write failure

An unsafe implementation commits an order and then publishes `order.created`. Kill it between the two operations: the order exists but no consumer knows. Publishing before commit creates the opposite problem: consumers react to an order that might roll back.

Outbox solves this local atomicity problem by writing business data and an outgoing message record in the same database transaction. A separate relay publishes later. It does not eliminate duplicate publication.

## 11.2 Define a reliable event envelope and topology

Use Chapter 8's envelope. Validate schema and keep stable event IDs. Distinguish domain events from directed commands.

| Exchange | Routing key example | Consumer queue |
|---|---|---|
| `shop.events` (topic) | `order.confirmed.v1` | `notification.order-confirmed.v1` |
| `shop.events` (topic) | `catalog.product-updated.v1` | `search.product-updated.v1` |
| `shop.commands` (direct/topic) | `inventory.reserve.v1` | `inventory.commands.v1` |

Each subscriber gets its own queue for pub/sub. Multiple consumers on the same queue compete for messages; they do not each receive every event. Bindings, durable queue settings, message persistence, publisher confirms, and consumer acknowledgements address different concerns.

## 11.3 Create the Outbox schema

**SQL pattern for the owning service's migration:**

```sql
CREATE TABLE outbox_events (
    event_id UUID PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    aggregate_version BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ,
    attempts INTEGER NOT NULL DEFAULT 0,
    lease_owner UUID,
    lease_until TIMESTAMPTZ
);
CREATE INDEX idx_outbox_pending
ON outbox_events (created_at, event_id)
WHERE published_at IS NULL;
```

The application constructs the event from the committed business decision. The event record and aggregate update are inserted together through one transaction, not two independent commits.

## 11.4 Claim batches without keeping row locks during network I/O

A relay can claim a short lease, commit that claim, publish outside the transaction, then mark the row published if it still owns the claim.

```sql
WITH candidates AS (
    SELECT event_id
    FROM outbox_events
    WHERE published_at IS NULL
      AND (lease_until IS NULL OR lease_until < now())
    ORDER BY created_at, event_id
    LIMIT 100
    FOR UPDATE SKIP LOCKED
)
UPDATE outbox_events AS o
SET lease_owner = :relay_id,
    lease_until = now() + interval '30 seconds',
    attempts = attempts + 1
FROM candidates AS c
WHERE o.event_id = c.event_id
RETURNING o.*;
```

Tune lease duration, batch size, renewal, and timeouts together. With two relays, a slow publisher can outlive its lease and publish a duplicate. That must be safe. `SKIP LOCKED` improves competing relay throughput but does not ensure strict per-aggregate event order.

Use publisher confirms and ensure unroutable messages are detected, for example with mandatory routing/returned-message handling as supported by your client. Marking an unroutable event delivered loses the business notification even if the broker accepted the publish.

After confirmed publication:

```sql
UPDATE outbox_events
SET published_at = now(), lease_owner = NULL, lease_until = NULL
WHERE event_id = :event_id AND lease_owner = :relay_id;
```

If a crash occurs after the broker accepted the message but before this update, the next relay republishes the same event ID. That is the expected duplicate window.

## 11.5 Make consumers transactional

**Inbox table:**

```sql
CREATE TABLE inbox_events (
    consumer_name TEXT NOT NULL,
    event_id UUID NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (consumer_name, event_id)
);
```

Consumer algorithm:

1. Begin a local database transaction.
2. Insert the inbox identity with `ON CONFLICT DO NOTHING RETURNING event_id`.
3. If no identity was inserted, this consumer has already handled it; finish and acknowledge.
4. Otherwise validate aggregate state/version and apply the local mutation.
5. If another action is needed, write its outbox record in this same transaction.
6. Commit, then acknowledge the broker delivery.

If the mutation fails, the transaction including the inbox insert rolls back. If the consumer crashes after commit but before ack, redelivery finds the inbox row and becomes a no-op.

This protects local database effects. It does not make a remote email/payment call atomic with the inbox; represent that as another durable dispatch with provider idempotency/reconciliation.

## 11.6 Handle ordering according to event semantics

For complete product snapshots, the search consumer can ignore versions older than its last applied version. For events expressing deltas, skipping a missing version can corrupt the result. Buffer, fetch an authoritative snapshot, or route/serialize per aggregate and reconcile gaps according to the domain.

Exactly-once transport is not the guarantee to aim for here. The goal is repeated delivery with correctly deduplicated business effects and a recoverable history.

## 11.7 Retries, quarantine, and replay

Separate transient failures from invalid events. Transient failures get bounded delayed retries. Invalid schema, unsupported versions, or repeated deterministic failures go to a quarantine/DLQ with reason, payload reference, original event ID, attempts, and timestamps.

Broker dead-letter queues do not automatically capture every failed Celery task. Configure the behavior for the actual task/event path and verify it with a poison-message test.

Replay keeps the original event identity when redelivering the same fact. If correcting the business fact, issue a new corrective event with a link to the original. Review inbox-retention policy before replaying old archives.

## 11.8 Prove the guarantee with crash points

Add local fault switches that terminate the relay/consumer at four points: before publish, after publish before marking, before consumer commit, and after commit before ack. Verify committed work eventually reaches the intended state once, despite repeated deliveries.

Monitor oldest pending outbox age, pending count, relay attempts, inbox duplicates, quarantine depth, and end-to-end event delay. A small queue can still contain one critically stuck message.

**Checkpoint:** You can draw each crash window, explain what is duplicated or retried, and recover a deliberately quarantined event without inventing a new business action.

---

# Chapter 12 — API gateway, identity, and edge behavior

## 12.1 Distinguish the jobs at the edge

A reverse proxy forwards HTTP traffic. A load balancer distributes it across backends. An API gateway can apply authentication, routing, quotas, and other API policy. One product can perform several roles, but business ownership should remain clear.

Use the Chapter 5 proxy first. Add a Python/FastAPI gateway only if you need behavior that justifies maintaining application code there. Every extra network hop introduces timeouts, connection pools, logging, deployment, and failure modes.

## 12.2 Specify routing and trust

Create `docs/api-contracts/edge-routing.md`:

| Public prefix | Owner | Edge policy |
|---|---|---|
| `/api/v1/auth` | Identity | Tight abuse protection |
| `/api/v1/products` | Catalog | Public read; protected admin write |
| `/api/v1/orders` | Ordering | Authenticated; ownership checked by Ordering |
| `/api/v1/payments/webhooks` | Payment | Provider-signature validation; body preserved |
| `/api/v1/search` | Search | Query limits and cost-aware rate limits |

Decide who may set forwarded headers and user identity headers. Strip untrusted client-supplied identity headers before adding trusted identity metadata. Backend authorization must not rely on an arbitrary `X-User-ID` supplied over a publicly accessible port.

For separate services, use verified tokens or a deliberate service-to-service identity mechanism. Rotate keys and cache verification keys with a defined refresh policy. A shared gateway secret alone does not encode end-user ownership permissions.

## 12.3 Configure bounded behavior

Set request-body and header limits, appropriate upstream timeouts, allowed CORS origins, TLS, and access logs. CORS is a browser policy, not authorization. Do not forward payment credentials or tokens into logs.

For payment webhooks, preserve the original request bytes for signature verification. Parsing and reserializing JSON can change the signed bytes. For large uploads, use direct object-storage upload rather than extending gateway deadlines indefinitely.

Define the client error contract:

```json
{
  "error": {
    "code": "DEPENDENCY_TIMEOUT",
    "message": "The request could not be completed in time.",
    "request_id": "8e6c71b87a424671aee38ce1d4f4cd33"
  }
}
```

Do not expose stack traces, internal hosts, or SQL in responses. Preserve a request ID so operators can find details internally.

## 12.4 Test the edge as a component

Send an invalid token, oversized body, forged identity header, expired webhook signature, unavailable upstream, and slow response. Verify the status and error contract. Test that a retryable GET and a non-idempotent POST are not automatically retried under identical assumptions.

**Checkpoint:** Every public route has an owner and trust policy. Gateway failure is observable; service-level authorization still protects the data.

---

# Chapter 13 — Search projections and eventual consistency

## 13.1 Identify what transactional search cannot comfortably answer

Exact product lookup and simple filters often work well in PostgreSQL. Full-text ranking, language analysis, typo tolerance, and complex faceting may justify a separate search engine. Learn the requirement before installing one.

Start with PostgreSQL text search or a simple indexed query. Measure search quality as well as latency: a fast result list containing irrelevant products is not a successful search implementation.

## 13.2 Build a projection with OpenSearch or Elasticsearch

Choose one engine and follow its version-specific local setup. Keep it private; do not expose an unsecured search port. Define a product document containing product ID, searchable name/description, category, filterable fields, display price snapshot, active flag, and catalog version.

Set mappings deliberately: analyzed text for full text; keyword fields for exact filters; numeric types for range filters. Do not send arbitrary metadata and rely on unbounded dynamic field creation.

Implement:

1. Catalog emits product-created/updated/deactivated events through Outbox.
2. Search consumes and validates each event.
3. Product ID is the stable document ID.
4. Apply only an applicable version, including deletion/deactivation semantics.
5. Record applied version and event lag.

The precise optimistic-versioning API differs between engines and clients. Wrap it in a small adapter and test stale updates against your chosen version.

## 13.3 Design rebuilding before relying on the index

A projection must be rebuildable. Create a fresh index, backfill authoritative catalog snapshots, consume concurrent changes using a defined watermark/catch-up scheme, validate counts and representative results, then switch a read alias.

A naive backfill can overwrite newer events with older rows or resurrect deleted products. Include version comparisons and deletion/tombstone behavior. Keep the previous index temporarily for rollback only if it remains compatible with current writes.

## 13.4 Separate browsing truth from checkout truth

Search may display stale stock or price. At checkout, Inventory and Catalog/Ordering policy validate the authoritative purchase data. Return a clear price/availability change response if the earlier view is no longer valid.

## 13.5 Laboratory

Update a product name and measure time until search returns it. Stop the consumer and observe stale search plus projection lag. Resume and verify catch-up. Replay an older update after a newer one. Delete a product during backfill and verify it does not reappear.

**Checkpoint:** The projection can be rebuilt; update/delete ordering is tested; freshness is measurable; a search outage does not corrupt transactional state.

---

# Chapter 14 — Logs, metrics, tracing, and P99 in operation

## 14.1 Ask different questions of each signal

Logs explain individual events. Metrics summarize a population over time. Traces connect the steps of one distributed operation. Use all three to move from a symptom such as high checkout P99 to evidence about SQL, queueing, or a remote dependency.

Keep request, trace, event, and order identifiers in logs/traces where useful. Do not use order IDs, user IDs, or raw product URLs as metric labels; that creates unbounded time-series cardinality.

## 14.2 Add structured request logs

Emit JSON to stdout with service, environment, severity, timestamp, method, normalized route, status, duration, request ID, and trace ID where available. Validate incoming request IDs before accepting them, or generate your own. Exclude access tokens, passwords, payment secrets, and unnecessary personal data.

Ship logs asynchronously via the platform/agent to a log backend. Avoid making every API request synchronously write to Elasticsearch: a logging outage could then become an application outage. Bound log queues and define drop/sampling behavior for low-priority logs.

## 14.3 Add a concrete latency histogram

Install `prometheus-client`. This middleware is for the simple one-process-per-container lab. With multiple Python worker processes, use an explicit multiprocess collection strategy or independent scrape endpoints; otherwise `/metrics` may expose only whichever worker answered.

**Complete lab file: `server/app/metrics.py`**

```python
import time
from prometheus_client import Counter, Histogram

REQUESTS = Counter(
    'shop_http_requests_total', 'HTTP requests handled',
    ['method', 'route', 'status'],
)
DURATION = Histogram(
    'shop_http_request_duration_seconds', 'ASGI request duration',
    ['method', 'route'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 2, 5, 10),
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['path'] in (
            '/metrics', '/health/live', '/health/ready'
        ):
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status = 500

        async def instrumented_send(message):
            nonlocal status
            if message['type'] == 'http.response.start':
                status = message['status']
            await send(message)

        try:
            await self.app(scope, receive, instrumented_send)
        finally:
            route = getattr(scope.get('route'), 'path', '__unmatched__')
            method = scope['method']
            REQUESTS.labels(method, route, str(status)).inc()
            DURATION.labels(method, route).observe(time.perf_counter() - started)
```

**Add to the Chapter 1 `main.py`:**

```python
from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from server.app.metrics import MetricsMiddleware

app.add_middleware(MetricsMiddleware)

@app.get('/metrics', include_in_schema=False)
async def metrics():
    return Response(generate_latest(), headers={'Content-Type': CONTENT_TYPE_LATEST})
```

This measures downstream ASGI handling until it returns, which can include response sending and cleanup. It is not identical to Locust's network measurement. If a streaming response fails after headers, the recorded status may still be the already-sent status; add explicit exception/stream completion telemetry for that use case.

## 14.4 Scrape each instance directly

**Configuration: `infrastructure/prometheus.yml`**

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: shop-api
    static_configs:
      - targets: ['api1:8000', 'api2:8000']
```

Run Prometheus on the same Compose network with this file mounted and publish its UI only on the loopback interface for the lab. Scrape application instances directly, not just the load balancer, so every process is represented. Connect Grafana to Prometheus as a data source.

Use these queries for the custom metrics above:

```promql
# Requests/sec by route
sum by (route) (rate(shop_http_requests_total[5m]))
```

```promql
# Approximate P99 in seconds by route, combined across instances
histogram_quantile(
  0.99,
  sum by (le, route) (rate(shop_http_request_duration_seconds_bucket[5m]))
)
```

```promql
# Fraction of requests returning 5xx
sum(rate(shop_http_requests_total{status=~"5.."}[5m]))
/
sum(rate(shop_http_requests_total[5m]))
```

Classic histogram percentiles depend on bucket boundaries and interpolation. Place buckets near the latency targets you want to distinguish. Aggregate buckets before calculating the quantile. An average of per-instance P99 values is not the service P99. See [Prometheus histograms](https://prometheus.io/docs/practices/histograms/).

A no-traffic interval can produce an undefined ratio; treat it deliberately in dashboards/alerts rather than hiding it with a misleading success value.

## 14.5 Trace one checkout

Start with local console traces before operating a tracing backend:

```bash
python -m pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install
OTEL_SERVICE_NAME=shop-api OTEL_TRACES_EXPORTER=console OTEL_METRICS_EXPORTER=none OTEL_LOGS_EXPORTER=none \
  opentelemetry-instrument python -m uvicorn server.app.main:app --port 8000
```

This uses installed instrumentation discovery; lock the resulting instrumentation versions. It is a lab process-launch pattern, not an instruction to install dynamically at production startup.

Next point the OTLP exporter to a configured collector/backend and view traces in Jaeger or Tempo. Instrument HTTP clients, SQL, broker publishing/consumption, and custom business spans such as `reserve_inventory` and `reconcile_payment`. Verify context crosses process/message boundaries; merely logging the same order ID is not full trace propagation.

Use [OpenTelemetry's Python guide](https://opentelemetry.io/docs/languages/python/getting-started/) to align SDK/exporter configuration with your selected versions. Avoid duplicate spans from enabling both automatic and manual instrumentation for the same operation.

## 14.6 Create dashboards that support diagnosis

| Dashboard | Panels |
|---|---|
| API | RPS, P95/P99, errors, in-flight requests, process CPU/memory |
| Database | Connection usage/wait, transactions, slow SQL, lock waits, I/O |
| Messaging | Queue depth, oldest age, publish errors, retries, DLQ |
| Checkout | Acceptance rate, confirmation delay, unknown payments, expired reservations |
| Reliability | Outbox lag, stuck Saga count, failed compensations, restore status |

Start alerts with user-visible symptoms and durable-work delay. A CPU alert without context may simply mean the system is productively busy. Every alert should link to a short runbook explaining how to inspect and mitigate it.

**Lab:** Add a controlled delay to one dependency. Use Locust to observe the tail increase, metrics to identify the route, and a trace to identify the slow child span. Remove the delay and verify recovery.

**Checkpoint:** You can follow one order across processes and explain why client P99 and server histogram P99 differ.

---

# Chapter 15 — Resilience and bounded failure

## 15.1 Treat time as a budget

Suppose checkout acceptance has a 1.5 s target. It cannot spend 1 s in each of three sequential services and meet that target. Budget queueing, database work, network calls, serialization, and safety margin.

An outer application deadline bounds the whole operation. Each dependency timeout must fit within remaining time. Cancellation does not undo a remote action that already committed; after a mutation timeout, reconcile by stable command identity.

## 15.2 Implement a safe retry policy

**Implementation pattern:** retry only classified transient errors for an idempotent operation.

```python
import asyncio
import random

async def bounded_retry(operation, transient_errors, attempts=3):
    for attempt in range(attempts):
        try:
            return await operation()
        except transient_errors:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(random.uniform(0, min(0.8, 0.1 * (2 ** attempt))))
```

Wrap the whole operation in its deadline and pass a deliberate tuple of exception classes. Do not include `BaseException`; cancellation must propagate. Do not blindly retry authentication failures, validation errors, out-of-stock, or every HTTP 500. Respect a dependency's overload/retry signal and your own remaining budget.

Three layers each retrying three times can create up to 27 downstream attempts. Choose one responsible retry layer and cap the total work.

## 15.3 Apply bulkheads and circuit breakers for observed problems

A bulkhead gives a dependency its own concurrency budget so it cannot consume every worker/connection. A semaphore inside one process is local; total concurrency is multiplied by replica count.

A circuit breaker stops repeated calls to a failing dependency, then allows limited probes after a recovery interval. Configure a minimum sample size, failure definition, open duration, and half-open limit. A breaker is not a fix for incorrect timeouts or missing idempotency.

Use a maintained implementation after validating its current API, or first build a small state-machine exercise without installing it in the critical path. Verify concurrency safety; a few module-global counters are not a distributed breaker.

## 15.4 Define degradation per business function

| Failure | Possible policy |
|---|---|
| Catalog cache unavailable | Bounded database fallback; reduce load if needed |
| Search unavailable | Basic catalog filter or explicit temporary error |
| Inventory unavailable | Do not promise unverified stock; pending workflow or controlled rejection |
| Payment status unknown | Reconcile; do not create a new charge blindly |
| Notification unavailable | Durable backlog with delivery delay shown internally |

A stale product description may be acceptable; invented payment success is not. Write the policy before fault injection.

## 15.5 Run a controlled game day

Choose one fault, a stop condition, and the observations to capture. Examples: stop Redis, stop a worker, add 500 ms dependency latency, hold an inventory lock, or restart one API instance.

Record detection time, user impact, retry amplification, backlog, mitigation, recovery time, and final data consistency. The goal is not merely to get green health checks again; verify no stuck orders, duplicate charges, or leaked reservations remain.

**Checkpoint:** Failure impact is bounded, retry behavior is measured, and a runbook can guide recovery without guessing.

---

# Chapter 16 — Distributed rate limits and overload control

## 16.1 Separate rate from concurrency

A rate limit controls requests over time. A concurrency limit controls in-flight work. A user making ten slow requests can consume more resources than another making ten fast requests. Sensitive or expensive endpoints often need both.

Choose keys deliberately: authenticated user, tenant, API credential, IP, or a combination. Trust forwarded IP headers only from known proxies. Shared networks mean IP-only limits can unfairly group unrelated users.

## 16.2 Implement an atomic fixed-window lab

Start with fixed-window counting because it is easy to reason about. It permits bursts around window boundaries; a token bucket/sliding-window refinement is the next exercise.

**Lua pattern executed atomically by Redis:**

```lua
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('PEXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('PTTL', KEYS[1])
if current > tonumber(ARGV[2]) then
  return {0, ttl}
end
return {1, ttl}
```

Use one key per principal and endpoint class, a window duration in milliseconds, and a maximum count. The window starts with the first request in this teaching version. Return `429` when denied and a non-negative rounded-up `Retry-After` in seconds. Bound key cardinality/retention so arbitrary unauthenticated values cannot grow memory indefinitely.

Lua avoids a crash gap between increment and setting expiration. Still define behavior when Redis errors: browsing may fail open with local protection, while login/checkout policy may fail closed or use a conservative fallback.

## 16.3 Test across replicas

Distribute one user's burst across `api1` and `api2`. The combined accepted count must respect the shared limit. Repeat using separate users to verify isolation. Test near expiry and Redis restart/eviction. Rate counters stored in an evicting cache can reset; use appropriate isolation/memory policy when limits must be strict.

## 16.4 Add queue admission

A bounded queue rejects or defers work when capacity is exhausted. An unbounded queue only turns immediate failure into delayed failure. Set maximum queue age and size, expose waiting status, and define cancellation/expiry for queued attempts.

**Checkpoint:** Limits have measurable fairness and failure behavior. Admission protects the expensive work rather than only throttling cheap HTTP responses.

---

# Chapter 17 — Database scaling, retention, and recovery

## 17.1 Diagnose which dimension needs scaling

Database pressure may come from inefficient queries, too much concurrent work, data larger than memory, lock contention, writes, or maintenance. A read replica helps eligible reads; it does not solve writes to one hot inventory row. Partitioning can simplify retention; it does not automatically accelerate queries that scan every partition.

Work in this order: query/schema optimization, bounded connections, caching where appropriate, retention/archival, replicas, partitioning where useful, then sharding only if justified.

## 17.2 Add a read replica laboratory

Use the replication procedure for your selected PostgreSQL version and isolated instances. Configure replication credentials, base backup, WAL retention, and monitoring. Keep the writer endpoint and reader endpoint distinct.

Classify each query:

| Query | Freshness requirement | Route |
|---|---|---|
| Inventory reservation | Authoritative mutation | Primary |
| Checkout/payment reconciliation | Current business state | Primary |
| Recently created order shown to creator | Read-after-write expected | Primary or explicit consistency mechanism |
| Older order history/analytics | Defined staleness acceptable | Replica candidate |

Pause replication or induce controlled lag. Create an order on the primary and immediately query the replica. Show the stale result. A fixed delay before routing to replicas is a heuristic, not a guarantee; lag can exceed it.

Measure replay lag and WAL retention. A disconnected replica can consume disk through retained WAL. Rehearse promotion/failover with a defined writer-fencing mechanism; two active writers are a data-consistency problem, not just a routing problem.

## 17.3 Partition a table for a real access pattern

A good first lab is an append-heavy audit/event table partitioned by month. Create time-range partitions and compare a bounded-time query with an unbounded one using `EXPLAIN`.

Before partitioning `orders`, consider uniqueness and foreign keys: PostgreSQL partitioned-table constraints have requirements around partition keys. If you need globally unique order IDs and many references, blindly changing the primary key to include date can ripple through the schema. Model that cost first.

Implement partition creation before the next period arrives, retention/archive checks before removing old partitions, and alerting for failed inserts due to missing ranges. Dropping old data requires a verified retention policy and restore path.

## 17.4 Study sharding as a ownership decision

A user-based shard key keeps many customer queries local but complicates cross-customer reports and hot users. A product-based inventory shard can make stock access local while orders span products on several shards.

Write routing rules, shard-key immutability policy, rebalancing plan, global ID scheme, cross-shard operation semantics, and backup/restore procedure before implementing a toy router. Do not add sharding merely because the dataset reaches a round number.

## 17.5 Rehearse restore, not just backup

A persistent container volume is not a backup. A backup is useful only if you can restore it to a separate target and verify the data.

For the Chapter 0 lab, create a logical backup from the host:

```bash
mkdir -p artifacts/backups
docker compose -f compose.lab.yml exec -T postgres \
  pg_dump -U shop -d shop -Fc > artifacts/backups/shop.dump
```

Restore to a **new disposable database**:

```bash
docker compose -f compose.lab.yml exec postgres createdb -U shop shop_restore_lab
docker compose -f compose.lab.yml exec -T postgres \
  pg_restore -U shop -d shop_restore_lab --exit-on-error < artifacts/backups/shop.dump
```

If that target already exists, choose another fresh name; do not overwrite a working database for the exercise. Check row counts, representative orders, inventory invariants, and application compatibility against the restored target. A database dump does not automatically include all cluster roles, external objects, secrets, or object-storage files.

Define RPO (how much recent data can be lost) and RTO (how long recovery may take). Later study base backups plus WAL archiving for point-in-time recovery and coordinated reconciliation across independently restored services.

**Checkpoint:** Scaling changes match a measured constraint, stale reads are handled deliberately, and at least one restoration has been verified.

---

# Chapter 18 — Product media, object storage, and CDN

## 18.1 Remove image bytes from the API path

The API should own metadata and access policy. Object storage owns bytes; a CDN can cache public variants near users. This reduces application bandwidth and worker work without changing order consistency.

Define an object record with immutable object key, owner/product association, size, media type, checksum where useful, upload status, and active variant references. Do not use a user's original filename directly as a trusted storage path.

## 18.2 Implement a two-step upload

1. Authenticated client requests an upload intent with expected size/type and product ownership.
2. Server allocates a unique object key and issues a short-lived constrained upload URL/policy.
3. Client uploads directly to storage.
4. Client calls finalize; server verifies object existence, allowed size/type/content as needed, and ownership.
5. Optional processing job validates/creates variants.
6. Only validated objects become visible in catalog metadata.

A signed URL is a bearer capability. Anyone who holds it can act within its permissions until expiry. Keep it out of public logs and scope it to one key/action. Enforce size/type constraints using the chosen storage operation and server-side finalization; a client-declared content type is not proof of file contents.

## 18.3 Cache with immutable names

Use content-versioned object keys for public product images. A new image receives a new URL; old immutable URLs can have long cache lifetimes. Define retention and garbage collection so abandoned uploads and replaced variants do not grow forever.

For private receipts/reports, use appropriate signed access and cache policy. Do not accidentally make private downloads public by using the same CDN behavior as product thumbnails.

## 18.4 Laboratory

Compare API-served and directly served media while measuring API CPU/network and client latency. Test expired URL, wrong object owner, interrupted upload, duplicate finalize, missing object, and processing failure. Verify deletion/replacement behavior in both storage and cached delivery.

**Checkpoint:** Media traffic bypasses API workers, incomplete uploads are not published, and cache invalidation follows a defined versioning policy.

---

# Chapter 19 — Kubernetes and safe deployment

## 19.1 Learn the control loop

A Pod runs containers. A Deployment declares a desired replica count and version. A Service gives stable discovery/routing to ready Pods. The cluster reconciles desired and actual state after failures.

Kubernetes does not automatically make application transactions correct, a database highly available, or a faulty migration reversible. Bring the same idempotency, probes, deadlines, and recovery behavior into this environment.

## 19.2 Prepare before applying manifests

Create a local kind/minikube cluster using its official installation instructions. Build/load the application image or publish it to a registry the cluster can access. Start with one process per API container for straightforward metrics and replica accounting.

The database URL inside a Pod must use a reachable database service/hostname. `127.0.0.1` inside the Pod refers to that Pod, not your laptop. Either deploy a disposable lab PostgreSQL instance with persistent storage or connect to a separately managed test database. Reapply the lab schema/migrations to that database and verify network/DNS access before enabling readiness checks.

In the cluster, create a namespace, database credential Secret, and image reference. Keep production credentials out of YAML/Git. Kubernetes Secret objects need appropriate access control and storage encryption policy; base64 encoding is not encryption.

## 19.3 Implement readiness without restart storms

**Add to the API; uses the Chapter 1 database engine:**

```python
import asyncio
from sqlalchemy.exc import SQLAlchemyError

@app.get('/health/ready', include_in_schema=False)
async def ready():
    try:
        async with asyncio.timeout(0.5):
            async with engine.connect() as connection:
                await connection.execute(text('SELECT 1'))
    except (TimeoutError, SQLAlchemyError):
        raise HTTPException(status_code=503, detail='Database unavailable')
    return {'status': 'ready'}
```

A saturated pool may make this probe fail. That can protect the instance, but if all instances fail together it can remove all serving capacity. Test the policy under overload. Liveness should usually check the process itself rather than a common remote dependency. Consult [Kubernetes probe behavior](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

## 19.4 Starting Deployment template

**Template: `infrastructure/kubernetes/api.yml`.** Prerequisites: namespace `shop-lab`, a reachable test database, Secret `shop-db` with key `DATABASE_URL`, image `shop-api:lab` loaded into the cluster, and the readiness endpoint above.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-api
  namespace: shop-lab
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: shop-api
  template:
    metadata:
      labels:
        app: shop-api
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: shop-api:lab
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: shop-db
                  key: DATABASE_URL
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: '1'
              memory: 512Mi
          startupProbe:
            httpGet:
              path: /health/live
              port: 8000
            failureThreshold: 30
            periodSeconds: 2
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: shop-api
  namespace: shop-lab
spec:
  selector:
    app: shop-api
  ports:
    - port: 8000
      targetPort: 8000
```

The resource values are initial lab settings. Measure actual memory/CPU, throttling, and restart behavior before selecting deployment budgets.

Useful commands after prerequisites:

```bash
kubectl apply -f infrastructure/kubernetes/api.yml
kubectl rollout status deployment/shop-api -n shop-lab
kubectl get pods -n shop-lab
kubectl port-forward service/shop-api 8000:8000 -n shop-lab
```

A port-forward is a development access path, not a realistic production load-balancer benchmark. Use ingress/Service access suited to the environment for scaling tests.

## 19.5 Practice compatible releases

Use an expand–migrate–contract sequence for schema changes:

1. Add a backward-compatible nullable column/table/index.
2. Deploy code that tolerates old and new schema/data states.
3. Backfill in bounded batches while measuring load.
4. Switch reads/writes under a defined single-owner policy.
5. Remove old fields only after older application versions can no longer run.

Run migration as a controlled deployment job, not once per replica startup. An application rollback does not reverse destructive schema changes.

Deploy a new immutable image version, inspect rollout, introduce a deliberately bad readiness response, and practice `kubectl rollout undo`. Check what happens to in-flight requests and long-running worker jobs during termination.

**Checkpoint:** Deployments, rollback, and Pod loss are practiced; readiness/liveness have distinct behavior; database compatibility survives mixed application versions.

---

# Chapter 20 — Autoscaling and backpressure

## 20.1 Understand the signal

CPU scaling helps CPU-bound workloads only when new replicas can receive traffic and downstream capacity exists. Waiting on a saturated database may create high latency with modest API CPU, so CPU-only scaling can miss the problem or make it worse.

For workers, backlog and oldest message age often reveal demand better than CPU. A backlog is not useful work capacity; you need the processing-time distribution and downstream rate limits to size workers.

## 20.2 Add a CPU HPA lab

Prerequisite: a functioning Metrics API/provider such as metrics-server and CPU requests on the Deployment.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: shop-api
  namespace: shop-lab
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: shop-api
  minReplicas: 2
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
```

A CPU utilization target is relative to CPU requests, not automatically to the container's limit. The controller operates periodically; new Pods need scheduling/startup/readiness time. See [Kubernetes HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).

Monitor with:

```bash
kubectl get hpa -n shop-lab -w
```

Run a sustainable ramp, then a spike. Record time from demand increase to ready capacity. If the spike finishes before scaling helps, minimum capacity, admission control, caching, or scheduled pre-scaling may be more useful.

## 20.3 Calculate a worker budget

For an illustrative queue with arrival rate 40 jobs/s and mean processing time 0.2 s:

```text
busy slots needed on average = arrival rate × mean service time = 8
slots at 65% utilization ≈ 8 / 0.65 = 12.3, so start by evaluating 13
```

This is a rough steady-state estimate. Tail job time, retries, heterogeneous work, I/O limits, and bursts can require a different budget. Validate by measuring queue age and completion times.

Use a queue metrics adapter or KEDA only after verifying its current broker/scaler configuration. Set a maximum constrained by database connections, provider quotas, and broker capacity. Do not allow worker autoscaling to flood a payment/email provider.

## 20.4 Measure recovery and scale-down

After load drops, verify the queue drains, replicas stabilize, tasks finish or requeue safely, and the database remains healthy. Aggressive scale-down can interrupt expensive jobs and create retry loops.

**Checkpoint:** Scaling improves the target SLI, respects downstream ceilings, and does not oscillate. You can state what happens before new capacity becomes ready.

---

# Chapter 21 — Flash-sale laboratory

## 21.1 Define success before building admission machinery

Scenario: 100 units and a very large burst of interest. Your local test may use 1,000–10,000 attempted buyers according to hardware. Keep the inventory-to-demand imbalance, but do not pretend a small test proves million-user capacity.

Define whether acceptance means a queue ticket, a reservation, or a confirmed sale. Define fairness: first arrived at which boundary, lottery, per-user limit, or another policy. Multiple distributed queues and retries do not preserve a universal first-come-first-served order by default.

## 21.2 Start with database correctness

Use the conditional reservation update from Chapter 3. Allocate unique test buyers and keys. Verify the durable inventory and order records after every run. Then observe contention and throughput.

Only introduce queued admission when direct admission creates a demonstrated bottleneck. The queue should be bounded, tickets should be durable enough for the promise made to users, and polling must not become a larger load than checkout itself.

## 21.3 Trace the state transitions

```mermaid
flowchart TD
  A[Purchase attempt] --> B{Already processed?}
  B -->|Yes| C[Return existing outcome]
  B -->|No| D{Admission available?}
  D -->|No| E[Reject or issue waiting status]
  D -->|Yes| F[Durably reserve stock]
  F --> G{Payment outcome}
  G -->|Success| H[Consume reservation and confirm]
  G -->|Decline or expiry| I[Release reservation]
  G -->|Unknown| J[Reconcile payment and reservation]
```

A Redis counter can be an admission optimization, but PostgreSQL/Inventory remains responsible for durable allocation in this course. If the counter and database diverge, reconciliation must prevent overselling. Counter decrement alone is not proof of a durable reservation.

## 21.4 Test more than the happy race

| Scenario | Invariant to verify |
|---|---|
| Duplicate clicks | One logical purchase per key |
| Same buyer uses new keys | Per-buyer purchase policy enforced separately |
| Worker crashes after reserve | Existing reservation recovered/released |
| Payment succeeds after expiry | Explicit reacquire/refund/review policy |
| Broker backlog exceeds deadline | Expired attempts do not buy silently later |
| Redis data lost | Durable stock cannot be oversold |
| Client never polls again | Server still reaches a valid terminal state |

Calculate active reservations plus completed consumption against original supply. Count out-of-stock/admission rejection separately from unexpected system errors. Measure queue wait and final outcome time, not just the fast ticket-creation endpoint.

**Checkpoint:** Confirmed sales never exceed supply, user-visible statuses have precise meanings, and restart/recovery tests leave no leaked reservations.

---

# Chapter 22 — Build a defensible million-user design

## 22.1 Translate users into workload

Registered users, daily active users, concurrent sessions, concurrent requests, and requests/sec are different quantities. Start with behavior assumptions.

**Illustrative capacity model:**

| Input | Assumption |
|---|---:|
| Daily active users | 1,000,000 |
| API requests per active user/day | 60 |
| Daily API requests | 60,000,000 |
| Average API RPS | 60,000,000 / 86,400 ≈ 694 |
| Peak factor | 10× |
| Estimated peak API RPS | ≈ 6,944 |
| Orders per day | 100,000 |
| Average order rate | ≈ 1.16/s |
| Order peak factor | 20× |
| Estimated peak order rate | ≈ 23.1/s |

Browse traffic and order writes have different scaling needs. Change the assumptions and see which component becomes limiting. Do not infer concurrent sessions directly from API RPS; think time and request duration matter.

## 22.2 Estimate storage and bandwidth

Suppose each order plus items, indexes, and audit allowance averages 5 KB in your measured schema. At 100,000 orders/day, that is approximately 500 MB/day before additional replicas/backups and unrelated data. Measure actual table/index sizes to replace the estimate.

Calculate separately:

- Primary tables and indexes.
- Replicas and backup retention.
- WAL, logs, traces, and event retention.
- Search projections.
- Object storage and CDN traffic.
- Network bytes per API request and peak egress.

Retention can dominate long-term cost. An unlimited log/event policy can consume more storage than the business records.

## 22.3 Convert measured capacity into a starting replica estimate

If one tested instance sustainably serves 300 RPS for the chosen workload and SLO, a crude estimate for 6,944 peak RPS at 65% of that measured ceiling is:

```text
ceil(6944 / (300 × 0.65)) = 36 instances
```

This arithmetic is only a starting model. Adding instances changes contention, connection count, cache hit rate, network, and downstream pressure. Validate the combined system and account for failure capacity. State whether the per-instance benchmark used the same dataset, endpoint mix, and resource limits.

## 22.4 Draw ownership and bottlenecks

```mermaid
flowchart TD
  U[Clients] --> G[Edge and gateway]
  U --> CDN[Media CDN]
  CDN --> O[Object storage]
  G --> C[Catalog and Search]
  G --> R[Ordering and Saga]
  G --> A[Identity and Cart]
  C --> CP[Catalog DB and search projection]
  A --> AP[Owned state stores]
  R --> RP[Order DB and Outbox]
  RP --> M[Message broker]
  M --> I[Inventory]
  M --> P[Payment]
  M --> N[Notification]
  I --> IDB[Inventory DB]
  P --> PDB[Payment DB]
```

This is an ownership sketch, not a full deployment design. Add API/event directions, reconciliation paths, security boundaries, high availability, and telemetry separately so one diagram does not become unreadable.

For every component ask: What is its measured ceiling? What happens when one instance/node fails? Is the state durable? What can be rebuilt? Where can traffic be rejected safely? Which consistency guarantee matters?

## 22.5 Submit a design review package

Produce a capacity spreadsheet or Markdown calculation table, workload assumptions, architecture diagrams, benchmark evidence, failure reports, restore results, and a list of unresolved risks.

Classify each claim as **measured**, **calculated from assumptions**, or **not yet validated**. A diagram with microservices and Kubernetes is not proof of capacity or availability.

**Checkpoint:** You can defend every major component, estimate, scaling threshold, and consistency trade-off using the experiments from earlier chapters.

---

# Appendix A — Turn the handbook into a weekly development routine

## A.1 Start from the code you already have

Do not rebuild a working backend merely to match these folder names. Inspect your existing implementation against the Chapter 1 invariants and contracts. Mark each requirement as implemented, missing, or uncertain. An uncertain feature needs a targeted test, not an assumption that it is correct.

Your immediate sequence is:

| Session | Work | Evidence to keep |
|---|---|---|
| 1 | Run the existing backend; record command, Python/packages, DB, workers | Environment note |
| 2 | Verify products and pagination with individual requests | Contract examples |
| 3 | Verify order/inventory/payment states and transactions | State diagram and gap list |
| 4 | Add/review checkout idempotency and ownership tests | Integration results |
| 5 | Run Locust with 10 users; correct script/data mistakes | Smoke CSV |
| 6 | Run 50/100 users with identical conditions | Baseline report |
| 7 | Investigate the first slow component | SQL plan, profile, or trace |
| 8 | Make one improvement and rerun | Before/after report |
| 9 | Run final-unit and duplicate-request races | Invariant results |
| 10 | Review completion criteria and tag the milestone | ADR and release tag |

A session may be one evening or several; correctness and understanding determine progress. The full course can occupy six months or substantially longer alongside a job. Advanced operations and failure labs deserve time rather than a rushed calendar promise.

## A.2 Separate the first measurable baseline from the later observability stack

In the monolith stage, Locust plus process/database metrics and request logs are enough to start answering simple performance questions. Add deeper instrumentation when those signals cannot explain the bottleneck. You may bring Chapter 14's histogram/tracing setup forward if useful; its later position groups the full operational discussion, not a rule to avoid earlier observability.

Likewise, Outbox is described after Saga for conceptual clarity, but reliable publication is a prerequisite for claiming the distributed Saga is robust. Read Chapters 10–11 together before extracting the critical checkout path.

## A.3 Milestone evidence

| Milestone | Must demonstrate |
|---|---|
| M1: Correct monolith | Full purchase flow; auth/ownership; rollback and idempotency |
| M2: Measured monolith | Reproducible load test; concurrency correctness; one diagnosed bottleneck |
| M3: Scaled monolith | Multi-instance behavior; bounded pools; cache and worker failure tests |
| M4: Distributed workflow | Contracts; owned databases; Saga/Outbox/Inbox recovery |
| M5: Operable services | Logs/metrics/traces; alerts/runbooks; deployment and restore practice |
| M6: Advanced design | Autoscaling, flash sale, capacity model, clearly stated uncertainties |

---

# Appendix B — Testing and CI as the system grows

## B.1 Choose the smallest test that proves the claim

| Test | Example | What it cannot prove alone |
|---|---|---|
| Unit | Invalid order-state transition rejected | Database locking |
| Database integration | Reservation constraint and rollback | Gateway behavior |
| API integration | Authenticated buyer cannot read another order | Multi-service recovery |
| Concurrency | 100 buyers, one stock unit | Million-user capacity |
| Contract | Consumer accepts producer v1/v2 fixtures | Real broker routing |
| End-to-end | Browse to confirmed order with fake payment | All provider failure modes |
| Fault test | Crash after publish, before marking Outbox | Every infrastructure outage |
| Load test | P99 and failures under a stated workload | Unconditional production readiness |

Mock external providers for deterministic business tests. Use PostgreSQL for transaction/concurrency tests. Include at least a small real broker integration suite for routing, acknowledgement, and recovery.

## B.2 Build CI in layers

On every pull request, run formatting/lint/type checks, unit tests, PostgreSQL migrations from empty state, integration tests, and contract compatibility checks. Use isolated test credentials/data and a fresh database.

For scheduled or release validation, run broker integration, failure-window tests, image build/scanning according to your repository policy, and a controlled benchmark. Store raw artifacts with commit identity. Run expensive soak/chaos tests deliberately in isolated environments.

Do not require a flaky shared-runner P99 gate for every tiny change. Establish the environmental stability and repeatability of the gate first.

## B.3 Deployment acceptance

A release should prove:

- The image starts with documented configuration and fails clearly when required settings are absent.
- Old/new application versions coexist with the migration sequence.
- Readiness, graceful termination, and rollback behave as documented.
- Metrics and logs are still emitted and contracts remain compatible.
- A quick business smoke test succeeds after deployment.

Retain immutable image versions and a rollback runbook. Do not call a release safe simply because the container entered Running state.

---

# Appendix C — Reusable experiment and incident templates

## C.1 Benchmark report

Create `docs/benchmarks/NNN-topic.md` with:

```markdown
# Benchmark: <change>

## Question and hypothesis
What limitation do we expect to improve, and why?

## Environment
Commit, Python/packages, CPU/RAM, OS, containers/processes, network placement.
Database/cache/broker settings and client generator resources.

## Dataset and workload
Rows/distribution, endpoint/task mix, users, spawn rate, think time,
duration, warm-up, cache state, request sizes, authentication behavior.

## Correctness conditions
Expected business outcomes; acceptable/expected rejections; invariant checks.

## Results
Requests, achieved RPS, P50/P95/P99, failure ratio, timeout count,
CPU/memory, DB connection waits, lock waits, queue age, useful completions.

## Interpretation
What evidence supports the cause? What alternative explanations remain?

## Change and rerun
Exactly one main change; same inputs; repeatability/variation.

## Decision
Keep/revert; cost and failure consequences; revisit threshold.
```

## C.2 Architecture decision record

Write context, constraints, alternatives, choice, positive consequences, costs, evidence, and a revisit condition. Example: “Introduce product cache because repeated catalog reads consume the measured DB read budget; tolerate at most 60 seconds of catalog-display staleness; retain primary validation at checkout.”

An ADR saying “Redis is fast” does not explain a decision. An ADR should help your future self know whether the choice still fits.

## C.3 Incident/game-day report

Record trigger, user impact, detection time, timeline, investigation, mitigation, recovery, data reconciliation, and follow-up owner. Distinguish the initiating fault from conditions that amplified it, such as retries or unbounded queues.

A useful follow-up changes the system or the runbook. “Be more careful” is not a testable improvement.

---

# Appendix D — Diagnostic reference

| Observation | Investigate first | Common misleading response |
|---|---|---|
| P99 rises while median stays stable | Rare slow SQL, contention, retries, GC/CPU bursts | Optimize only the average |
| RPS plateaus while latency grows | Saturated resource and queue length | Keep increasing virtual users |
| More API replicas make DB errors worse | Total pools and admitted DB concurrency | Increase every pool again |
| Fast checkout response but slow confirmations | Saga/queue wait and downstream jobs | Report only HTTP P99 |
| Duplicate notification/payment request | Stable identities and side-effect deduplication | Assume the broker delivers once |
| Stale product reappears after invalidation | Reader/writer race and version policy | Reduce TTL without examining the race |
| Low API CPU but high latency | Connection waits, remote I/O, locks | Scale only on CPU |
| All Pods restart during DB outage | Liveness depends on shared DB | Add more liveness retries without policy review |
| Orders disappear after redeploy | Storage persistence and deployment lifecycle | Treat a Git commit of a DB file as database durability |
| Replica misses newly created order | Replication lag and read routing | Assume replicas are immediately consistent |
| DLQ grows silently | Alerting, failure classification, replay ownership | Purge the queue to clear the dashboard |
| Restore command succeeds but app fails | Roles/extensions/schema versions/external objects | Declare recovery complete from exit code alone |

Use measured evidence to choose an intervention. A tool name is not a diagnosis.

---

# Appendix E — Learning checks and transfer to your test platform

## E.1 Questions to answer without looking at code

1. Why can a monolith scale horizontally?
2. What does `async` allow while a database query is waiting?
3. Why does one SQLAlchemy session per concurrent task matter?
4. Why does a conditional update prevent the last-unit race?
5. What can P99 tell you that the average cannot?
6. Why are 1,000 virtual users not the same as 1,000 RPS?
7. How can an overloaded closed workload understate arrival pressure?
8. Why does a Redis cache need a staleness policy?
9. What changes between a publisher confirm and a consumer acknowledgement?
10. What happens if a worker dies after a remote side effect succeeds?
11. Why does splitting a module remove a useful local transaction boundary?
12. What does Saga compensation do that database rollback cannot?
13. Where can an Outbox publisher duplicate a message?
14. Why is the Inbox insert part of the consumer's business transaction?
15. When can an older event be ignored safely, and when does that lose a delta?
16. Why should histogram buckets be aggregated before computing P99?
17. Why can aggressive retries and autoscaling worsen an outage?
18. What is the difference between readiness and liveness?
19. Why is a restored database not sufficient to prove the entire system recovered?
20. Which parts of your million-user design are measured versus assumed?

If you cannot answer one, return to its lab and deliberately reproduce the failure. Reading an explanation and observing the failure are different levels of understanding.

## E.2 Apply the same ideas to your Robot Framework platform

| E-commerce concept | Test-platform equivalent |
|---|---|
| Checkout idempotency | Repeated execute request should not launch duplicate runs |
| Inventory reservation | Reserve a limited DUT/lab resource for one execution |
| Saga state | Orchestrate data fetch, execution, artifact upload, report processing |
| Payment unknown outcome | Worker disconnected while the test may still be running |
| Outbox/Inbox | Durable execution-status events and safe repeated report processing |
| Queue age and worker budget | Time waiting for Robot/Celery execution capacity |
| Object storage | `output.xml`, logs, screenshots, reports |
| End-to-end completion latency | Time from trigger to usable report, beyond HTTP acceptance |
| Trace/correlation IDs | Follow one execution across gateway, execution service, worker, report service |

Resource ownership matters especially for tests controlling real devices: redelivery of a task must not launch the same destructive test concurrently on one device. Lease/fencing and an authoritative execution state deserve their own lab when you transfer this course to that platform.

---

# Appendix F — Official technical references and version policy

These references support tool/API details. The chapter designs, example workloads, thresholds, and exercises are proposed learning implementations. Consult the documentation matching your locked versions when an interface differs.

| Topic | Official reference | Read alongside |
|---|---|---|
| FastAPI concurrency | [Async and await](https://fastapi.tiangolo.com/async/) | Chapter 1 |
| Password hashing/JWT | [FastAPI security tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) | Chapter 1 |
| SQLAlchemy sessions | [Asyncio integration](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) | Chapters 1, 3 |
| Migrations | [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) | Chapters 1, 19 |
| Query plans | [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html) | Chapter 3 |
| Concurrency semantics | [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html) | Chapter 3 |
| Locust workload code | [Writing a locustfile](https://docs.locust.io/en/stable/writing-a-locustfile.html) | Chapter 4 |
| Locust CLI/exports | [Configuration](https://docs.locust.io/en/stable/configuration.html) | Chapter 4 |
| Reverse proxy | [Nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) | Chapters 5, 12 |
| Redis writes/expiry | [SET command](https://redis.io/docs/latest/commands/set/) | Chapter 6 |
| Worker acknowledgement/retry | [Celery tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html) | Chapter 7 |
| Broker delivery guarantees | [RabbitMQ confirms and acknowledgements](https://www.rabbitmq.com/docs/confirms) | Chapters 7, 11 |
| HTTP timeouts | [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/) | Chapters 9, 15 |
| Payment test integration | [Razorpay integration steps](https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/integration-steps/) | Chapter 10 |
| Search rebuild cutover | [OpenSearch aliases](https://docs.opensearch.org/latest/im-plugin/index-alias/) | Chapter 13 |
| Metrics quantiles | [Prometheus histograms](https://prometheus.io/docs/practices/histograms/) | Chapter 14 |
| Tracing | [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/getting-started/) | Chapter 14 |
| Database backups | [PostgreSQL SQL dump](https://www.postgresql.org/docs/current/backup-dump.html) | Chapter 17 |
| Signed storage access | [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html) | Chapter 18 |
| Health probes | [Kubernetes probe configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) | Chapter 19 |
| Autoscaling | [Kubernetes HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) | Chapter 20 |

## F.1 Completion record

Keep a small table in your repository:

| Chapter | Code commit | Normal test | Failure test | Benchmark/ADR | What I can explain |
|---|---|---|---|---|---|
| 0 | | | | | |
| 1 | | | | | |
| 2–22 | Add one row per chapter | | | | |

Treat a chapter as complete when you can run its implementation, explain its invariants, interpret the measurements, and recover from its chosen failure. Installing the named tool is only one step.


## F.2 Validation of this handbook

The embedded Python examples were syntax-checked; YAML, JSON, and Bash blocks were parsed/checked. The Locust CSV threshold script was exercised with synthetic passing, excessive-latency, excessive-failure, low-sample, and missing-endpoint inputs. These checks validate the examples' structure and threshold behavior. They do not represent a live end-to-end run of FastAPI, PostgreSQL, Redis, RabbitMQ, Kubernetes, or your existing repository. Run each chapter's verification procedure in your own lab and record its actual results.
