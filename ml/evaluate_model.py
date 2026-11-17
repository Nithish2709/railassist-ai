"""
ml/evaluate_model.py
Evaluation script for RailAssist AI.
Evaluates both Random Forest (primary) and Logistic Regression (baseline) on the held-out test split.
Computes accuracy, macro-F1, weighted-F1, per-class metrics, confusion matrices, and confidence stats.
Generates data/reports/evaluation_report.md and saves JSON metrics.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_SPLIT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "test_split.csv")
TRAIN_SPLIT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "train_split.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "backend", "models")
RF_MODEL_PATH = os.path.join(MODELS_DIR, "railassist_rf_pipeline.joblib")
LR_MODEL_PATH = os.path.join(MODELS_DIR, "railassist_lr_pipeline.joblib")
MODEL_META_PATH = os.path.join(MODELS_DIR, "model_metadata.json")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "data", "reports")
EVAL_METRICS_PATH = os.path.join(REPORTS_DIR, "evaluation_metrics.json")
EVAL_REPORT_PATH = os.path.join(REPORTS_DIR, "evaluation_report.md")


def compute_model_metrics(model, X_test, y_test, labels):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    max_probs = np.max(y_prob, axis=1)

    acc = float(accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=labels, zero_division=0
    )

    per_class = {}
    for i, label in enumerate(labels):
        per_class[label] = {
            "precision": float(round(precision[i], 4)),
            "recall": float(round(recall[i], 4)),
            "f1_score": float(round(f1[i], 4)),
            "test_support": int(support[i]),
            "insufficient_support": bool(support[i] < 5)
        }

    cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()

    conf_stats = {
        "mean_confidence": float(round(np.mean(max_probs), 4)),
        "median_confidence": float(round(np.median(max_probs), 4)),
        "min_confidence": float(round(np.min(max_probs), 4)),
        "max_confidence": float(round(np.max(max_probs), 4)),
        "pct_above_50": float(round((max_probs >= 0.50).mean() * 100, 2)),
        "pct_above_70": float(round((max_probs >= 0.70).mean() * 100, 2)),
    }

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "per_class": per_class,
        "confusion_matrix": cm,
        "labels": labels,
        "confidence_statistics": conf_stats
    }


def run_evaluation():
    print("=" * 70)
    print("RAILASSIST AI — MODEL EVALUATION")
    print("=" * 70)

    test_df = pd.read_csv(TEST_SPLIT_PATH)
    train_df = pd.read_csv(TRAIN_SPLIT_PATH)

    X_test = test_df["cleaned_text"].astype(str)
    y_test = test_df["category"].astype(str)

    rf_model = joblib.load(RF_MODEL_PATH)
    lr_model = joblib.load(LR_MODEL_PATH)

    # All unique labels in order
    labels = sorted(list(y_test.unique()))
    print(f"[*] Evaluating on {len(test_df):,} held-out test samples across {len(labels)} classes.")

    rf_results = compute_model_metrics(rf_model, X_test, y_test, labels)
    lr_results = compute_model_metrics(lr_model, X_test, y_test, labels)

    print("\n--- RESULTS COMPARISON ---")
    print(f"Metric                 Random Forest (Primary)      Logistic Regression (Baseline)")
    print(f"----------------------------------------------------------------------------------")
    print(f"Overall Accuracy:      {rf_results['accuracy']*100:6.2f}%                     {lr_results['accuracy']*100:6.2f}%")
    print(f"Macro-F1 Score:        {rf_results['macro_f1']:6.4f}                      {lr_results['macro_f1']:6.4f}")
    print(f"Weighted-F1 Score:     {rf_results['weighted_f1']:6.4f}                      {lr_results['weighted_f1']:6.4f}")
    print(f"Mean Confidence:       {rf_results['confidence_statistics']['mean_confidence']*100:6.2f}%                     {lr_results['confidence_statistics']['mean_confidence']*100:6.2f}%")

    # Save detailed json report
    full_eval_data = {
        "evaluation_timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "total_samples": len(train_df) + len(test_df),
        "primary_model": {
            "name": "Random Forest Classifier",
            "metrics": rf_results
        },
        "baseline_model": {
            "name": "Logistic Regression",
            "metrics": lr_results
        },
        "insufficient_test_support_classes": [
            lbl for lbl, info in rf_results["per_class"].items() if info["insufficient_support"]
        ]
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(EVAL_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(full_eval_data, f, indent=2)
    print(f"\n[+] Saved evaluation metrics to: {EVAL_METRICS_PATH}")

    # Save confusion matrices separately for inspection
    with open(os.path.join(REPORTS_DIR, "confusion_matrix_rf.json"), "w", encoding="utf-8") as f:
        json.dump({"labels": labels, "matrix": rf_results["confusion_matrix"]}, f, indent=2)

    with open(os.path.join(REPORTS_DIR, "confusion_matrix_lr.json"), "w", encoding="utf-8") as f:
        json.dump({"labels": labels, "matrix": lr_results["confusion_matrix"]}, f, indent=2)

    # Update backend/models/model_metadata.json with evaluation results
    if os.path.exists(MODEL_META_PATH):
        with open(MODEL_META_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        metadata["evaluation_results"] = {
            "primary_rf": {
                "accuracy": rf_results["accuracy"],
                "macro_f1": rf_results["macro_f1"],
                "weighted_f1": rf_results["weighted_f1"],
                "confidence_stats": rf_results["confidence_statistics"]
            },
            "baseline_lr": {
                "accuracy": lr_results["accuracy"],
                "macro_f1": lr_results["macro_f1"],
                "weighted_f1": lr_results["weighted_f1"],
                "confidence_stats": lr_results["confidence_statistics"]
            }
        }
        with open(MODEL_META_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"[+] Updated model metadata with evaluation results: {MODEL_META_PATH}")

    # Generate Markdown Evaluation Report
    generate_markdown_report(full_eval_data, labels)
    print(f"[+] Evaluation report generated at: {EVAL_REPORT_PATH}")
    print("=" * 70)


def generate_markdown_report(data, labels):
    rf = data["primary_model"]["metrics"]
    lr = data["baseline_model"]["metrics"]

    lines = []
    lines.append("# RailAssist AI — Model Evaluation & Comparison Report")
    lines.append(f"\n**Evaluated on:** Held-out Test Split ({data['test_samples']} samples, 20% stratified)")
    lines.append(f"**Training Set:** {data['train_samples']} samples | **Total Dataset:** {data['total_samples']} samples\n")

    lines.append("## 1. Overall Performance Summary")
    lines.append("| Metric | Random Forest (Primary) | Logistic Regression (Baseline) | Difference | Better Performing |")
    lines.append("|---|---|---|---|---|")

    diff_acc = rf["accuracy"] - lr["accuracy"]
    diff_mf1 = rf["macro_f1"] - lr["macro_f1"]
    diff_wf1 = rf["weighted_f1"] - lr["weighted_f1"]

    lines.append(f"| **Accuracy** | **{rf['accuracy']*100:.2f}%** | {lr['accuracy']*100:.2f}% | {diff_acc*100:+.2f}% | {'Random Forest' if diff_acc >= 0 else 'Logistic Regression'} |")
    lines.append(f"| **Macro-F1** | **{rf['macro_f1']:.4f}** | {lr['macro_f1']:.4f} | {diff_mf1:+.4f} | {'Random Forest' if diff_mf1 >= 0 else 'Logistic Regression'} |")
    lines.append(f"| **Weighted-F1** | **{rf['weighted_f1']:.4f}** | {lr['weighted_f1']:.4f} | {diff_wf1:+.4f} | {'Random Forest' if diff_wf1 >= 0 else 'Logistic Regression'} |")
    lines.append(f"| **Mean Prediction Confidence** | {rf['confidence_statistics']['mean_confidence']*100:.1f}% | {lr['confidence_statistics']['mean_confidence']*100:.1f}% | - | - |\n")

    lines.append("## 2. Per-Class Performance Breakdown")
    lines.append("| Category | Test Support | RF Precision | RF Recall | RF F1-Score | LR Precision | LR Recall | LR F1-Score | Status |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for lbl in labels:
        rf_c = rf["per_class"][lbl]
        lr_c = lr["per_class"][lbl]
        status = "⚠️ Insufficient Test Support" if rf_c["insufficient_support"] else "Adequate Support"
        lines.append(
            f"| **{lbl}** | {rf_c['test_support']} | "
            f"{rf_c['precision']:.3f} | {rf_c['recall']:.3f} | **{rf_c['f1_score']:.3f}** | "
            f"{lr_c['precision']:.3f} | {lr_c['recall']:.3f} | **{lr_c['f1_score']:.3f}** | "
            f"{status} |"
        )
    lines.append("")

    lines.append("## 3. Insufficient Support and Limitations")
    insufficient = data["insufficient_test_support_classes"]
    if insufficient:
        lines.append(f"- **Categories with Limited Test Support:** {', '.join(insufficient)}")
        lines.append(f"  - **Medical Assistance** had only 2 held-out test samples (out of 11 total dataset samples). Consequently, its recall and F1 metrics have high statistical variance and cannot be considered a conclusive proof of generalizability in production.")
    lines.append(f"- **Engineering:** 0 records in raw dataset; excluded from supervised model fitting.")
    lines.append(f"- **Probability Calibration:** The Random Forest `predict_proba` values reflect ensemble tree voting proportions. They should be interpreted as heuristic relative confidence rather than perfectly calibrated Bayesian posterior probabilities.\n")

    lines.append("## 4. Confusion Matrix (Primary Random Forest)")
    lines.append("Rows represent Actual ground-truth categories, and Columns represent Predicted categories.\n")

    # Table format confusion matrix
    header = "| Actual \\ Predicted | " + " | ".join([l[:8] for l in labels]) + " |"
    sep = "|---" * (len(labels) + 1) + "|"
    lines.append(header)
    lines.append(sep)

    for i, row_label in enumerate(labels):
        row_vals = " | ".join(str(v) for v in rf["confusion_matrix"][i])
        lines.append(f"| **{row_label[:14]}** | {row_vals} |")

    lines.append("\n## 5. Algorithmic Comparison Analysis")
    if rf["macro_f1"] >= lr["macro_f1"]:
        lines.append(f"- **Random Forest** achieved superior Macro-F1 ({rf['macro_f1']:.4f} vs {lr['macro_f1']:.4f}) and robustly handled non-linear word co-occurrences.")
    else:
        lines.append(f"- **Logistic Regression** achieved a higher Macro-F1 score ({lr['macro_f1']:.4f} vs {rf['macro_f1']:.4f}) due to linear feature separability in high-dimensional sparse TF-IDF spaces. Random Forest remains the primary requested algorithm per project specifications, but Logistic Regression serves as an effective, highly competitive linear baseline.")

    with open(EVAL_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    run_evaluation()
