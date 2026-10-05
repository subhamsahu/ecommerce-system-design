"""Regression coverage for the Phase 0 transactional invariants."""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test_phase0.sqlite"
os.environ["JWT_SECRET"] = "test-secret-not-for-production"

import pytest
from sqlalchemy import event
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, select

from app import models
from app.core.database import engine
from app.main import app


@pytest.fixture(autouse=True)
def schema():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


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
        admin = db.exec(select(models.User).where(models.User.username == "admin")).one()
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
        assert db.exec(select(models.Inventory).where(models.Inventory.product_id == product_id)).one().quantity == 3


def test_product_list_batches_inventory_queries():
    client = TestClient(app)
    with Session(engine) as db:
        products = [
            models.Product(name=f"Catalog item {index}", sku=f"CATALOG-{index}", is_published=True)
            for index in range(20)
        ]
        db.add_all(products)
        db.commit()
        db.add_all([
            models.Inventory(product_id=product.id, quantity=index)
            for index, product in enumerate(products, start=1)
        ])
        db.commit()

    select_statements = []

    def record_select(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            select_statements.append(statement)

    event.listen(engine, "before_cursor_execute", record_select)
    try:
        response = client.get("/api/v1/products", params={"page": 1, "page_size": 20})
    finally:
        event.remove(engine, "before_cursor_execute", record_select)

    assert response.status_code == 200, response.text
    assert len(response.json()["items"]) == 20
    assert len(select_statements) == 3


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
        assert db.exec(select(models.Inventory).where(models.Inventory.product_id == product_id)).one().quantity == 3


def test_failed_payment_restores_stock_once_and_cannot_be_retried_as_success():
    client = TestClient(app)
    _, customer_headers, product_id, order_id = setup_order(client)
    url = f"/api/v1/payments/{order_id}/attempt"
    headers = {**customer_headers, "Idempotency-Key": "payment-failure-key"}
    first = client.post(url, headers=headers, json={"outcome": "failure"})
    assert first.status_code == 201, first.text
    assert first.json()["status"] == "failed"
    repeat = client.post(url, headers=headers, json={"outcome": "failure"})
    assert repeat.status_code == 200, repeat.text
    assert repeat.json()["id"] == first.json()["id"]
    later_success = client.post(url, headers={**customer_headers, "Idempotency-Key": "payment-new-key"}, json={"outcome": "success"})
    assert later_success.status_code == 409
    assert client.get(f"/api/v1/orders/{order_id}", headers=customer_headers).json()["status"] == "payment_failed"
    with Session(engine) as db:
        inventory = db.exec(select(models.Inventory).where(models.Inventory.product_id == product_id)).one()
        assert inventory.quantity == 3
        movements = db.exec(select(models.InventoryMovement).where(models.InventoryMovement.reference_id == str(order_id))).all()
        assert [row.quantity_delta for row in movements] == [-1, 1]


def test_timeout_holds_stock_until_admin_resolves_failure():
    client = TestClient(app)
    admin_headers, customer_headers, product_id, order_id = setup_order(client)
    url = f"/api/v1/payments/{order_id}/attempt"
    timed_out = client.post(url, headers={**customer_headers, "Idempotency-Key": "payment-timeout-key"}, json={"outcome": "timeout"})
    assert timed_out.status_code == 201, timed_out.text
    assert client.get(f"/api/v1/orders/{order_id}", headers=customer_headers).json()["status"] == "payment_review"
    assert client.post(url, headers={**customer_headers, "Idempotency-Key": "payment-new-key"}, json={"outcome": "success"}).status_code == 409
    with Session(engine) as db:
        assert db.exec(select(models.Inventory).where(models.Inventory.product_id == product_id)).one().quantity == 2

    resolve_url = f"/api/v1/payments/{order_id}/resolve-timeout"
    assert client.post(resolve_url, headers=customer_headers, json={"outcome": "failure"}).status_code == 403
    resolved = client.post(resolve_url, headers=admin_headers, json={"outcome": "failure"})
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["status"] == "failed"
    assert client.post(resolve_url, headers=admin_headers, json={"outcome": "failure"}).status_code == 409
    with Session(engine) as db:
        assert db.exec(select(models.Inventory).where(models.Inventory.product_id == product_id)).one().quantity == 3


def test_timeout_resolution_success_then_repeated_cancellation_restores_once():
    client = TestClient(app)
    admin_headers, customer_headers, product_id, order_id = setup_order(client)
    assert client.post(
        f"/api/v1/payments/{order_id}/attempt",
        headers={**customer_headers, "Idempotency-Key": "payment-timeout-key"},
        json={"outcome": "timeout"},
    ).status_code == 201
    resolved = client.post(f"/api/v1/payments/{order_id}/resolve-timeout", headers=admin_headers, json={"outcome": "success"})
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["status"] == "succeeded"
    assert client.get(f"/api/v1/orders/{order_id}", headers=customer_headers).json()["status"] == "paid"
    cancel_url = f"/api/v1/orders/{order_id}/cancellation"
    assert client.post(cancel_url, headers=customer_headers).status_code == 200
    assert client.post(cancel_url, headers=customer_headers).status_code == 200
    with Session(engine) as db:
        assert db.exec(select(models.Inventory).where(models.Inventory.product_id == product_id)).one().quantity == 3
        assert len(db.exec(select(models.Refund)).all()) == 1
