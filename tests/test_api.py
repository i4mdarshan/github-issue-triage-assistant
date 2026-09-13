import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "model": "issue_classifier",
    }


def test_prediction_endpoint(client: TestClient) -> None:
    response = client.post(
        "/api/predict",
        json={
            "title": "Application crashes when configuration is missing",
            "body": (
                "The server exits unexpectedly instead of returning "
                "a useful validation message."
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["label"] in {
        "bug",
        "feature",
        "documentation",
        "question",
    }
    assert 0 <= result["confidence"] <= 1
    assert set(result["probabilities"]) == {
        "bug",
        "feature",
        "documentation",
        "question",
    }


def test_rejects_invalid_request(client: TestClient) -> None:
    response = client.post(
        "/api/predict",
        json={
            "title": "Hi",
            "body": "",
        },
    )

    assert response.status_code == 422