"""Locust scenarios for the ecommerce-system-design API.

Run one scenario at a time from the repository root. Authenticated scenarios
require one distinct customer/admin bearer token per concurrent Locust user.
Set PERF_AUTH_TOKENS to a comma-separated token list, or PERF_AUTH_TOKEN for a
single-user run. Do not put real or long-lived credentials in this file.

Checkout scenarios create real local orders and consume inventory. Run them
against disposable data, and provision enough stock for approximately:

    users * PERF_CHECKOUTS_PER_USER

The idempotency scenario creates one order per iteration and immediately
replays the same request/key to verify the original order is returned.
"""

from __future__ import annotations

import os
import uuid
from queue import Empty, Queue

from locust import HttpUser, StopUser, between, task


PRODUCTS_PATH = "/api/v1/products"
PROFILE_PATH = "/api/v1/users/me"
CART_ITEMS_PATH = "/api/v1/cart/items"
ORDERS_PATH = "/api/v1/orders"
MAX_PRODUCT_PAGE_SIZE = 200

CHECKOUT_BODY = {
    "address": {
        "line1": "Locust performance test address",
        "city": "Test City",
        "state": "Test State",
        "postal_code": "00000",
    }
}


def _load_tokens() -> list[str]:
    many = [token.strip() for token in os.getenv("PERF_AUTH_TOKENS", "").split(",") if token.strip()]
    single = os.getenv("PERF_AUTH_TOKEN", "").strip()
    tokens = many or ([single] if single else [])
    # A repeated token is not a distinct user and causes cart/profile overlap.
    if len(set(tokens)) != len(tokens):
        raise RuntimeError("PERF_AUTH_TOKENS must contain distinct bearer tokens")
    return tokens


_TOKEN_POOL: Queue[str] = Queue()
for _token in _load_tokens():
    _TOKEN_POOL.put(_token)


def _positive_int_env(name: str, default: int | None = None) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        if default is None:
            raise RuntimeError(f"Set {name} before running this scenario")
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a positive integer") from exc
    if value < 1:
        raise RuntimeError(f"{name} must be a positive integer")
    return value


class AuthenticatedUserMixin:
    """Lease a distinct test account token to each active user in one process."""

    token: str | None = None

    def on_start(self) -> None:
        try:
            self.token = _TOKEN_POOL.get_nowait()
        except Empty:
            # This keeps concurrent virtual users from sharing a cart/account.
            raise StopUser from None
        self.client.headers["Authorization"] = f"Bearer {self.token}"

    def on_stop(self) -> None:
        if self.token:
            self.client.headers.pop("Authorization", None)
            _TOKEN_POOL.put(self.token)
            self.token = None


