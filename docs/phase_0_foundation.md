# Phase 0 — E-commerce System Foundation

## Project: E-commerce System Design Laboratory

**Status:** Draft baseline for implementation  
**Phase objective:** Define what will be built, what will not be built, how success will be measured, and why the initial architecture is intentionally simple.

---

## 1. Decisions Already Made

| Decision | Selection | Reason |
|---|---|---|
| Business model | Single-seller store | Keeps the MVP focused on system design instead of marketplace settlement and seller-management complexity |
| Customer frontend | Thin end-to-end customer flow | Provides a real browse-to-order journey without spending excessive time on UI polish |
| Administration | Complete admin panel for the MVP scope | Makes catalog, inventory, order, and user operations testable through real workflows |
| Initial environment | Local Docker Compose | Makes the environment repeatable and avoids premature cloud complexity and cost |
| Initial architecture | Modular monolith | Preserves business boundaries without introducing distributed-system failures too early |
| Primary database | PostgreSQL | Strong fit for transactional order and inventory data, constraints, joins, and concurrency exercises |

---

## 2. Product Vision

Build a single-seller e-commerce platform in which customers can discover physical products, maintain a cart, place and manage orders, and make a simulated payment. Administrators can manage the complete MVP business operation through an admin panel.

The application is also a controlled laboratory. Every later infrastructure component must be introduced to solve an observed limitation and supported by measurements.

### Product success for the learning project

The project succeeds when it can demonstrate, with code and evidence, how a simple modular monolith evolves toward a scalable distributed architecture while preserving business correctness.

---

## 3. Actors and Responsibilities

### Guest

- Browse products and categories
- Search products
- View product details
- Register
- Log in

### Customer

- Perform all guest operations
- Add, update, and remove cart items
- View cart totals
- Add or select a delivery address
- Place an order
- Make a simulated payment
- View order history and order details
- Cancel an eligible order
- View personal profile

### Administrator

- Log in to the admin panel
- View dashboard summaries
- Create, update, publish, unpublish, and archive products
- Manage categories
- Manage product prices
- Add or adjust inventory with a reason
- View low-stock products
- View customers
- View and filter orders
- Change permitted order states
- Cancel and refund simulated orders
- Review inventory movements

### System

- Validate business rules
- Calculate prices and totals server-side
- Preserve order price snapshots
- Prevent negative inventory
- Maintain audit timestamps
- Reject unauthorized operations
- Produce consistent API errors

---

## 4. MVP Functional Requirements

Requirements use stable identifiers so tests, APIs, and future ADRs can refer to them.

### 4.1 Identity and access

| ID | Requirement | Priority |
|---|---|---|
| FR-ID-001 | A guest can register using name, email, and password | Must |
| FR-ID-002 | A registered user can log in and receive authentication credentials | Must |
| FR-ID-003 | A customer can view and update permitted profile fields | Must |
| FR-ID-004 | The system enforces customer and administrator roles | Must |
| FR-ID-005 | Passwords are never stored in plaintext | Must |
| FR-ID-006 | An administrator can view users but cannot read their passwords | Must |
| FR-ID-007 | Password reset is supported | Later |
| FR-ID-008 | Social login and multi-factor authentication are supported | Later |

### 4.2 Catalog

| ID | Requirement | Priority |
|---|---|---|
| FR-CAT-001 | Customers can list active products | Must |
| FR-CAT-002 | Customers can view product details | Must |
| FR-CAT-003 | Customers can filter by category and price range | Must |
| FR-CAT-004 | Customers can search by product name or SKU using PostgreSQL initially | Must |
| FR-CAT-005 | Administrators can manage products and categories | Must |
| FR-CAT-006 | Administrators can publish and unpublish products | Must |
| FR-CAT-007 | Product lists are paginated | Must |
| FR-CAT-008 | Product variants such as size and color are supported | Later |
| FR-CAT-009 | Reviews, ratings, recommendations, and wishlists are supported | Later |

