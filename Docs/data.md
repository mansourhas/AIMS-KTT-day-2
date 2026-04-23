To successfully hand off this dataset to another AI agent (or an automated modeling pipeline) for the modeling phase, that agent needs a clear map of the statistical realities and the strict hackathon constraints. 

If the agent treats this as a standard out-of-the-box regression or classification task, it will fail the evaluation metrics. Here is the summary of exactly what the modeling agent needs to know.

### 🎯 The Necessities (What the Agent MUST Know)

**1. The Dual-Model Architecture**
The agent must build two distinct systems, not one monolithic model:
* [cite_start]**The Forecaster:** A probabilistic time-series model outputting two things per hour: `P(outage)` and `E[duration | outage]`[cite: 26, 27]. 
* [cite_start]**The Prioritizer:** A constrained optimization algorithm (like a greedy knapsack solver) that takes the forecast and the appliance JSONs to output an hourly ON/OFF schedule[cite: 31].

**2. The Ground Truth Signals**
The agent needs to know that the synthetic data isn't just random noise; it has specific, engineered correlations it must learn:
* [cite_start]**Outage Triggers:** Outages are heavily correlated with high grid load from the *previous* hour (`load_lag1`), rainfall events, and specific times of day[cite: 21].
* [cite_start]**Duration Distribution:** Outage duration is not normally distributed; it follows a LogNormal distribution with an expected mean of 90 minutes[cite: 24].

**3. The Hard Constraints & Metrics**
* [cite_start]**Scoring:** The forecaster will be judged on **Brier Score** for the probability, and **MAE** (Mean Absolute Error) for the duration[cite: 30]. 
* [cite_start]**Business Logic:** The prioritizer *must* enforce the rule: "drop luxury before critical"[cite: 32]. If a luxury item is running while a critical item is off during an outage, the plan is invalid.
* [cite_start]**Compute Limits:** The final inference pipeline must run in under 300 ms on a CPU-only environment[cite: 59, 60]. 

---

### ⚠️ The Pitfalls (Traps the Agent Must Avoid)

**1. The "Accuracy" Trap (Class Imbalance)**
[cite_start]Because the base rate for outages is strictly 4% per hour[cite: 22], a naive classifier that simply predicts "0" (no outage) every single hour will achieve 96% accuracy. 
* *The Fix:* The agent must be instructed to optimize for Brier Score and use probabilistic outputs (e.g., `predict_proba` in LightGBM/XGBoost) rather than hard class predictions.

**2. The Optimization Trap (Standard RMSE)**
Because the duration data has a LogNormal long tail (some outages will be very long), training a regression model using standard Mean Squared Error (MSE) will cause the model to over-predict durations to compensate for the extreme outliers. 
* *The Fix:* The agent must use Mean Absolute Error (MAE) or a custom Log-Cosh objective function during training.

**3. Data Leakage in Time-Series**
If the agent blindly splits the data using `train_test_split`, it will leak future weather and load data into the past. 
* [cite_start]*The Fix:* The agent must use strict temporal splitting (e.g., a rolling 30-day window) [cite: 30] and ensure that features like `load_mw` are shifted appropriately so it only predicts hour $T$ using data from hour $T-1$ and earlier.

**4. The Deep Learning Trap**
An autonomous coding agent might default to building a complex LSTM or Transformer architecture for the time-series forecasting. 
* *The Fix:* Explicitly steer the agent toward tree-based models like LightGBM or XGBoost on lagged features. [cite_start]Deep learning models will likely violate the < 10-minute training and < 300ms CPU inference constraints[cite: 59, 60], and tree models are generally superior for this scale of tabular data anyway.

**Next Step for the Agent:**
When prompting the downstream agent, explicitly pass it the `appliances.json` schema and tell it: *"Treat the prioritization task as a dynamic knapsack problem where the capacity is the expected length of the outage, and the values are the `revenue_if_running_rwf_per_h`."*