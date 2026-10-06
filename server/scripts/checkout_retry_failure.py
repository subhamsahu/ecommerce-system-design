#!/usr/bin/env python3
"""Verify checkout and failed-payment retries against the running API.

Run with PostgreSQL-backed Compose services, from inside the API container:

    docker compose up --build -d api
    docker compose exec api python scripts/checkout_retry_failure.py

Each invocation creates one product and one customer, so it is safe to repeat
against a disposable local development database.
"""

import argparse
from getpass import getpass
from typing import Any
from uuid import uuid4

import httpx


def expect(response: httpx.Response, status: int, step: str) -> Any:
    if response.status_code != status:
        raise AssertionError(
            f"{step}: expected HTTP {status}, got {response.status_code}: "
            f"{response.text}"
        )
    return response.json()


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(base_url: str) -> None:
    admin_username = input("Admin username: ").strip()
    admin_password = getpass("Admin password: ")
    run_id = uuid4().hex[:10]
    print(f"Run ID: {run_id}")

    with httpx.Client(base_url=base_url, timeout=20) as client:
        expect(client.get("/health"), 200, "API health")
        admin_login = expect(
            client.post(
                "/api/v1/auth/login",
                json={"username": admin_username, "password": admin_password},
            ),
            200,
            "Admin login",
        )
        ensure(admin_login["user"]["role"] == "admin", "This account is not an admin")
        admin_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}

        # Set up an isolated product with exactly one unit of stock.
        product = expect(
            client.post(
                "/api/v1/admin/products",
                headers=admin_headers,
                json={
                    "name": f"Retry Experiment {run_id}",
                    "sku": f"RETRY-{run_id}",
                    "price": "10.00",
                    "currency": "INR",
                },
            ),
            201,
            "Create product",
        )
        product_id = product["id"]
        print(f"Product ID: {product_id}")
        expect(
            client.post(
                "/api/v1/admin/inventory/adjustments",
                headers=admin_headers,
                json={
                    "product_id": product_id,
                    "quantity_delta": 1,
                    "reason": "Checkout retry experiment",
                },
            ),
            200,
            "Set stock to one",
        )
        expect(
            client.patch(
                f"/api/v1/admin/products/{product_id}",
                headers=admin_headers,
                json={"is_published": True},
            ),
            200,
            "Publish product",
        )

        username = f"retry_{run_id}"
        password = f"LocalTest{run_id}!"
        expect(
            client.post(
                "/api/v1/auth/register",
                json={
                    "username": username,
                    "email": f"{username}@example.test",
                    "full_name": "Retry Experiment Customer",
                    "password": password,
                },
            ),
            201,
            "Register customer",
        )
        customer_login = expect(
            client.post(
                "/api/v1/auth/login",
                json={"username": username, "password": password},
            ),
            200,
            "Customer login",
        )
        customer_headers = {
            "Authorization": f"Bearer {customer_login['access_token']}"
        }

        def stock() -> int:
            return expect(
                client.get(f"/api/v1/products/{product_id}"),
                200,
                "Read product stock",
            )["available_quantity"]

        ensure(stock() == 1, "Starting stock was not one")
        expect(
            client.post(
                "/api/v1/cart/items",
                headers=customer_headers,
                json={"product_id": product_id, "quantity": 1},
            ),
            200,
            "Add one unit to cart",
        )

        address = {
            "address": {
                "line1": "1 Test Road",
                "city": "Test City",
                "state": "Test State",
                "postal_code": "123456",
                "country": "IN",
            }
        }
        checkout_headers = {
            **customer_headers,
            "Idempotency-Key": f"checkout-{run_id}",
        }
        first_order = expect(
            client.post("/api/v1/orders", headers=checkout_headers, json=address),
            201,
            "First checkout",
        )
        order_id = first_order["id"]
        ensure(first_order["status"] == "pending_payment", "Order was not pending payment")
        first_stock = stock()
        ensure(first_stock == 0, f"Stock after checkout was {first_stock}, expected 0")

        repeated_order = expect(
            client.post("/api/v1/orders", headers=checkout_headers, json=address),
            200,
            "Repeat identical checkout",
        )
        ensure(repeated_order["id"] == order_id, "Retry created a different order")
        ensure(stock() == 0, "Checkout retry changed stock again")

        orders = expect(
            client.get("/api/v1/orders", headers=customer_headers),
            200,
            "List customer orders",
        )
        ensure(orders["pagination"]["total_items"] == 1, "Customer has more than one order")

        payment_headers = {
            **customer_headers,
            "Idempotency-Key": f"payment-failure-{run_id}",
        }
        payment_url = f"/api/v1/payments/{order_id}/attempt"
        failed_payment = expect(
            client.post(payment_url, headers=payment_headers, json={"outcome": "failure"}),
            201,
            "Simulate failed payment",
        )
        ensure(failed_payment["status"] == "failed", "Payment was not failed")
        order = expect(
            client.get(f"/api/v1/orders/{order_id}", headers=customer_headers),
            200,
            "Read order after failure",
        )
        ensure(order["status"] == "payment_failed", "Order was not payment_failed")
        ensure(stock() == 1, "Payment failure did not restore stock to one")

        repeated_payment = expect(
            client.post(payment_url, headers=payment_headers, json={"outcome": "failure"}),
            200,
            "Repeat failed payment",
        )
        ensure(repeated_payment["id"] == failed_payment["id"], "Retry created a second payment")
        ensure(stock() == 1, "Payment retry restored stock twice")

        payments = expect(
            client.get(f"/api/v1/payments/{order_id}", headers=customer_headers),
            200,
            "List payment records",
        )
        ensure(len(payments) == 2, f"Expected initial pending + failed payment, got {len(payments)}")

        late_success = client.post(
            payment_url,
            headers={**customer_headers, "Idempotency-Key": f"late-success-{run_id}"},
            json={"outcome": "success"},
        )
        expect(late_success, 409, "Reject success after failed payment")
        ensure(stock() == 1, "Rejected payment changed stock")

    print(f"First checkout: 201, order ID {order_id}, stock 1 -> 0")
    print(f"Checkout retry: 200, same order ID {order_id}, stock 0")
    print(f"Payment failure: 201, payment ID {failed_payment['id']}, stock 0 -> 1")
    print(f"Payment retry: 200, same payment ID {failed_payment['id']}, stock 1")
    print("Later success attempt: 409; one order; two payment records")
    print("PASS: Checkout and failed-payment retries changed stock exactly once each.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    arguments = parser.parse_args()
    try:
        run(arguments.base_url)
    except (AssertionError, httpx.HTTPError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
