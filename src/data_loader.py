import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

class DataLoader:
    def __init__(self, data_path = None):
        self.data_path = data_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.preprocessor = None

    def load_data(self):
        np.random.seed(42)
        n = 5000
        print("📦 Loading Airbnb dataset...")
        #synthetic features
        self.df = pd.DataFrame({
            'neighbourhood': np.random.choice(['Downtown', 'Uptown', 'Midtown', 'Suburbs', 'Riverside'], n),
            'room_type': np.random.choice(['Entire home/apt', 'Private room', 'Shared room'], n),
            'minimum_nights': np.random.randint(1, 30, n),
            'number_of_reviews': np.random.randint(0, 500, n),
            'reviews_per_month': np.random.uniform(0, 5, n),
            'calculated_host_listing_count': np.random.randint(1, 50, n),
            'availibility_365': np.random.randint(0, 365, n),
            'latitude': np.random.uniform(40.7, 40.8, n),
            'longitude': np.random.uniform(-74.0, -73.9, n)
        })  

        self.df['price'] = (
            50 * (self.df['minimum_nights']/ 10) +
            0.5 * (self.df['number_of_reviews']) +
            10 * (self.df['availibility_365'] / 365) + 
            self.df['reviews_per_month'] * 20 +
            np.random.normal(0, 10, n)
        ) 
        self.df['price'] = self.df['price'].clip(20, 500)
        print(f"✅ Loaded {len(self.df)} records")
        return self.df 
    
    def preprocess(self):
        print("🔄 Preprocessing data...")
        self.df['reviews_per_month'] = self.df['reviews_per_month'].fillna(0)
        features = ['neighbourhood', 'room_type', 'minimum_nights', 'number_of_reviews','reviews_per_month',
                    'calculated_host_listing_count','availibility_365' ]
        X = self.df[features]
        y = self.df['price']

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state = 42)

        categorical_features = ['neighbourhood', 'room_type']
        numeric_features = ['minimum_nights', 'number_of_reviews', 
                           'reviews_per_month', 'calculated_host_listing_count', 
                           'availibility_365']
        
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        numeric_transformer = StandardScaler()

        self.preprocessor = ColumnTransformer(
            transformers = [
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        self.preprocessor.fit(self.X_train)


        print(f"✅ Preprocessing complete. Training size: {len(self.X_train)}, Test size: {len(self.X_test)}")

        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def save_preprocessor(self, path = 'artifacts/preprocessor.pkl'):
        os.makedirs('artifacts', exist_ok=True)
        joblib.dump(self.preprocessor, path)
        print(f"📁 Preprocessor saved to {path}")

    def load_preprocessor(self, path = 'artifacts/preprocessor.pkl'):
        self.preprocessor = joblib.load(path)  
        print(f"📁 Preprocessor loaded from {path}")
        return self.preprocessor
    
    def transform_input(self, input_data):
        if self.preprocessor is None:
            raise ValueError("Preprocessor not loaded. Call load_preprocessor() first.")
        if isinstance(input_data, dict):
            input_df = pd.DataFrame(input_data)
        else:
            input_df = input_data

        transformed = self.preprocessor.transform(input_df)
        return transformed        
      

        