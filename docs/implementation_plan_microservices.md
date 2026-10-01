# Detailed Implementation Plan: Advanced Microservices and System Design

## Project goal

Build one e-commerce system in stages and use each stage to learn a specific system design problem. The project begins as a production-minded monolith, becomes a modular monolith, and evolves into a distributed system through measured experiments. The final result should include working software, repeatable tests, architecture decisions, operational evidence, and a defensible capacity design.

The learning loop for every major change is:

1. State a user or operational problem.
2. Form a testable hypothesis about its cause.
3. Capture the current behavior and measurements.
4. Implement the smallest change that addresses the problem.
5. Repeat the same tests and compare results.
6. Document the trade-offs in an ADR and benchmark note.

Do not treat “one million users” as a target that can be proven by a local load test. Model the workload, state assumptions, measure the application at practical scale, and identify which parts of the design still need production validation.

## Recommended project setup

### Keep the existing repository and mark milestones

Continue in the existing `ecommerce-system-design` repository. Keep one main code line and mark completed architectural stages using Git tags or release branches. Avoid maintaining separate copies of the application for every phase; the point is to show how one system evolved.

Suggested structure:

```text
ecommerce-system-design/
├── server/                     # FastAPI application(s)
├── client/                     # React + TypeScript UI, if in scope
├── services/                   # Extracted services as they appear
├── load-tests/                 # Locust or k6 scenarios and test data
├── scripts/                    # Seed, benchmark, and failure-injection tools
├── infrastructure/
│   ├── compose/
│   ├── prometheus/
│   ├── grafana/
│   └── kubernetes/
├── docs/
│   ├── requirements/
│   ├── architecture/
│   ├── adr/
│   ├── api-contracts/
│   ├── event-contracts/
│   ├── benchmarks/
│   ├── incidents/
│   └── capacity-plans/
├── docker-compose.yml
└── README.md
```

Use the tools already selected for the project: Python, FastAPI, PostgreSQL, Docker Compose, and a load-testing tool such as Locust or k6. Add Redis, RabbitMQ/Celery, search, tracing, or Kubernetes only in the stages where the plan calls for them. Prefer one tool per job while learning; using both Locust and k6, for example, is unnecessary unless there is a clear comparison to make.

### Repository hygiene before feature work

- Confirm the application starts from a clean checkout using documented commands.
- Pin runtime and dependency versions; keep development and production settings separate.
- Add `.env.example` with names and safe sample values, never secrets.
- Establish formatting, linting, type-checking, and test commands.
- Add CI to run the fast checks on each pull request.
- Add a migration tool and verify migrations against an empty database.
- Keep `--reload` and debug settings out of load-test runs. Run the load target with a production-style ASGI server configuration and record worker count, CPU, memory, and database settings.
- For each load test, record the exact commit, configuration, workload, and test duration. A run that crashes is diagnostic evidence, not a valid capacity result.

## Cross-cutting engineering rules

Apply these rules from the first phase onward:

- Put business invariants in application/domain logic and reinforce critical invariants with database constraints.
- Use UTC timestamps internally and define monetary precision and rounding explicitly.
- Give each request a request/correlation ID; propagate it through logs and service calls.
- Validate all external input and return one consistent error response shape.
- Set timeouts on network calls; once services are split, never leave an unbounded request waiting on a dependency.
- Use idempotency for operations that can be retried, especially checkout, payment callbacks, and message consumers.
- Keep credentials in environment or a secret manager, not source control.
- Test authorization and ownership at the API boundary.
- Keep database transactions short. Never hold row locks while calling a remote service.
- Make migrations reversible where practical and test deployment ordering for schema changes.
- Track a baseline before changing architecture. A faster result with more errors or weaker correctness is not an improvement.
- Add a new infrastructure dependency only when there is a written problem statement, a small experiment, and a rollback path.

## Phase 0 — Requirements, local environment, and baseline

### Objective

Define a stable MVP and make the project repeatable before adding features or scaling components.

### Implementation tasks

