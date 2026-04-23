import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
# ==========================================
# CONFIGURATION & MAGIC NUMBERS
# ==========================================
PROJECT_ROOT = Path(__file__).parent.parent
seed = 42
np.random.seed(seed)
sys.path.append(str(Path(__file__).parent.parent))  # Add parent directory to path for imports
OUTPUT_DIR = PROJECT_ROOT / "dataset"
DAYS = 180
HOURS = DAYS * 24
START_DATE = datetime(2025, 1, 1)

# Grid Signal Parameters
BASE_LOAD_MW = 20.0
PEAK_MORNING_HOUR = 8
PEAK_EVENING_HOUR = 19
WEEKEND_DROP_FACTOR = 0.75
NOISE_SCALE = 2.0

# Weather Parameters
TEMP_BASE = 22.0
HUMIDITY_BASE = 60.0
WIND_BASE = 3.0

# Rainy Season (Days 60 to 120)
RAIN_SEASON_START = 60
RAIN_SEASON_END = 120
RAIN_PROB_DRY = 0.05
RAIN_PROB_WET = 0.35

# Outage Probability Parameters
# P(outage) = a0 + a1*load_lag1 + a2*rain + a3*hour_of_day
A0_BASE = 0.01      # Base probability
A1_LOAD = 0.0005    # Load sensitivity
A2_RAIN = 0.001     # Rain sensitivity
A3_HOUR = 0.0002    # Hour of day sensitivity
TARGET_BASE_RATE = 0.04

# Outage Duration Parameters (LogNormal)
# E[X] = 90, sigma = 0.6 -> mu = ln(90) - (0.6^2)/2 = 4.3198
DURATION_MU = 4.3198
DURATION_SIGMA = 0.6

# ==========================================
# GENERATOR FUNCTIONS
# ==========================================

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_grid_history():
    timestamps = [START_DATE + timedelta(hours=i) for i in range(HOURS)]
    df = pd.DataFrame({'timestamp': timestamps})
    
    # Time features
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    
    # 1. Weather Data (Temp, Humidity, Wind, Rain)
    df['temp_c'] = TEMP_BASE + np.sin(df['hour_of_day'] * np.pi / 12) * 5 + np.random.normal(0, 1, HOURS)
    df['humidity'] = HUMIDITY_BASE + np.cos(df['hour_of_day'] * np.pi / 12) * 15 + np.random.normal(0, 5, HOURS)
    df['wind_ms'] = WIND_BASE + np.random.lognormal(0.5, 0.5, HOURS)
    
    # Rain injection
    is_rainy_season = (df['day_of_year'] >= RAIN_SEASON_START) & (df['day_of_year'] <= RAIN_SEASON_END)
    rain_prob = np.where(is_rainy_season, RAIN_PROB_WET, RAIN_PROB_DRY)
    rain_events = np.random.binomial(1, rain_prob)
    df['rain_mm'] = rain_events * np.random.exponential(5.0, HOURS) # Average 5mm when it rains
    
    # 2. Load Generation (Morning/Evening Peaks + Weekend Drop + Noise)
    morning_peak = np.exp(-0.1 * (df['hour_of_day'] - PEAK_MORNING_HOUR)**2) * 15
    evening_peak = np.exp(-0.1 * (df['hour_of_day'] - PEAK_EVENING_HOUR)**2) * 20
    weekend_multiplier = np.where(df['day_of_week'] >= 5, WEEKEND_DROP_FACTOR, 1.0)
    
    df['load_mw'] = (BASE_LOAD_MW + morning_peak + evening_peak) * weekend_multiplier
    df['load_mw'] += np.random.normal(0, NOISE_SCALE, HOURS)
    
    # 3. Outage Probability Calculation
    df['load_lag1'] = df['load_mw'].shift(1).fillna(BASE_LOAD_MW)
    
    raw_prob = (A0_BASE + 
                (A1_LOAD * df['load_lag1']) + 
                (A2_RAIN * df['rain_mm']) + 
                (A3_HOUR * df['hour_of_day']))
    
    # Clip probabilities and run Bernoulli sampler
    prob_clipped = np.clip(raw_prob, 0, 1)
    df['outage'] = np.random.binomial(1, prob_clipped)
    
    # 4. Outage Duration
    durations = np.random.lognormal(DURATION_MU, DURATION_SIGMA, HOURS)
    df['duration_min'] = np.where(df['outage'] == 1, np.round(durations), 0)
    
    # Print diagnostic for base rate calibration
    actual_rate = df['outage'].mean()
    print(f"[Diagnostics] Target Base Rate: {TARGET_BASE_RATE:.1%} | Actual Simulated Rate: {actual_rate:.2%}")
    
    # Cleanup unneeded columns
    cols_to_keep = ['timestamp', 'load_mw', 'temp_c', 'humidity', 'wind_ms', 'rain_mm', 'outage', 'duration_min']
    return df[cols_to_keep]

