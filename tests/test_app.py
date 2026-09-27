from fastapi.testclient import TestClient

from app.main import app


def test_home_page():

    with TestClient(app) as client:

        response = client.get("/")

        assert response.status_code == 200

        assert "FitBuddy" in response.text


def test_health():

    with TestClient(app) as client:

        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "healthy"


def test_invalid_user():

    with TestClient(app) as client:

        response = client.get(
            "/api/users/unknown-user"
        )

        assert response.status_code == 404