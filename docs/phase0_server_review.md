# Phase 0 server review — `latest_changes`

Review scope: `server/app`, its migration and tests, and `load-tests/locustfile.py`.
The MVP requirements are the target; this is an assessment of code behavior, not a performance certification.

## Functional implementation inventory

| Area | Status | Evidence and remaining work |
|---|---|---|
| Product listing and details | Implemented for MVP | Public list/detail, category and price filters, name/SKU substring search, pagination, admin catalog. The list still performs an exact count on each request; measure it with the planned 100k-product dataset before optimizing. |
| Cart | Implemented for authenticated users | One cart per user; add/update/remove and backend totals. There is no guest cart, which is explicitly later. Concurrent creation/update of the same cart is not covered by a regression test. |
| Checkout and stock control | Partial | Order creation, item/price snapshots, idempotency key, stock row lock, movement, and initial payment record are in one local transaction. `inventory.quantity` is decremented at checkout. The separate `on_hand` / `reserved` / `available` invariant proposed in `mvp.md` is not represented in this schema. PostgreSQL last-item concurrency needs a real database test; SQLite does not validate `FOR UPDATE` behavior. |
| Simulated payment | Implemented for the MVP simulator | Success, failure, and timeout attempts; duplicate-key handling; failure releases stock and closes the order, timeout holds stock and blocks additional attempts. Admin can resolve an unknown simulator result to success or failure. A real gateway, reconciliation job, and reservation expiry are later work. |
| Order history and cancellation | Partial | Own-order listing/details, admin listing/status changes, cancellation, stock restoration, and simulated refunds exist. Repeated cancellation returns the same result. Order history is recorded internally but has no dedicated read endpoint. |
| Admin catalog and inventory | Implemented for the basic MVP | Admin product/category management, stock adjustments and movements, low-stock view, dashboard and order filtering exist. Inventory adjustments do not distinguish physically held stock from checkout reservations. |

## Non-functional assessment

| Requirement area | Current evidence | Next check |
|---|---|---|
| Correctness | Database constraints and transaction-oriented checkout/payment/cancellation; focused SQLite API regression tests pass | Run last-item and duplicate-checkout concurrency tests on PostgreSQL; exercise migration `20261005_0003` against a disposable DB |
| Security | Password hashing, JWT authentication, ownership checks for orders/payments, admin dependencies, validation, and problem-style errors | Review every route's authorization and remove development fallback credentials before any public deployment |
| Maintainability | Separate domain routers, order/payment service functions, Alembic migrations | Further move business rules out of cart/inventory/product route handlers |
| Performance | Locust scenarios for product list/detail, profile write, checkout plus payment, page limit, and checkout replay | Seed the agreed dataset; measure each endpoint separately after warm-up, with 1–3 s wait and sufficient seeded accounts/stock |
| Reliability | No production availability, restore, or backup evidence yet | Test restore and observe app/database behavior during faults in later phases |

## Load-test interpretation

- Run from the repository root with `-f load-tests/locustfile.py`. Select **one** user class per run to keep its percentile meaningful.
- Use `CatalogReadUser` with `-u 100 -r 10` for product-list reads. Use `ProductDetailReadUser` separately, with `PERF_PRODUCT_ID` set to a published product.
- Use `CheckoutUser` with `-u 20 -r 2` for the purchase path. Its order request and payment request have **separate** latency rows; neither alone measures the complete user journey. Give the chosen product enough stock for the entire timed test. All checkout users target one product, so this is also a deliberate row-contention scenario.
- `ProfileWriteUser` measures profile PATCH; it does not establish a P95 for cart or admin writes. `CheckoutIdempotencyUser` is a correctness exercise with an order creation and replay in each iteration.
- The account queue is process-local. Distributed Locust workers can reuse the same seeded usernames; give each worker a disjoint `PERF_USER_START_INDEX` range before treating a distributed run as a valid baseline.
- Exclude setup/login requests, expected 4xx boundary checks, and warm-up traffic from the specific endpoint's reported P95 and error-rate comparison. Record exact dataset, hardware, process/worker count, duration, and throughput with the result.

## Changes from this review

1. A failed simulated payment releases stock once and moves the order to `payment_failed`, so a later success cannot charge an order whose stock was released.
2. A timeout moves the order to `payment_review` and keeps the stock held until an administrator resolves the simulated outcome. A second payment attempt is blocked while the outcome is unknown.
3. Repeated cancellation returns the already-cancelled order without a second stock restoration/refund.
4. Registration handles a unique-key race as a conflict instead of an internal server error.
5. The Locust checkout user continues throughout the configured test and completes the simulated payment rather than stopping after ten orders and recycling accounts.

## Verification and limits

`python -m pytest -q tests/test_order_payment_invariants.py` from `server/`: 7 passed.
`python -m compileall -q server/app server/tests load-tests/locustfile.py server/migrations/versions/20261005_0003_payment_resolution_states.py`: passed.

These tests use SQLite. The PostgreSQL enum migration, row-lock behavior, and target P95/error rates still require a local PostgreSQL run and a seeded Locust baseline. Avoid interpreting test success as proof of the performance targets.
