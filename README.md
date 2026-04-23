# AI-Powered Grid Outage Forecasting & Appliance Prioritization System

## Overview

This project implements an intelligent power management solution for small businesses (SMEs) operating in regions with unreliable electrical grids. It combines:

- **Probabilistic Outage Forecaster**: A 24-hour ahead forecasting model predicting both the probability and expected duration of grid outages
- **Smart Appliance Prioritizer**: An optimization algorithm that schedules which appliances to keep running during predicted outages, maximizing revenue while protecting critical equipment
- **Low-Resource UI**: A lightweight web dashboard and SMS alert system designed for illiterate/low-literacy users in off-grid settings

The system targets three business archetypes: salons, cold storage facilities (vaccine cold chains), and tailoring shops.

---

## 📁 Project Structure

```
.
├── README.md                           # This file
├── Daily_plan.json                     # Sample 24-hour appliance schedule output
├── digest_spec.md                      # SMS notification specification & offline protocol
├── eval+experiments.ipynb              # Full evaluation pipeline (run on Colab CPU)
├── lite_ui.html                        # Static web dashboard (~50 KB)
├── process_log.md                      # Timeline, LLM usage log, and prompt library
├── SIGNED.md                           # Honor code signature
├── requirment.txt                      # Python dependencies
│
├── dataset/                            # Synthetic and working data
│   ├── grid_history.csv               # 180 days of hourly grid data with outages
│   ├── appliances.json                # Master appliance repository (10 devices)
│   ├── businesses.json                # Business archetypes (salon, cold room, tailor)
│   ├── recent_24h.csv                 # Last 24 hours for inference/prediction
│   ├── train_history.csv              # Training set snapshot
│   ├── forecast.json                  # Latest 24-hour forecast output
│   └── prep/                          # Preprocessing artifacts
│
├── Docs/                               # Documentation
│   ├── task.md                        # Complete hackathon brief and requirements
│   └── data.md                        # Data schema, ground truth signals, modeling pitfalls
│
├── model/                              # Trained model artifacts
│   ├── lgbm_classifier.pkl            # LightGBM outage probability model
│   └── lgbm_regressor.pkl             # LightGBM outage duration model
│
├── scripts/                            # Utilities
│   ├── data_generation.py             # Generates synthetic grid_history.csv, appliances.json, businesses.json
│   ├── prep.py                        # Data preprocessing and feature engineering
│   └── hf_auto_dataupload.py          # Uploads datasets to Hugging Face (optional)
│
└── src/                                # Core modules
    ├── forecaster.py                  # OutageForecaster class - trains & predicts outage probabilities + durations
    └── prioritizer.py                 # AppliancePrioritizer class - generates optimal ON/OFF schedules
```

---

## 🎯 Key Features

### 1. **Synthetic Data Generation**
- 180 days of highly realistic grid data with:
  - Hourly load patterns (morning/evening peaks, weekend drops)
  - Weather simulation (temperature, humidity, wind, rain)
  - Correlated outage events (load-driven, rain-driven, time-of-day effects)
  - LogNormal outage duration distribution (mean 90 min)
- Reproduces in **<2 minutes** on any machine
- Base outage rate calibrated to 4% per hour (realistic for sub-Saharan Africa)

### 2. **Machine Learning Pipeline**
- **Model Architecture**: Dual LightGBM system
  - **Classifier**: Predicts `P(outage)` for each hour (Brier Score metric)
  - **Regressor**: Predicts `E[duration | outage]` in minutes (MAE metric)
- **Features**: Cyclical time encoding, lagged load/rain, rolling statistics
- **Constraints**: 
  - Training: <10 min on CPU
  - Inference: <300 ms per 24-hour forecast

### 3. **Smart Prioritization**
- Greedy algorithm maximizing expected revenue
- **Strict rule enforcement**: Luxury appliances dropped before critical ones
- Example: During a predicted 80% outage risk at 19:00, the salon keeps hair clippers & lighting ON but schedules the blow dryer for 20:00

