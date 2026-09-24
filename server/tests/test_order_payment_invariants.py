"""Regression coverage for the Phase 0 transactional invariants."""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test_phase0.sqlite"
os.environ["JWT_SECRET"] = "test-secret-not-for-production"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import models
from app.core.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def register(client: TestClient, username: str, email: str) -> str:
    result = client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "full_name": username.title(),
        "password": "password123",
    })
    assert result.status_code == 201, result.text
    login = client.post("/api/v1/auth/login", json={"username": username, "password": "password123"})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def setup_order(client: TestClient):
    admin_token = register(client, "admin", "admin@example.test")
    with Session(engine) as db:
        admin = db.query(models.User).filter(models.User.username == "admin").one()
        admin.role = models.UserRole.admin
        db.commit()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    product = client.post("/api/v1/admin/products", headers=admin_headers, json={
        "name": "Widget", "sku": "WIDGET-1", "price": "10.00", "currency": "INR",
    }).json()
    assert client.post("/api/v1/admin/inventory/adjustments", headers=admin_headers, json={
        "product_id": product["id"], "quantity_delta": 3, "reason": "initial stock",
    }).status_code == 200
    assert client.patch(f"/api/v1/admin/products/{product['id']}", headers=admin_headers, json={"is_published": True}).status_code == 200
    customer_token = register(client, "customer", "customer@example.test")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    assert client.post("/api/v1/cart/items", headers=customer_headers, json={"product_id": product["id"], "quantity": 1}).status_code == 200
    order = client.post("/api/v1/orders", headers={**customer_headers, "Idempotency-Key": "checkout-key-1"}, json={
        "address": {"line1": "1 Road", "city": "City", "state": "State", "postal_code": "11111"},
    })
    assert order.status_code == 201, order.text
    return admin_headers, customer_headers, product["id"], order.json()["id"]


def test_cancelled_order_cannot_be_paid_and_stock_is_restored():
    client = TestClient(app)
    _, customer_headers, product_id, order_id = setup_order(client)
    assert client.post(f"/api/v1/orders/{order_id}/cancellation", headers=customer_headers).status_code == 200
    payment = client.post(f"/api/v1/payments/{order_id}/attempt", headers={**customer_headers, "Idempotency-Key": "payment-key-1"}, json={"outcome": "success"})
    assert payment.status_code == 409
    with Session(engine) as db:
        assert db.query(models.Inventory).filter(models.Inventory.product_id == product_id).one().quantity == 3


def test_checkout_idempotency_rejects_a_different_request_body():
    client = TestClient(app)
    _, customer_headers, _, _ = setup_order(client)
    repeat = client.post("/api/v1/orders", headers={**customer_headers, "Idempotency-Key": "checkout-key-1"}, json={
        "address": {"line1": "Different Road", "city": "City", "state": "State", "postal_code": "11111"},
    })
    assert repeat.status_code == 409


def test_one_successful_payment_and_admin_cancellation_refunds_once():
    client = TestClient(app)
    admin_headers, customer_headers, product_id, order_id = setup_order(client)
    payment = client.post(f"/api/v1/payments/{order_id}/attempt", headers={**customer_headers, "Idempotency-Key": "payment-key-1"}, json={"outcome": "success"})
    assert payment.status_code == 201, payment.text
    duplicate_charge = client.post(f"/api/v1/payments/{order_id}/attempt", headers={**customer_headers, "Idempotency-Key": "payment-key-2"}, json={"outcome": "success"})
    assert duplicate_charge.status_code == 409
    cancelled = client.post(f"/api/v1/orders/{order_id}/cancellation", headers=admin_headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    payments = client.get(f"/api/v1/payments/{order_id}", headers=admin_headers).json()
    assert any(row["status"] == "refunded" for row in payments)
    with Session(engine) as db:
        assert db.query(models.Inventory).filter(models.Inventory.product_id == product_id).one().quantity == 3