1. Write customer journeys: registration/login, product browsing/search, cart changes, checkout, simulated payment, order history, and eligible cancellation.
2. Write admin journeys: product/category maintenance, inventory adjustment, order lookup/status update, and user lookup.
3. Define out-of-scope features for the MVP, such as recommendations, promotions, shipment integrations, and real payment settlement.
4. Record initial workload assumptions: catalog size, user count, normal and peak request mix, order rate, and expected data retention. Mark assumptions as assumptions.
5. Define initial service-level objectives for the learning environment, for example product-list read latency, checkout success/error rate, and local service availability. These are targets to test, not guarantees.
6. Create context and container diagrams for the initial single-application design.
7. Start PostgreSQL and the application with Docker Compose; add a health check and persistent local database volume.
8. Add a seed command that creates deterministic products, inventory, customers, and orders.
9. Add a smoke test that starts from empty state, applies migrations, seeds minimal data, and checks health.
10. Write ADR 001: initial database choice and why SQLite is or is not suitable for this learning stage. Use PostgreSQL for the main concurrency and scaling journey; SQLite can still be useful for isolated unit tests, but it does not model PostgreSQL locking or deployment behavior faithfully.

### Learning and evidence

- Requirements versus implementation choices
- Availability, latency, throughput, durability, and consistency
- SLI/SLO concepts and basic capacity arithmetic
- Docker Compose networking, health checks, environment configuration

### Deliverables and exit gate

- `docs/requirements/mvp.md`
- Initial context/container diagram
- ADR 001
- One-command local startup and test instructions
- A clean database can be migrated and seeded reproducibly

Do not begin scaling experiments until another developer or a clean environment can follow the setup instructions successfully.

## Phase 1 — Implement the MVP monolith

### Objective

Build and verify the complete customer order journey in one deployable FastAPI application backed by PostgreSQL.

### Suggested module layout

```text
server/app/
├── api/
├── auth/
├── users/
├── catalog/
├── inventory/
├── cart/
├── orders/
├── payments/
├── core/
├── db/
└── main.py
```

### Implementation sequence

1. Define entities and relationships: user, category, product, inventory, cart/cart item, order/order item, payment attempt.
2. Add migrations, unique constraints, foreign keys, check constraints, and indexes needed for correctness.
3. Implement authentication with password hashing and short-lived access tokens. Add role-based authorization for customer and admin endpoints.
4. Implement product/category reads and admin CRUD with filtering, sorting, and bounded pagination.
5. Implement inventory adjustment with audit fields and validation that prevents invalid quantities.
6. Implement persistent cart operations and verify users cannot access another user’s cart.
7. Implement checkout as an explicit application use case. In one database transaction, validate cart and prices, reserve/decrement inventory safely, create an order and order items, and create a simulated payment attempt. Do not call a real payment provider inside this transaction.
8. Implement simulated payment outcomes (success, decline, timeout/failure) and a clear order/payment state model.
9. Implement order history/details and cancellation rules. Restore inventory only according to the defined cancellation policy.
10. Add consistent request validation, error mapping, structured logging, request IDs, and API documentation.
11. Add unit tests for domain rules, API/integration tests against PostgreSQL, and authorization tests.

### Essential invariants

- Product prices on an order are snapshots; later catalog changes do not rewrite past orders.
- Inventory never falls below zero.
- An order has a valid state transition history; illegal transitions are rejected.
- The same checkout idempotency key cannot create multiple orders.
- A payment attempt is not silently treated as successful when its result is unknown.
- A customer can only read or cancel their own eligible order.

### Experiments and exit gate

- Force a database error midway through checkout and verify rollback.
- Submit duplicate checkout requests and verify a single order is created.
- Race two buyers for the last unit and verify no overselling.
- Test failed/declined payment and verify order/inventory behavior matches the chosen policy.
- Run all tests from a clean database.

Exit when a customer can complete browse → cart → checkout → payment simulation → order history, and correctness is covered by meaningful integration tests.

## Phase 2 — Refactor into a modular monolith

### Objective

Create boundaries that can be understood and tested before introducing network boundaries.

### Implementation tasks

1. Define bounded contexts: Identity, Catalog, Inventory, Cart, Ordering, Payments, and Notifications.
2. Give each module its own API/application layer, domain rules, and persistence access.
3. Stop modules from importing another module’s ORM models or writing directly to its tables. Use explicit application interfaces or internal commands/queries.
4. Move business decisions out of route handlers into application/domain services.
5. Identify synchronous module calls and document why they must be immediate.
6. Add module-level tests and dependency checks (or a simple architecture test) to enforce allowed imports.
7. Add internal domain events only when they clarify a business fact or decouple a real responsibility; avoid a generic event framework.

### Learning and experiment

Study cohesion, coupling, dependency inversion, bounded contexts, and the difference between a code boundary and a separately deployed service. Change how inventory is implemented and observe whether ordering logic needs to know its storage details.