### 4. **User Interfaces**
- **SMS Digest**: 3 messages max (160 chars each) for feature phone users
- **Offline Protocol**: 6-hour staleness budget with fallback defensive heuristics
- **HTML Dashboard**: Charts, uncertainty bands, appliance status
- **Accessibility**: Icons and colored LEDs for non-literate users

---

## 🚀 Quick Start (Reproducibility: ≤2 Commands)

### Prerequisites
- Python 3.8+ 
- ~200 MB disk space (for models + data artifacts)

### Installation & Setup
```bash
# Option 1: On Your Local Machine (Windows)
pip install -r requirment.txt
python scripts/data_generation.py
python src/forecaster.py --train --data dataset/grid_history.csv
python src/forecaster.py --predict --data dataset/recent_24h.csv

# Option 2: On Your Local Machine (Linux/Mac)
pip install -r requirment.txt
python scripts/data_generation.py
python src/forecaster.py --train --data dataset/grid_history.csv
python src/forecaster.py --predict --data dataset/recent_24h.csv
```

### Colab (Recommended for Reproducibility)
To reproduce results on **free Colab CPU** in ≤2 commands:

**Command 1: Install & Generate Data**
```bash
!pip install -q -r https://raw.githubusercontent.com/mansourhas/AIMS-KTT-day-2/main/requirment.txt
!git clone https://github.com/mansourhas/AIMS-KTT-day-2.git && cd AIMS-KTT-day-2 && python scripts/data_generation.py
```

**Command 2: Train & Evaluate**
```bash
%cd AIMS-KTT-day-2
!python src/forecaster.py --train --data dataset/grid_history.csv
%run eval+experiments.ipynb  # Opens full evaluation notebook
```

---

## 📊 Usage Examples

### 1. Train the Forecaster
```bash
python src/forecaster.py --train --data dataset/grid_history.csv
# Output: Saves lgbm_classifier.pkl and lgbm_regressor.pkl to ./model/
```

### 2. Generate Predictions for 24 Hours
```bash
python src/forecaster.py --predict --data dataset/recent_24h.csv
# Output: JSON with hourly P(outage) and E[duration | outage]
```

### 3. Generate Appliance Schedule
```python
from src.prioritizer import AppliancePrioritizer
import json

# Load business definition
with open('dataset/businesses.json', 'r') as f:
    businesses = json.load(f)

# Create prioritizer for salon
prioritizer = AppliancePrioritizer(
    appliances_file='dataset/appliances.json',
    business_mix=businesses[0]['appliance_mix']  # Salon archetype
)

# Generate plan given forecast
forecast = [0.02, 0.05, ..., 0.15]  # 24-hour P(outage)
daily_plan = prioritizer.generate_plan(forecast)
```

### 4. View the Dashboard
```bash
python -m http.server 8000 --directory .
# Open browser to http://localhost:8000/lite_ui.html
```


## 🔧 Technical Notes

### Why LightGBM Instead of ONNX?
We use LightGBM's native `.pkl` format (with joblib) instead of ONNX conversion because:
1. **Dependency Conflicts**: ONNX tools (`onnxmltools`, `skl2onnx`) cause package conflicts in Colab's isolated environment
2. **Performance**: LightGBM's optimized C++ backend is faster than ONNX Runtime on CPU
3. **Industry Standard**: Lightweight deployment frameworks (like MobileEdge, TensorFlow Lite) are overkill for this tabular task
4. **Reproducibility**: Ensures bit-for-bit identical predictions across machines

### Model Constraints
- **min_child_samples=50**: Prevents overfitting on 180-day dataset
- **max_depth=6**: Enforces shallow trees for <300 ms inference on CPU
- **single_metric='binary_logloss'**: Optimizes for probability calibration, not accuracy

## 📄 License & Submission

This project is submitted as-is for hackathon evaluation. See [SIGNED.md](SIGNED.md) for honor code.
