# Excercises

## Practical exercise 1: Run the monolith and place one order

We’ll use your stage-01-monolith branch. By the end, you should have a running PostgreSQL database, API, and React client; one successful test order; and a record of what you observed.

**Time**: About 30–45 minutes. Run the commands on the computer where you have the repository and Docker.

**First, understand the pieces**
| Term | Meaning in this exercise |
|---|---|
| Docker Compose | Starts the database, API, and client together using `docker-compose.yml`. |
| Migration | Changes the database structure so its tables match the application code. |
| Seed data | Sample accounts and products that let us test the app. |
| Health check | A quick check that a component is responding. |
| Payment simulator | Your API pretends a payment succeeded; no real money moves. |


### Step 1 — Check your branch and Docker
Open a terminal in the repository’s root directory—the directory containing docker-compose.yml—and run:

```bash 
git branch --show-current
docker --version
docker compose version
```

The first command should print stage-01-monolith. The other two should print version information. Make sure Docker Desktop or the Docker service is running.
If you do not have the repository on this computer yet, get it with:

```bash
git clone -b stage-01-monolith https://github.com/subhamsahu/ecommerce-system-design.git
cd ecommerce-system-design
```

### Step 2 — Configure your local environment
Before the first startup, create a file named .env beside docker-compose.yml:

```dotenv
POSTGRES_PASSWORD=choose_a_local_password
JWT_SECRET=choose_a_long_random_local_secret
VITE_API_URL=http://localhost:8000
```

Replace the two choose_... values. Use letters, numbers, and underscores for the database password for now. Do not commit .env.
If you have already started this project with an existing PostgreSQL data directory, keep its original database password. Changing .env does not change the password inside an existing database.

### Step 3 — Start the application
From the same root directory, run:

```bash
docker compose up --build -d
docker compose ps
```
--build creates the API and client images from your code. -d leaves them running while you use the terminal. In docker compose ps, look for three running services: ecomm-postgrs-service, api, and client. The database should become healthy. Compose runs the database migration before starting the API.

### Step 4 — Check each layer
Run these separately:

```bash
docker compose exec ecomm-postgrs-service pg_isready -U labadmin -d ecommerce
```

Expected: PostgreSQL reports that it is accepting connections.

```bash
docker compose exec api alembic current
```

Expected: Alembic prints a current migration revision.
Then open **http://localhost:8000/health** in your browser. Expected:

```json
{"status":"healthy"}
```

What you just proved: the database accepts connections, its migrations ran, the API responds, and the client is served. The /health response alone does not test the database, which is why we checked both.

### Step 5 - Create test data

Run:
```bash
docker compose exec api python manage.py seed
docker compose exec api python manage.py seed_fake --count 10
docker compose exec api python manage.py createsuperuser
```

- seed creates the initial role permissions.
- seed_fake --count 10 creates sample customers and published products with stock.
- createsuperuser asks you to enter an admin username, email, name, and password. Remember these credentials.
The sample customer seed_user_000001 has the local test password TestPassword123!. Each newly seeded product starts with 100 units. These are disposable development accounts.

### Step 6 — Place an order as a customer
1. Go to http://localhost:5173/login.
2. Log in as seed_user_000001 with TestPassword123!.
3. Open http://localhost:5173/store.
4. Find a seeded product and write down its displayed available quantity. It may differ from 100 if this database was used before.
5. Add one unit to the cart.
6. Open the cart and choose Checkout.
7. Enter a test address, then select Pay once.
8. Write down the order number shown in the confirmation.
Expected: the client reports that the simulated payment succeeded, the cart becomes empty, and the product’s available quantity falls by one. Checkout creates an order, and the client then makes a separate simulated payment request. 
If you get an error after pressing Pay, record the message and order number before trying again. We identified a retry gap in this screen during review, and investigating that result is part of our upcoming exercise.

### Step 7 — Run the existing regression tests
```bash
docker compose exec api python -m pytest -q tests/test_order_payment_invariants.py
```

Expected: seven tests pass. These tests use a disposable SQLite database inside the test process. They check important application rules, while today’s manual order checks that the running app works with PostgreSQL. A later exercise will test competing checkouts directly on PostgreSQL.

### Step 8 — Record your results
Create docs/verification/phase1-postgres-smoke.md in your branch and fill in actual results:

### Phase 1 PostgreSQL smoke test

Date:
Commit:
Machine/OS:

| Check | Result | Observation |
|---|---|---|
| Three Compose services running | Pass/Fail | |
| PostgreSQL accepting connections | Pass/Fail | |
| Alembic current revision shown | Pass/Fail | |
| API /health responds | Pass/Fail | |
| Client login works | Pass/Fail | |
| Customer order and payment succeed | Pass/Fail | Order ID: |
| Product stock decreases by one | Pass/Fail | Before: / After: |
| API regression tests pass | Pass/Fail | Number passed: |

Problems encountered:




## Practical exercise 2: Two customers, one item
**Question we are testing**: If stock is 1 and two customers check out together, can both create an order?
Expected result: one checkout succeeds (201), one is rejected (409), and stock ends at 0. We will leave payment out of this exercise so we can focus on the checkout transaction.

**Why this matters**
Both customers may see “1 available” and add the product to their carts. That is okay: adding to a cart does not reserve stock. At checkout, the API must read and change stock safely. Your code uses a PostgreSQL row lock with with_for_update() inside the checkout transaction. The second checkout should wait, then discover that the first used the last unit. See the checkout code at **server/app/orders/service.py**

```bash
ecommerce-system-design\server\scripts>python last_item_race.py

Customer 1: HTTP 201 ...
Customer 2: HTTP 409 ...
Final stock: 0
Orders by customer: [1, 0]
PASS: One order, one rejected checkout, zero stock.

```

The winning customer may switch between runs; either [1, 0] or [0, 1] is correct. Their successful order will be pending_payment, because this script deliberately stops before payment.
Explain the result
Add these answers to your verification notes:
1. Why could both customers add the item to their carts? --> Because Adding in cart is just placeholder, buyer can order or it or may not
2. Why did only one checkout create an order? At run time if only 1 item in stock it can go to one person only
3. What does HTTP 409 mean here? --> Conflict
4. Why must this experiment use PostgreSQL, given that the existing seven tests use SQLite? -> The checkout code uses with_for_update(), which asks PostgreSQL to lock the inventory row. SQLite handles concurrent writes differently and does not provide the same SELECT FOR UPDATE row-lock mechanism. The seven SQLite tests check business behavior, but passing them cannot establish that two PostgreSQL checkouts safely compete for the last unit.

## Excerscise 3: Retry checkout and fail a payment
This teaches two rules:
- **Idempotency**: retrying the same checkout request must return the same order.
- **Compensation**: a failed payment must return the reserved stock exactly once.

Use http://localhost:8000/docs for this exercise. It lets you send API requests without writing a script.

1. Prepare a new customer
In /docs, use **POST /api/v1/auth/register** with a new username and email. For example:
```json
{
  "username": "retry_student_01",
  "email": "retry_student_01@example.test",
  "full_name": "Retry Student",
  "password": "TestPassword123!"
}
```
If you have already used that username, change the 01 in both fields.
Use POST **/api/v1/auth/login** with the same username and password. 
Copy access_token from the response. 
Click Authorize at the top of /docs and paste the token. 
This lets subsequent requests act as that customer.

2. Record the starting stock
Use **GET /api/v1/products** to find a seeded product. Write down its id and available_quantity. Choose a product with at least one unit.
Call this starting quantity S. For example, S = 100.

3. Add one unit to the cart
Use **POST /api/v1/cart/items**:
```json
{
  "product_id": 1,
  "quantity": 1
}
```

Replace 1 with the product ID you selected. Check that the response contains the item.

4. Submit checkout twice
Use **POST /api/v1/orders**. Set the Idempotency-Key header to a value you have not used before, such as:
lesson-checkout-001

Use this request body:
```json
{
  "address": {
    "line1": "1 Test Road",
    "city": "Test City",
    "state": "Test State",
    "postal_code": "123456",
    "country": "IN"
  }
}
```

The first request should return 201. Write down its order id; its status should be pending_payment.
Now press Execute again without changing the key or body. The second request should return 200 with the same order ID. Check the product again: stock should be S − 1, not S − 2.
This simulates a client that did not receive the first response and sent the request again.

5. Simulate payment failure
Use **POST /api/v1/payments/{order_id}/attempt**, replacing {order_id} with your order ID. Give this request a different Idempotency-Key, such as lesson-payment-failure-001, and send:

```json
{
  "outcome": "failure"
}
```

Expected: payment status failed. Check GET /api/v1/orders/{order_id}: the order should be payment_failed. Check the product: stock should return to S.
Execute the same payment request with the same payment key once more. It should return the existing payment (200), and stock should remain S.
Record these five results
| Check | Expected |
|---|---|
| First checkout | `201`, new order ID |
| Same checkout key and body | `200`, same order ID |
| Stock after checkout retries | `S − 1` |
| Payment failure | Order becomes `payment_failed`; stock returns to `S` |
| Same payment failure repeated | `200`, same payment; stock remains `S` |