### Exit gate

Each module owns its business rules and persistence access. Cross-module dependencies are explicit. No HTTP/RabbitMQ call is added merely to imitate microservices.

## Phase 3 — Database performance and concurrency

### Objective

Understand how data model, query plans, transactions, isolation, and contention affect the application.

### Implementation tasks

1. Build a deterministic data generator with configurable sizes and skewed distributions (popular products and high-activity users).
2. Capture representative SQL for product listing, product detail, user order history, and admin order search.
3. Use `EXPLAIN (ANALYZE, BUFFERS)` to inspect slow queries. Record plans and timings before adding indexes.
4. Add only indexes supported by query patterns; explain write/storage costs and index column order.
5. Compare offset pagination with cursor pagination for deep pages.
6. Implement inventory concurrency with a documented strategy such as conditional updates or row-level locking. Keep the transaction short.
7. Add concurrent integration tests for final-unit checkout, repeated checkout, cancellation racing checkout, and payment-result updates.
8. Capture connection pool size and database connection usage under concurrency.
9. Reproduce and diagnose one deadlock or serialization failure, then implement bounded retry only for safe transient transaction errors.

### Learning topics

Normalization, indexes, query planner, isolation levels, row locks, optimistic versioning, deadlocks, connection pooling, keyset pagination.

### Exit gate

Inventory cannot become negative under the test workload. Critical queries have measured plans and justified indexes. Failures caused by concurrency are understood, handled, and observable.

## Phase 4 — Load test and find the first bottleneck

### Objective

Create repeatable performance evidence before introducing caches or more application instances.

### Workload design

Build separate scenarios for product browsing, search/filter, cart changes, checkout, and mixed traffic. Include authenticated users and realistic think time. Bound page sizes and use realistic payload sizes. Create baseline, load, stress, spike, and soak profiles with configurable user/rate counts.

### Measurements

- Throughput and completed transactions per second
- P50/P95/P99 latency by endpoint and business flow
- HTTP errors, timeouts, and failed business outcomes
- Application CPU, memory, worker count, and event-loop/process failures
- PostgreSQL CPU, active connections, locks, slow queries, and I/O where available
- Load-generator CPU/network so it does not become the bottleneck

### Implementation and experiment

1. Pin the test script, seed data, server command, and machine configuration.
2. Run a low-rate smoke test before a larger ramp.
3. Increase concurrency gradually and capture server logs and metrics.
4. For a failure, first establish whether it is a code defect, worker/process limit, database saturation, client bottleneck, or infrastructure limit.
5. Record a baseline report before changing code.
6. Repeat the same workload after each optimization.

### Exit gate

At least one actual bottleneck is identified with supporting evidence. The test can be rerun from a documented command, and results distinguish capacity limits from application crashes or invalid load generation.

## Phase 5 — Scale the monolith horizontally

### Objective

Learn stateless request handling and load balancing without changing business boundaries.

### Implementation tasks

1. Run two or more application instances behind Nginx or Traefik.
2. Move any process-local session, rate-limit, or coordination state to a shared mechanism only when the feature requires it.
3. Add liveness and readiness endpoints with distinct meanings.
4. Configure graceful shutdown and drain connections during termination.
5. Set per-instance database pool limits and calculate total possible connections across replicas.
6. Ensure scheduled/background work cannot accidentally run once per web replica without coordination.
7. Load test one instance versus multiple instances at the same total resource budget.

### Experiments and exit gate

Kill an instance during traffic, restart it, and observe errors and recovery. Verify requests do not depend on sticky routing. Demonstrate how adding API instances can overload PostgreSQL if connection pools are not bounded.

## Phase 6 — Add Redis for a measured need

### Objective

Learn cache behavior and shared ephemeral state while keeping PostgreSQL authoritative.

### Implementation sequence

1. Select a read-heavy endpoint whose database cost is already measured.
2. Add cache-aside for a clearly defined key and value schema.
3. Define TTL, invalidation/update behavior, and behavior when Redis is unavailable.
4. Add cache hit/miss/latency metrics without logging sensitive values.
5. Test stale reads, cache stampede, hot keys, and key expiration.
6. Compare database load and tail latency using the same workload; include cache warm-up and cold-cache runs.
7. Only after cache behavior is understood, evaluate Redis for carts, rate limits, or short-lived coordination state. Define durability/eviction expectations for each use.