### 4.3 Inventory

| ID | Requirement | Priority |
|---|---|---|
| FR-INV-001 | Every sellable product has an inventory record | Must |
| FR-INV-002 | Administrators can increase or decrease inventory with a reason | Must |
| FR-INV-003 | Every adjustment creates an inventory movement record | Must |
| FR-INV-004 | Inventory cannot become negative | Must |
| FR-INV-005 | Checkout validates current availability | Must |
| FR-INV-006 | Successful order placement reduces available inventory atomically | Must |
| FR-INV-007 | Eligible order cancellation restores inventory exactly once | Must |
| FR-INV-008 | Administrators can view low-stock products | Should |
| FR-INV-009 | Warehouse-level inventory and stock transfers are supported | Later |

### 4.4 Cart

| ID | Requirement | Priority |
|---|---|---|
| FR-CART-001 | An authenticated customer has one active cart | Must |
| FR-CART-002 | A customer can add, update, and remove cart items | Must |
| FR-CART-003 | The cart returns current product price and availability | Must |
| FR-CART-004 | Quantity must be a positive integer and obey a configurable per-item limit | Must |
| FR-CART-005 | Cart totals are calculated by the backend | Must |
| FR-CART-006 | Guest carts and cross-device merging are supported | Later |

### 4.5 Checkout and orders

| ID | Requirement | Priority |
|---|---|---|
| FR-ORD-001 | A customer can create an order from the active cart | Must |
| FR-ORD-002 | Checkout requires a delivery address | Must |
| FR-ORD-003 | The server recalculates all prices and totals | Must |
| FR-ORD-004 | An order stores immutable item-name, SKU, quantity, and price snapshots | Must |
| FR-ORD-005 | A customer can list and view only their own orders | Must |
| FR-ORD-006 | An administrator can list, filter, and view all orders | Must |
| FR-ORD-007 | Order creation is idempotent for a repeated client request | Must |
| FR-ORD-008 | Order history records important status transitions | Must |
| FR-ORD-009 | Split shipments, partial fulfilment, and returns are supported | Later |

### 4.6 Simulated payment

| ID | Requirement | Priority |
|---|---|---|
| FR-PAY-001 | Checkout creates a simulated payment attempt | Must |
| FR-PAY-002 | The simulator supports success, failure, and timeout outcomes | Must |
| FR-PAY-003 | The system prevents duplicate charges for the same payment request | Must |
| FR-PAY-004 | The system records payment state changes | Must |
| FR-PAY-005 | No real card or banking data is stored | Must |
| FR-PAY-006 | A real external payment gateway is integrated | Later |

### 4.7 Order cancellation

| ID | Requirement | Priority |
|---|---|---|
| FR-CAN-001 | A customer can cancel an order only in a permitted state | Must |
| FR-CAN-002 | Cancellation restores reserved/deducted inventory exactly once | Must |
| FR-CAN-003 | A successful simulated payment produces a simulated refund record | Must |
| FR-CAN-004 | Cancellation and refund history is auditable | Must |

### 4.8 Administration

| ID | Requirement | Priority |
|---|---|---|
| FR-ADM-001 | The admin panel provides catalog management | Must |
| FR-ADM-002 | The admin panel provides inventory management | Must |
| FR-ADM-003 | The admin panel provides order management | Must |
| FR-ADM-004 | The admin panel provides user visibility and role-protected actions | Must |
| FR-ADM-005 | The dashboard shows total products, low-stock products, orders, and customers | Should |
| FR-ADM-006 | The admin panel supports bulk import/export | Later |

---

## 5. MVP User Journeys

### Journey A — Customer places an order

1. Customer registers or logs in.
2. Customer browses or searches the catalog.
3. Customer opens a product detail page.
4. Customer adds an available quantity to the cart.
5. Customer reviews cart items and totals.
6. Customer supplies a delivery address.
7. Customer submits checkout with an idempotency key.
8. The server validates prices and stock.
9. The server creates the order, order items, inventory movements, and simulated payment state.
10. The customer sees a confirmation or a clear failure response.

