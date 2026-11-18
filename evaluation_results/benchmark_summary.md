# Model Evaluation & Benchmark Summary
**Dataset:** `production_server_large.log` (5000 logs, 63 time windows)
**Evaluated At:** 2026-11-18 12:33:12

## Quantitative Comparison Table
| Model                      |   Precision |   Recall |   F1-Score | False Positive Rate   |   Latency (ms) |
|:---------------------------|------------:|---------:|-----------:|:----------------------|---------------:|
| Rule-Based (Baseline)      |       0.25  |   1      |     0.4    | 37.5%                 |           1.87 |
| Z-Score (Statistical)      |       0.875 |   1      |     0.9333 | 1.8%                  |           1.08 |
| Isolation Forest (ML)      |       1     |   0.1429 |     0.25   | 0.0%                  |          83.56 |
| Hybrid Ensemble (Proposed) |       1     |   1      |     1      | 0.0%                  |          90.09 |

## Key Academic Insights
1. **Rule-Based Baseline**: Fast but rigid; suffers from false positives when operational thresholds fluctuate.
2. **Z-Score (Statistical)**: Effective on volume spikes, but blind to subtle multi-variable interactions (e.g. low volume with rare templates).
3. **Isolation Forest (ML)**: Isolates non-linear multidimensional outliers in feature space without requiring prior thresholds.
4. **Hybrid Ensemble (Our System)**: Achieves the highest F1-Score by balancing statistical sensitivity with ML isolation and rule-based safety nets.