### Exit gate

Measured cache benefit outweighs added complexity. A cache outage or stale value has defined behavior. PostgreSQL remains the source of truth for orders, payments, and inventory correctness.

## Phase 7 — Background jobs and message broker

### Objective

Move work that need not finish in the request path to asynchronous processing.

### Candidate work

Order confirmation email, invoice generation, audit export, and other retryable side effects. Keep checkout acceptance and the order's durable state synchronous enough to give a correct response.

### Implementation tasks

1. Add RabbitMQ and Celery through Docker Compose with health checks and persistent development configuration.
2. Define task/event schemas with IDs, schema version, timestamp, and correlation ID.
3. Implement one worker task end-to-end, with idempotent handling and bounded retries.
4. Configure acknowledgements, prefetch, retry/backoff, visibility/ack behavior, and a dead-letter path intentionally.
5. Record queue depth, oldest message age, task success/failure, retry count, and processing time.
6. Add an operator command to inspect and safely replay a failed task.
7. Test worker crash before acknowledgement, duplicate delivery, malformed event, unavailable broker, and prolonged backlog.
8. Document which operations are at-most-once, at-least-once, or effectively-once through idempotency.

### Exit gate

The API does not wait for eligible background work. Duplicate delivery does not duplicate effects. Backlog and poison messages are visible and have a recovery procedure.

## Phase 8 — Extract the first service

### Objective

Learn the full cost of a network boundary with a low-risk capability before splitting checkout or inventory.

### Recommended candidate

Notification service, because email/notification delivery is a side effect and has limited transactional coupling to the order core.

### Extraction sequence

1. Document the module’s current responsibilities, data, API/events, and dependencies.
2. Define an owned contract and versioning policy.
3. Move implementation to a separate FastAPI service and give it its own data store if it needs persistent state.
4. Replace the in-process call with an asynchronous event or a timeout-protected HTTP call, based on delivery requirements.
5. Keep the old path behind a temporary adapter or feature flag during migration.
6. Add contract tests, service health checks, timeouts, retries only where safe, and dashboards.
7. Run integration and failure tests with the new service unavailable, slow, and restarting.
8. Remove the old implementation after the migration is verified; do not keep two owners indefinitely.

### Exit gate

The service can be deployed independently, owns its data, and has an explicit contract. The team can explain the latency, availability, and operational costs introduced by extraction.

## Phase 9 — Establish service ownership and service data boundaries

### Objective

Split only domains whose independent scaling, deployment, team ownership, or fault isolation justifies the added complexity.

### Candidate boundaries

- Catalog
- Inventory
- Ordering
- Payments (initially simulated)
- Notification
- Search projection

### Rules and implementation steps

1. Write a context map showing service ownership and allowed communication.
2. Assign each service exclusive write ownership of its data. No other service writes its tables.
3. Replace cross-module joins with service APIs or read projections where required.
4. Define API/event contracts and compatibility rules before consumers depend on them.
5. Add service-specific migrations, health checks, structured logs, and integration tests.
6. Add local development orchestration to start the required service subset.
7. Test partial failures and version skew between producer and consumer.
8. Record operational ownership: deploy, alert, restore, and support path for each service.

### Exit gate

Each service boundary has an owner, data policy, contract, deployment reason, and operational runbook. No service uses another service’s database as a shortcut.

## Phase 10 — Distributed checkout and Saga

### Objective

Handle a business flow that crosses independently owned services without pretending a distributed ACID transaction exists.

### Implement a workflow

Example order flow: create pending order → reserve inventory → authorize simulated payment → confirm order; if a step fails, run a compensating action such as release reservation or void authorization.

### Implementation tasks

1. Draw state transitions, success path, timeout path, and compensation path.
2. Choose choreography or orchestration for this learning scenario and write an ADR explaining the choice.
3. Give each command/event a stable workflow ID and idempotency key.
4. Persist Saga state and every step result so the workflow survives process restarts.
5. Give every remote step a timeout; distinguish definite failure from unknown outcome.
6. Make compensations idempotent and safe when repeated.
7. Add expiry/reconciliation for stuck workflows and an operator-visible state/history.
8. Test failures after each boundary, duplicate messages, late responses, and service restart.

### Exit gate

Orders eventually reach a documented terminal state or an explicit manual-recovery state. Inventory and payment state can be reconciled after interruption. No compensation is assumed to erase history.

