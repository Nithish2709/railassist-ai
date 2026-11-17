"""
tests/test_backend_api.py
Unit and integration tests for RailAssist AI FastAPI endpoints.
Tests health, categories, prediction, validation errors, and deterministic routing.
"""

import json
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.classifier import map_category_to_department, load_category_mapping


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "RailAssist AI" in data["name"]
    assert "2.0.0" in data["version"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "Random Forest" in data["model_name"]


def test_categories_endpoint(client):
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()

    assert data["total_categories"] == 8
    assert data["active_supported_count"] == 8

    # All 8 categories are supported
    cat_names = [c["name"] for c in data["categories"]]
    expected_8 = [
        "Operations & Traffic",
        "Passenger Grievance",
        "Housekeeping",
        "Security",
        "Electrical",
        "Catering",
        "Coach Maintenance",
        "Water & Sanitation"
    ]
    for c in expected_8:
        assert c in cat_names, f"Category {c} missing from API response"

    # Check department mapping dictionary
    dept_map = data["department_mapping"]
    assert len(dept_map) == 8
    assert "Operations & Traffic" in dept_map
    assert "Housekeeping" in dept_map
    assert "Catering" in dept_map


def test_predict_endpoint_valid_complaints(client):
    payload = {"text": "The toilet in my coach S4 is extremely dirty and smelling bad."}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["complaint_text"] == payload["text"]
    assert data["predicted_category"] == "Housekeeping"
    assert "Housekeeping" in data["department"]
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert "%" in data["confidence_percentage"]
    assert len(data["confidence_explanation"]) > 20
    assert data["status"] in ("success", "uncertain")


def test_predict_endpoint_empty_input_rejection(client):
    # Empty text
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422  # Pydantic validation failure

    # Whitespace text
    response_ws = client.post("/predict", json={"text": "      "})
    assert response_ws.status_code == 422


def test_predict_endpoint_too_short_rejection(client):
    response = client.post("/predict", json={"text": "Late"})
    assert response.status_code == 422


def test_predict_endpoint_excessive_length_rejection(client):
    long_text = "The train is late. " * 150  # ~2,850 characters (> 1500 limit)
    response = client.post("/predict", json={"text": long_text})
    assert response.status_code == 422


def test_deterministic_department_mapping_for_all_supported_categories():
    cfg = load_category_mapping()
    departments = cfg["departments"]

    for cat_name, expected_dept in departments.items():
        mapped_dept = map_category_to_department(cat_name)
        assert mapped_dept == expected_dept, f"Mismatch for {cat_name}: got {mapped_dept}, expected {expected_dept}"


def test_client_supplied_category_ignored(client):
    # Ensure client cannot force/tamper the predicted category
    tampered_payload = {
        "text": "The toilet is filthy and has no water.",
        "category": "Catering",
        "predicted_category": "Catering"
    }
    response = client.post("/predict", json=tampered_payload)
    assert response.status_code == 200
    data = response.json()
    # It must predict Housekeeping based on text, NOT Catering
    assert data["predicted_category"] in ("Housekeeping", "Water & Sanitation")
    assert data["predicted_category"] != "Catering"
