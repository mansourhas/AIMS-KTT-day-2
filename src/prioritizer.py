import os
import json
import pandas as pd
import numpy as np
import lightgbm as lgb
from pathlib import Path
import json

# --- DIRECTORY SETUP ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "dataset"
GRID_CSV_PATH = os.path.join(DATA_DIR, "grid_history.csv")
APPLIANCES_PATH = os.path.join(DATA_DIR, "appliances.json")
BUSINESSES_PATH = os.path.join(DATA_DIR, "businesses.json")

class AppliancePrioritizer:
    def __init__(self, appliances_file, business_mix):
        """
        Initializes the prioritizer with the master appliance list 
        and the specific business's appliance mix.
        """
        with open(appliances_file, 'r') as f:
            catalog = json.load(f)
            
        # Filter catalog for only the appliances this business owns
        self.appliances = [app for app in catalog if app['name'] in business_mix]
        
        # Pre-calculate Revenue Efficiency (RWF generated per Watt)
        # We factor in the startup spike penalty to minimize grid tripping
        for app in self.appliances:
            effective_watts = app['watts_avg'] + (app['start_up_spike_w'] * 0.1)
            # Max ensures we don't divide by zero for zero-watt anomalies
            app['rwf_per_watt'] = app['revenue_if_running_rwf_per_h'] / max(effective_watts, 1)

    def generate_plan(self, hourly_forecast):
        """
        Generates a 24-hour ON/OFF schedule.
        Respects the strict 'drop luxury before critical' rule.
        """
        plan = []
        
        for hour_data in hourly_forecast:
            p_outage = hour_data['p_outage']
            hour = hour_data['hour']
            
            hourly_state = {'hour': hour, 'p_outage': p_outage, 'status': {}}
            
            # --- SHEDDING RISK THRESHOLDS ---
            shed_luxury = p_outage >= 0.20
            shed_comfort = p_outage >= 0.50
            shed_critical = p_outage >= 0.85 
            
            # --- OPTIMIZATION LOGIC ---
            # 1. Enforce hierarchy: Luxury drops first, then Comfort, then Critical[cite: 32].
            # 2. Within a category, drop the least revenue-efficient appliances first.
            category_rank = {'luxury': 1, 'comfort': 2, 'critical': 3}
            sorted_apps = sorted(
                self.appliances, 
                key=lambda x: (category_rank[x['category']], x['rwf_per_watt'])
            )
            
            for app in sorted_apps:
                cat = app['category']
                
                # Execute shedding protocol
                if cat == 'luxury' and shed_luxury:
                    hourly_state['status'][app['name']] = 'OFF'
                elif cat == 'comfort' and shed_comfort:
                    hourly_state['status'][app['name']] = 'OFF'
                elif cat == 'critical' and shed_critical:
                    hourly_state['status'][app['name']] = 'OFF'
                else:
                    hourly_state['status'][app['name']] = 'ON'
                    
            plan.append(hourly_state)
            
        return plan

if __name__ == "__main__":
    import os
    import json
    
    # 1. Load the Archetype Mix
    with open("dataset/businesses.json", 'r') as f:
        businesses = json.load(f)
    salon_data = next(b for b in businesses if b['archetype'] == "salon")
    
    # 2. Initialize Prioritizer
    prioritizer = AppliancePrioritizer("dataset/appliances.json", salon_data['appliance_mix'])
    
    # ==========================================
    # 3. FORECAST TOGGLE (Comment/Uncomment here)
    # ==========================================
    
    # OPTION A: Use the Mock Forecast (For quick testing)
    # forecast_to_use = [
    #     {'hour': 8, 'p_outage': 0.05, 'exp_duration': 0},    # Safe
    #     {'hour': 14, 'p_outage': 0.60, 'exp_duration': 45},  # Medium Risk
    #     {'hour': 19, 'p_outage': 0.95, 'exp_duration': 120}  # High Risk
    # ]
    # OPTION A: Use the Mock Forecast (Full 24-hour curve)
    forecast_to_use = [
        {'hour': 0, 'p_outage': 0.02, 'exp_duration': 0},
        {'hour': 1, 'p_outage': 0.02, 'exp_duration': 0},
        {'hour': 2, 'p_outage': 0.02, 'exp_duration': 0},
        {'hour': 3, 'p_outage': 0.03, 'exp_duration': 0},
        {'hour': 4, 'p_outage': 0.05, 'exp_duration': 0},
        {'hour': 5, 'p_outage': 0.10, 'exp_duration': 0},
        {'hour': 6, 'p_outage': 0.25, 'exp_duration': 30},
        {'hour': 7, 'p_outage': 0.40, 'exp_duration': 45},
        {'hour': 8, 'p_outage': 0.65, 'exp_duration': 60},  # Morning Peak
        {'hour': 9, 'p_outage': 0.45, 'exp_duration': 40},
        {'hour': 10, 'p_outage': 0.20, 'exp_duration': 0},
        {'hour': 11, 'p_outage': 0.15, 'exp_duration': 0},
        {'hour': 12, 'p_outage': 0.10, 'exp_duration': 0},
        {'hour': 13, 'p_outage': 0.15, 'exp_duration': 0},
        {'hour': 14, 'p_outage': 0.25, 'exp_duration': 20},
        {'hour': 15, 'p_outage': 0.35, 'exp_duration': 30},
        {'hour': 16, 'p_outage': 0.50, 'exp_duration': 45},
        {'hour': 17, 'p_outage': 0.70, 'exp_duration': 60},
        {'hour': 18, 'p_outage': 0.85, 'exp_duration': 90},  # Evening Peak
        {'hour': 19, 'p_outage': 0.95, 'exp_duration': 120}, # Highest Risk
        {'hour': 20, 'p_outage': 0.80, 'exp_duration': 90},
        {'hour': 21, 'p_outage': 0.40, 'exp_duration': 45},
        {'hour': 22, 'p_outage': 0.15, 'exp_duration': 0},
        {'hour': 23, 'p_outage': 0.05, 'exp_duration': 0},
    ]

    # OPTION B: Use the Real JSON (Uncomment the two lines below to use real ML data)
    # with open("dataset/forecast.json", 'r') as f:
    #     forecast_to_use = json.load(f)
        
    # ==========================================
    
    # 4. Generate and print plan
    # Notice we pass 'forecast_to_use' here, not the mock directly!
    daily_plan = prioritizer.generate_plan(forecast_to_use)

    # Save to JSON for the UI to read
    with open("daily_plan.json", "w") as f:
        json.dump(daily_plan, f)
    print("Plan saved to daily_plan.json")
    
    print(f"--- Load-Shedding Plan for {salon_data['archetype'].upper()} ---")
    for h in daily_plan:
        print(f"\nHour {h['hour']:02d} | Outage Risk: {h['p_outage']:.1%}")
        for appliance, status in h['status'].items():
            status_indicator = "🟢 ON" if status == 'ON' else "🔴 OFF"
            print(f"  {appliance:<20}: {status_indicator}")