## Phase 11 — Reliable event publication with Outbox/Inbox

### Objective

Prevent the database commit/message publish dual-write problem.

### Implementation tasks

1. Reproduce the failure: commit an order, then crash before publishing its event.
2. Add an outbox table written in the same local transaction as the business state.
3. Implement a publisher that claims pending rows, publishes with a stable event ID, and records delivery progress.
4. Assume publish can be repeated; make consumers deduplicate through an inbox or processed-event table.
5. Add retention/cleanup policy, retry schedule, poison-event handling, and outbox lag alerts.
6. Add event schema versioning and compatibility tests.
7. Test crash before publish, crash after broker publish but before marking sent, duplicate event, and consumer crash before commit.

### Exit gate

Committed business changes are eventually published, duplicates are harmless, and operators can find and recover stuck outbox/inbox records.

## Phase 12 — API gateway and edge concerns

### Objective

Learn routing and cross-cutting edge controls while keeping business rules in their owning services.

### Implementation tasks

1. Put Nginx/Traefik in front for TLS termination and reverse proxying in local/staging environments.
2. Add a gateway only for concrete needs such as route aggregation, authentication enforcement, request limits, or version routing.
3. Define which service validates the user identity and which authorization checks remain domain-owned.
4. Propagate request IDs, timeouts, tracing headers, and client metadata safely.
5. Add request/body size limits, rate limits, CORS policy, and consistent error mapping.
6. Avoid business orchestration in the gateway; keep checkout workflow in the ordering/Saga layer.
7. Test gateway failure, service 404/5xx, timeout behavior, and route configuration changes.

### Exit gate

Edge policy is explicit and tested. A gateway outage and downstream timeout have understandable client behavior. Service-level authorization remains enforced.

## Phase 13 — Search and read projections

### Objective

Separate search-oriented reads from transactional writes and understand eventual consistency.

### Implementation tasks

1. Implement product search first with PostgreSQL search to establish a basic functional baseline.
2. Add OpenSearch/Elasticsearch only when query, relevance, or scale requirements justify it.
3. Publish catalog changes through the Outbox and build a search projection asynchronously.
4. Add full reindex/backfill tooling and support rebuilding the index from source-of-truth data.
5. Define freshness expectations and expose projection lag.
6. Test delete/update propagation, duplicate/out-of-order events, index outage, and rebuild during traffic.
7. Keep final price and inventory validation in checkout; search results are not authoritative for purchase eligibility.

### Exit gate

The search index can be rebuilt, stale results have a defined user impact, and checkout correctness does not depend on index freshness.

## Phase 14 — Observability and operational readiness

### Objective

Trace one user action across processes and distinguish user-facing symptoms from internal causes.

### Implementation tasks

1. Emit structured JSON logs with timestamp, severity, service, environment, request ID, trace ID, and safe business identifiers.
2. Add Prometheus metrics for request count/latency/errors, database pools, queue depth/age, task outcomes, and Saga/outbox progress.
3. Instrument FastAPI, database, HTTP clients, RabbitMQ/Celery, and background tasks with OpenTelemetry traces.
4. Use low-cardinality metric labels; never label by user ID, order ID, or arbitrary URL.
5. Create dashboards for API health, database health, queue/workers, and checkout workflow.
6. Define alert conditions around user impact, SLO burn, queue age, and stuck workflows.
7. Add a runbook for each alert with diagnosis steps and safe mitigations.
8. Correlate one order from incoming request through service calls, events, workers, and notification.

### Exit gate

An injected checkout delay/failure can be diagnosed from metrics, logs, and traces without relying on console print statements.

## Phase 15 — Resilience, timeouts, and graceful degradation

### Objective

Prevent one slow or failed dependency from exhausting the whole system.

### Implementation tasks

1. Set connect/read/overall timeouts on all inter-service and database calls.
2. Add bounded retries with exponential backoff and jitter only for transient, idempotent operations.
3. Add circuit breakers or bulkheads where tests show they reduce cascading failure risk.
4. Define fallback behavior per endpoint: fail closed for inventory/payment correctness; potentially serve stale catalog data for browsing.
5. Add queue backpressure, concurrency limits, and graceful overload responses.
6. Define graceful shutdown, readiness removal, and in-flight request behavior.
7. Add fault injection for latency, errors, broker outage, database saturation, and worker termination.
8. Conduct a game day: inject a failure, diagnose, mitigate, recover, and write an incident review.

