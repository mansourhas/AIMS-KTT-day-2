import pandas as pd
import os

# Paths
GRID_CSV = "dataset/grid_history.csv"
TRAIN_CSV = "dataset/train_history.csv"
RECENT_CSV = "dataset/recent_24h.csv"

def prepare_demo_data():
    print(f"Loading full dataset from {GRID_CSV}...")
    df = pd.read_csv(GRID_CSV)
    
    # Ensure it's sorted by time
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Split the data
    # We need a bit more than 24 hours for the recent file because our model 
    # uses a 6-hour rolling window for rain. We pass the last 30 hours to be safe.
    train_df = df.iloc[:-24]
    recent_df = df.iloc[-30:] # Pass 30 hours so the rolling features can compute properly
    
    # Save them
    train_df.to_csv(TRAIN_CSV, index=False)
    recent_df.to_csv(RECENT_CSV, index=False)
    
    print(f"✅ Success!")
    print(f"Created {TRAIN_CSV} ({len(train_df)} rows) for training.")
    print(f"Created {RECENT_CSV} ({len(recent_df)} rows) for live inference.")

if __name__ == "__main__":
    # Ensure the dataset directory exists
    os.makedirs("dataset", exist_ok=True)
    prepare_demo_data()