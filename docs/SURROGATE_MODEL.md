# Machine Learning Surrogate Benchmark & Domain Safety

**Training Script**: `scripts/04_train_surrogate.py`  
**Dataset**: `data/membrane_doe.csv` (N=500, 85/15 Train/Test Split)  
**Metrics Report**: `results/ml_metrics.csv`  

---

## 1. Multi-Model Benchmark Comparison

| Model Architecture | Target Output | $R^2$ Score | MAE | RMSE | MAPE (%) |
|---|---|---|---|---|---|
| **ExtraTrees (Best)** | $\text{CO}_2$ Conversion | **0.9709** | **0.0071** | **0.0154** | **9.06%** |
| **ExtraTrees (Best)** | $\text{CH}_3\text{OH}$ Yield | **0.9729** | **0.0062** | **0.0133** | **8.90%** |
| **ExtraTrees (Best)** | $\text{CH}_3\text{OH}$ Selectivity | **0.9451** | **0.0046** | **0.0068** | **0.52%** |
| **ExtraTrees (Best)** | $\text{H}_2\text{O}$ Removal | **0.9213** | **0.0230** | **0.0343** | **3.75%** |
| RandomForest | $\text{CO}_2$ Conversion | 0.8876 | 0.0164 | 0.0302 | 19.66% |
| RandomForest | $\text{CH}_3\text{OH}$ Yield | 0.8891 | 0.0147 | 0.0270 | 20.20% |
| GradientBoosting | $\text{CO}_2$ Conversion | 0.8865 | 0.0164 | 0.0303 | 20.79% |
| GradientBoosting | $\text{CH}_3\text{OH}$ Yield | 0.8866 | 0.0157 | 0.0273 | 23.36% |

---

## 2. Surrogate Safety & Extrapolation Guard
The platform incorporates the `is_in_training_domain()` validation function:
- **Interpolation Mode**: Input conditions lie strictly within the multi-dimensional parameter bounding box; surrogate predictions are active.
- **Extrapolation Mode**: If operating conditions exceed the validated bounding box, the UI displays an explicit warning and recommends running the physics engine directly.
