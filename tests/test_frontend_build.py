"""
tests/test_frontend_build.py
Automated tests for frontend build artifacts, UI contract, input validation logic,
and prediction response view elements.
"""

import os
import re
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
INDEX_HTML = os.path.join(DIST_DIR, "index.html")
SRC_DIR = os.path.join(FRONTEND_DIR, "src")


def test_frontend_build_artifacts_exist():
    assert os.path.exists(DIST_DIR), "Frontend dist/ directory must exist after npm run build"
    assert os.path.exists(INDEX_HTML), "Frontend dist/index.html must exist"

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    assert "RailAssist AI" in html, "HTML title must include RailAssist AI"
    assert "viewport" in html, "HTML must include responsive viewport meta"
    assert "assets/index" in html, "HTML must link to bundled JS/CSS assets"


def test_classify_page_contract():
    classify_jsx = os.path.join(SRC_DIR, "pages", "ClassifyPage.jsx")
    assert os.path.exists(classify_jsx), "ClassifyPage.jsx must exist"

    with open(classify_jsx, "r", encoding="utf-8") as f:
        code = f.read()

    # Empty and length validation logic
    assert "1500" in code, "Max character count of 1500 must be enforced"
    assert "isTooShort" in code or "charCount < 5" in code or "isValid" in code, "Minimum character validation must be present"
    assert "clear-complaint-btn" in code or "handleClear" in code, "Clear button functionality must exist"
    assert "disabled={!isValid" in code or "disabled={loading" in code, "Submit button must be disabled when input is invalid"

    # Prediction result fields
    assert "result.predicted_category" in code, "Result card must display predicted_category"
    assert "result.department" in code, "Result card must display department"
    assert "result.confidence_percentage" in code, "Result card must display confidence_percentage"
    assert "confidence_explanation" in code, "Result card must display confidence_explanation"

    # Loading and error handling
    assert "loading" in code, "Loading state must be handled"
    assert "error" in code, "Error state must be handled"

    # Crucial restriction: No manual category dropdown
    assert "<select" not in code, "ClassifyPage must NOT include a manual category selection dropdown"


def test_home_page_contract():
    home_jsx = os.path.join(SRC_DIR, "pages", "HomePage.jsx")
    assert os.path.exists(home_jsx), "HomePage.jsx must exist"

    with open(home_jsx, "r", encoding="utf-8") as f:
        code = f.read()

    assert "AI-Powered Railway Complaint Classification" in code, "Hero title must be present"
    assert "Academic" in code, "Academic prototype disclaimer must be present"
    assert "01" in code and "02" in code and "03" in code, "3-step process must be displayed"


def test_about_page_contract():
    about_jsx = os.path.join(SRC_DIR, "pages", "AboutPage.jsx")
    assert os.path.exists(about_jsx), "AboutPage.jsx must exist"

    with open(about_jsx, "r", encoding="utf-8") as f:
        code = f.read()

    # Provenance and real evaluation metrics
    assert "faizmubeen/indian_railways_complaint_tweets" in code, "Hugging Face dataset source must be cited"
    assert "MIT" in code, "MIT license must be cited"
    assert "75.38%" in code, "Actual Random Forest accuracy must be reported"
    assert "80.51%" in code, "Actual Logistic Regression baseline accuracy must be reported"