### Journey B — Customer cancels an eligible order

1. Customer opens their order details.
2. The application shows whether cancellation is allowed.
3. Customer confirms cancellation.
4. The server changes the order state once.
5. Inventory is restored once.
6. A simulated refund is recorded when required.

### Journey C — Administrator prepares a product for sale

1. Administrator logs in.
2. Administrator creates a category.
3. Administrator creates a product with a unique SKU and price.
4. Administrator adds initial inventory with a reason.
5. Administrator publishes the product.
6. The product becomes visible in the customer catalog.

### Journey D — Administrator manages an order

1. Administrator opens the order list.
2. Administrator filters by date, customer, or status.
3. Administrator opens an order.
4. Administrator applies a valid status transition.
5. Invalid transitions are rejected and logged.

---

## 6. Initial Business Rules

1. Email addresses are unique after normalization.
2. Product SKU is unique and cannot be silently reused.
3. Money is represented with decimal-safe types and stored in the smallest currency unit or a fixed-precision numeric column—never binary floating point.
4. Product price must be zero or positive; sellable MVP products normally require a positive price.
5. Inventory quantity cannot be negative.
6. Cart quantity must be at least one and cannot exceed the configured limit.
7. Cart prices are informational; checkout always uses server-side current prices.
8. An order preserves item and price snapshots even if the product later changes.
9. A customer can access only their own addresses, cart, payments, and orders.
10. Administrators use explicitly authorized endpoints.
11. Cancellation is allowed only before fulfilment reaches a configured terminal boundary.
12. Inventory restoration, payment, refund, and order creation operations must be idempotent.
13. Timestamps are stored in UTC and rendered in the user's locale by the client.
14. Hard deletion is avoided for business records that are part of order or inventory history.

---

## 7. Explicit MVP Exclusions

These are intentionally excluded from Phase 1:

- Multiple sellers or vendor onboarding
- Seller commissions, settlements, and payouts
- Multiple warehouses
- Product variants
- Real payment provider integration
- Real shipping provider integration
- Tax engine for multiple jurisdictions
- Coupons, loyalty points, gift cards, and promotions
- Reviews, ratings, wishlist, and recommendations
- Returns and partial refunds
- Full-text search engine
- Redis caching
- RabbitMQ and Celery
- Microservices
- Kubernetes
- Multi-region deployment

Exclusion does not mean these features are unimportant. It protects the learning sequence from premature complexity.

---

## 8. Non-Functional Requirements

### 8.1 Performance targets

Targets are evaluated under the defined Phase 1 baseline workload, after a short warm-up, on the documented local machine.

| ID | Target |
|---|---|
| NFR-PERF-001 | Read API P95 latency ≤ 300 ms |
| NFR-PERF-002 | Ordinary write API P95 latency ≤ 500 ms |
| NFR-PERF-003 | Checkout P95 latency ≤ 1,000 ms with the local payment simulator |
| NFR-PERF-004 | Error rate under baseline load < 1%, excluding intentional validation and authorization failures |
| NFR-PERF-005 | Product-list responses return no more than the configured maximum page size |

These are learning baselines, not claims about public production performance.

### 8.2 Correctness and consistency

| ID | Requirement |
|---|---|
| NFR-CON-001 | Order, payment, and inventory changes requiring atomicity use database transactions |
| NFR-CON-002 | Confirmed inventory never becomes negative |
| NFR-CON-003 | Repeating an idempotent checkout request does not create a second order |
| NFR-CON-004 | Order totals and price snapshots remain unchanged after order creation |
| NFR-CON-005 | Later search and notification projections may be eventually consistent, but the system of record remains authoritative |

### 8.3 Security

