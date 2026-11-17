"""
ml/clean_data.py
Data cleaning and preparation pipeline for RailAssist AI.
Loads raw dataset, excludes non-complaints and ambiguous categories,
cleans and normalizes text, removes duplicate records, retains provenance,
and saves the cleaned dataset to data/processed/cleaned_complaints.csv.
"""

import html
import json
import os
import re
import unicodedata
import pandas as pd

RAW_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "raw", "inidian_railway_complaint_tweets.csv")
)
MAPPING_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "category_mapping.json")
)
PROCESSED_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "processed")
)
CLEANED_FILE = os.path.join(PROCESSED_DIR, "cleaned_complaints.csv")
REPORTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "reports")
)
CLEANING_SUMMARY_FILE = os.path.join(REPORTS_DIR, "data_cleaning_summary.json")


def clean_tweet_text(text: str) -> str:
    """Normalize text while preserving meaningful railway complaint content."""
    if not isinstance(text, str):
        return ""

    # Unescape HTML entities (e.g. &amp; -> &, &lt; -> <)
    text = html.unescape(text)

    # Unicode normalization (NFKC decomposes special chars like ligatures into standard equivalents)
    text = unicodedata.normalize("NFKC", text)

    # Remove URLs (http://... or https://...)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Normalize excessive whitespace and line breaks
    text = re.sub(r"\s+", " ", text).strip()

    return text


def run_data_cleaning():
    print("=" * 70)
    print("RAILASSIST AI — DATA CLEANING & PREPARATION")
    print("=" * 70)

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(f"Raw dataset missing at {RAW_FILE}")

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    raw_type_map = mapping_data["raw_type_to_category"]
    departments = mapping_data["departments"]

    # 1. Load unmodified raw data
    raw_df = pd.read_csv(RAW_FILE)
    total_raw = len(raw_df)
    print(f"[*] Total raw records loaded: {total_raw:,}")

    # 2. Exclude non-complaint records
    complaints_df = raw_df[raw_df["Label"] == "complaint"].copy()
    non_complaint_excluded = total_raw - len(complaints_df)
    print(f"[*] Filtered to complaints: {len(complaints_df):,} (Excluded non-complaints: {non_complaint_excluded:,})")

    # 3. Map Type to Target Category & Exclude unsupported / ambiguous
    complaints_df["category"] = complaints_df["Type"].map(raw_type_map)
    mapped_df = complaints_df.dropna(subset=["category"]).copy()
    ambiguous_excluded = len(complaints_df) - len(mapped_df)
    print(f"[*] Mapped to target categories: {len(mapped_df):,} (Excluded ambiguous/unsupported types: {ambiguous_excluded:,})")

    # 4. Text Cleaning and Normalization
    mapped_df["cleaned_text"] = mapped_df["Tweet"].apply(clean_tweet_text)

    # Drop any records that became empty after URL stripping / cleaning
    non_empty_mask = mapped_df["cleaned_text"].str.strip().str.len() > 5
    empty_dropped = len(mapped_df) - non_empty_mask.sum()
    valid_df = mapped_df[non_empty_mask].copy()

    # 5. Deduplication
    dup_mask = valid_df.duplicated(subset=["cleaned_text"], keep="first")
    duplicates_dropped = int(dup_mask.sum())
    cleaned_df = valid_df[~dup_mask].copy()

    # 6. Add deterministic department and metadata
    cleaned_df["department"] = cleaned_df["category"].map(departments)

    # Organize columns preserving full raw provenance
    final_df = pd.DataFrame({
        "cleaned_text": cleaned_df["cleaned_text"],
        "category": cleaned_df["category"],
        "department": cleaned_df["department"],
        "raw_tweet": cleaned_df["Tweet"],
        "raw_label": cleaned_df["Label"],
        "raw_type": cleaned_df["Type"]
    })

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    final_df.to_csv(CLEANED_FILE, index=False, encoding="utf-8")
    print(f"[+] Cleaned dataset saved to: {CLEANED_FILE}")
    print(f"[*] Final retained rows: {len(final_df):,}")

    # Class distribution
    dist = final_df["category"].value_counts().to_dict()
    print("\n--- Final Cleaned Class Distribution ---")
    for cat, count in dist.items():
        pct = (count / len(final_df)) * 100
        print(f"  {cat:24s}: {count:4d} ({pct:5.1f}%)")

    dist_native = {str(k): int(v) for k, v in dist.items()}
    summary = {
        "raw_total_records": int(total_raw),
        "non_complaint_records_excluded": int(non_complaint_excluded),
        "ambiguous_types_excluded": int(ambiguous_excluded),
        "empty_texts_dropped": int(empty_dropped),
        "duplicate_texts_dropped": int(duplicates_dropped),
        "final_retained_records": int(len(final_df)),
        "total_active_categories": int(len(dist)),
        "class_distribution": dist_native,
        "cleaned_file": CLEANED_FILE
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(CLEANING_SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[+] Cleaning summary written to: {CLEANING_SUMMARY_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    run_data_cleaning()