### Exit gate

Critical dependencies have timeout and failure policies. Failure tests show bounded impact and a known recovery path. Retries do not amplify overload or duplicate business actions.

## Phase 16 — Distributed rate limiting and abuse protection

### Objective

Protect expensive or sensitive operations across multiple API instances.

### Implementation tasks

1. Identify endpoints by risk and cost: login, search, checkout, payment simulation, admin operations.
2. Define limits by identity/IP and document proxy trust boundaries.
3. Implement a Redis-backed algorithm such as token bucket, including atomic updates.
4. Return appropriate status and retry information.
5. Define Redis outage behavior separately for login, browsing, and checkout.
6. Test traffic spread across replicas, bursts, clock behavior, and abusive clients.

### Exit gate

Limits apply consistently across instances and protect high-risk endpoints without blocking normal workload unexpectedly.

## Phase 17 — Database scaling and data lifecycle

### Objective

Explore database scaling methods in increasing operational complexity.

### Sequence

1. Revisit queries, schema, indexes, and pool sizing.
2. Define retention, archival, and deletion policies.
3. Test partitioning on a time-oriented table if data size and maintenance needs justify it.
4. Add a read replica for eligible read workloads and measure replication lag.
5. Define read-after-write routing for endpoints requiring fresh data.
6. Model sharding only after a single database cannot meet a stated capacity/availability constraint.
7. For a sharding exercise, pick a shard key, model hot-key and cross-shard query behavior, and estimate rebalancing cost.

### Exit gate

Each scaling mechanism addresses a demonstrated bottleneck. Stale-read, failover, migration, archival, and restore implications are documented. Sharding remains a design exercise until evidence requires it.

## Phase 18 — Object storage and CDN

### Objective

Serve product media without using API workers as file servers.

### Implementation tasks

1. Store image metadata in PostgreSQL and file bytes in MinIO locally or a compatible object store.
2. Generate pre-signed upload/download URLs with constrained size, content type, and expiration.
3. Create image variants asynchronously if needed.
4. Add cache headers and model invalidation/versioned asset URLs.
5. Test unauthorized upload, expired URL, large object, and missing/deleted asset behavior.

### Exit gate

Media bytes bypass API worker capacity; upload and access policies are enforced and testable.

## Phase 19 — Kubernetes and deployment practice

### Objective

Learn orchestration after Docker Compose and service operations are understood.

### Implementation sequence

1. Containerize and deploy stateless API services and workers first.
2. Add Deployments, Services, ConfigMaps, Secrets references, ingress, and resource requests/limits.
3. Configure startup, readiness, and liveness probes based on actual service state.
4. Use managed or separately operated stateful dependencies where available; for learning, document limits of local stateful workloads.
5. Perform rolling updates and rollbacks with backward-compatible database migrations.
6. Add namespace/resource boundaries and network policies as the lab permits.
7. Test pod termination, unavailable dependency, bad deployment, and recovery.

### Exit gate

Deployment is repeatable, probes do not hide dependency failures, rollout/rollback is practiced, and application replicas do not exceed database/broker capacity.

## Phase 20 — Autoscaling and capacity management

### Objective

Scale based on measured demand while protecting downstream systems.

### Implementation tasks

1. Establish resource requests/limits and realistic baseline utilization.
2. Scale API replicas on CPU/latency or an appropriate request metric.
3. Scale workers using queue depth and message age, with maximum concurrency tied to dependency capacity.
4. Add minimum/maximum replicas, cooldowns, and stabilization windows.
5. Run a normal profile and a burst profile; observe scale-up delay, latency, errors, queue backlog, and recovery.
6. Verify database connection and throughput ceilings before allowing additional replicas.

### Exit gate

Autoscaling responds to an observed signal without causing downstream overload or oscillation. Manual capacity limits and emergency controls are documented.

## Phase 21 — Flash-sale design lab

### Scenario

Model 100 items offered to a large burst of buyers, with a short purchase window. Run a safe local equivalent of the workload rather than attempting a million real virtual users on a laptop.

### Build and test

1. Define acceptance, waiting, rejection, and purchase fairness behavior.
2. Start with PostgreSQL conditional inventory updates/locking and measure contention.
3. Add idempotency to prevent duplicate orders from repeat clicks.
4. Introduce rate limiting and an admission queue if direct request load overwhelms the transactional path.
5. If Redis is used for admission/counters, document how it reconciles with durable PostgreSQL inventory after crash or duplicate events.
6. Test worker backlog, client retries, payment failure, cancellation, and system recovery.
7. Verify confirmed units sold never exceed durable inventory.

