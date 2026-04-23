import os
from huggingface_hub import HfApi, DatasetCard, DatasetCardData

# ==========================================
# CONFIGURATION
# ==========================================
# Ensure you have set your HF_TOKEN environment variable
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("Please set the HF_TOKEN environment variable with your Hugging Face write token.")

# Replace 'your-username' with your actual Hugging Face handle
USERNAME = "mansouro"
DATASET_NAME = "aims-ktt-grid-outage-synthetic"
REPO_ID = f"{USERNAME}/{DATASET_NAME}"
DATASET_DIR = "../dataset"

# ==========================================
# 1. INITIALIZE API & CREATE REPO
# ==========================================
api = HfApi()

print(f"Creating dataset repository: {REPO_ID}...")
api.create_repo(
    repo_id=REPO_ID,
    repo_type="dataset",
    exist_ok=True, # Will not fail if the repo already exists
    token=HF_TOKEN,
    private=False  # The brief requires public access for the code, good practice for the data too
)

# ==========================================
# 2. UPLOAD THE DATA FILES
# ==========================================
print(f"Uploading files from {DATASET_DIR} to {REPO_ID}...")
api.upload_folder(
    folder_path=DATASET_DIR,
    repo_id=REPO_ID,
    repo_type="dataset",
    token=HF_TOKEN,
    commit_message="Upload synthetic grid outage and appliance data"
)

# ==========================================
# 3. GENERATE & PUSH PROFESSIONAL DATASET CARD
# ==========================================
print("Generating professional Dataset Card with YAML metadata...")

# Define the YAML metadata (Tags and configurations)
card_data = DatasetCardData(
    language=["en"],
    license="mit",
    task_categories=["time-series-forecasting", "tabular-classification", "optimization"],
    tags=["energy", "synthetic", "grid-outage", "sme", "aims-ktt-hackathon", "actionable-ai"],
    pretty_name="AIMS KTT Grid Outage & Appliance Prioritization Dataset"
)

# Define the Markdown content for the README
markdown_content = """
# Synthetic Grid Outage & Appliance Prioritization Dataset

## Dataset Description
This dataset is synthetically generated for the **AIMS KTT Hackathon (Tier 2.3 - Grid Outage Forecaster + Appliance Prioritizer)**. It simulates a 180-day history of electrical grid performance alongside weather correlates, and includes economic and power profiles for typical Small and Medium Enterprises (SMEs) in East Africa.

### Dataset Structure
The repository contains three primary files:
- `grid_history.csv`: 180 days of hourly data containing timestamps, grid load (MW), temperature, humidity, wind, rainfall, an outage flag (0/1), and outage duration (minutes).
- `appliances.json`: A catalog of 10 typical SME appliances, categorized by necessity (critical, comfort, luxury), including their power draw, startup spikes, and equivalent revenue per hour.
- `businesses.json`: Archetype definitions for three distinct businesses (Salon, Cold Room, Tailor) and their specific appliance mixes.

### Intended Use
This dataset is designed to train probabilistic time-series forecasters (e.g., Prophet, ARIMA-X, LightGBM) to predict both the likelihood `P(outage)` and expected duration `E[duration | outage]` of grid failures. Furthermore, it serves as the foundation for a constrained optimization task: creating an appliance load-shedding plan that maximizes SME revenue during outages.

### Data Generation Profile
- **Grid Load**: Features morning and evening peaks, weekly seasonality, and Gaussian noise.
- **Outage Probability**: Correlated linearly with lagged load, rainfall, and hour of the day, plus a base hourly risk.
- **Outage Duration**: Drawn from a LogNormal distribution ($\mu \approx 4.32, \sigma = 0.6$) to simulate a mean expected downtime of 90 minutes.
"""

# Combine metadata and markdown
card = DatasetCard.from_template(card_data, template_str=markdown_content)

print("Pushing Dataset Card to Hub...")
card.push_to_hub(REPO_ID, token=HF_TOKEN)

print(f"\n✅ Success! Your dataset is live and professionally tagged at: https://huggingface.co/datasets/{REPO_ID}")