class CatalogReadUser(HttpUser):
    """Measures the public product-list read path (NFR-PERF-001)."""

    wait_time = between(0.5, 1.5)

    @task
    def list_products(self) -> None:
        with self.client.get(
            PRODUCTS_PATH,
            params={"page": 1, "page_size": 20},
            name="GET /api/v1/products (page_size=20)",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
                return
            try:
                body = response.json()
            except ValueError:
                response.failure("Response body was not valid JSON")
                return
            if not isinstance(body.get("items"), list) or not isinstance(body.get("pagination"), dict):
                response.failure("Expected paginated response with items and pagination")


class ProfileWriteUser(AuthenticatedUserMixin, HttpUser):
    """Measures an authenticated profile update (NFR-PERF-002)."""

    wait_time = between(0.5, 1.5)

    def on_start(self) -> None:
        super().on_start()
        with self.client.get(PROFILE_PATH, name="GET /api/v1/users/me (setup)", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Could not load test profile: HTTP {response.status_code}")
                raise StopUser
            try:
                self.full_name = response.json()["full_name"]
            except (ValueError, KeyError, TypeError):
                response.failure("Profile response did not contain full_name")
                raise StopUser

    @task
    def update_profile(self) -> None:
        with self.client.patch(
            PROFILE_PATH,
            json={"full_name": self.full_name},
            name="PATCH /api/v1/users/me",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")


class ProductPageSizeUser(HttpUser):
    """Checks the public product-list maximum and rejection above it."""

    wait_time = between(1, 2)

    @task
    def check_maximum_page_size(self) -> None:
        with self.client.get(
            PRODUCTS_PATH,
            params={"page": 1, "page_size": MAX_PRODUCT_PAGE_SIZE},
            name="GET /api/v1/products (page_size=200)",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
                return
            try:
                items = response.json().get("items")
            except (ValueError, AttributeError):
                response.failure("Response did not contain valid JSON")
                return
            if not isinstance(items, list) or len(items) > MAX_PRODUCT_PAGE_SIZE:
                response.failure(f"Expected at most {MAX_PRODUCT_PAGE_SIZE} items")

        with self.client.get(
            PRODUCTS_PATH,
            params={"page": 1, "page_size": MAX_PRODUCT_PAGE_SIZE + 1},
            name="GET /api/v1/products (page_size=201, expected 422)",
            catch_response=True,
        ) as response:
            # This API declares page_size <= 200, so 422 is the expected result.
            if response.status_code == 422:
                response.success()
            elif response.status_code == 200:
                try:
                    count = len(response.json().get("items", []))
                except (ValueError, AttributeError):
                    response.failure("Over-limit response did not contain valid JSON")
                    return
                if count <= MAX_PRODUCT_PAGE_SIZE:
                    response.success()
                else:
                    response.failure(f"API returned {count} items; maximum is {MAX_PRODUCT_PAGE_SIZE}")
            else:
                response.failure(f"Expected 422 or a capped 200 response, got {response.status_code}")


class CheckoutUser(AuthenticatedUserMixin, HttpUser):
    """Measures checkout creation (NFR-PERF-003); consumes one unit per order."""

    wait_time = between(0.5, 1.5)

    def on_start(self) -> None:
        super().on_start()
        self.product_id = _positive_int_env("PERF_PRODUCT_ID")
        self.checkouts_completed = 0
        self.max_checkouts = _positive_int_env("PERF_CHECKOUTS_PER_USER", default=10)

    @task
    def create_order(self) -> None:
        self.checkouts_completed += 1
        with self.client.post(
            CART_ITEMS_PATH,
            json={"product_id": self.product_id, "quantity": 1},
            name="POST /api/v1/cart/items (checkout setup)",
            catch_response=True,
        ) as cart_response:
            if cart_response.status_code != 200:
                cart_response.failure(f"Could not prepare cart: HTTP {cart_response.status_code}")
                self._stop_at_limit()
                return

        with self.client.post(
            ORDERS_PATH,
            json=CHECKOUT_BODY,
            headers={"Idempotency-Key": f"locust-{uuid.uuid4().hex}"},
            name="POST /api/v1/orders (checkout)",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Expected a newly created order (201), got {response.status_code}")
        self._stop_at_limit()

    def _stop_at_limit(self) -> None:
        if self.checkouts_completed >= self.max_checkouts:
            raise StopUser


class CheckoutIdempotencyUser(AuthenticatedUserMixin, HttpUser):
    """Creates an order, then replays the identical key/body and checks its ID."""

    wait_time = between(1, 2)

    def on_start(self) -> None:
        super().on_start()
        self.product_id = _positive_int_env("PERF_PRODUCT_ID")
        self.iterations = 0
        self.max_iterations = _positive_int_env("PERF_CHECKOUTS_PER_USER", default=10)

    @task
    def create_then_replay(self) -> None:
        self.iterations += 1
        with self.client.post(
            CART_ITEMS_PATH,
            json={"product_id": self.product_id, "quantity": 1},
            name="POST /api/v1/cart/items (idempotency setup)",
            catch_response=True,
        ) as cart_response:
            if cart_response.status_code != 200:
                cart_response.failure(f"Could not prepare cart: HTTP {cart_response.status_code}")
                self._stop_at_limit()
                return

        key = f"locust-idem-{uuid.uuid4().hex}"
        headers = {"Idempotency-Key": key}
        with self.client.post(
            ORDERS_PATH,
            json=CHECKOUT_BODY,
            headers=headers,
            name="POST /api/v1/orders (first idempotent checkout)",
            catch_response=True,
        ) as first:
            if first.status_code != 201:
                first.failure(f"Expected first request to create an order (201), got {first.status_code}")
                self._stop_at_limit()
                return
            try:
                first_order_id = first.json()["id"]
            except (ValueError, KeyError, TypeError):
                first.failure("First checkout response did not contain an order ID")
                self._stop_at_limit()
                return

        with self.client.post(
            ORDERS_PATH,
            json=CHECKOUT_BODY,
            headers=headers,
            name="POST /api/v1/orders (idempotency replay)",
            catch_response=True,
        ) as replay:
            if replay.status_code != 200:
                replay.failure(f"Expected replay to return the existing order (200), got {replay.status_code}")
                self._stop_at_limit()
                return
            try:
                replay_order_id = replay.json()["id"]
            except (ValueError, KeyError, TypeError):
                replay.failure("Replay response did not contain an order ID")
                self._stop_at_limit()
                return
            if replay_order_id != first_order_id:
                replay.failure("Idempotency replay returned a different order ID")

        self._stop_at_limit()

    def _stop_at_limit(self) -> None:
        if self.iterations >= self.max_iterations:
            raise StopUser
