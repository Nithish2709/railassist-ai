"""
tests/test_ml_models.py
Unit tests for RailAssist AI ML models, pipelines, inference validity, and schema output.
"""

import json
import os
import joblib
import numpy as np
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RF_MODEL_PATH = os.path.join(PROJECT_ROOT, "backend", "models", "railassist_rf_pipeline.joblib")
LR_MODEL_PATH = os.path.join(PROJECT_ROOT, "backend", "models", "railassist_lr_pipeline.joblib")
META_PATH = os.path.join(PROJECT_ROOT, "backend", "models", "model_metadata.json")
MAPPING_PATH = os.path.join(PROJECT_ROOT, "data", "category_mapping.json")


@pytest.fixture(scope="module")
def rf_pipeline():
    assert os.path.exists(RF_MODEL_PATH), "Random Forest pipeline artifact must exist"
    pipeline = joblib.load(RF_MODEL_PATH)
    return pipeline


@pytest.fixture(scope="module")
def target_categories():
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [c["name"] for c in data["target_categories"]]


def test_model_loads_and_has_expected_components(rf_pipeline):
    assert hasattr(rf_pipeline, "named_steps"), "Pipeline must contain named_steps"
    assert "tfidf" in rf_pipeline.named_steps, "Pipeline must have a 'tfidf' vectorizer step"
    assert "rf" in rf_pipeline.named_steps, "Pipeline must have a 'rf' classifier step"


def test_prediction_returns_category_from_supported_set(rf_pipeline, target_categories):
    test_complaints = [
        "The food served in 12952 Rajdhani was stale and unhygienic.",
        "AC is completely off in coach B2 and suffocating passengers.",
        "Toilets in coach S5 are overflowing with water and filthy.",
        "Train is running 5 hours late without any announcement.",
        "Someone stole my handbag while I was sleeping in coach A1."
    ]

    for text in test_complaints:
        pred = rf_pipeline.predict([text])[0]
        assert isinstance(pred, str), "Prediction must be a string"
        assert pred in target_categories, f"Predicted class '{pred}' not in target categories"


def test_predict_proba_validity(rf_pipeline):
    text = "The washroom in coach S3 has no water since morning."
    probs = rf_pipeline.predict_proba([text])[0]

    assert len(probs) == len(rf_pipeline.classes_), "Probabilities count must match classes count"
    assert np.isclose(np.sum(probs), 1.0, atol=1e-4), "Probabilities must sum to 1.0"
    assert (probs >= 0.0).all() and (probs <= 1.0).all(), "All probabilities must be within [0, 1]"


def test_representative_semantic_predictions(rf_pipeline):
    # Verify domain-specific complaints map reasonably
    food_text = "Bad quality food served for lunch, catering tea was cold and tasteless."
    pred_food = rf_pipeline.predict([food_text])[0]
    assert pred_food == "Catering", f"Expected Catering for meal complaint, got {pred_food}"

    clean_text = "The toilet is extremely dirty with bad smell and cockroaches everywhere."
    pred_clean = rf_pipeline.predict([clean_text])[0]
    assert pred_clean == "Housekeeping", f"Expected Housekeeping for dirty toilet, got {pred_clean}"

    delay_text = "Train 12301 is delayed by 6 hours and stuck at outer signal for 2 hours."
    pred_delay = rf_pipeline.predict([delay_text])[0]
    assert pred_delay == "Operations & Traffic", f"Expected Operations & Traffic for delay, got {pred_delay}"

    ac_text = "Air conditioning is not cooling in coach B4, temperature is 40 degrees, fan not working."
    pred_ac = rf_pipeline.predict([ac_text])[0]
    assert pred_ac == "Electrical", f"Expected Electrical for AC failure, got {pred_ac}"


def test_model_metadata_structure():
    assert os.path.exists(META_PATH), "Model metadata json must exist"
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["primary_algorithm"] == "RandomForestClassifier"
    assert "evaluation_results" in meta
    assert "primary_rf" in meta["evaluation_results"]
    assert "baseline_lr" in meta["evaluation_results"]
    assert meta["train_rows"] == 1559
    assert meta["test_rows"] == 390
