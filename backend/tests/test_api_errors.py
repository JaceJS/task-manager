from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.main import app


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_body_that_is_not_json_returns_400(client):
    response = client.post(
        "/api/boards", content="not json", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Request body is not valid JSON", "data": None}


def test_empty_board_name_returns_422_in_the_same_shape(client):
    response = client.post("/api/boards", json={"name": "   "})

    assert response.status_code == 422
    body = response.json()
    assert body["data"] is None
    assert body["message"] == "Name must not be empty"


def test_unknown_board_returns_404_in_the_same_shape(client):
    response = client.get("/api/boards/999999/tasks")

    assert response.status_code == 404
    assert response.json() == {"message": "Board 999999 was not found", "data": None}
