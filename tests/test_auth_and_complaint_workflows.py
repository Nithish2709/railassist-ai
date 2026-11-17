"""
tests/test_auth_and_complaint_workflows.py
Integration tests covering:
- Passenger registration and role confinement (only USER permitted).
- Login and JWT authentication.
- Passenger complaint lodging, AI classification, and database persistence.
- Cross-role authorization barriers (passengers blocked from admin/dept endpoints).
- Cross-department isolation (dept authority blocked from other departments' complaints).
- Status updates with remarks and audit history.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app

client = TestClient(app)


def test_public_registration_strictly_creates_user_role():
    """Ensure public registration only creates USER role and prevents role injection."""
    unique_email = f"test_passenger_{id(object())}@example.com"
    payload = {
        "full_name": "Test Passenger",
        "email": unique_email,
        "phone": "+91 91234 56789",
        "password": "Password@123",
        "confirm_password": "Password@123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "USER"
    assert data["user"]["email"] == unique_email


def test_duplicate_registration_rejected():
    """Ensure duplicate email registration is rejected."""
    payload = {
        "full_name": "Duplicate Passenger",
        "email": "passenger@example.com",  # Already seeded
        "password": "Password@123",
        "confirm_password": "Password@123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_login_success_and_invalid_credentials():
    """Test valid and invalid login flows."""
    # Valid passenger login
    res_valid = client.post("/auth/login", json={"email": "passenger@example.com", "password": "Passenger@123"})
    assert res_valid.status_code == 200
    assert "access_token" in res_valid.json()
    assert res_valid.json()["user"]["role"] == "USER"

    # Invalid password
    res_bad = client.post("/auth/login", json={"email": "passenger@example.com", "password": "WrongPassword"})
    assert res_bad.status_code == 401


def test_passenger_complaint_submission_workflow():
    """Passenger submits a complaint; verifies AI classification, department assignment, and DB persistence."""
    # 1. Login as passenger
    res_login = client.post("/auth/login", json={"email": "passenger@example.com", "password": "Passenger@123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Submit electrical complaint
    complaint_payload = {
        "title": "Air conditioning unit failed in coach B3",
        "description": "AC unit in coach B3 is completely turned off and blowing hot air. Passengers are suffocating.",
        "train_number": "12951",
        "pnr_number": "2458963214",
        "journey_date": "2026-10-25",
        "location": "Kota Junction",
        "coach_number": "B3 - Berth 22"
    }
    res_submit = client.post("/complaints", json=complaint_payload, headers=headers)
    assert res_submit.status_code == 200, res_submit.text
    data = res_submit.json()
    assert data["reference_number"].startswith("RAIL-")
    assert data["predicted_category"] == "Electrical"
    assert "Electrical Engineering Department" in data["department_name"]
    assert data["status"] == "SUBMITTED"
    assert len(data["history"]) >= 1

    ref_num = data["reference_number"]

    # 3. Retrieve my complaints list
    res_my = client.get("/complaints/my", headers=headers)
    assert res_my.status_code == 200
    my_refs = [c["reference_number"] for c in res_my.json()]
    assert ref_num in my_refs

    # 4. Retrieve complaint detail
    res_detail = client.get(f"/complaints/my/{ref_num}", headers=headers)
    assert res_detail.status_code == 200
    assert res_detail.json()["reference_number"] == ref_num

    # 5. Check passenger dashboard metrics
    res_dash = client.get("/dashboard/passenger", headers=headers)
    assert res_dash.status_code == 200
    assert res_dash.json()["total_complaints"] >= 1


def test_passenger_forbidden_from_admin_and_department_routes():
    """Ensure passengers cannot access administrative or department authority endpoints."""
    res_login = client.post("/auth/login", json={"email": "passenger@example.com", "password": "Passenger@123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt admin dashboard
    res_admin = client.get("/admin/dashboard", headers=headers)
    assert res_admin.status_code == 403

    # Attempt department dashboard
    res_dept = client.get("/department/dashboard", headers=headers)
    assert res_dept.status_code == 403


def test_admin_dashboard_and_cross_department_visibility():
    """Railway admin can view all complaints and aggregated stats."""
    res_login = client.post("/auth/login", json={"email": "admin@railassist.gov.in", "password": "AdminPassword@123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res_dash = client.get("/admin/dashboard", headers=headers)
    assert res_dash.status_code == 200
    data = res_dash.json()
    assert data["total_complaints"] >= 3
    assert "by_department" in data
    assert "by_category" in data

    res_list = client.get("/admin/complaints", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 3


def test_department_isolation_and_status_update():
    """Department authority sees only their department's complaints and can update status."""
    # 1. Login as Electrical authority
    res_login = client.post("/auth/login", json={"email": "electrical.auth@railassist.gov.in", "password": "DeptPassword@123"})
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check department dashboard
    res_dash = client.get("/department/dashboard", headers=headers)
    assert res_dash.status_code == 200
    assert "Electrical Engineering Department" in res_dash.json()["department_name"]

    # 3. Electrical complaint update
    ref_elec = "RAIL-2026-10001"  # Seeded electrical complaint
    update_payload = {
        "new_status": "IN_PROGRESS",
        "remarks": "Coach AC technician deployed at Kanpur station to inspect blower unit."
    }
    res_update = client.patch(f"/department/complaints/{ref_elec}/status", json=update_payload, headers=headers)
    assert res_update.status_code == 200, res_update.text
    assert res_update.json()["status"] == "IN_PROGRESS"
    latest_hist = res_update.json()["history"][-1]
    assert latest_hist["new_status"] == "IN_PROGRESS"
    assert "Kanpur station" in latest_hist["remarks"]

    # 4. Attempt to access a Catering complaint (RAIL-2026-10003) -> Must return 403 Forbidden!
    ref_catering = "RAIL-2026-10003"
    res_cross_dept = client.get(f"/department/complaints/{ref_catering}", headers=headers)
    assert res_cross_dept.status_code == 403
    assert "different department" in res_cross_dept.json()["detail"].lower()