def generate_appliances():
    # 10 diverse appliances spanning the three archetypes
    return [
        {"name": "Hair Clippers", "category": "critical", "watts_avg": 15, "start_up_spike_w": 20, "revenue_if_running_rwf_per_h": 4000},
        {"name": "Blow Dryer", "category": "critical", "watts_avg": 1500, "start_up_spike_w": 2000, "revenue_if_running_rwf_per_h": 6000},
        {"name": "Water Heater", "category": "luxury", "watts_avg": 3000, "start_up_spike_w": 3000, "revenue_if_running_rwf_per_h": 0},
        {"name": "Main Compressor", "category": "critical", "watts_avg": 2500, "start_up_spike_w": 6000, "revenue_if_running_rwf_per_h": 15000},
        {"name": "Display Fridge", "category": "critical", "watts_avg": 500, "start_up_spike_w": 1200, "revenue_if_running_rwf_per_h": 5000},
        {"name": "Industrial Sewing Machine", "category": "critical", "watts_avg": 250, "start_up_spike_w": 400, "revenue_if_running_rwf_per_h": 3500},
        {"name": "Steam Iron", "category": "critical", "watts_avg": 1200, "start_up_spike_w": 1200, "revenue_if_running_rwf_per_h": 2500},
        {"name": "Ceiling Fan", "category": "comfort", "watts_avg": 70, "start_up_spike_w": 100, "revenue_if_running_rwf_per_h": 500},
        {"name": "LED Lighting", "category": "comfort", "watts_avg": 40, "start_up_spike_w": 40, "revenue_if_running_rwf_per_h": 1000},
        {"name": "Waiting Area TV", "category": "luxury", "watts_avg": 100, "start_up_spike_w": 120, "revenue_if_running_rwf_per_h": 0}
    ]

def generate_businesses():
    return [
        {
            "archetype": "salon",
            "appliance_mix": ["Hair Clippers", "Blow Dryer", "Water Heater", "Ceiling Fan", "LED Lighting", "Waiting Area TV"]
        },
        {
            "archetype": "cold room",
            "appliance_mix": ["Main Compressor", "Display Fridge", "LED Lighting", "Ceiling Fan"]
        },
        {
            "archetype": "tailor",
            "appliance_mix": ["Industrial Sewing Machine", "Steam Iron", "Ceiling Fan", "LED Lighting", "Waiting Area TV"]
        }
    ]

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    ensure_dir(OUTPUT_DIR)
    
    # 1. Grid Data
    print("Generating grid_history.csv...")
    grid_df = generate_grid_history()
    grid_df.to_csv(os.path.join(OUTPUT_DIR, "grid_history.csv"), index=False)
    
    # 2. Appliances
    print("Generating appliances.json...")
    appliances = generate_appliances()
    with open(os.path.join(OUTPUT_DIR, "appliances.json"), "w") as f:
        json.dump(appliances, f, indent=4)
        
    # 3. Businesses
    print("Generating businesses.json...")
    businesses = generate_businesses()
    with open(os.path.join(OUTPUT_DIR, "businesses.json"), "w") as f:
        json.dump(businesses, f, indent=4)
        
    print(f"Data successfully generated in '{OUTPUT_DIR}' folder.")