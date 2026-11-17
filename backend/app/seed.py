"""
backend/app/seed.py
Database creation, schema migration, and initial realistic seed data for PostgreSQL.
Creates 8 verified departments, administrative users, department officers, and sample complaints.
"""

import os
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.orm import Session

from .auth import get_password_hash
from .database import (
    SessionLocal,
    engine,
    init_db,
)
from .models import Complaint, ComplaintStatusHistory, Department, User

# Read connection parameters from env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "railassist_db")

# 8 Strictly Supported Departments (matching category_mapping.json)
DEPARTMENTS_LIST = [
    "Operating Department (Traffic & Scheduling)",
    "Commercial Department (Public Grievance Cell)",
    "Environment & Housekeeping Management (EnHM) / OBHS",
    "Security Department (Railway Protection Force - RPF)",
    "Electrical Engineering Department (Train Lighting & AC)",
    "Catering & Vending Services (IRCTC / Commercial)",
    "Mechanical Engineering Department (Carriage & Wagon)",
    "Water Supply & Sanitation Department",
]


def ensure_database_exists():
    """Ensure the target PostgreSQL database exists."""
    print(f"[*] Verifying database '{DB_NAME}' on {DB_HOST}:{DB_PORT}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
            if not cursor.fetchone():
                cursor.execute(f'CREATE DATABASE "{DB_NAME}" WITH ENCODING \'UTF8\';')
                print(f"[+] Database '{DB_NAME}' created.")
            else:
                print(f"[+] Database '{DB_NAME}' confirmed.")
        conn.close()
    except Exception as e:
        print(f"[-] Note during database creation check: {e}")


def seed_database(db: Session):
    """Seed departments, admin user, department officers, passenger, and sample complaints."""
    # 1. Seed Departments
    dept_map = {}
    for dept_name in DEPARTMENTS_LIST:
        existing = db.query(Department).filter(Department.name == dept_name).first()
        if not existing:
            dept = Department(name=dept_name, created_at=datetime.utcnow())
            db.add(dept)
            db.flush()
            dept_map[dept_name] = dept.id
            print(f"[+] Created department: {dept_name}")
        else:
            dept_map[dept_name] = existing.id

    # 2. Seed Central Railway Admin
    admin_email = "admin@railassist.gov.in"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin = User(
            full_name="Chief Grievance Officer (Admin)",
            email=admin_email,
            phone="+91 11 2338 7227",
            password_hash=get_password_hash("AdminPassword@123"),
            role="RAILWAY_ADMIN",
            department_id=None,
            created_at=datetime.utcnow()
        )
        db.add(admin)
        db.flush()
        print(f"[+] Created central admin: {admin_email}")

    # 3. Seed Department Authority Accounts
    dept_accounts = [
        ("Catering Authority Officer", "catering.auth@railassist.gov.in", "Catering & Vending Services (IRCTC / Commercial)"),
        ("Electrical Maintenance Officer", "electrical.auth@railassist.gov.in", "Electrical Engineering Department (Train Lighting & AC)"),
        ("Railway Protection Force Officer", "security.auth@railassist.gov.in", "Security Department (Railway Protection Force - RPF)"),
        ("Housekeeping Management Officer", "housekeeping.auth@railassist.gov.in", "Environment & Housekeeping Management (EnHM) / OBHS"),
        ("Traffic Controller", "operations.auth@railassist.gov.in", "Operating Department (Traffic & Scheduling)"),
        ("Commercial Grievance Officer", "grievance.auth@railassist.gov.in", "Commercial Department (Public Grievance Cell)"),
        ("Carriage & Wagon Engineer", "carriage.auth@railassist.gov.in", "Mechanical Engineering Department (Carriage & Wagon)"),
        ("Sanitation Engineer", "sanitation.auth@railassist.gov.in", "Water Supply & Sanitation Department"),
    ]

    for full_name, email, d_name in dept_accounts:
        existing_auth = db.query(User).filter(User.email == email).first()
        if not existing_auth:
            d_id = dept_map.get(d_name)
            auth_user = User(
                full_name=full_name,
                email=email,
                phone="+91 11 2300 0000",
                password_hash=get_password_hash("DeptPassword@123"),
                role="DEPARTMENT_AUTHORITY",
                department_id=d_id,
                created_at=datetime.utcnow()
            )
            db.add(auth_user)
            db.flush()
            print(f"[+] Created department authority: {email} ({d_name})")

    # 4. Seed Standard Passenger User
    passenger_email = "passenger@example.com"
    passenger = db.query(User).filter(User.email == passenger_email).first()
    if not passenger:
        passenger = User(
            full_name="Surendar Kumar",
            email=passenger_email,
            phone="+91 98765 43210",
            password_hash=get_password_hash("Passenger@123"),
            role="USER",
            department_id=None,
            created_at=datetime.utcnow()
        )
        db.add(passenger)
        db.flush()
        print(f"[+] Created passenger user: {passenger_email}")

    # 5. Seed Initial Realistic Sample Complaints
    sample_complaints = [
        {
            "ref": "RAIL-2026-10001",
            "title": "Air conditioning unit failure in 3AC coach B2",
            "desc": "The air conditioning unit in coach B2 has stopped cooling completely since train departed Kanpur. Temperature inside is unbearable and suffocating.",
            "train": "12301",
            "pnr": "2458963214",
            "date": "2026-10-25",
            "loc": "Kanpur Central (CNB)",
            "coach": "B2 - Berth 24",
            "cat": "Electrical",
            "dept_name": "Electrical Engineering Department (Train Lighting & AC)",
            "status": "IN_PROGRESS",
            "history": [
                ("SUBMITTED", "Complaint logged by passenger through RailAssist AI portal.", passenger.id),
                ("ASSIGNED", "Automatically routed to Electrical Engineering Department via AI classification.", admin.id),
                ("IN_PROGRESS", "Onboard AC technician dispatched from Allahabad junction to inspect coach compressor unit.", admin.id)
            ]
        },
        {
            "ref": "RAIL-2026-10002",
            "title": "Uncleaned bio-toilet and overflowing garbage in coach S4",
            "desc": "The bio-toilet in coach S4 is clogged and overflowing with foul smell spreading to adjacent berths. Dustbins are overflowing with waste.",
            "train": "12626",
            "pnr": "6852417930",
            "date": "2026-10-25",
            "loc": "Bhopal Junction (BPL)",
            "coach": "S4 - Berth 48",
            "cat": "Housekeeping",
            "dept_name": "Environment & Housekeeping Management (EnHM) / OBHS",
            "status": "ASSIGNED",
            "history": [
                ("SUBMITTED", "Complaint logged by passenger through RailAssist AI portal.", passenger.id),
                ("ASSIGNED", "Automatically routed to Environment & Housekeeping Management (EnHM) via AI classification.", admin.id)
            ]
        },
        {
            "ref": "RAIL-2026-10003",
            "title": "Spoiled stale lunch served by pantry car staff",
            "desc": "Pantry car staff served spoiled dinner with stale yellow dal and foul smelling curry. Staff refused to issue a printed bill.",
            "train": "12951",
            "pnr": "8521479630",
            "date": "2026-10-24",
            "loc": "Ratlam Junction (RTM)",
            "coach": "B5 - Berth 12",
            "cat": "Catering",
            "dept_name": "Catering & Vending Services (IRCTC / Commercial)",
            "status": "RESOLVED",
            "history": [
                ("SUBMITTED", "Complaint logged by passenger through RailAssist AI portal.", passenger.id),
                ("ASSIGNED", "Automatically routed to Catering & Vending Services (IRCTC / Commercial) via AI classification.", admin.id),
                ("IN_PROGRESS", "IRCTC catering supervisor alerted at Ratlam station for inspection.", admin.id),
                ("RESOLVED", "Pantry vendor penalised with fine; fresh replacement meal and apology provided to passenger.", admin.id)
            ]
        }
    ]

    for item in sample_complaints:
        existing_c = db.query(Complaint).filter(Complaint.reference_number == item["ref"]).first()
        if not existing_c:
            d_id = dept_map.get(item["dept_name"])
            complaint = Complaint(
                reference_number=item["ref"],
                user_id=passenger.id,
                title=item["title"],
                description=item["desc"],
                train_number=item["train"],
                pnr_number=item["pnr"],
                journey_date=item["date"],
                location=item["loc"],
                coach_number=item["coach"],
                predicted_category=item["cat"],
                department_id=d_id,
                status=item["status"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(complaint)
            db.flush()

            prev_st = None
            for new_st, remarks, updated_by_id in item["history"]:
                history_entry = ComplaintStatusHistory(
                    complaint_id=complaint.id,
                    previous_status=prev_st,
                    new_status=new_st,
                    remarks=remarks,
                    updated_by=updated_by_id,
                    created_at=datetime.utcnow()
                )
                db.add(history_entry)
                prev_st = new_st

            print(f"[+] Seeded complaint: {item['ref']} ({item['title']})")

    db.commit()
    print("[+] Database seeding successfully completed.")


def run_seed():
    """Entry point to ensure DB exists, tables created, and seed applied."""
    if not os.getenv("DATABASE_URL"):
        ensure_database_exists()
    init_db()
    with SessionLocal() as db:
        seed_database(db)


if __name__ == "__main__":
    run_seed()
