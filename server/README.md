# E-commerce Backend

Phase 1 modular-monolith backend for the e-commerce system-design learning project.

The API is deliberately one deployable FastAPI application with one PostgreSQL database. It contains domain packages for authentication, catalog, inventory, cart, orders, and simulated payments. It is not a microservice system yet.

## Current guarantees

- PostgreSQL is the primary local database.
- Alembic migrations are the only schema-creation mechanism.
- Checkout locks inventory rows and records inventory movements in the same transaction.
- Checkout requests use an idempotency key and request fingerprint.
- Simulated payments lock the order and only proceed from pending_payment.
- API responses include X-Request-ID; validation and HTTP failures use problem-details JSON.

## Start the full local environment

Run these commands from the repository root:

~~~bash
cp server/.env.example .env
docker compose up --build -d
docker compose exec api alembic upgrade head
~~~

The API documentation is available at http://localhost:8000/docs.

Verify service health:

~~~bash
curl http://localhost:8000/api/v1/health/live
curl http://localhost:8000/api/v1/health/ready
~~~

Stop the environment:

~~~bash
docker compose down
~~~

Avoid docker compose down -v unless you intentionally want to delete the local PostgreSQL data volume.

## Run the API directly

Use a running PostgreSQL instance, then:

~~~bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
~~~

When running directly on the host, the default database URL in .env.example uses localhost. Docker Compose injects the correct internal db host for containers.

## API flow

1. Register and log in through /api/v1/auth.
2. An administrator creates and publishes a product, then adds inventory.
3. A customer adds published products to /api/v1/cart.
4. The customer creates an order at POST /api/v1/orders with Idempotency-Key.
5. The customer calls POST /api/v1/payments/{order_id}/attempt with success, failure, or timeout.
6. The customer cancels an eligible order through POST /api/v1/orders/{order_id}/cancellation.

## Migrations

~~~bash
cd server
alembic upgrade head
alembic current
alembic revision --autogenerate -m "describe the change"
~~~

Review every generated migration before committing it. Do not use Base.metadata.create_all() in the application; it bypasses migration history.

## Testing and CI

~~~bash
cd server
pytest -q
~~~

GitHub Actions starts PostgreSQL, applies the migration, compiles the application, and runs API contract tests on pushes and pull requests.

## Next hardening work

- Add integration tests for inventory contention, duplicate checkout submissions, and payment/cancellation races.
- Add pagination to administrative list endpoints.
- Move non-trivial checkout, payment, and inventory rules from routers into service/use-case modules.
- Add structured logs and domain metrics before load testing.
