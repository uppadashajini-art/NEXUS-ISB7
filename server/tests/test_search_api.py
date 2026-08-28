import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

def test_search_api_valid_idea():
    response = client.post(
        "/api/search",
        json={"idea": "AI based fitness platform"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

def test_search_api_empty_input():
    response = client.post(
        "/api/search",
        json={"idea": "   "}
    )
    assert response.status_code == 400
    assert "Idea cannot be empty" in response.json()["detail"]

def test_search_api_short_input():
    response = client.post(
        "/api/search",
        json={"idea": "AI"}
    )
    assert response.status_code == 400
    assert "Idea is too short" in response.json()["detail"]

def test_search_api_missing_field():
    response = client.post(
        "/api/search",
        json={}
    )
    assert response.status_code == 422 # FastAPI validation error for missing field

def test_search_api_with_domain():
    response = client.post(
        "/api/search",
        json={
            "idea": "AI based fitness platform",
            "domain": "healthcare"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
