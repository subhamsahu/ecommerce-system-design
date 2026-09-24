from fastapi.testclient import TestClient

from app.main import app


def test_liveness_preserves_a_valid_request_id() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live", headers={"X-Request-ID": "phase-1-test"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "request_id": "phase-1-test"}
    assert response.headers["X-Request-ID"] == "phase-1-test"


def test_unknown_route_uses_problem_details() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "NOT_FOUND"
    assert response.json()["request_id"].startswith("req_")


def test_readiness_checks_postgresql() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
