# Implement Razorpay Test Mode payment integration in the existing ecommerce application.

First inspect the current backend and frontend structure, especially:

- Order models and order status values
- Existing payment models, routers, and services
- Checkout and cancellation flow
- Database session and transaction handling
- Existing authentication and API versioning conventions
- Existing simulated payment implementation
- Current React checkout page/components
- Alembic migration setup
- Existing tests and test fixtures

Do not replace the existing payment design blindly. Extend the current architecture consistently with the existing codebase.

## Objective

Add a production-like Razorpay Test Mode integration while preserving the existing simulated payment provider for automated tests.

Use this abstraction:

```text
PaymentProvider
├── SimulatedPaymentProvider
└── RazorpayPaymentProvider
```

The provider must be selectable through configuration:

```env
PAYMENT_PROVIDER=simulated
```

or:

```env
PAYMENT_PROVIDER=razorpay
```

The default test configuration should not require Razorpay credentials. Never commit real credentials.

## Backend configuration

Add the following environment variables:

```env
PAYMENT_PROVIDER=simulated
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
RAZORPAY_CURRENCY=INR
```

Update the application settings class and `.env.example`.

Validate Razorpay configuration only when:

```env
PAYMENT_PROVIDER=razorpay
```

Fail clearly during startup or payment initialization if required Razorpay credentials are missing.

Keep `RAZORPAY_KEY_SECRET` and `RAZORPAY_WEBHOOK_SECRET` server-side only. The frontend may receive the public Razorpay key ID, but never either secret.

## Razorpay order creation

Implement a backend endpoint similar to:

```http
POST /api/v1/orders/{order_id}/payments
```

This endpoint must:

1. Authenticate the user.
2. Confirm that the order belongs to the authenticated user or that the caller is an authorized admin.
3. Lock or safely re-check the order state.
4. Allow payment only when the business order is in `pending_payment`.
5. Reject cancelled, paid, refunded, or already completed orders.
6. Calculate the amount from the database order total.
7. Never trust an amount sent by the frontend.
8. Convert the amount to the smallest currency unit, such as paise for INR.
9. Create exactly one Razorpay order for each payment attempt.
10. Store the Razorpay order ID in the local payment record.
11. Store the amount, currency, provider, and payment status locally.
12. Return only the data required by the frontend.

Expected response shape:

```json
{
  "payment_id": "local-payment-id",
  "provider": "razorpay",
  "razorpay_key_id": "rzp_test_xxxxx",
  "razorpay_order_id": "order_xxxxx",
  "amount": 50000,
  "currency": "INR",
  "business_order_id": "order-id"
}
```

Do not hold a database transaction or row lock while making a slow external Razorpay API call. Use a safe state transition and handle retries/idempotency correctly.

## Payment model

Extend the existing payment model or create a migration with fields equivalent to:

```text
id
order_id
provider
provider_order_id
provider_payment_id
provider_signature
amount
currency
status
failure_code
failure_description
captured_at
refunded_amount
created_at
updated_at
```

Use the existing project naming conventions and enums.

Add appropriate constraints and indexes:

- Unique provider payment ID when present
- Unique provider order ID when present
- One successful payment per business order
- Indexes for order ID, provider order ID, provider payment ID, and status

Do not allow multiple successful payments for the same business order.

## Frontend Razorpay Checkout

Integrate Razorpay Standard Checkout into the existing React frontend.

The frontend must:

1. Call the backend payment-initiation endpoint.
2. Receive the Razorpay order ID and amount from the backend.
3. Load Razorpay Checkout using the official supported browser integration.
4. Open checkout with:
   - Razorpay key ID
   - Razorpay order ID
   - Amount
   - Currency
   - Customer name
   - Customer email
   - Customer contact
5. Never calculate or modify the amount locally.
6. Never expose the Razorpay secret.
7. Send the successful checkout response to the backend for verification.
8. Display clear success, failure, cancelled, and retry states.
9. Prevent accidental duplicate payment initiation while a request is active.

Use the existing UI style and error-handling conventions.

## Payment verification endpoint

Implement:

```http
POST /api/v1/payments/razorpay/verify
```

Accept:

```json
{
  "business_order_id": "local-order-id",
  "razorpay_order_id": "order_xxxxx",
  "razorpay_payment_id": "pay_xxxxx",
  "razorpay_signature": "signature"
}
```

The backend must:

1. Authenticate the user.
2. Load the local payment using the trusted local business order and stored provider order ID.
3. Confirm that the supplied Razorpay order ID matches the locally stored provider order ID.
4. Verify the signature using HMAC-SHA256:

```text
HMAC_SHA256(razorpay_order_id + "|" + razorpay_payment_id, RAZORPAY_KEY_SECRET)
```

5. Use constant-time comparison for signatures.
6. Reject invalid signatures with a consistent 400 or 401 error.
7. Never trust a frontend success response without signature verification.
8. Verify that the payment amount and currency match the local order.
9. Make the operation idempotent.
10. If the payment is already successfully recorded, return the existing result rather than charging or recording it again.
11. Allow the order transition to paid/confirmed only from `pending_payment`.
12. Reject payment verification if the order was cancelled.
13. Ensure inventory is not restored or deducted twice.
14. Return the current order and payment status.

