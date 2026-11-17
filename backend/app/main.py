"""
backend/app/main.py
FastAPI application for RailAssist AI — Railway Complaint Classification and Management System.
Features:
- PostgreSQL persistent storage via SQLAlchemy.
- Role-based authentication (USER, RAILWAY_ADMIN, DEPARTMENT_AUTHORITY).
- Passenger complaint logging integrated with TF-IDF + Random Forest AI classification.
- Central administrative monitoring and department-scoped status management with audit trails.
"""

import random
import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    require_roles,
    verify_password,
)
from .classifier import (
    classify_complaint_text,
    get_category_config,
    is_model_loaded,
    load_category_mapping,
    load_model_pipeline,
)
from .database import get_db, init_db
from .models import Complaint, ComplaintStatusHistory, Department, User
from .schemas import (
    AdminDashboardResponse,
    CategoriesResponse,
    CategoryItem,
    ComplaintCreateRequest,
    ComplaintDetailResponse,
    ComplaintListItem,
    ComplaintStatusHistoryItem,
    DepartmentDashboardResponse,
    HealthResponse,
    LoginRequest,
    PassengerDashboardResponse,
    PredictionRequest,
    PredictionResponse,
    RootResponse,
    StatusUpdateRequest,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load configuration, verify database schema, and preload ML model pipeline on startup."""
    print("[*] RailAssist AI backend initializing...")
    try:
        load_category_mapping()
        print("[+] Category and department mapping loaded.")
    except Exception as e:
        print(f"[-] Warning: Failed to load category mapping: {e}")

    try:
        load_model_pipeline()
        print("[+] TF-IDF + Random Forest model pipeline preloaded into memory.")
    except Exception as e:
        print(f"[-] Warning: ML Model could not be preloaded on startup: {e}")

    try:
        init_db()
        print("[+] PostgreSQL database tables verified.")
    except Exception as e:
        print(f"[-] Warning: Database initialization warning: {e}")

    yield

    print("[*] RailAssist AI backend shutting down.")


app = FastAPI(
    title="RailAssist AI — Railway Complaint Management & Classification API",
    description=(
        "Indian Railways-inspired complaint management portal powered by "
        "TF-IDF + Random Forest AI text classification, PostgreSQL persistence, and role-based access control."
    ),
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend web application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_reference_number(db: Session) -> str:
    """Generate a unique reference number formatted as RAIL-YYYY-XXXXX."""
    year = datetime.utcnow().year
    for _ in range(20):
        suffix = random.randint(10000, 99999)
        ref = f"RAIL-{year}-{suffix}"
        if not db.query(Complaint).filter(Complaint.reference_number == ref).first():
            return ref
    timestamp_suffix = int(datetime.utcnow().timestamp() * 1000) % 100000
    return f"RAIL-{year}-{timestamp_suffix:05d}"


def build_complaint_detail(complaint: Complaint) -> ComplaintDetailResponse:
    """Helper to convert Complaint ORM model into full ComplaintDetailResponse with history."""
    history_items = []
    for h in complaint.status_history:
        author_name = h.author.full_name if h.author else "System / Automated Router"
        history_items.append(
            ComplaintStatusHistoryItem(
                id=h.id,
                previous_status=h.previous_status,
                new_status=h.new_status,
                remarks=h.remarks,
                updated_by_name=author_name,
                created_at=h.created_at
            )
        )

    return ComplaintDetailResponse(
        id=complaint.id,
        reference_number=complaint.reference_number,
        user_id=complaint.user_id,
        passenger_name=complaint.passenger.full_name if complaint.passenger else "Unknown",
        passenger_email=complaint.passenger.email if complaint.passenger else "",
        passenger_phone=complaint.passenger.phone if complaint.passenger else None,
        title=complaint.title,
        description=complaint.description,
        train_number=complaint.train_number,
        pnr_number=complaint.pnr_number,
        journey_date=complaint.journey_date,
        location=complaint.location,
        coach_number=complaint.coach_number,
        predicted_category=complaint.predicted_category,
        department_id=complaint.department_id,
        department_name=complaint.department.name if complaint.department else "Unassigned",
        status=complaint.status,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
        history=history_items
    )


def build_complaint_list_item(complaint: Complaint) -> ComplaintListItem:
    """Helper to convert Complaint ORM model into ComplaintListItem."""
    return ComplaintListItem(
        id=complaint.id,
        reference_number=complaint.reference_number,
        passenger_name=complaint.passenger.full_name if complaint.passenger else "Unknown",
        passenger_email=complaint.passenger.email if complaint.passenger else "",
        title=complaint.title,
        predicted_category=complaint.predicted_category,
        department_id=complaint.department_id,
        department_name=complaint.department.name if complaint.department else "Unassigned",
        status=complaint.status,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at
    )


# ==========================================
# General & Diagnostic Endpoints
# ==========================================

@app.get("/", response_model=RootResponse, tags=["General"])
def read_root():
    """Return API metadata and documentation link."""
    return RootResponse(
        name="RailAssist AI — Railway Complaint Classification & Portal API",
        version="2.0.0",
        description="Text-based railway complaint classification and role-based portal with PostgreSQL persistence.",
        docs_url="/docs"
    )


@app.get("/health", response_model=HealthResponse, tags=["Diagnostics"])
def health_check():
    """Return backend operational status and ML model availability."""
    loaded = is_model_loaded()
    uptime = round(time.time() - START_TIME, 2)
    return HealthResponse(
        status="healthy" if loaded else "degraded",
        model_loaded=loaded,
        model_name="TF-IDF + Random Forest Classifier (200 estimators)",
        version="2.0.0",
        uptime_seconds=uptime
    )


@app.get("/categories", response_model=CategoriesResponse, tags=["Classification"])
def get_categories():
    """Return the active 8 operational categories and deterministic department mapping."""
    cfg = get_category_config()
    items = []
    active_count = 0

    for cat in cfg.get("target_categories", []):
        if cat.get("status") in ("supported", "operational"):
            active_count += 1
        items.append(
            CategoryItem(
                id=cat["id"],
                name=cat["name"],
                department=cat["department"],
                status=cat["status"],
                description=cat["description"],
                limitation_note=cat.get("limitation_note"),
                raw_types_mapped=cat.get("raw_types_mapped", [])
            )
        )

    return CategoriesResponse(
        total_categories=len(items),
        active_supported_count=active_count,
        categories=items,
        department_mapping=cfg.get("departments", {})
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Classification"])
def predict_complaint(request: PredictionRequest):
    """
    Direct ML text classification endpoint (preserved for API reference and testing).
    Returns predicted category, department, confidence score, and status without saving to database.
    """
    category, department, confidence, status_str = classify_complaint_text(request.text)

    pct_str = f"{confidence * 100:.1f}%"
    conf_explanation = (
        f"The primary Random Forest model scored this complaint with {pct_str} ensemble tree agreement. "
        "This score represents the proportion of 200 decision trees voting for this class, "
        "serving as a relative certainty heuristic rather than a calibrated Bayesian posterior."
    )

    if status_str == "uncertain":
        conf_explanation += (
            " Note: The confidence is below the reliable threshold (30%), indicating high ambiguity "
            "or multi-topic phrasing in the complaint."
        )

    return PredictionResponse(
        complaint_text=request.text,
        predicted_category=category,
        department=department,
        confidence_score=round(confidence, 4),
        confidence_percentage=pct_str,
        confidence_explanation=conf_explanation,
        status=status_str,
        model_name="TF-IDF + RandomForestClassifier"
    )


# ==========================================
# Authentication Endpoints
# ==========================================

@app.post("/auth/register", response_model=TokenResponse, tags=["Authentication"])
def register_passenger(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new passenger account.
    Public registration strictly assigns role 'USER'. Admin or Department roles cannot be chosen.
    """
    existing_user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in instead."
        )

    new_user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower().strip(),
        phone=payload.phone.strip() if payload.phone else None,
        password_hash=get_password_hash(payload.password),
        role="USER",
        department_id=None,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role})

    user_resp = UserResponse(
        id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email,
        phone=new_user.phone,
        role=new_user.role,
        department_id=new_user.department_id,
        department_name=None,
        created_at=new_user.created_at
    )
    return TokenResponse(access_token=token, user=user_resp)


