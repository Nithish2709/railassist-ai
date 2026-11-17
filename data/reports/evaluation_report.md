# RailAssist AI — Model Evaluation & Comparison Report

**Evaluated on:** Held-out Test Split (390 samples, 20% stratified)
**Training Set:** 1559 samples | **Total Dataset:** 1949 samples

## 1. Overall Performance Summary
| Metric | Random Forest (Primary) | Logistic Regression (Baseline) | Difference | Better Performing |
|---|---|---|---|---|
| **Accuracy** | **75.38%** | 80.51% | -5.13% | Logistic Regression |
| **Macro-F1** | **0.5670** | 0.6827 | -0.1157 | Logistic Regression |
| **Weighted-F1** | **0.7255** | 0.7957 | -0.0702 | Logistic Regression |
| **Mean Prediction Confidence** | 60.0% | 39.1% | - | - |

## 2. Per-Class Performance Breakdown
| Category | Test Support | RF Precision | RF Recall | RF F1-Score | LR Precision | LR Recall | LR F1-Score | Status |
|---|---|---|---|---|---|---|---|---|
| **Catering** | 18 | 0.769 | 0.556 | **0.645** | 0.688 | 0.611 | **0.647** | Adequate Support |
| **Coach Maintenance** | 13 | 1.000 | 0.077 | **0.143** | 0.667 | 0.154 | **0.250** | Adequate Support |
| **Electrical** | 19 | 0.706 | 0.632 | **0.667** | 0.682 | 0.789 | **0.732** | Adequate Support |
| **Housekeeping** | 66 | 0.676 | 0.758 | **0.714** | 0.778 | 0.849 | **0.812** | Adequate Support |
| **Operations & Traffic** | 157 | 0.829 | 0.955 | **0.888** | 0.896 | 0.936 | **0.916** | Adequate Support |
| **Passenger Grievance** | 80 | 0.670 | 0.787 | **0.724** | 0.792 | 0.762 | **0.777** | Adequate Support |
| **Security** | 28 | 0.833 | 0.179 | **0.294** | 0.560 | 0.500 | **0.528** | Adequate Support |
| **Water & Sanitation** | 9 | 0.750 | 0.333 | **0.462** | 0.727 | 0.889 | **0.800** | Adequate Support |

## 3. Insufficient Support and Limitations
- **Engineering:** 0 records in raw dataset; excluded from supervised model fitting.
- **Probability Calibration:** The Random Forest `predict_proba` values reflect ensemble tree voting proportions. They should be interpreted as heuristic relative confidence rather than perfectly calibrated Bayesian posterior probabilities.

## 4. Confusion Matrix (Primary Random Forest)
Rows represent Actual ground-truth categories, and Columns represent Predicted categories.

| Actual \ Predicted | Catering | Coach Ma | Electric | Housekee | Operatio | Passenge | Security | Water &  |
|---|---|---|---|---|---|---|---|---|
| **Catering** | 10 | 0 | 0 | 3 | 2 | 2 | 0 | 1 |
| **Coach Maintena** | 0 | 1 | 3 | 7 | 0 | 2 | 0 | 0 |
| **Electrical** | 0 | 0 | 12 | 3 | 2 | 2 | 0 | 0 |
| **Housekeeping** | 0 | 0 | 1 | 50 | 8 | 7 | 0 | 0 |
| **Operations & T** | 2 | 0 | 0 | 0 | 150 | 5 | 0 | 0 |
| **Passenger Grie** | 1 | 0 | 1 | 5 | 9 | 63 | 1 | 0 |
| **Security** | 0 | 0 | 0 | 2 | 8 | 13 | 5 | 0 |
| **Water & Sanita** | 0 | 0 | 0 | 4 | 2 | 0 | 0 | 3 |

## 5. Algorithmic Comparison Analysis
- **Logistic Regression** achieved a higher Macro-F1 score (0.6827 vs 0.5670) due to linear feature separability in high-dimensional sparse TF-IDF spaces. Random Forest remains the primary requested algorithm per project specifications, but Logistic Regression serves as an effective, highly competitive linear baseline.
