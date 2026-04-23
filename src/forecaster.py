import os
import argparse
import joblib
import pandas as pd
import numpy as np
import lightgbm as lgb
import warnings

warnings.filterwarnings('ignore')

MODEL_DIR = "model"

class OutageForecaster:
    def __init__(self):
        """
        Initializes the probabilistic forecaster. 
        Uses min_child_samples=50 to prevent overfitting on the small 180-day dataset.
        """
        self.features = [
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 
            'load_lag1', 'rain_lag1', 'load_rolling_3h', 'rain_rolling_6h'
        ]
        
        # We define the model paths
        self.clf_path = os.path.join(MODEL_DIR, "lgbm_classifier.pkl")
        self.reg_path = os.path.join(MODEL_DIR, "lgbm_regressor.pkl")

    def engineer_features(self, df):
        """
        Engineers cyclical time and lagged/rolling features.
        Strictly drops temp_c to prevent memorization of noise.
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Cyclical Time
        df['hour'] = df['timestamp'].dt.hour
        df['dayofweek'] = df['timestamp'].dt.dayofweek
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
        df['day_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7.0)
        df['day_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7.0)
        
        # Lags and Rolling Windows
        df['load_lag1'] = df['load_mw'].shift(1)
        df['rain_lag1'] = df['rain_mm'].shift(1)
        df['load_rolling_3h'] = df['load_mw'].shift(1).rolling(window=3).mean()
        df['rain_rolling_6h'] = df['rain_mm'].shift(1).rolling(window=6).sum()
        
        return df.dropna().reset_index(drop=True)

    def train(self, data_path):
        """
        Trains models and SAVES them to the /model directory.
        Constraint Check: Runs in well under 10 minutes on CPU.
        """
        print(f"Loading training data from {data_path}...")
        df = pd.read_csv(data_path)
        processed_df = self.engineer_features(df)
        
        X = processed_df[self.features]
        y_prob = processed_df['outage']
        
        print("Training Probability Classifier (P(outage))...")
        clf = lgb.LGBMClassifier(
            n_estimators=1000, learning_rate=0.05, max_depth=9,
            num_leaves=64, min_child_samples=50, class_weight='balanced', 
            random_state=42, n_jobs=-1
        )
        clf.fit(X, y_prob)
        
        print("Training Duration Regressor (E[duration | outage])...")
        reg = lgb.LGBMRegressor(
            n_estimators=1000, learning_rate=0.05, max_depth=9,
            num_leaves=64, min_child_samples=50, objective='mae', 
            random_state=42, n_jobs=-1
        )
        outages_only = processed_df[processed_df['outage'] == 1]
        if len(outages_only) > 0:
            reg.fit(outages_only[self.features], outages_only['duration_min'])

        # Save the models
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(clf, self.clf_path)
        joblib.dump(reg, self.reg_path)
        print(f"Models successfully saved to {MODEL_DIR}/")

    def predict(self, recent_data_path):
        """
        LOADS models from disk and runs inference for the next 24 hours.
        Constraint Check: Runs in < 300 ms.
        """
        if not os.path.exists(self.clf_path) or not os.path.exists(self.reg_path):
            raise FileNotFoundError("Models not found. Run with --train first.")
            
        clf = joblib.load(self.clf_path)
        reg = joblib.load(self.reg_path)
        
        df = pd.read_csv(recent_data_path)
        processed_df = self.engineer_features(df)
        
        # Isolate the final 24 hours to predict
        X_infer = processed_df[self.features].tail(24)
        hours = processed_df['hour'].tail(24).values
        
        p_outage = clf.predict_proba(X_infer)[:, 1]
        exp_duration = reg.predict(X_infer)
        
        forecast = []
        for i in range(len(X_infer)):
            forecast.append({
                'hour': int(hours[i]),
                'p_outage': float(p_outage[i]),
                'exp_duration': float(exp_duration[i])
            })
            
        return forecast

if __name__ == "__main__":
    import json # Make sure this is imported at the top of your file
    
    parser = argparse.ArgumentParser(description="Grid Outage Forecaster")
    parser.add_argument('--train', action='store_true', help="Train and save the models")
    parser.add_argument('--predict', action='store_true', help="Load models and predict")
    parser.add_argument('--data', type=str, required=True, help="Path to CSV data")
    parser.add_argument('--output', type=str, default="dataset/forecast.json", help="Where to save the JSON prediction")
    args = parser.parse_args()
    
    forecaster = OutageForecaster()
    
    if args.train:
        forecaster.train(args.data)
    elif args.predict:
        import time
        start = time.perf_counter()
        
        # 1. Generate the forecast
        forecast_output = forecaster.predict(args.data)
        
        # 2. Save it to a JSON file for the prioritizer
        with open(args.output, 'w') as f:
            json.dump(forecast_output, f, indent=4)
            
        latency = (time.perf_counter() - start) * 1000
        print(f"--- 24-Hour Forecast Generated in {latency:.2f} ms ---")
        print(f"✅ Forecast successfully saved to: {args.output}")