### Exit gate

The tested design has no overselling, duplicate requests are safe, queue/rejection behavior is clear, and durability/fairness trade-offs are documented.

## Phase 22 — One-million-user capacity design

### Objective

Produce a quantified architecture proposal rather than claiming readiness from a diagram.

### Work items

1. Define users, daily active users, concurrent users, traffic mix, peak factor, order rate, and retention assumptions.
2. Calculate average and peak requests/sec by endpoint class, not only an aggregate number.
3. Estimate database writes, storage growth, index overhead, cache working set, broker throughput/backlog, object storage, and network egress.
4. Identify the first likely bottleneck and a scaling path for each subsystem.
5. Add capacity headroom and single-failure scenarios (one app instance, worker pool, AZ, or dependency unavailable, depending on environment).
6. Compare at least two architecture options with latency, consistency, availability, cost, and operational complexity.
7. State which assumptions are measured locally, estimated, or require cloud/vendor validation.
8. Create a final architecture diagram, capacity plan, and review checklist.

### Exit gate

Every major component is tied to a requirement or measurement. Estimates show inputs and formulas, trade-offs are explicit, and the remaining uncertainties are listed.

## Six-month learning schedule

Treat the months as a pacing guide. Extend a phase when its exit gate is not met.

| Month | Focus | Expected state |
|---|---|---|
| 1 | Requirements, environment, monolith, API/database fundamentals | Tested MVP |
| 2 | Modular boundaries, SQL tuning, concurrency, load testing | Measured modular monolith |
| 3 | Horizontal scaling, Redis, RabbitMQ/Celery | Scaled monolith with async work |
| 4 | Service extraction, contracts, Saga, Outbox | Distributed order workflow |
| 5 | Gateway, search, observability, reliability, rate limits | Observable resilient services |
| 6 | Database scaling, object storage, Kubernetes, autoscaling, flash sale, capacity design | Production-like learning portfolio |

### Weekly cadence

- Day 1: Learn the concept and write a short problem/hypothesis.
- Days 2–3: Implement the smallest slice and its tests.
- Day 4: Exercise normal, edge, and failure paths.
- Day 5: Run the benchmark or load test.
- Day 6: Record results, update ADR/runbook, review code.
- Day 7: Summarize what changed and choose the next evidence-based problem.

## Documentation templates

### ADR template

```markdown
# ADR NNN: Decision title

## Status
Proposed | Accepted | Superseded

## Context and problem

## Constraints and assumptions

## Options considered

## Decision

## Benefits and costs

## Failure and operational consequences

## Evidence or benchmark

## Revisit when
```

### Benchmark template

```markdown
# Benchmark: change name

## Hypothesis
## Commit and environment
## Dataset and workload
## Server and database configuration
## Before: throughput, P50/P95/P99, errors, CPU/memory, DB/queue
## After: throughput, P50/P95/P99, errors, CPU/memory, DB/queue
## Correctness checks
## Conclusion and trade-offs
## Follow-up
```

### Incident/game-day note

```markdown
# Exercise: failure injected

## User-visible symptom
## What was injected
## Timeline
## Detection and diagnosis
## Mitigation and recovery
## Data consistency check
## Follow-up actions
```

## Final portfolio checklist

The repository is complete when it contains:

- A working customer/admin e-commerce flow with meaningful automated tests
- Database constraints and concurrency tests for inventory and checkout
- Repeatable seed and load-test scripts
- Before/after benchmark reports
- Architecture diagrams for the major stages
- ADRs for decisions to add Redis, messaging, service boundaries, Saga, Outbox, gateway, search, Kubernetes, and scaling approaches
- Versioned API and event contracts with compatibility tests
- Runbooks for deployment, queue recovery, stuck workflows, and dependency failures
- Metrics, logs, traces, and dashboards for the order journey
- Failure-injection/game-day notes
- Deployment manifests and rollback practice
- One-million-user capacity model with explicit assumptions and uncertainty
- A final retrospective identifying which complexity was justified by evidence and which remained unnecessary

## Completion principle

The goal is not to reach the highest number of technologies. The goal is to be able to show, for each architectural change, the problem it addressed, the evidence that supported it, the failure modes it introduced, and the conditions under which a simpler design would still be preferable.