Do not mark an order as paid if any business invariant fails.

## Razorpay webhook endpoint

Implement:

```http
POST /api/v1/webhooks/razorpay
```

This endpoint must not require normal user authentication, but it must validate the Razorpay webhook signature using the raw request body and:

```env
RAZORPAY_WEBHOOK_SECRET
```

Do not parse and re-serialize the JSON before signature verification.

Support at least these events where applicable:

```text
payment.authorized
payment.captured
payment.failed
order.paid
refund.created
refund.processed
refund.failed
```

Use the actual payload structure documented by Razorpay and inspect the event type safely.

Webhook processing must:

1. Validate the webhook signature.
2. Store the event ID or a deterministic event hash.
3. Ignore duplicate webhook deliveries safely.
4. Update payment state idempotently.
5. Update the business order only through valid state transitions.
6. Never move a cancelled order back to paid.
7. Record failure code and description for failed payments.
8. Return a successful response for already-processed duplicate events.
9. Avoid doing slow external work inside the webhook request.
10. Log the request ID, event ID, event type, local order ID, and provider IDs without logging secrets.

If the current system has an outbox/event mechanism, publish a local payment event after the database transaction commits.

## Refund support

Implement a provider-level refund method and an endpoint consistent with the existing API style, for example:

```http
POST /api/v1/orders/{order_id}/refund
```

Refund rules:

- Refund only captured payments.
- Do not refund an unpaid or failed payment.
- Make refund requests idempotent.
- Store the provider refund ID.
- Update local status only after a successful provider response or verified webhook.
- Restore inventory exactly once according to the existing cancellation rules.
- Do not refund more than the captured amount.
- Keep refund processing separate from order cancellation state logic.

If full refund implementation is too large for the current increment, create the provider interface and database fields, then clearly document the remaining work.

## Error handling and security

Use the existing `ProblemDetail` or standard API error format.

Return appropriate status codes for:

- Order not found
- Unauthorized order access
- Invalid order state
- Missing Razorpay configuration
- Invalid signature
- Amount mismatch
- Currency mismatch
- Duplicate payment
- Payment already captured
- Payment provider timeout
- Payment provider failure
- Invalid webhook signature

Add structured logs with:

```text
request_id
user_id
business_order_id
local_payment_id
provider_order_id
provider_payment_id
webhook_event_id
payment_status
```

Never log:

```text
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
card details
CVV
UPI PIN
full sensitive payment payloads
```

Add timeout handling for Razorpay API calls. Do not retry non-idempotent operations blindly. Use safe retry behavior and preserve local idempotency.

## Automated tests

Add unit and integration tests using mocked Razorpay API calls. Tests must not require real Razorpay credentials.

Cover at least:

1. Payment initiation creates a provider order.
2. Amount is calculated from the local order, not the frontend request.
3. Razorpay amount is converted correctly to paise.
4. Missing Razorpay credentials produce a clear configuration error.
5. Successful signature verification.
6. Invalid signature rejection.
7. Provider order ID mismatch rejection.
8. Payment amount mismatch rejection.
9. Payment currency mismatch rejection.
10. Duplicate verification is idempotent.
11. Payment after cancellation is rejected.
12. Payment for an already-paid order is rejected or returns the existing success result.
13. Duplicate webhook delivery is processed only once.
14. Invalid webhook signature is rejected.
15. `payment.captured` updates the local payment and order correctly.
16. `payment.failed` preserves a retryable pending/failed state correctly.
17. Two concurrent payment confirmations cannot create two successful payments.
18. Refund cannot exceed the captured amount.
19. SimulatedPaymentProvider tests continue to pass.
20. Existing checkout, inventory, and cancellation tests continue to pass.

Use database transactions and PostgreSQL-compatible behavior for concurrency tests.

## Documentation

Update:

- `.env.example`
- Backend README
- Frontend README if present
- API documentation
- Payment architecture documentation
- Local Razorpay Test Mode setup instructions
- Webhook setup instructions
- Test payment instructions
- Troubleshooting instructions
- Security notes

Document that Test Mode does not deduct real money and that live credentials must never be used during local development.

Include the manual test flow:

```text
1. Create Razorpay Test Mode credentials.
2. Configure backend environment variables.
3. Start the backend and frontend.
4. Create a product and inventory.
5. Add the product to the cart.
6. Create an order.
7. Start payment.
8. Complete payment using Razorpay test credentials.
9. Verify the callback.
10. Confirm the webhook.
11. Check the local payment, order, and inventory records.
12. Repeat the callback and webhook to verify idempotency.
13. Test payment failure and order cancellation.
```

## Implementation constraints

- Follow the existing project structure and naming conventions.
- Do not introduce microservices yet.
- Keep the modular monolith architecture.
- Keep the simulated payment provider for automated tests.
- Use Alembic for all schema changes.
- Do not use `create_all()` for production schema creation.
- Do not commit `.env` files or secrets.
- Do not weaken authentication or authorization.
- Do not trust frontend payment amounts or order IDs.
- Do not mark an order paid solely from frontend JavaScript.
- Run formatting, linting, migrations, and the complete test suite after implementation.
- Provide a concise summary of changed files, migration commands, environment variables, test results, and any remaining limitations.