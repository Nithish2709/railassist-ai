"""
ml/find_benchmark_samples.py
Vectorized extraction of benchmark test complaints for each department.
"""

import json
import joblib
import numpy as np
import pandas as pd

df = pd.read_csv('data/processed/cleaned_complaints.csv')
rf = joblib.load('backend/models/railassist_rf_pipeline.joblib')
with open('backend/app/category_mapping.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

depts = cfg['departments']

# Batch predict on entire cleaned dataset in a single call
X_all = df['cleaned_text'].astype(str)
preds_all = rf.predict(X_all)
probs_all = rf.predict_proba(X_all)
max_probs_all = np.max(probs_all, axis=1)

df['model_pred'] = preds_all
df['model_prob'] = max_probs_all

categories = [
    "Operations & Traffic",
    "Housekeeping",
    "Passenger Grievance",
    "Catering",
    "Electrical",
    "Security",
    "Water & Sanitation",
    "Coach Maintenance",
    "Medical Assistance",
    "Engineering"
]

results = {}

for cat in categories:
    dept = depts.get(cat, "Department")
    # Exact matches where prediction equals category, sorted by confidence
    matches = df[df['model_pred'] == cat].copy()
    matches = matches.sort_values(by='model_prob', ascending=False)

    top_samples = []
    seen = set()
    for _, row in matches.iterrows():
        t = " ".join(row['cleaned_text'].split())
        # Filter for readable length and remove duplicate text starts
        key = t[:50].lower()
        if key not in seen and 40 < len(t) < 250:
            seen.add(key)
            top_samples.append({
                "confidence": f"{row['model_prob']*100:.1f}%",
                "text": t
            })
            if len(top_samples) >= 10:
                break

    results[cat] = {
        "department": dept,
        "sample_count": len(top_samples),
        "samples": top_samples
    }

with open('data/reports/curated_10_samples_per_dept.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("[+] Vectorized extraction complete. Output saved.")
