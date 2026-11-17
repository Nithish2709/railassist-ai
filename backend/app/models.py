"""
backend/app/models.py
SQLAlchemy database models for RailAssist AI PostgreSQL schema.
Defines Users, Departments, Complaints, and ComplaintStatusHistory.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from .database import Base


class Department(Base):
    """Indian Railways operational department."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(160), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="department")
    complaints = relationship("Complaint", back_populates="department")


class User(Base):
    """System user: Passenger (USER), Central Admin (RAILWAY_ADMIN), or DEPARTMENT_AUTHORITY."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="USER", index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="users")
    complaints = relationship("Complaint", back_populates="passenger")
    status_updates = relationship("ComplaintStatusHistory", back_populates="author")


class Complaint(Base):
    """Passenger complaint record with ML category and department routing."""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reference_number = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    train_number = Column(String(30), nullable=True)
    pnr_number = Column(String(20), nullable=True)
    journey_date = Column(String(30), nullable=True)
    location = Column(String(120), nullable=True)
    coach_number = Column(String(30), nullable=True)
    predicted_category = Column(String(100), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="SUBMITTED", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    passenger = relationship("User", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    status_history = relationship(
        "ComplaintStatusHistory",
        back_populates="complaint",
        cascade="all, delete-orphan",
        order_by="ComplaintStatusHistory.created_at.asc()"
    )


class ComplaintStatusHistory(Base):
    """Audit trail tracking each status change, remarks, and user attribution."""
    __tablename__ = "complaint_status_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    previous_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    remarks = Column(Text, nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    complaint = relationship("Complaint", back_populates="status_history")
    author = relationship("User", back_populates="status_updates")
