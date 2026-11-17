"""
ml/train_model.py
Training pipeline for RailAssist AI.
Splits cleaned data (train/test 80/20 stratified, seed 42),
fits a scikit-learn Pipeline (TF-IDF Vectorizer + RandomForestClassifier),
fits an optional LogisticRegression baseline on the identical split,
and saves the fitted pipelines and metadata.
"""

import json
import os
import sys
from datetime import datetime, timezone
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "cleaned_complaints.csv")
RAW_META_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "metadata.json")
MAPPING_PATH = os.path.join(PROJECT_ROOT, "data", "category_mapping.json")
MODELS_DIR = os.path.join(PROJECT_ROOT, "backend", "models")
RF_MODEL_PATH = os.path.join(MODELS_DIR, "railassist_rf_pipeline.joblib")
LR_MODEL_PATH = os.path.join(MODELS_DIR, "railassist_lr_pipeline.joblib")
MODEL_META_PATH = os.path.join(MODELS_DIR, "model_metadata.json")
SPLIT_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def load_dataset():
    if not os.path.exists(CLEANED_DATA_PATH):
        raise FileNotFoundError(f"Cleaned dataset not found at {CLEANED_DATA_PATH}. Run ml/clean_data.py first.")
    df = pd.read_csv(CLEANED_DATA_PATH)
    return df


def train_pipelines():
    print("=" * 70)
    print("RAILASSIST AI — MODEL TRAINING PIPELINE")
    print("=" * 70)

    df = load_dataset()
    X = df["cleaned_text"].astype(str)
    y = df["category"].astype(str)

    print(f"[*] Total dataset size: {len(df):,} records")
    print(f"[*] Number of categories: {y.nunique()}")

    # 1. Reproducible stratified split
    # Test size = 0.20, seed = 42
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(f"[*] Training samples: {len(X_train):,} ({len(X_train)/len(df)*100:.1f}%)")
    print(f"[*] Test samples:     {len(X_test):,} ({len(X_test)/len(df)*100:.1f}%)")

    # Save split indices for exact auditability and evaluation
    train_df = df.loc[X_train.index]
    test_df = df.loc[X_test.index]
    train_df.to_csv(os.path.join(SPLIT_DATA_DIR, "train_split.csv"), index=False)
    test_df.to_csv(os.path.join(SPLIT_DATA_DIR, "test_split.csv"), index=False)
    print(f"[+] Saved train_split.csv and test_split.csv to {SPLIT_DATA_DIR}")

    # 2. Pipeline Configuration
    # TF-IDF fitted strictly on training data
    tfidf_config = {
        "ngram_range": (1, 2),
        "max_features": 5000,
        "sublinear_tf": True,
        "min_df": 2,
        "stop_words": "english"
    }

    rf_config = {
        "n_estimators": 200,
        "random_state": 42,
        "class_weight": "balanced_subsample",
        "min_samples_leaf": 1,
        "max_features": "sqrt",
        "n_jobs": -1
    }

    lr_config = {
        "class_weight": "balanced",
        "max_iter": 1000,
        "random_state": 42,
        "C": 1.0
    }

    # Primary: Random Forest Pipeline
    rf_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(**tfidf_config)),
        ("rf", RandomForestClassifier(**rf_config))
    ])

    print("\n[*] Fitting Primary Model: TF-IDF + RandomForestClassifier...")
    rf_pipeline.fit(X_train, y_train)
    print("[+] Primary Random Forest pipeline fitted successfully.")

    # Baseline: Logistic Regression Pipeline
    lr_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(**tfidf_config)),
        ("lr", LogisticRegression(**lr_config))
    ])

    print("[*] Fitting Baseline Model: TF-IDF + LogisticRegression...")
    lr_pipeline.fit(X_train, y_train)
    print("[+] Baseline Logistic Regression pipeline fitted successfully.")

    # 3. Save Artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(rf_pipeline, RF_MODEL_PATH)
    print(f"[+] Saved Random Forest Pipeline: {RF_MODEL_PATH}")

    joblib.dump(lr_pipeline, LR_MODEL_PATH)
    print(f"[+] Saved Logistic Regression Pipeline: {LR_MODEL_PATH}")

    # Read raw metadata and mapping
    raw_meta = {}
    if os.path.exists(RAW_META_PATH):
        with open(RAW_META_PATH, "r", encoding="utf-8") as f:
            raw_meta = json.load(f)

    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    training_metadata = {
        "model_name": "RailAssist AI Text Classifier",
        "primary_algorithm": "RandomForestClassifier",
        "baseline_algorithm": "LogisticRegression",
        "training_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "random_seed": 42,
        "test_size": 0.20,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "total_rows": len(df),
        "raw_dataset": {
            "source_url": raw_meta.get("source_url", ""),
            "huggingface_repo_id": raw_meta.get("huggingface_repo_id", ""),
            "revision_sha": raw_meta.get("revision_sha", ""),
            "license": raw_meta.get("license", "MIT"),
            "sha256_hash": raw_meta.get("sha256_hash", "")
        },
        "category_mapping_version": mapping_data.get("version", "1.0.0"),
        "active_categories": sorted(list(y.unique())),
        "all_target_categories": [c["name"] for c in mapping_data["target_categories"]],
        "unsupported_categories": [
            c["name"] for c in mapping_data["target_categories"] if c["status"] == "unsupported"
        ],
        "insufficient_data_categories": [
            c["name"] for c in mapping_data["target_categories"] if c["status"] == "insufficient_data"
        ],
        "pipeline_configuration": {
            "tfidf": tfidf_config,
            "random_forest": rf_config,
            "logistic_regression": lr_config
        },
        "model_files": {
            "primary_rf": os.path.basename(RF_MODEL_PATH),
            "baseline_lr": os.path.basename(LR_MODEL_PATH)
        }
    }

    with open(MODEL_META_PATH, "w", encoding="utf-8") as f:
        json.dump(training_metadata, f, indent=2)
    print(f"[+] Saved Model Metadata: {MODEL_META_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    train_pipelines()
