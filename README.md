# RailAssist AI — Full-Stack Railway Grievance Classification & Management System

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1.svg)](https://www.postgresql.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/pytest-30%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Academic Project Notice:** RailAssist AI is a standalone academic research and demonstration prototype developed for automated text classification and grievance management. It demonstrates machine learning classification and deterministic routing for Indian Railways passenger complaints. It is **not** an officially integrated Indian Railways service, and emergency complaints do not dispatch real-world rescue teams.

---

## Table of Contents
1. [Executive Summary & Project Abstract](#1-executive-summary--project-abstract)
2. [Problem Statement & Objectives](#2-problem-statement--objectives)
3. [Summary of What Was Built (Project Work Report)](#3-summary-of-what-was-built-project-work-report)
4. [System Architecture](#4-system-architecture)
5. [Machine Learning Pipeline & Model Evaluation](#5-machine-learning-pipeline--model-evaluation)
6. [Deterministic Department Routing](#6-deterministic-department-routing)
7. [Database Schema & Entity Relationships (PostgreSQL)](#7-database-schema--entity-relationships-postgresql)
8. [Role-Based Access Control (RBAC)](#8-role-based-access-control-rbac)
9. [Frontend Design System & Dual-Theme Engine](#9-frontend-design-system--dual-theme-engine)
10. [Test Bench: 10 Sample Complaints for Each Department](#10-test-bench-10-sample-complaints-for-each-department)
11. [Installation & Setup Instructions](#11-installation--setup-instructions)
12. [How to Run the Application Manually](#12-how-to-run-the-application-manually)
13. [Default Demonstration Accounts](#13-default-demonstration-accounts)
14. [Automated Testing & Verification Suite](#14-automated-testing--verification-suite)
15. [Academic Viva / Presentation Q&A Highlights](#15-academic-viva--presentation-qa-highlights)

---

## 1. Executive Summary & Project Abstract

Indian Railways is one of the largest rail transportation networks in the world, serving millions of passengers daily. Managing and routing passenger grievances through conventional manual dispatching creates administrative bottlenecks, delayed response times, and human misrouting.

**RailAssist AI** addresses this challenge by implementing an intelligent, end-to-end grievance classification and complaint management portal. 
- A passenger enters an unstructured plain-English complaint description.
- A **TF-IDF Vectorizer + Random Forest Classifier (200 trees)** trained on real-world Indian Railways passenger tweets analyzes the text and predicts the complaint category.
- An independent **Deterministic Department Mapping Engine** routes the grievance to the designated Indian Railways department.
- The record is persisted in a **PostgreSQL** relational database with a unique tracking reference number (e.g., `RAIL-2026-XXXXXX`).
- A **Role-Based Portal** enables passengers to track complaint progress, department officers to update operational remarks, and central administrators to monitor grievance resolution analytics across the entire network.
- A newly redesigned modern interface supports instantaneous **Light / Dark Mode switching** with browser persistence.

---

## 2. Problem Statement & Objectives

### Problem Statement
Unstructured passenger grievances submitted via digital channels vary greatly in vocabulary, length, urgency, and colloquial phrasing. Manual triage by dispatchers is error-prone, labor-intensive, and causes critical complaints (e.g., coach cleanliness, broken electrical switches, theft, food contamination) to be delayed before reaching the correct field division.

### Project Objectives
1. **Automated NLP Classification:** Classify free-form plain-English complaints into validated operational categories using machine learning.
2. **Deterministic Department Routing:** Prevent hallucinated or non-existent departments by strictly binding predicted categories to authentic Indian Railways administrative departments.
3. **Persistent Relational Storage:** Store all complaints, passenger records, departmental assignments, and chronological status change logs in a reliable PostgreSQL database.
4. **Role-Based Access Control (RBAC):** Provide distinct operational views and permission boundaries for Passengers, Department Authorities, and Central Railway Administrators.
5. **Executive Visual Design & Dual Theme:** Deliver a responsive web application honoring Indian Railways visual identity, featuring an interactive Light/Dark theme switch.
6. **Academic Rigor:** Ensure 100% reproducible training pipelines, benchmark datasets with cryptographic SHA-256 validation, and full automated test coverage.

---

## 3. Summary of What Was Built (Project Work Report)

Below is an itemized breakdown of the engineering work completed across all layers of the project:

### A. Data Engineering & Provenance
- **Dataset Sourcing:** Downloaded the official open-source dataset [`faizmubeen/indian_railways_complaint_tweets`](https://huggingface.co/datasets/faizmubeen/indian_railways_complaint_tweets) (MIT License) with exact commit hash tracking and cryptographic SHA-256 verification.
- **Data Hygiene Pipeline:** Built automated data cleaning scripts (`ml/clean_data.py`) to eliminate non-complaint social chatter, remove exact text duplicates, and normalize text whitespace.
- **Statistically Justified Category Pruning:** 
  - Excluded `Medical Assistance` (only 11 samples, producing 0.000 test F1 due to severe sample scarcity).
  - Excluded `Engineering` (0 samples in the empirical dataset).
  - Focused the production model strictly on **8 operational categories** with robust statistical representation.
- **Data Splitting:** Created an 80/20 stratified split (`1,559` train samples, `390` test samples) with fixed random seed `42` to guarantee zero data leakage between training and testing splits.

### B. Machine Learning Architecture
- **Feature Extraction:** Implemented **TF-IDF Vectorization** with sublinear term-frequency scaling, unigram + bigram extraction (`ngram_range=(1, 2)`), `min_df=2`, and English stopword elimination.
- **Primary Classifier:** Trained a **Random Forest Classifier with 200 estimators**, Gini impurity split criteria, and balanced sub-sample class weighting.
- **Baseline Comparative Classifier:** Built and evaluated a **Logistic Regression baseline** (`C=1.0`, `max_iter=1000`, `class_weight='balanced'`) to evaluate linear vs. non-linear ensemble boundaries.
- **Serialization:** Saved trained pipelines using `joblib` along with comprehensive metadata (`model_metadata.json`, `evaluation_metrics.json`, confusion matrices).

### C. Persistent PostgreSQL Database Architecture
- Configured **PostgreSQL** (`railassist_db`) using **SQLAlchemy ORM** and **psycopg2**.
- Designed a relational schema with 4 primary tables:
  1. `users` (Passengers, Department Officers, Central Admins)
  2. `departments` (8 Indian Railways operational departments)
  3. `complaints` (Grievance descriptions, predicted categories, assigned departments, PNR, train details, status)
  4. `complaint_status_history` (Append-only audit trail logging timestamps, status changes, and officer remediation remarks)
- Developed an automated idempotent database seeding script (`backend/app/seed.py`) that initializes tables, seeds departments, creates initial demo accounts, and provisions benchmark complaints.

### D. Secure Authentication & Role-Based Authorization
- Implemented **JWT (JSON Web Token)** authentication using `HS256` signatures and 8-hour token expiration.
- Integrated **native bcrypt password hashing** with salt generation.
- Established 3 mutually exclusive operational roles:
  - `USER`: Passenger submitting complaints and tracking own grievances.
  - `DEPARTMENT_AUTHORITY`: Department officer who can view only their department's queue and submit resolution remarks.
  - `RAILWAY_ADMIN`: Central oversight officer with full visibility across all departments and complaint reassignment capabilities.

### E. Backend API Architecture (FastAPI)
- Built 15+ RESTful endpoints organized with modular routers:
  - Public authentication (`/auth/register`, `/auth/login`, `/auth/me`)
  - Plain-text ML inference (`/predict`)
  - Passenger complaint workflows (`/complaints`, `/complaints/my`, `/complaints/track/{ref}`)
  - Admin management & analytics (`/admin/dashboard`, `/admin/complaints`, `/admin/departments`)
  - Department queues & status remediation (`/department/dashboard`, `/department/complaints`, `/department/complaints/{ref}/status`)
  - System health inspection (`/health`, `/categories`)
- Enforced strict Pydantic v2 data validation for request schemas, preventing SQL injection, negative train numbers, invalid PNRs, and empty text payloads.

### F. Frontend Overhaul & Dual-Theme Engine (React + Vite)
- **Official Design Language:** Designed a UI inspired by Indian Railways and RailMadad branding:
  - National Flag tri-color ribbon (`Saffron`, `White`, `Green`) in the identity topbar.
  - Indian Railways Navy (`#0B2545`) and Crimson (`#8B0000`) color tokens.
  - Academic demonstration disclaimers and numbered workflow process cards (`01`, `02`, `03`).
- **Dual-Theme Engine (Light & Dark Mode):**
  - Built an interactive toggle button (`#theme-toggle-btn`) in the main navigation bar.
  - **Light Mode (Default):** Authoritative governmental palette with crisp slate-white backgrounds (`#F4F6F9`, `#FFFFFF`), crimson primary action buttons, and high-contrast typography.
  - **Dark Mode:** Sleek deep-navy canvas (`#070D18`, `#101D33`) with glowing electric cyan (`#38BDF8`) and amber (`#F59E0B`) accents.
  - **Persistence:** Synchronizes automatically with `localStorage` (`railassist_theme`) and applies CSS custom variables dynamically via `data-theme`.
- **Responsive Layouts:** Implemented pure Vanilla CSS with zero external heavyweight styling libraries, ensuring ultra-fast load times and seamless mobile/tablet/desktop responsiveness.

### G. Quality Assurance & Automated Testing
- Wrote **30 automated unit and integration tests** using `pytest`.
- Validated raw data hashes, label mapping integrity, model prediction contracts, API security/RBAC boundaries, and frontend build outputs.

---

## 4. System Architecture

```mermaid
flowchart TD
    subgraph Passenger_Interface [Frontend Layer: React + Vite]
        UI[Passenger / Admin / Dept UI]
        ThemeEngine[Dual-Theme Engine: Light / Dark]
        State[Auth & Session State]
    end

    subgraph Backend_Gateway [API Layer: FastAPI]
        Router[REST API Endpoints]
        AuthGuard[JWT Auth & RBAC Security Guard]
        Validator[Pydantic Request Validation]
    end

    subgraph ML_Engine [Machine Learning Subsystem]
        TFIDF[TF-IDF Vectorizer (1-2 N-Grams)]
        RF[Random Forest Classifier (200 Trees)]
        RouterEngine[Deterministic Department Router]
    end

    subgraph Storage [Persistence Layer: PostgreSQL]
        DB[(railassist_db)]
        T1[users]
        T2[departments]
        T3[complaints]
        T4[complaint_status_history]
    end

    UI <-->|HTTP / REST JSON| Router
    Router --> AuthGuard
    AuthGuard --> Validator
    Validator -->|Complaint Text| TFIDF
    TFIDF --> RF
    RF -->|Predicted Category| RouterEngine
    RouterEngine -->|Department ID| Router
    Router <-->|SQLAlchemy ORM| DB
    DB --- T1
    DB --- T2
    DB --- T3
    DB --- T4
```

---

## 5. Machine Learning Pipeline & Model Evaluation

### Data Pipeline & Cleaning Summary

| Step | Operations Performed | Output Count |
|---|---|---|
| **Raw Ingestion** | Sourced from Hugging Face (`inidian_railway_complaint_tweets.csv`) | 4,535 records |
| **Complaint Filtering** | Kept only verified complaints (`complaint_or_not == 1`) | 2,615 records |
| **Category Pruning** | Removed low-data `Medical Assistance` (11 rows) & unsupported classes | 1,958 records |
| **Deduplication** | Stripped whitespace, lowered case, removed exact text duplicates | **1,949 records** |
| **Stratified Split** | 80% Training set (`train_split.csv`) / 20% Held-out test set (`test_split.csv`) | Train: 1,559 / Test: 390 |

### Eight Supported Operational Categories

| Category | Cleaned Records | Dataset % | Assigned Indian Railways Department |
|---|---|---|---|
| **Operations & Traffic** | 785 | 40.3% | Operating Department (Traffic & Scheduling) |
| **Passenger Grievance** | 401 | 20.6% | Commercial Department (Public Grievance Cell) |
| **Housekeeping** | 328 | 16.8% | Environment & Housekeeping Management (EnHM) / OBHS |
| **Security** | 141 | 7.2% | Security Department (Railway Protection Force - RPF) |
| **Electrical** | 95 | 4.9% | Electrical Engineering Department (Train Lighting & AC) |
| **Catering** | 88 | 4.5% | Catering & Vending Services (IRCTC / Commercial) |
| **Coach Maintenance** | 66 | 3.4% | Mechanical Engineering Department (Carriage & Wagon) |
| **Water & Sanitation** | 45 | 2.3% | Water Supply & Sanitation Department |

### Held-Out Evaluation Results (390 Test Samples)

| Evaluation Metric | Random Forest (Primary) | Logistic Regression (Baseline) | Academic Analysis |
|---|---|---|---|
| **Overall Accuracy** | **75.38%** | 80.51% | High-dimensional sparse text provides strong linear separability |
| **Macro-F1 Score** | **0.5670** | 0.6827 | Logistic Regression achieves higher sensitivity on minority categories |
| **Weighted-F1 Score** | **0.7255** | 0.7957 | Both models perform reliably across frequent categories |
| **Mean Ensemble Confidence**| **60.04%** | 39.15% | Random Forest produces higher consensus across 200 decision trees |

---

## 6. Deterministic Department Routing

To eliminate AI hallucinations, the machine learning classifier **only predicts the complaint category**. The assignment to an Indian Railways administrative department is executed by a strictly deterministic, single-source-of-truth mapping table (`category_mapping.json`):

```json
{
  "Catering": "Catering & Vending Services (IRCTC / Commercial)",
  "Coach Maintenance": "Mechanical Engineering Department (Carriage & Wagon)",
  "Electrical": "Electrical Engineering Department (Train Lighting & AC)",
  "Housekeeping": "Environment & Housekeeping Management (EnHM) / OBHS",
  "Operations & Traffic": "Operating Department (Traffic & Scheduling)",
  "Passenger Grievance": "Commercial Department (Public Grievance Cell)",
  "Security": "Security Department (Railway Protection Force - RPF)",
  "Water & Sanitation": "Water Supply & Sanitation Department"
}
```

*Rule:* No user input, client parameter, or model prediction can route a complaint to a non-existent or arbitrary department.

---

## 7. Database Schema & Entity Relationships (PostgreSQL)

The application uses **PostgreSQL** (`railassist_db`) structured into 4 relational tables:

```text
+------------------+       +-------------------+
|      users       |       |    departments    |
+------------------+       +-------------------+
| id (PK)          |       | id (PK)           |
| email (Unique)   |       | code (Unique)     |
| hashed_password  |       | name              |
| full_name        |       | description       |
| role (Enum)      |       +-------------------+
| department_id(FK)+---┐             ^
+------------------+   |             |
                       |             |
+----------------------+--+          |
|        complaints       |          |
+-------------------------+          |
| id (PK)                 |          |
| reference_number (UQ)   |          |
| passenger_id (FK) ------+----------+ (users.id)
| train_number            |          |
| pnr_number              |          |
| complaint_text          |          |
| predicted_category      |          |
| department_id (FK) -----+----------+ (departments.id)
| status (Enum)           |
| created_at              |
| updated_at              |
+-------------------------+
            |
            | 1-to-Many
            v
+-------------------------------+
|  complaint_status_history     |
+-------------------------------+
| id (PK)                       |
| complaint_id (FK)             |
| old_status                    |
| new_status                    |
| changed_by_user_id (FK)       |
| remarks                       |
| created_at                    |
+-------------------------------+
```

---

## 8. Role-Based Access Control (RBAC)

The application enforces strict permission boundaries across 3 roles:

```text
+-----------------------+------------------+------------------------+------------------+
| Feature / Operation   | USER (Passenger) | DEPARTMENT_AUTHORITY   | RAILWAY_ADMIN    |
+-----------------------+------------------+------------------------+------------------+
| Public Registration   | Allowed          | Blocked (Admin only)   | Blocked          |
| Lodge Complaint       | Allowed          | Allowed                | Allowed          |
| Track by Reference    | Allowed          | Allowed                | Allowed          |
| View Personal History | Own complaints   | Own complaints         | Own complaints   |
| View Department Queue | 403 Forbidden    | Assigned Dept Only     | All Departments  |
| Update Status/Remarks | 403 Forbidden    | Assigned Dept Only     | All Departments  |
| Global Analytics      | 403 Forbidden    | 403 Forbidden          | Full Access      |
+-----------------------+------------------+------------------------+------------------+
```

---

## 9. Frontend Design System & Dual-Theme Engine

The frontend is built with modern Vanilla CSS design tokens supporting seamless **Light / Dark theme transitions**:

### Light Theme (Default)
- **Aesthetic:** Formal Indian Railways governmental portal.
- **Surfaces:** Clean off-white canvas (`#F4F6F9`) with pure white card surfaces (`#FFFFFF`).
- **Brand Accents:** Indian Railways Crimson (`#8B0000`), deep navy header (`#0B2545`), and amber highlights.
- **Typography:** High-contrast slate typography (`#0F172A`) ensuring accessibility.

### Dark Theme
- **Aesthetic:** Modern nocturnal operations monitoring console.
- **Surfaces:** Deep space navy background (`#070D18`) with layered slate-navy cards (`#101D33`, `#182845`).
- **Brand Accents:** Electric cyan (`#38BDF8`), warm amber (`#F59E0B`), and emerald resolution indicators.
- **Typography:** Luminous soft-white (`#F8FAFC`) with subtle slate dividers.

### Theme Engine Implementation
- Managed through React state: `theme = localStorage.getItem('railassist_theme') || 'light'`.
- Synchronized dynamically: `document.documentElement.setAttribute('data-theme', theme)`.
- Triggered by `#theme-toggle-btn` featuring dynamic SVG icons (`☀️ Light` / `🌙 Dark`).

---

## 10. Test Bench: 10 Sample Complaints for Each Department

Use these verified test complaints in your presentation or viva to demonstrate real-time classification across all 8 Indian Railways departments:

### 1. Catering & Vending Services (IRCTC / Commercial)
1. *"The pantry car supplied stale curd and cold rice that smelled sour and foul."*
2. *"Charged Rs 120 for a standard veg thali instead of the official IRCTC menu price of Rs 80."*
3. *"The tea served by the unauthorized vendor had insect particles floating inside."*
4. *"Pantry staff refused to issue a printed GST bill for dinner in the AC coach."*
5. *"The packaged drinking water provided was not Rail Neer and had a broken seal."*
6. *"Breakfast cutlets were completely undercooked and oily, causing stomach pain."*
7. *"Vendor on platform 3 overcharged by 20 rupees for biscuits and was aggressive."*
8. *"Evening snacks served in Shatabdi were spoiled and smelled like burnt plastic."*
9. *"No catering service was provided during the 6-hour delay despite passenger requests."*
10. *"The pantry staff argued rudely when I asked for a fresh bottle of drinking water."*

### 2. Electrical Engineering Department (Train Lighting & AC)
1. *"The air conditioner in B2 coach is not cooling and the temperature is suffocating."*
2. *"Charging socket at berth 42 is completely dead and sparking when plugged in."*
3. *"All reading lamps in coach H1 are fused and flickering violently throughout the night."*
4. *"The coach fan above berth 17 makes a loud screeching noise and stopped spinning."*
5. *"Power failure in entire sleeper coach S4, all lights and fans are switched off."*
6. *"AC vents are leaking chilled water directly onto passengers sleeping on upper berths."*
7. *"Exposed high-voltage wire hanging near the washbasin in coach B1 is dangerous."*
8. *"Emergency light near the coach exit doorway is broken and dangling."*
9. *"AC control panel is displaying error code and no attendant is adjusting temperature."*
10. *"Mobile charging ports are loose and not delivering current to any passenger device."*

### 3. Environment & Housekeeping Management (EnHM) / OBHS
1. *"The bio-toilet in coach S3 is severely choked with dirty sewage water overflowing into the aisle."*
2. *"Floor of coach B4 is covered with food waste and empty plastic bottles since morning."*
3. *"Bedrolls and blankets supplied in 3AC have bad odors and dirty grease stains."*
4. *"Cockroaches and tiny insects are crawling all over the seats and berths in coach A1."*
5. *"The washbasin mirror is filthy and stained with gutkha spits, no liquid soap available."*
6. *"Dustbins in the coach vestibule are completely full and trash is spilling on the floor."*
7. *"Mosquito menace inside the coach is unbearable and no pest fogging was done."*
8. *"No On-Board Housekeeping Staff (OBHS) visited the coach for cleaning in the last 12 hours."*
9. *"The toilet floor is slippery with filth and the stench is spreading into passenger berths."*
10. *"The curtains in First AC coach are full of dust and need urgent washing."*

### 4. Security Department (Railway Protection Force - RPF)
1. *"Someone stole my black laptop backpack from under berth 33 while I was asleep."*
2. *"A group of drunk men are harassing female passengers and using abusive language in coach S2."*
3. *"Unauthorized vendors and beggars are entering the reserved coach without any RPF check."*
4. *"A passenger is threatening everyone with violence during an argument over seat sharing."*
5. *"Suspicious unattended bag lying near the toilet door for the past three hours."*
6. *"Gold chain was snatched from an elderly lady near the coach door when the train slowed down."*
7. *"Unauthorized people without tickets have occupied all floor space in sleeper coach S7."*
8. *"A person is smoking openly inside the coach vestibule and abusing passengers who object."*
9. *"Pickpocket took my wallet containing Aadhaar card and cash at the previous station."*
10. *"Group of rowdy boys playing loud music and banging coach panels late at night."*

### 5. Operating Department (Traffic & Scheduling)
1. *"Train 12626 is delayed by over 5 hours with zero announcement or SMS update from control."*
2. *"Train has been halted on the outer signal for 45 minutes without any apparent reason."*
3. *"Platform number was changed at the last minute causing heavy rush and stampede-like situation."*
4. *"Connecting train at Vijayawada departed early without accommodating the delayed inbound passengers."*
5. *"Train diverted via another route without informing reserved passengers in advance."*
6. *"Station display boards are showing incorrect departure timings and wrong platform numbers."*
7. *"Unscheduled stoppage at an unknown station for 2 hours causing passengers to miss flights."*
8. *"Train running at very low speed since morning, arrival delayed by over four hours."*
9. *"Automated announcement system at the station is completely silent during heavy festival rush."*
10. *"Train skipped its scheduled commercial halt leaving several passengers stranded on platform."*

### 6. Commercial Department (Public Grievance Cell)
1. *"TTE demanded a cash bribe of Rs 500 to allocate vacant berths in coach B3."*
2. *"Ticket refund for cancelled train has not been credited to my bank account after 15 days."*
3. *"TTE marked me absent and allotted my confirmed berth to someone else despite my presence."*
4. *"Counter clerk was extremely rude and refused to issue an unreserved ticket before train departure."*
5. *"Excess fare penalty charged incorrectly despite holding a valid upgraded ticket."*
6. *"Senior citizen concession was wrongly removed during online ticket booking."*
7. *"Clerk at luggage booking counter demanded illegal handling charges for my parcel."*
8. *"TTE refused to verify my digital Aadhaar on DigiLocker and forced me to pay fine."*
9. *"Booking office counter closed 30 minutes before time, unable to purchase general ticket."*
10. *"Refund claim rejected without stating any valid reason on the ticketing portal."*

### 7. Mechanical Engineering Department (Carriage & Wagon)
1. *"Coach window shutter is completely jammed and will not slide down against heavy rain."*
2. *"Berth chain is broken and the middle berth is collapsing down dangerously when used."*
3. *"The coach sliding vestibule door is rattling loudly and cannot be latched shut."*
4. *"Emergency alarm pull chain is broken and hanging loose from the coach ceiling."*
5. *"Heavy mechanical metal grinding noise coming from the coach wheel bogie underneath."*
6. *"Coach entrance door lock is jammed and passengers cannot open it at the station."*
7. *"Foldable table between seats is broken with sharp metal edges sticking out."*
8. *"The ladder to climb to the upper berth is missing in coach S6."*
9. *"Window glass is cracked and shattered, cold wind entering inside the AC compartment."*
10. *"Severe coach vibration and jerking making it impossible for passengers to stand."*

### 8. Water Supply & Sanitation Department
1. *"Water tank is completely empty in coach S5, no water in washbasins or toilets."*
2. *"Water tap in the western toilet is broken and water is continuously flooding the floor."*
3. *"Washbasin pipe is disconnected underneath, spilling dirty water directly onto passenger shoes."*
4. *"Platform drinking water taps are completely dry and not working during hot afternoon."*
5. *"Water jet spray inside the toilet is missing, only empty pipe hanging."*
6. *"Train departed the source junction without refilling water in coach overhead tanks."*
7. *"No running water in any coach of the entire train for the last 6 hours."*
8. *"Water coming out of the bathroom tap is muddy, brown, and foul-smelling."*
9. *"Water pipe leaking heavily outside the coach between couplers."*
10. *"Station water cooler is defunct and warm dirty water is trickling out."*

---

## 11. Installation & Setup Instructions

### Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** Python 3.10+
- **Node.js:** Node.js 18+ (includes npm)
- **Database:** PostgreSQL 14+ running locally on port `5432`.

### Step 1: Clone Repository & Create Virtual Environment
Open **PowerShell** (or your terminal):
```powershell
cd "c:\Users\knith\Downloads\MULTI-PROJECT\project\im project\railassist-ai-text-classifier"

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### Step 4: Configure Environment Variables
Verify or edit `backend/.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=railassist_db
SECRET_KEY=railassist_jwt_secret_dev_key_2026_indian_railways
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### Step 5: Initialize PostgreSQL Database & Seeds
```powershell
python -m backend.app.seed
```
*This command automatically creates `railassist_db`, provisions all 4 relational tables, seeds the 8 operational departments, generates demonstration user accounts, and populates benchmark complaints.*

---

## 12. How to Run the Application Manually

Run the backend and frontend in **two separate terminal windows**:

### Terminal 1: Start FastAPI Backend
```powershell
cd "c:\Users\surendar\OneDrive\Documents\Projects\im project\railassist-ai-text-classifier"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --port 8000
```
- **Backend API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Terminal 2: Start React Frontend
```powershell
cd "c:\Users\surendar\OneDrive\Documents\Projects\im project\railassist-ai-text-classifier\frontend"
npm run dev
```
- **Application Portal:** [http://localhost:5173](http://localhost:5173)

---

## 13. Default Demonstration Accounts

Use these pre-seeded accounts to demonstrate role-based access during presentations:

| Role | Name | Email | Password | Department / Scope |
|---|---|---|---|---|
| **Central Admin** | Chief Grievance Officer | `admin@railassist.gov.in` | `AdminPassword@123` | Master Network Oversight (All Departments) |
| **Dept Officer** | Catering Authority | `catering.auth@railassist.gov.in` | `DeptPassword@123` | Catering & Vending Services (IRCTC) |
| **Dept Officer** | Electrical Officer | `electrical.auth@railassist.gov.in` | `DeptPassword@123` | Electrical Engineering (Lighting & AC) |
| **Dept Officer** | RPF Security Officer | `security.auth@railassist.gov.in` | `DeptPassword@123` | Security Department (RPF) |
| **Dept Officer** | Housekeeping Officer | `housekeeping.auth@railassist.gov.in` | `DeptPassword@123` | Environment & Housekeeping (EnHM / OBHS) |
| **Dept Officer** | Traffic Controller | `operations.auth@railassist.gov.in` | `DeptPassword@123` | Operating Department (Traffic & Scheduling) |
| **Dept Officer** | Commercial Officer | `grievance.auth@railassist.gov.in` | `DeptPassword@123` | Commercial Department (Public Grievance Cell) |
| **Dept Officer** | Carriage & Wagon Eng. | `carriage.auth@railassist.gov.in` | `DeptPassword@123` | Mechanical Engineering (Carriage & Wagon) |
| **Dept Officer** | Sanitation Engineer | `sanitation.auth@railassist.gov.in` | `DeptPassword@123` | Water Supply & Sanitation Department |
| **Passenger** | Surendar Kumar | `passenger@example.com` | `Passenger@123` | Passenger Portal (Own Complaints Only) |

---

## 14. Automated Testing & Verification Suite

The repository includes a comprehensive automated test suite consisting of **30 unit and integration tests**:

```powershell
.\.venv\Scripts\pytest.exe -v tests
```

### Test Coverage Breakdown
- `tests/test_data_pipeline.py` (5 tests): Validates raw dataset presence, cryptographic SHA-256 hash, label mapping integrity, absence of duplicate texts, and reproducible stratified train/test splitting.
- `tests/test_ml_models.py` (5 tests): Tests pipeline loading, model components, prediction validity across supported categories, probability distribution validity, and semantic predictions.
- `tests/test_backend_api.py` (9 tests): Validates FastAPI `/health`, `/categories`, `/predict`, input length boundaries (empty, <5 chars, >1500 chars), and deterministic department routing.
- `tests/test_auth_and_complaint_workflows.py` (7 tests): Validates public registration, duplicate email rejection, JWT authentication, passenger submission workflow, RBAC permission denial (403), and department isolation.
- `tests/test_frontend_build.py` (4 tests): Validates Vite production build artifacts and UI contracts on ClassifyPage, HomePage, and AboutPage.

---

## 15. Academic Viva / Presentation Q&A Highlights

When presenting this project for evaluation, review these key technical discussion points:

1. **Why use TF-IDF with Random Forest instead of a Deep Learning Transformer (e.g., BERT)?**  
   *Answer:* Academic evaluation and practical constraints: TF-IDF with Random Forest trains in under 15 seconds, has zero external GPU requirements, achieves 75.38% held-out test accuracy, requires low computational memory (<100MB), and responds with sub-50ms inference latency suitable for edge server deployment.

2. **Why were Medical Assistance and Engineering categories pruned?**  
   *Answer:* The raw dataset contained only 11 genuine Medical records and 0 Engineering records. Attempting to train machine learning models on extreme sample scarcity results in statistical noise and 0.000 F1 scores. Responsible data science demands pruning unsupported classes to ensure high reliability across all production categories.

3. **How is hallucination prevented in department allocation?**  
   *Answer:* The machine learning model is strictly restricted to predicting the complaint category. Department routing is handled deterministically via a hardcoded, single-source-of-truth lookup table (`category_mapping.json`), ensuring no fabricated departments can ever be assigned.

4. **How is security handled across different user roles?**  
   *Answer:* Authentication uses signed JSON Web Tokens (`HS256`). FastAPI endpoint dependencies inspect the decoded token's role and department ID. If an unauthorized passenger attempts to query departmental queues, or if an officer queries another department's complaint, FastAPI immediately returns an HTTP `403 Forbidden` response.

5. **How does the dual-theme switcher work?**  
   *Answer:* The application implements CSS custom variables for all color tokens. A single toggle switches the `data-theme` attribute on the root HTML element (`light` or `dark`), which persists in browser `localStorage` and updates all surfaces dynamically with zero page reloads.

---

## License

This project is licensed under the [MIT License](LICENSE) — developed for academic demonstration and research purposes.