| ID | Requirement |
|---|---|
| NFR-SEC-001 | Passwords use a modern adaptive password hash |
| NFR-SEC-002 | Every protected operation authenticates the caller and checks authorization |
| NFR-SEC-003 | Secrets are supplied through environment/configuration mechanisms and never committed |
| NFR-SEC-004 | Logs exclude passwords, access tokens, and payment-sensitive data |
| NFR-SEC-005 | Request bodies and query parameters are validated with explicit limits |
| NFR-SEC-006 | API error responses do not expose stack traces or internal credentials |

### 8.4 Maintainability and testability

| ID | Requirement |
|---|---|
| NFR-MNT-001 | Business domains have explicit module boundaries |
| NFR-MNT-002 | Business rules are not implemented directly in route handlers |
| NFR-MNT-003 | Database changes use migrations |
| NFR-MNT-004 | Core business rules have unit tests |
| NFR-MNT-005 | Critical user journeys have integration tests |
| NFR-MNT-006 | Local setup is reproducible from documented commands |

### 8.5 Reliability learning target

The local MVP has no real production SLA. For architecture exercises, use this hypothetical small-production target:

- Monthly availability objective: 99.5%
- Recovery point objective: 15 minutes
- Recovery time objective: 60 minutes
- All critical data changes are durable after a successful response

These targets will be revisited when observability, backups, deployment, and resilience are introduced.

---

## 9. Scale and Capacity Assumptions

Use three separate levels so the architecture is not prematurely designed for fictional traffic.

| Metric | MVP dataset | Phase 3 stress dataset | Final design target |
|---|---:|---:|---:|
| Registered users | 10,000 | 1,000,000 | 10,000,000 |
| Daily active users | 1,000 | 100,000 | 1,000,000 |
| Concurrent users | 100 | 10,000 | 100,000 |
| Products | 2,000 | 500,000 | 5,000,000 |
| Orders | 20,000 total | 5,000,000 total | 500,000/day |
| Order items | 60,000 total | 15,000,000 total | Estimated from measured average basket size |
| Baseline API traffic | 50 requests/second | Discover limit through testing | 50,000 requests/second peak |
| Order traffic | 1 order/second | Discover limit through testing | Approximately 116 orders/second peak under stated assumptions |

### Initial storage estimate

For the MVP, assume approximately:

- 10,000 users × 2 KB logical row/index footprint ≈ 20 MB
- 2,000 products × 5 KB logical row/index footprint ≈ 10 MB
- 20,000 orders × 3 KB ≈ 60 MB
- 60,000 order items × 1 KB ≈ 60 MB
- Audit, inventory, payment, indexes, and overhead: apply a generous 5–10× multiplier

The resulting database remains comfortably small. The point of Phase 3 is to generate much larger data and measure actual query behavior rather than over-engineer Phase 1.

---

## 10. Service-Level Indicators and Objectives

### Initial SLIs

- Request count by route and status class
- P50, P95, and P99 server latency
- 5xx error ratio
- Checkout success ratio
- Order creation duplication count
- Inventory invariant violation count
- Database connection utilization

### Initial objectives

| SLI | Objective |
|---|---|
| Read latency | 95% of valid read requests complete within 300 ms under baseline load |
| Write latency | 95% of ordinary valid writes complete within 500 ms under baseline load |
| Checkout latency | 95% complete within 1 second using the local simulator |
| Server reliability | At least 99% of valid requests avoid 5xx responses during the baseline test |
| Inventory correctness | Zero negative inventory records |
| Checkout idempotency | Zero duplicate orders for repeated identical idempotency keys |

The exact hardware, dataset seed, application build, and test script must accompany every benchmark.

---

## 11. API Conventions

### 11.1 General rules

- Base path: `/api/v1`
- JSON request and response bodies
- Resource-oriented URLs use plural nouns
- HTTP methods carry their conventional meanings
- Timestamps use UTC ISO 8601 representation
- Money is serialized as a decimal string plus currency, or as an explicitly named smallest-unit integer
- Server-calculated fields cannot be trusted from the client
- Unknown fields should be rejected for command-style requests where silent acceptance would hide errors

