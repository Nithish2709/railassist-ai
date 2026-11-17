"""
ml/inspect_dataset.py
Dataset inspection and exploratory analysis for RailAssist AI.
Analyzes raw dataset columns, missing values, duplicates, Label & Type distributions,
and displays sample tweets for each distinct Type to support rigorous label mapping.
"""

import json
import os
import sys
import pandas as pd

RAW_FILEPATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "raw", "inidian_railway_complaint_tweets.csv")
)
REPORTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "reports")
)


def inspect_raw_dataset():
    if not os.path.exists(RAW_FILEPATH):
        print(f"[-] Error: Raw dataset not found at {RAW_FILEPATH}")
        sys.exit(1)

    df = pd.read_csv(RAW_FILEPATH)
    print("=" * 70)
    print("RAILASSIST AI — DATASET INSPECTION REPORT")
    print("=" * 70)
    print(f"Total Rows:    {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"Columns:       {list(df.columns)}")
    print(f"Data Types:\n{df.dtypes}\n")

    # 1. Missing and Empty Values
    print("-" * 50)
    print("1. MISSING AND EMPTY VALUES")
    print("-" * 50)
    null_counts = df.isnull().sum()
    print(null_counts)
    empty_tweet_count = df["Tweet"].dropna().apply(lambda s: len(str(s).strip()) == 0).sum()
    print(f"Whitespace-only Tweet count: {empty_tweet_count}")

    # 2. Duplicate Complaint Texts
    print("\n" + "-" * 50)
    print("2. EXACT DUPLICATE TWEET TEXTS")
    print("-" * 50)
    dup_all_count = df.duplicated(subset=["Tweet"], keep=False).sum()
    dup_dropped_count = df.duplicated(subset=["Tweet"], keep="first").sum()
    unique_tweets_count = df["Tweet"].nunique()
    print(f"Unique Tweet Texts: {unique_tweets_count}")
    print(f"Total Rows with Non-unique Tweets: {dup_all_count}")
    print(f"Duplicate Rows that would be dropped (keep='first'): {dup_dropped_count}")

    # 3. Label Distribution (Complaint vs Non-Complaint)
    print("\n" + "-" * 50)
    print("3. 'Label' VALUE COUNTS (Primary Intent)")
    print("-" * 50)
    print(df["Label"].value_counts(dropna=False))

    # Cross-tab of Label vs Type
    print("\n" + "-" * 50)
    print("4. 'Type' VALUE COUNTS (All Records)")
    print("-" * 50)
    type_counts = df["Type"].value_counts(dropna=False)
    print(type_counts)

    print("\n" + "-" * 50)
    print("5. 'Type' VALUE COUNTS FOR COMPLAINTS ONLY (Label == 'complaint')")
    print("-" * 50)
    complaint_df = df[df["Label"] == "complaint"]
    complaint_type_counts = complaint_df["Type"].value_counts(dropna=False)
    print(complaint_type_counts)

    print("\n" + "-" * 50)
    print("6. 'Type' VALUE COUNTS FOR NON-COMPLAINTS (Label != 'complaint')")
    print("-" * 50)
    non_complaint_df = df[df["Label"] != "complaint"]
    print(non_complaint_df["Type"].value_counts(dropna=False))

    # 7. Representative Examples for Each Unique Type
    print("\n" + "-" * 50)
    print("7. REPRESENTATIVE SAMPLES BY 'Type'")
    print("-" * 50)
    unique_types = df["Type"].dropna().unique()
    sample_data = {}
    for t in sorted(unique_types):
        subset = df[df["Type"] == t]
        labels = subset["Label"].value_counts().to_dict()
        samples = subset["Tweet"].head(3).tolist()
        sample_data[t] = {
            "total_count": len(subset),
            "label_distribution": labels,
            "samples": samples
        }
        print(f"\n>>> Type: [{t}] (Total: {len(subset)}, Labels: {labels})")
        for i, s in enumerate(samples, 1):
            clean_s = " ".join(s.split())[:180]
            print(f"  {i}. {clean_s}...")

    # Save inspection summary json for downstream reporting
    inspection_summary = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "missing_values": {k: int(v) for k, v in null_counts.items()},
        "unique_tweets": int(unique_tweets_count),
        "duplicate_rows_to_drop": int(dup_dropped_count),
        "label_counts": {str(k): int(v) for k, v in df["Label"].value_counts().items()},
        "type_counts_all": {str(k): int(v) for k, v in type_counts.items()},
        "type_counts_complaint_only": {str(k): int(v) for k, v in complaint_type_counts.items()},
        "type_samples": sample_data
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    summary_path = os.path.join(REPORTS_DIR, "dataset_inspection_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(inspection_summary, f, indent=2)
    print(f"\n[+] Inspection summary saved to {summary_path}")


if __name__ == "__main__":
    inspect_raw_dataset()
