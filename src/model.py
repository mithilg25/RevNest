import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import json
from datetime import datetime
import warnings

class AirbnbModel():
    def __init__(self, model_type = 'random_forest'):
        self.model_type = model_type
        self.model = None
        self.metrics = {}
        self.feature_importance = None
        self.class_names = None

    def create_model(self):
        if self.model_type ==  'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)

        elif self.model_type == 'xgboost':
            self.model = XGBRegressor(
                n_estimators = 100, learning_rate = 0.1, max_depth = 6, random_state = 42 )

        elif self.model_type == 'catboost':
            self.model = CatBoostRegressor(
                iterations=100, learning_rate=0.1, depth=6, verbose = False, random_state=42)

        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        print(f"🏗️  Created {self.model_type} model")
        return self.model      

    def train(self, X_train, y_train, X_val = None, y_val = None):
        print(f"🏋️  Training {self.model_type} model...")

        if self.model is None:
            self.create_model()

        if self.model is not None:
            self.model.fit(X_train, y_train)
            print("✅ Training complete")
        else:
            raise ValueError(f"Model creation failed. self.model is still None.")

        if X_val is not None and y_val is not None:
            self.evaluate(X_val, y_val)

        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_

        return self.model

    def predict(self, X):
        if self.model is None:
            raise ValueError("Model is not trained")
        return self.model.predict(X)

    def evaluate(self, X_test, y_test):
        print("📊 Evaluating model...")

        y_pred = self.predict(X_test)
        self.metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)} 
        
        print(f"   RMSE: {self.metrics['rmse']:.2f}")
        print(f"   MAE: {self.metrics['mae']:.2f}")
        print(f"   R²: {self.metrics['r2']:.4f}")
        
        return self.metrics
    
    def save_model(self, path = 'models/airbnb_model.pkl'):
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, path)
        print(f"📁 Model saved to {path}")

        metadata = {
             'model_type': self.model_type,
             'metrics': self.metrics,
             'training_date': datetime.now().isoformat() ,
             'feature_importance': self.feature_importance.tolist()
        }
        metadata_path = path.replace('.pkl', '_metadata.json')
        with open(metadata_path , 'w') as f:
            json.dump(metadata, f, indent = 2)
        print(f"📁 Metadata saved to {metadata_path}")

    def load_model(self, path = 'models/airbnb_model.pkl'):
        self.model = joblib.load(path)
        print(f"📁 Model loaded from {path}")

        metadata_path = path.replace('.pkl', '_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.metrics = json.load(f)  
            print(f"📁 Metadata loaded")

        return self.model          


