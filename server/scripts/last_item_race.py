"""Try two checkouts for a product with exactly one unit of stock."""

from concurrent.futures import ThreadPoolExecutor
from getpass import getpass
from threading import Barrier
from uuid import uuid4

import httpx


BASE_URL = "http://127.0.0.1:8000"
TEST_PASSWORD = "TestPassword123!"
ADDRESS = {
    "address": {
        "line1": "1 Test Road",
        "city": "Test City",
        "state": "Test State",
        "postal_code": "123456",
        "country": "IN",
    }
}


def expect(response: httpx.Response, status: int) -> dict:
    if response.status_code != status:
        raise RuntimeError(
            f"{response.request.method} {response.request.url} "
            f"returned {response.status_code}, expected {status}: "
            f"{response.text}"
        )
    return response.json()


def checkout(token: str, key: str, start: Barrier) -> tuple[int, dict]:
    # Give each customer a separate HTTP client.
    with httpx.Client(base_url=BASE_URL, timeout=20) as client:
        start.wait(timeout=10)
        response = client.post(
            "/api/v1/orders",
            json=ADDRESS,
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": key,
            },
        )
        return response.status_code, response.json()


def main() -> None:
    admin_name = input("Admin username: ")
    admin_password = getpass("Admin password: ")
    run_id = uuid4().hex[:8]

    with httpx.Client(base_url=BASE_URL, timeout=20) as client:
        admin_token = expect(
            client.post(
                "/api/v1/auth/login",
                json={"username": admin_name, "password": admin_password},
            ),
            200,
        )["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # A unique product means this run cannot accidentally use old stock.
        product = expect(
            client.post(
                "/api/v1/admin/products",
                headers=admin_headers,
                json={
                    "name": f"Last Item Experiment {run_id}",
                    "sku": f"RACE-{run_id}",
                    "price": "10.00",
                    "currency": "INR",
                },
            ),
            201,
        )
        product_id = product["id"]

        expect(
            client.post(
                "/api/v1/admin/inventory/adjustments",
                headers=admin_headers,
                json={
                    "product_id": product_id,
                    "quantity_delta": 1,
                    "reason": "Last-item concurrency experiment",
                },
            ),
            200,
        )
        expect(
            client.patch(
                f"/api/v1/admin/products/{product_id}",
                headers=admin_headers,
                json={"is_published": True},
            ),
            200,
        )

        customer_tokens = []
        for number in (1, 2):
            username = f"race_{run_id}_{number}"
            expect(
                client.post(
                    "/api/v1/auth/register",
                    json={
                        "username": username,
                        "email": f"{username}@example.test",
                        "full_name": f"Race Customer {number}",
                        "password": TEST_PASSWORD,
                    },
                ),
                201,
            )
            token = expect(
                client.post(
                    "/api/v1/auth/login",
                    json={"username": username, "password": TEST_PASSWORD},
                ),
                200,
            )["access_token"]
            customer_tokens.append(token)

            # Both carts contain the same one-unit product.
            expect(
                client.post(
                    "/api/v1/cart/items",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"product_id": product_id, "quantity": 1},
                ),
                200,
            )

        print(f"Product ID: {product_id}; initial stock: 1")
        print("Both customers have the product in their carts.")

        # Three participants wait: two workers and this main thread.
        # Releasing the barrier starts both checkout requests together.
        start = Barrier(3)
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [
                pool.submit(
                    checkout,
                    token,
                    f"race-checkout-{run_id}-{number}",
                    start,
                )
                for number, token in enumerate(customer_tokens, start=1)
            ]
            start.wait(timeout=10)
            results = [job.result(timeout=30) for job in jobs]

        stock = expect(
            client.get(f"/api/v1/products/{product_id}"), 200
        )["available_quantity"]

        order_counts = []
        for token in customer_tokens:
            page = expect(
                client.get(
                    "/api/v1/orders",
                    headers={"Authorization": f"Bearer {token}"},
                ),
                200,
            )
            order_counts.append(len(page["items"]))

    for number, (status, body) in enumerate(results, start=1):
        print(f"Customer {number}: HTTP {status}; response: {body}")

    print(f"Final stock: {stock}")
    print(f"Orders by customer: {order_counts}")

    assert sorted(status for status, _ in results) == [201, 409]
    assert stock == 0
    assert sum(order_counts) == 1
    print("PASS: One order, one rejected checkout, zero stock.")


if __name__ == "__main__":
    main()