@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user (Passenger, Railway Admin, or Department Authority) with email and password.
    Returns a JWT access token and user role profile.
    """
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    dept_name = user.department.name if user.department else None

    user_resp = UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        department_id=user.department_id,
        department_name=dept_name,
        created_at=user.created_at
    )
    return TokenResponse(access_token=token, user=user_resp)


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    dept_name = current_user.department.name if current_user.department else None
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        department_id=current_user.department_id,
        department_name=dept_name,
        created_at=current_user.created_at
    )


# ==========================================
# Passenger Complaint Endpoints
# ==========================================

@app.post("/complaints", response_model=ComplaintDetailResponse, tags=["Passenger"])
def submit_complaint(
    payload: ComplaintCreateRequest,
    current_user: User = Depends(require_roles(["USER"])),
    db: Session = Depends(get_db)
):
    """
    Submit a new railway passenger complaint:
    1. Runs the complaint description through the trained TF-IDF + Random Forest model.
    2. Maps the predicted category deterministically to the corresponding Indian Railways department.
    3. Generates a unique reference number (RAIL-YYYY-XXXXX).
    4. Persists the complaint and creates the initial status history entry in PostgreSQL.
    """
    # 1. Run AI inference on description
    category, department_name, confidence, conf_status = classify_complaint_text(payload.description)

    # 2. Look up the department record in PostgreSQL
    dept = db.query(Department).filter(Department.name == department_name).first()
    if not dept:
        # Fallback to the first department if exact name match fails
        dept = db.query(Department).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Department records not configured in database. Please run seed script."
            )

    # 3. Create complaint record
    ref_num = generate_reference_number(db)
    new_complaint = Complaint(
        reference_number=ref_num,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        train_number=payload.train_number.strip() if payload.train_number else None,
        pnr_number=payload.pnr_number.strip() if payload.pnr_number else None,
        journey_date=payload.journey_date.strip() if payload.journey_date else None,
        location=payload.location.strip() if payload.location else None,
        coach_number=payload.coach_number.strip() if payload.coach_number else None,
        predicted_category=category,
        department_id=dept.id,
        status="SUBMITTED",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_complaint)
    db.flush()

    # 4. Create initial status history audit entry
    history_entry = ComplaintStatusHistory(
        complaint_id=new_complaint.id,
        previous_status=None,
        new_status="SUBMITTED",
        remarks=f"Complaint lodged by passenger. AI categorized as '{category}' and assigned to {dept.name}.",
        updated_by=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(history_entry)
    db.commit()
    db.refresh(new_complaint)

    return build_complaint_detail(new_complaint)


@app.get("/complaints/my", response_model=List[ComplaintListItem], tags=["Passenger"])
def get_my_complaints(
    current_user: User = Depends(require_roles(["USER"])),
    db: Session = Depends(get_db)
):
    """Retrieve all complaints submitted by the authenticated passenger (newest first)."""
    complaints = (
        db.query(Complaint)
        .filter(Complaint.user_id == current_user.id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
    return [build_complaint_list_item(c) for c in complaints]


@app.get("/complaints/my/{reference_number}", response_model=ComplaintDetailResponse, tags=["Passenger"])
def get_my_complaint_detail(
    reference_number: str,
    current_user: User = Depends(require_roles(["USER"])),
    db: Session = Depends(get_db)
):
    """
    Retrieve full details and status history of a complaint owned by the passenger.
    Enforces strict ownership: passengers cannot view other passengers' complaints.
    """
    complaint = (
        db.query(Complaint)
        .filter(Complaint.reference_number == reference_number.strip().upper())
        .first()
    )
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with reference '{reference_number}' was not found."
        )

    if complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to view this complaint."
        )

    return build_complaint_detail(complaint)


@app.get("/complaints/track/{reference_number}", response_model=ComplaintDetailResponse, tags=["Passenger"])
def track_complaint(
    reference_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track a complaint by reference number.
    Ensures passengers can only track their own complaints, while Admins can track any complaint.
    """
    complaint = (
        db.query(Complaint)
        .filter(Complaint.reference_number == reference_number.strip().upper())
        .first()
    )
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No complaint found matching reference number '{reference_number}'."
        )

    # Role-based visibility check
    if current_user.role == "USER" and complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You can only track complaints submitted from your account."
        )
    elif current_user.role == "DEPARTMENT_AUTHORITY" and complaint.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: This complaint is assigned to another department."
        )

    return build_complaint_detail(complaint)


