"""
backend/app/classifier.py
Inference engine and deterministic department routing for RailAssist AI.
Decouples ML category prediction from application-level department routing.
Loads the model pipeline once on startup; handles missing/corrupt artifacts cleanly.
"""

import json
import os
from typing import Dict, Tuple
import joblib
import numpy as np
from fastapi import HTTPException

# Relative paths resolved safely
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "railassist_rf_pipeline.joblib")
MAPPING_PATH = os.path.join(APP_DIR, "category_mapping.json")

# Global singleton handles
_pipeline = None
_mapping_config = None
_departments_map: Dict[str, str] = {}


def load_category_mapping() -> Dict:
    """Load deterministic category-to-department configuration."""
    global _mapping_config, _departments_map
    if not os.path.exists(MAPPING_PATH):
        raise FileNotFoundError(f"Category mapping configuration missing at {MAPPING_PATH}")

    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        _mapping_config = json.load(f)

    _departments_map = _mapping_config.get("departments", {})
    return _mapping_config


def load_model_pipeline():
    """Load the trained scikit-learn TF-IDF + Random Forest pipeline once."""
    global _pipeline
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model artifact not found at {MODEL_PATH}. "
            "Please train the model using: python ml/train_model.py"
        )

    try:
        _pipeline = joblib.load(MODEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to load or deserialize model artifact: {e}") from e

    return _pipeline


def is_model_loaded() -> bool:
    """Check if model is currently loaded in memory."""
    return _pipeline is not None


def get_category_config() -> Dict:
    """Return the loaded category mapping configuration."""
    global _mapping_config
    if _mapping_config is None:
        load_category_mapping()
    return _mapping_config


def map_category_to_department(category: str) -> str:
    """
    Deterministic mapping function: category -> department.
    Decoupled from ML model.
    """
    global _departments_map
    if not _departments_map:
        load_category_mapping()

    department = _departments_map.get(category)
    if not department:
        # Fallback to general passenger assistance if category is unknown
        return "Public Grievance Cell / General Railway Inquiries"
    return department


def classify_complaint_text(text: str) -> Tuple[str, str, float, str]:
    """
    Classify a complaint text using the fitted pipeline.

    Returns:
        (predicted_category, department, confidence_score, status)

    Raises:
        HTTPException(503): If model is missing or corrupt (never fabricates answers).
        HTTPException(400): If input text is invalid.
    """
    global _pipeline
    if _pipeline is None:
        try:
            load_model_pipeline()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Classification service unavailable: ML model could not be loaded ({str(e)})"
            )

    cleaned = " ".join(text.strip().split())
    if not cleaned or len(cleaned) < 5:
        raise HTTPException(
            status_code=400,
            detail="Complaint description is too short or empty. Please provide a detailed description."
        )

    # 1. ML Category Prediction
    try:
        predicted_classes = _pipeline.predict([cleaned])
        predicted_category = str(predicted_classes[0])

        probabilities = _pipeline.predict_proba([cleaned])[0]
        confidence_score = float(np.max(probabilities))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Inference error during text classification: {str(exc)}"
        )

    # 2. Deterministic Department Mapping (Separate from ML)
    department = map_category_to_department(predicted_category)

    # 3. Confidence Thresholding
    # 9 active classes: uniform random is ~0.11. If confidence is below 0.30, flag as uncertain.
    status = "uncertain" if confidence_score < 0.30 else "success"

    return predicted_category, department, confidence_score, status