### 11.2 Example resource routes

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login

GET    /api/v1/products
GET    /api/v1/products/{product_id}

GET    /api/v1/cart
POST   /api/v1/cart/items
PATCH  /api/v1/cart/items/{item_id}
DELETE /api/v1/cart/items/{item_id}

POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{order_id}
POST   /api/v1/orders/{order_id}/cancellation

GET    /api/v1/admin/products
POST   /api/v1/admin/products
PATCH  /api/v1/admin/products/{product_id}
POST   /api/v1/admin/inventory/adjustments
GET    /api/v1/admin/orders
```

### 11.3 Success responses

Return the resource directly for a single-resource request:

```json
{
  "id": "01JEXAMPLE",
  "status": "pending_payment",
  "currency": "INR",
  "total": "2499.00",
  "created_at": "2026-09-23T09:00:00Z"
}
```

Return an `items` collection plus pagination metadata for lists:

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 0,
    "total_pages": 0
  }
}
```

Offset pagination is acceptable for the MVP. Phase 3 will measure it against cursor pagination on large datasets.

### 11.4 Error responses

Use one problem-details-style structure:

```json
{
  "type": "https://example.local/problems/insufficient-inventory",
  "title": "Insufficient inventory",
  "status": 409,
  "detail": "Only 2 units are currently available.",
  "instance": "/api/v1/orders",
  "code": "INSUFFICIENT_INVENTORY",
  "request_id": "req_01JEXAMPLE",
  "errors": [
    {
      "field": "items[0].quantity",
      "message": "Requested quantity exceeds available inventory."
    }
  ]
}
```

Recommended status usage:

| Status | Usage |
|---:|---|
| 200 | Successful read or update |
| 201 | Resource created |
| 204 | Successful operation with no response body |
| 400 | Malformed request |
| 401 | Missing or invalid authentication |
| 403 | Authenticated but not authorized |
| 404 | Resource not found or intentionally hidden |
| 409 | Business conflict, duplicate, invalid state, or insufficient stock |
| 422 | Structurally valid request with field validation errors |
| 429 | Rate limit exceeded in later phases |
| 500 | Unexpected server failure |

### 11.5 Idempotency

- `POST /orders` requires an `Idempotency-Key` header.
- The key is scoped to the authenticated customer and operation.
- A repeated key with the same request returns the original outcome.
- A repeated key with a different request body returns a conflict.
- Idempotency records have a documented retention duration.

### 11.6 Request tracing

- Accept or generate `X-Request-ID`.
- Return the request ID in the response.
- Include it in application logs and errors.
- Replace externally supplied values that violate length or character limits.

---

## 12. Initial Domain Boundaries

The MVP is one deployable application, but the code is divided into domains.

| Module | Owns | Does not own |
|---|---|---|
| Identity | Users, credentials, roles | Orders or inventory |
| Catalog | Products, categories, current product price | Stock quantities and order snapshots |
| Inventory | Stock balance, adjustments, movements | Product descriptions or payment state |
| Cart | Active carts and cart items | Final order price snapshots |
| Order | Orders, order items, addresses, state history | User credentials or product master data |
| Payment | Simulated attempts and refunds | Order fulfilment rules |
| Administration | Authorized use cases across domains | A separate copy of domain data |

These are module boundaries, not network services. Cross-module access will occur through explicit application interfaces rather than arbitrary table manipulation.

---

## 13. System Context

```mermaid
flowchart TD
    Customer[Customer] -->|Browse, cart, checkout, orders| Web[React Web Application]
    Admin[Administrator] -->|Catalog, inventory, orders, users| Web
    Web -->|HTTPS/JSON API| App[FastAPI Modular Monolith]
    App -->|Transactional reads and writes| DB[(PostgreSQL)]
    App -->|Success, failure, timeout| Pay[Local Payment Simulator]
```

### Trust boundaries

