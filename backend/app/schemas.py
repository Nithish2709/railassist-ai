"""
backend/app/schemas.py
Pydantic schemas for RailAssist AI request and response payloads,
including ML classification, authentication, role dashboards, and complaint management.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ==========================================
# Existing ML & System Schemas (Preserved)
# ==========================================

class PredictionRequest(BaseModel):
    """Incoming complaint classification request payload."""
    text: str = Field(
        ...,
        description="The passenger's railway complaint described in plain English.",
        examples=["The air conditioning in coach B3 is not working and it is very hot."]
    )

    @field_validator("text")
    @classmethod
    def validate_complaint_text(cls, v: str) -> str:
        trimmed = v.strip() if isinstance(v, str) else ""
        if not trimmed:
            raise ValueError("Complaint text must not be empty or whitespace only.")
        if len(trimmed) < 5:
            raise ValueError("Complaint text is too short. Please provide at least 5 characters.")
        if len(trimmed) > 1500:
            raise ValueError(f"Complaint text exceeds the maximum permitted length of 1,500 characters (provided: {len(trimmed)}).")
        return trimmed


class PredictionResponse(BaseModel):
    """Complaint prediction response payload."""
    complaint_text: str = Field(..., description="The verified input complaint text.")
    predicted_category: str = Field(..., description="The ML-predicted complaint category.")
    department: str = Field(..., description="The deterministically mapped Indian Railways department.")
    confidence_score: float = Field(..., description="Maximum ensemble tree probability score (0.0 to 1.0).")
    confidence_percentage: str = Field(..., description="Formatted confidence score as a percentage string.")
    confidence_explanation: str = Field(..., description="Plain-English explanation of how confidence is obtained.")
    status: str = Field(..., description="'success' or 'uncertain'")
    model_name: str = Field(..., description="Identifier of the model used.")
    disclaimer: str = Field(
        default="Academic prototype: ML predictions may be incorrect. Not an officially integrated Indian Railways service.",
        description="Academic disclaimer."
    )


class CategoryItem(BaseModel):
    """Detailed target category metadata."""
    id: str
    name: str
    department: str
    status: str = Field(..., description="'supported' | 'insufficient_data' | 'unsupported'")
    description: str
    limitation_note: Optional[str] = None
    raw_types_mapped: List[str] = Field(default_factory=list)


class CategoriesResponse(BaseModel):
    """Response containing all categories and department mapping."""
    total_categories: int
    active_supported_count: int
    categories: List[CategoryItem]
    department_mapping: Dict[str, str]


class HealthResponse(BaseModel):
    """Health status and model operational state."""
    status: str
    model_loaded: bool
    model_name: str
    version: str
    uptime_seconds: float


class RootResponse(BaseModel):
    """Root endpoint basic metadata."""
    name: str
    version: str
    description: str
    docs_url: str


# ==========================================
# Authentication & User Schemas
# ==========================================

class UserRegisterRequest(BaseModel):
    """Passenger registration request. Role is strictly assigned to USER."""
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match.")
        return v


class LoginRequest(BaseModel):
    """User credentials for authentication."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Public user identity details."""
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Bearer token response payload upon successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==========================================
# Complaint Management Schemas
# ==========================================

class ComplaintCreateRequest(BaseModel):
    """Passenger complaint submission request."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=5, max_length=1500)
    train_number: Optional[str] = Field(None, max_length=30)
    pnr_number: Optional[str] = Field(None, max_length=20)
    journey_date: Optional[str] = Field(None, max_length=30)
    location: Optional[str] = Field(None, max_length=120)
    coach_number: Optional[str] = Field(None, max_length=30)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        trimmed = v.strip() if isinstance(v, str) else ""
        if len(trimmed) < 5:
            raise ValueError("Complaint title must be at least 5 characters.")
        return trimmed

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        trimmed = v.strip() if isinstance(v, str) else ""
        if len(trimmed) < 5:
            raise ValueError("Complaint description must be at least 5 characters.")
        return trimmed


class ComplaintStatusHistoryItem(BaseModel):
    """Single history audit log entry for a complaint."""
    id: int
    previous_status: Optional[str] = None
    new_status: str
    remarks: str
    updated_by_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplaintListItem(BaseModel):
    """Compact summary of a complaint for listings and tables."""
    id: int
    reference_number: str
    passenger_name: str
    passenger_email: str
    title: str
    predicted_category: str
    department_id: int
    department_name: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplaintDetailResponse(BaseModel):
    """Comprehensive complaint detail record with journey metadata and status timeline."""
    id: int
    reference_number: str
    user_id: int
    passenger_name: str
    passenger_email: str
    passenger_phone: Optional[str] = None
    title: str
    description: str
    train_number: Optional[str] = None
    pnr_number: Optional[str] = None
    journey_date: Optional[str] = None
    location: Optional[str] = None
    coach_number: Optional[str] = None
    predicted_category: str
    department_id: int
    department_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    history: List[ComplaintStatusHistoryItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class StatusUpdateRequest(BaseModel):
    """Department authority status update payload."""
    new_status: str = Field(..., description="'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', or 'CLOSED'")
    remarks: str = Field(..., min_length=5, max_length=1000, description="Mandatory remarks explaining the status transition.")

    @field_validator("new_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"}
        upper_v = v.upper().strip()
        if upper_v not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Permitted values: {', '.join(sorted(valid_statuses))}.")
        return upper_v


# ==========================================
# Dashboard Statistics Schemas
# ==========================================

class PassengerDashboardResponse(BaseModel):
    """Passenger personal overview metrics and recent complaints."""
    total_complaints: int
    submitted_count: int
    in_progress_count: int
    resolved_count: int
    recent_complaints: List[ComplaintListItem]


class AdminDashboardResponse(BaseModel):
    """Central railway administrator metrics and breakdowns."""
    total_complaints: int
    submitted_count: int
    assigned_count: int
    in_progress_count: int
    resolved_count: int
    closed_count: int
    by_department: Dict[str, int]
    by_category: Dict[str, int]
    recent_activity: List[ComplaintListItem]


class DepartmentDashboardResponse(BaseModel):
    """Department authority scoped metrics."""
    department_id: int
    department_name: str
    total_assigned: int
    newly_assigned: int
    in_progress: int
    resolved: int
    closed: int
    recent_complaints: List[ComplaintListItem]