@app.get("/dashboard/passenger", response_model=PassengerDashboardResponse, tags=["Passenger"])
def get_passenger_dashboard(
    current_user: User = Depends(require_roles(["USER"])),
    db: Session = Depends(get_db)
):
    """Retrieve real database metrics and recent complaints for the authenticated passenger."""
    base_query = db.query(Complaint).filter(Complaint.user_id == current_user.id)

    total = base_query.count()
    submitted = base_query.filter(Complaint.status == "SUBMITTED").count()
    in_prog = base_query.filter(Complaint.status.in_(["ASSIGNED", "IN_PROGRESS"])).count()
    resolved = base_query.filter(Complaint.status.in_(["RESOLVED", "CLOSED"])).count()

    recent = (
        base_query
        .order_by(Complaint.created_at.desc())
        .limit(5)
        .all()
    )

    return PassengerDashboardResponse(
        total_complaints=total,
        submitted_count=submitted,
        in_progress_count=in_prog,
        resolved_count=resolved,
        recent_complaints=[build_complaint_list_item(c) for c in recent]
    )


# ==========================================
# Railway Admin Endpoints
# ==========================================

@app.get("/admin/dashboard", response_model=AdminDashboardResponse, tags=["Admin"])
def get_admin_dashboard(
    current_user: User = Depends(require_roles(["RAILWAY_ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Central administrative dashboard metrics.
    Calculated strictly from real database queries.
    """
    total = db.query(Complaint).count()
    submitted = db.query(Complaint).filter(Complaint.status == "SUBMITTED").count()
    assigned = db.query(Complaint).filter(Complaint.status == "ASSIGNED").count()
    in_prog = db.query(Complaint).filter(Complaint.status == "IN_PROGRESS").count()
    resolved = db.query(Complaint).filter(Complaint.status == "RESOLVED").count()
    closed = db.query(Complaint).filter(Complaint.status == "CLOSED").count()

    # Department breakdown
    dept_rows = (
        db.query(Department.name, func.count(Complaint.id))
        .outerjoin(Complaint, Department.id == Complaint.department_id)
        .group_by(Department.name)
        .all()
    )
    by_dept = {name: count for name, count in dept_rows}

    # Category breakdown
    cat_rows = (
        db.query(Complaint.predicted_category, func.count(Complaint.id))
        .group_by(Complaint.predicted_category)
        .all()
    )
    by_cat = {cat: count for cat, count in cat_rows}

    # Recent complaints
    recent = (
        db.query(Complaint)
        .order_by(Complaint.created_at.desc())
        .limit(10)
        .all()
    )

    return AdminDashboardResponse(
        total_complaints=total,
        submitted_count=submitted,
        assigned_count=assigned,
        in_progress_count=in_prog,
        resolved_count=resolved,
        closed_count=closed,
        by_department=by_dept,
        by_category=by_cat,
        recent_activity=[build_complaint_list_item(c) for c in recent]
    )


@app.get("/admin/complaints", response_model=List[ComplaintListItem], tags=["Admin"])
def get_all_complaints_admin(
    status_filter: Optional[str] = Query(None, alias="status"),
    department_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_roles(["RAILWAY_ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Retrieve all complaints across the entire network with flexible filtering and search.
    """
    query = db.query(Complaint)

    if status_filter:
        query = query.filter(Complaint.status == status_filter.upper())
    if department_id:
        query = query.filter(Complaint.department_id == department_id)
    if category:
        query = query.filter(Complaint.predicted_category == category)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Complaint.reference_number.ilike(search_pattern)) |
            (Complaint.title.ilike(search_pattern)) |
            (Complaint.description.ilike(search_pattern)) |
            (Complaint.pnr_number.ilike(search_pattern)) |
            (Complaint.train_number.ilike(search_pattern))
        )

    complaints = (
        query
        .order_by(Complaint.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [build_complaint_list_item(c) for c in complaints]


@app.get("/admin/complaints/{reference_number}", response_model=ComplaintDetailResponse, tags=["Admin"])
def get_complaint_detail_admin(
    reference_number: str,
    current_user: User = Depends(require_roles(["RAILWAY_ADMIN"])),
    db: Session = Depends(get_db)
):
    """Central admin view for any complaint and its complete status audit history."""
    complaint = (
        db.query(Complaint)
        .filter(Complaint.reference_number == reference_number.strip().upper())
        .first()
    )
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint '{reference_number}' not found."
        )
    return build_complaint_detail(complaint)


@app.get("/admin/departments", tags=["Admin"])
def get_departments_admin(
    current_user: User = Depends(require_roles(["RAILWAY_ADMIN"])),
    db: Session = Depends(get_db)
):
    """List all departments and total complaint volume."""
    results = (
        db.query(
            Department.id,
            Department.name,
            func.count(Complaint.id).label("complaint_count")
        )
        .outerjoin(Complaint, Department.id == Complaint.department_id)
        .group_by(Department.id, Department.name)
        .all()
    )
    return [{"id": r[0], "name": r[1], "complaint_count": r[2]} for r in results]


# ==========================================
# Department Authority Endpoints
# ==========================================

@app.get("/department/dashboard", response_model=DepartmentDashboardResponse, tags=["Department"])
def get_department_dashboard(
    current_user: User = Depends(require_roles(["DEPARTMENT_AUTHORITY"])),
    db: Session = Depends(get_db)
):
    """
    Department-specific dashboard metrics.
    Strictly scoped to current_user.department_id.
    """
    if not current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your authority account is not associated with an active department."
        )

    dept = db.query(Department).filter(Department.id == current_user.department_id).first()
    dept_name = dept.name if dept else "Unknown Department"

    base_query = db.query(Complaint).filter(Complaint.department_id == current_user.department_id)

    total = base_query.count()
    newly = base_query.filter(Complaint.status.in_(["SUBMITTED", "ASSIGNED"])).count()
    in_prog = base_query.filter(Complaint.status == "IN_PROGRESS").count()
    resolved = base_query.filter(Complaint.status == "RESOLVED").count()
    closed = base_query.filter(Complaint.status == "CLOSED").count()

    recent = (
        base_query
        .order_by(Complaint.updated_at.desc())
        .limit(10)
        .all()
    )

    return DepartmentDashboardResponse(
        department_id=current_user.department_id,
        department_name=dept_name,
        total_assigned=total,
        newly_assigned=newly,
        in_progress=in_prog,
        resolved=resolved,
        closed=closed,
        recent_complaints=[build_complaint_list_item(c) for c in recent]
    )


@app.get("/department/complaints", response_model=List[ComplaintListItem], tags=["Department"])
def get_department_complaints(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_roles(["DEPARTMENT_AUTHORITY"])),
    db: Session = Depends(get_db)
):
    """
    Retrieve complaints assigned strictly to the authenticated authority's department.
    """
    if not current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not linked to a department."
        )

    query = db.query(Complaint).filter(Complaint.department_id == current_user.department_id)

    if status_filter:
        query = query.filter(Complaint.status == status_filter.upper())
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Complaint.reference_number.ilike(search_pattern)) |
            (Complaint.title.ilike(search_pattern)) |
            (Complaint.description.ilike(search_pattern))
        )

    complaints = (
        query
        .order_by(Complaint.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [build_complaint_list_item(c) for c in complaints]


@app.get("/department/complaints/{reference_number}", response_model=ComplaintDetailResponse, tags=["Department"])
def get_department_complaint_detail(
    reference_number: str,
    current_user: User = Depends(require_roles(["DEPARTMENT_AUTHORITY"])),
    db: Session = Depends(get_db)
):
    """
    View a specific complaint assigned to this department.
    Raises 403 Forbidden if the complaint belongs to another department!
    """
    complaint = (
        db.query(Complaint)
        .filter(Complaint.reference_number == reference_number.strip().upper())
        .first()
    )
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint '{reference_number}' not found."
        )

    if complaint.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: This complaint is assigned to a different department."
        )

    return build_complaint_detail(complaint)


@app.patch("/department/complaints/{reference_number}/status", response_model=ComplaintDetailResponse, tags=["Department"])
def update_complaint_status_by_department(
    reference_number: str,
    payload: StatusUpdateRequest,
    current_user: User = Depends(require_roles(["DEPARTMENT_AUTHORITY"])),
    db: Session = Depends(get_db)
):
    """
    Update complaint status (ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED) with mandatory remarks.
    Validates department ownership; preserves full history and attribution.
    """
    complaint = (
        db.query(Complaint)
        .filter(Complaint.reference_number == reference_number.strip().upper())
        .first()
    )
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint '{reference_number}' not found."
        )

    if complaint.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot update complaints assigned to another department."
        )

    previous_status = complaint.status
    complaint.status = payload.new_status
    complaint.updated_at = datetime.utcnow()

    # Append to status history audit trail
    history_entry = ComplaintStatusHistory(
        complaint_id=complaint.id,
        previous_status=previous_status,
        new_status=payload.new_status,
        remarks=payload.remarks.strip(),
        updated_by=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(history_entry)
    db.commit()
    db.refresh(complaint)

    return build_complaint_detail(complaint)
