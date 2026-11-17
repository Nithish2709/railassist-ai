"""
tests/test_data_pipeline.py
Unit tests for RailAssist AI data pipeline, cleaning, mapping, and split reproducibility.
"""

import json
import os
import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "inidian_railway_complaint_tweets.csv")
CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "cleaned_complaints.csv")
MAPPING_PATH = os.path.join(PROJECT_ROOT, "data", "category_mapping.json")
TRAIN_SPLIT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "train_split.csv")
TEST_SPLIT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "test_split.csv")


def test_raw_dataset_exists_and_unmodified():
    assert os.path.exists(RAW_DATA_PATH), "Raw dataset file must exist"
    df = pd.read_csv(RAW_DATA_PATH)
    assert len(df) == 4535, "Raw dataset should contain exactly 4,535 rows"
    assert list(df.columns) == ["Tweet", "Label", "Type"], "Columns should be ['Tweet', 'Label', 'Type']"


def test_label_mapping_integrity():
    assert os.path.exists(MAPPING_PATH), "Category mapping configuration must exist"
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    # 8 target categories must be specified
    target_cats = [c["name"] for c in mapping["target_categories"]]
    expected_8 = [
        "Operations & Traffic",
        "Passenger Grievance",
        "Housekeeping",
        "Security",
        "Electrical",
        "Catering",
        "Coach Maintenance",
        "Water & Sanitation"
    ]
    assert len(target_cats) == 8, f"Expected 8 target categories, got {len(target_cats)}"
    for cat in expected_8:
        assert cat in target_cats, f"Target category {cat} missing from configuration"

    # Every target category must have a distinct non-empty department
    for cat in expected_8:
        assert cat in mapping["departments"], f"Department for {cat} must exist in departments mapping"
        assert len(mapping["departments"][cat]) > 5, f"Department string for {cat} must be meaningful"


def test_cleaned_dataset_excludes_non_complaints():
    assert os.path.exists(CLEANED_DATA_PATH), "Cleaned dataset must exist"
    cleaned = pd.read_csv(CLEANED_DATA_PATH)

    # All records in cleaned must have been complaints in raw data
    assert (cleaned["raw_label"] == "complaint").all(), "All cleaned records must originate from Label == 'complaint'"


def test_cleaned_dataset_no_empty_texts_or_duplicates():
    cleaned = pd.read_csv(CLEANED_DATA_PATH)

    # No missing or null texts
    assert cleaned["cleaned_text"].isnull().sum() == 0, "Cleaned text column must have 0 nulls"
    assert (cleaned["cleaned_text"].str.strip().str.len() >= 5).all(), "All cleaned texts must be >= 5 chars"

    # No exact duplicate texts
    duplicates = cleaned.duplicated(subset=["cleaned_text"]).sum()
    assert duplicates == 0, f"Cleaned dataset contains {duplicates} duplicate texts"


def test_reproducible_split_and_no_data_leakage():
    assert os.path.exists(TRAIN_SPLIT_PATH), "train_split.csv must exist"
    assert os.path.exists(TEST_SPLIT_PATH), "test_split.csv must exist"

    train_df = pd.read_csv(TRAIN_SPLIT_PATH)
    test_df = pd.read_csv(TEST_SPLIT_PATH)

    # Check row counts: 80% train, 20% test of 1949 records
    assert len(train_df) == 1559, f"Expected 1,559 train records, got {len(train_df)}"
    assert len(test_df) == 390, f"Expected 390 test records, got {len(test_df)}"

    # Check zero overlap between train and test texts
    train_texts = set(train_df["cleaned_text"])
    test_texts = set(test_df["cleaned_text"])
    overlap = train_texts.intersection(test_texts)
    assert len(overlap) == 0, f"Found {len(overlap)} overlapping records between train and test splits!"