- The browser is untrusted.
- Every business rule is revalidated by the backend.
- The API authenticates and authorizes protected actions.
- PostgreSQL is reachable only by the backend in the local Compose network.
- The payment simulator contains no real financial data.

---

## 14. Initial Container View

```mermaid
flowchart LR
    Browser[Browser] --> Frontend[React Container]
    Frontend --> Backend[FastAPI Container]
    Backend --> Database[(PostgreSQL Container)]
```

Phase 0 provisions PostgreSQL first. The FastAPI and React services are added when their Phase 1 projects exist.

### Planned local ports

| Component | Host port | Purpose |
|---|---:|---|
| React development server | 5173 | Customer and admin UI |
| FastAPI | 8000 | REST API and generated API documentation |
| PostgreSQL | 5432 | Local database; avoid public exposure outside development |

---

## 15. Local Docker Baseline

The initial `docker-compose.yml` should start with only PostgreSQL:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: ecommerce
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ecommerce_dev_only}
    ports:
      - "5432:5432"
    volumes:
      - ecommerce_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ecommerce -d ecommerce"]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 10s

volumes:
  ecommerce_postgres_data:
```

### Environment contract

```dotenv
APP_ENV=development
APP_NAME=ecommerce-system-design
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+asyncpg://ecommerce:ecommerce_dev_only@postgres:5432/ecommerce
POSTGRES_PASSWORD=ecommerce_dev_only
JWT_SECRET=replace-with-a-long-local-secret
ACCESS_TOKEN_TTL_MINUTES=30
LOG_LEVEL=INFO
```

The real `.env` file must not be committed. Commit `.env.example` with non-sensitive examples.

### Intended local commands

```bash
docker compose up -d postgres
docker compose ps
docker compose logs postgres
docker compose down
```

Do not use `docker compose down -v` casually because it deletes the named development database volume.

---

## 16. ADR-001 — Use PostgreSQL as the Initial Database

## Definition

An Architecture Decision Record (ADR) is a short document that records an important technical decision, including:

The problem or context
The options considered
The decision made
The reasons for choosing it
Benefits and disadvantages
Operational consequences
When the decision should be reconsidered
For example:

Decision: Use PostgreSQL as the initial database

Context:
The MVP needs reliable transactions for users, inventory, carts, and orders.

Options:
- PostgreSQL
- MongoDB
- SQLite

Decision:
Use PostgreSQL.

Reason:
The application has relational data, transactional checkout, foreign keys,
constraints, indexing, and concurrency requirements.

Trade-offs:
PostgreSQL requires more setup than SQLite but provides stronger production
capabilities.

Revisit when:
Database scale, workload, or access patterns require a different solution.


### Status

Accepted for the monolith and early scaling phases.

### Context

The MVP contains users, products, inventory, carts, orders, order items, payments, addresses, and state histories. Several workflows require constraints and atomic multi-record changes. Inventory correctness and order creation are more important than independent scaling in Phase 1.

### Decision

Use one PostgreSQL database for the modular monolith. Organize access by application module and keep ownership rules explicit. Use migrations for every schema change.

### Options considered

#### PostgreSQL

- Strong transactions and constraints
- Rich indexing and query-planning tools
- Row locking and isolation-level experiments
- Appropriate for relational order and inventory data
- Familiar operational ecosystem

#### MongoDB

- Flexible document model
- Convenient for some product metadata shapes
- Does not remove the need to model transactional invariants
- Adds unnecessary polyglot persistence to the first phase

#### Separate database per planned service

- Resembles the eventual microservice target
- Introduces distributed transactions and operational overhead before module boundaries have been proven
- Makes early business changes slower and harder to reason about

### Consequences

#### Positive

- Checkout can use local transactions.
- Foreign keys and unique/check constraints protect invariants.
- Joins simplify early admin reporting.
- Database behavior can be explored with `EXPLAIN ANALYZE`, locks, and isolation levels.

#### Negative

- Modules can become coupled through shared tables if discipline is weak.
- The database is initially a shared scaling and failure boundary.
- Later extraction requires deliberate data migration and integration contracts.

### Guardrails

- Each module owns its tables conceptually.
- One module does not update another module's tables directly.
- Cross-module operations go through explicit application interfaces.
- No additional database technology is introduced without a measured need and an ADR.

### Revisit conditions

Revisit this decision when:

- A bounded context is extracted as an independently deployed service.
- Search requirements exceed suitable PostgreSQL capabilities for the experiment.
- Read or write scale tests expose a database bottleneck that simpler optimizations cannot solve.
- A module has a clearly different data model, lifecycle, or availability requirement.

---

## 17. Risks and Early Mitigations

| Risk | Impact | Initial mitigation |
|---|---|---|
| Scope grows into an Amazon clone | Learning stalls | Enforce the explicit exclusion list |
| Admin UI consumes most project time | Backend learning slows | Use functional forms/tables and a reusable theme, not custom visual polish |
| Shared database causes module coupling | Hard service extraction | Establish table ownership and interfaces from the first migration |
| Checkout creates duplicate orders | Financial and inventory inconsistency | Require idempotency keys and database uniqueness |
| Concurrent checkout oversells | Incorrect stock | Add database constraints and concurrency tests |
| Benchmarks become incomparable | Architectural claims lack evidence | Version scripts, dataset seeds, hardware notes, and configuration |
| Infrastructure is introduced by enthusiasm | Unnecessary complexity | Require a problem statement, baseline measurement, and ADR |

---

## 18. Phase 0 Completion Checklist

- [x] Business model chosen: single seller
- [x] Customer UI scope chosen: thin end-to-end flow
- [x] Admin UI scope chosen: complete MVP administration
- [x] Initial environment chosen: local Docker Compose
- [x] Product vision documented
- [x] Actors documented
- [x] MVP functional requirements documented
- [x] MVP exclusions documented
- [x] Business rules documented
- [x] Non-functional targets documented
- [x] Initial capacity assumptions documented
- [x] API response and error conventions documented
- [x] High-level system context documented
- [x] Initial module boundaries documented
- [x] PostgreSQL decision recorded
- [ ] Project repository initialized
- [ ] Directory structure created
- [ ] `.gitignore` and `.env.example` created
- [ ] Initial `docker-compose.yml` created
- [ ] PostgreSQL health check verified locally
- [ ] Root README contains start/stop/health commands
- [ ] Phase 0 tagged in Git

Phase 0 is complete only after the unchecked environment items are implemented and verified.

---

## 19. Immediate Implementation Sequence

1. Create the repository and baseline directories.
2. Add `.gitignore`, `.env.example`, and `docker-compose.yml`.
3. Start PostgreSQL and verify its health.
4. Add a root README with local commands and current architecture.
5. Save this requirements document under `docs/requirements/`.
6. Save the context design under `docs/architecture/` when the project repository exists.
7. Save ADR-001 under `docs/adr/`.
8. Commit the Phase 0 foundation.
9. Tag the milestone as `v0-phase-0-foundation`.
10. Begin Phase 1 with the FastAPI project skeleton and initial database migration.

---

## 20. Phase 0 Learning Review

Before moving to Phase 1, be able to answer:

1. Why are functional and non-functional requirements different?
2. Why is P95 more useful than average latency for many user-facing APIs?
3. What is the difference between an SLI, an SLO, and an SLA?
4. Why is the browser considered untrusted?
5. Which business operations require strong consistency in this design?
6. Which future operations can tolerate eventual consistency?
7. Why is a modular monolith preferable to immediate microservices here?
8. Why was PostgreSQL chosen over MongoDB for the initial system of record?
9. What problem does an idempotency key solve?
10. Which measurements would justify adding Redis, RabbitMQ, a search engine, or another service?

The next practical action is to create and verify the Phase 0 repository scaffold. No application endpoints are implemented until this foundation is reproducible.
