# ADR 001: Use PostgreSQL as the Primary Database

**Status:** Accepted  
**Date:** 2026-10-06

## Problem

The MVP is a modular monolith for a single-seller store. Its core workflows update related business records: checkout creates an order and reserves inventory, payment attempts change order/payment state, and cancellation may release stock or record a refund. The system must preserve these invariants under retries and concurrent requests, not merely store and retrieve product data.

The database therefore needs transactions, relational constraints, precise money types, and a way to coordinate concurrent updates. The initial design should keep these workflows in one deployable application and one database rather than introduce distributed transactions before the system needs independent services.

## Options Considered

1. **PostgreSQL:** A relational database with transactions, foreign keys, unique and check constraints, row-level locking, and fixed-precision numeric types. It is the project's selected primary database and is available as PostgreSQL 16 in Docker Compose.
2. **MySQL:** A capable relational alternative that could support the MVP. It offers no project-specific advantage over PostgreSQL for the current requirements, so adopting it would add a second candidate without solving a demonstrated problem.
3. **SQLite:** Simple to run and useful for fast, disposable tests. Its concurrency and locking behavior do not establish that PostgreSQL-specific production behavior is correct, so it is not the system of record.
4. **MongoDB or another document database:** Flexible for document-shaped data, but the MVP has strongly related users, carts, products, inventory, orders, payments, and audit history. It would move more integrity and cross-record consistency work into application code without a current requirement for document-oriented storage.
5. **Multiple databases or a database per service:** Could support independently owned services later, but would add operational overhead and distributed consistency concerns to the initial monolith.

## Decision

Use PostgreSQL as the single primary database for the initial modular monolith. Keep the modules on one PostgreSQL database and use local transactions for each operation that must update related records atomically. Manage schema changes with Alembic migrations. PostgreSQL is the source of truth for catalog, inventory, carts, orders, payments, and their histories.

The local Compose environment uses PostgreSQL 16. SQLite may remain a fast test backend, but PostgreSQL integration tests are required for behavior that depends on PostgreSQL transaction or locking semantics. Redis, search engines, and separate service databases are not part of this decision; introduce them only when a measured requirement justifies them.

## Why

- The requirements depend on relational integrity across business records, including foreign keys, uniqueness, and non-negative quantity/amount constraints.
- Checkout and inventory operations need atomic updates and protection against concurrent requests overselling stock. The implementation uses row locks for these operations.
- Idempotency keys for orders and payment attempts are enforced with database uniqueness constraints, making the database a final guard against duplicate requests.
- `NUMERIC` columns preserve decimal monetary values; binary floating-point arithmetic is unsuitable for prices and payment amounts.
- A shared relational database supports the current modular-monolith boundary without requiring network calls or eventual consistency between modules.
- PostgreSQL is already used by the Compose environment and is the database selected by the Phase 0 system design.

## Advantages

- Transactions and constraints keep important invariants close to the persisted data.
- Row-level locking supports safe coordination of concurrent inventory and order updates.
- Relational queries and joins fit the MVP's connected data and administrative views.
- PostgreSQL, SQLModel/SQLAlchemy, and Alembic provide a well-supported development and migration path.
- One database keeps local development and the first deployment architecture straightforward.

## Disadvantages

- The database is a stateful component that needs explicit backup, restore, monitoring, and connection-pool practices before production use.
- A single primary database can become a throughput or availability bottleneck as demand grows; scaling and failover require additional design and operations.
- Shared schema and transactions couple modules at the persistence boundary. They do not provide independent ownership if modules later become services.
- SQLite-based regression tests do not verify PostgreSQL row-lock behavior. PostgreSQL-backed integration testing is needed for concurrency-sensitive guarantees.

## Tradeoffs

This decision prioritizes transactional correctness and a simple MVP architecture over schema flexibility and independent database scaling. The modular monolith may use local ACID transactions, but future service boundaries must not rely on cross-service database transactions or shared-table access. A service extraction will require explicit data ownership and may require patterns such as an outbox, idempotent consumers, or sagas.

PostgreSQL is an initial choice, not a claim that one relational database is optimal at every scale. Read replicas, caching, partitioning, or a different persistence technology should be considered only when measurements show a specific bottleneck and the change preserves required business invariants.

## Benchmark

No comparative database benchmark or production-scale performance claim is made by this ADR. Establish a repeatable PostgreSQL baseline before tuning or adding infrastructure:

- Run representative catalog-read, product-detail, and checkout workloads with Locust against the Compose stack.
- Record the dataset, request mix, concurrency, application worker count, warm-up, throughput, P50/P95/P99 latency, error rate, database CPU/memory, connection count, and relevant query/lock timings.
- Exercise concurrent checkout for the last available unit and retries using the same idempotency key. Verify that inventory never becomes negative and that retries do not create duplicate orders or payments.
- Run the concurrency and locking checks against PostgreSQL. SQLite results are useful for fast application regression tests but are not evidence for PostgreSQL locking behavior.
- Save the workload and results so later indexing, caching, or database changes can be compared under the same conditions.

## Future Consequences

- Continue to evolve the schema through reviewed Alembic migrations; test migrations against PostgreSQL.
- Add PostgreSQL-backed integration coverage for transaction boundaries, row locks, constraints, and idempotency before relying on those properties in production.
- Define and test backup/restore, connection-pool sizing, monitoring, and availability objectives before production deployment.
- Use query plans and benchmark evidence to guide indexes and database tuning. Add Redis or read replicas only when measurements identify read load or latency as a bottleneck.
- If the application is split into services, assign each service ownership of its data. Revisit consistency and failure handling rather than assuming the current single-database transactions span service boundaries.