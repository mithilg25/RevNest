import sys
import os
from pathlib import Path
#ADding src to path
sys.path.append(str(Path(__file__).parent/'src'))

from src.data_loader import DataLoader
from src.model import AirbnbModel

def main():
    print("🏠 Airbnb Price Prediction - Training Pipeline")
    #Step 1
    print("\n📊 Step 1: Loading and preprocessing data")
    data_loader = DataLoader()
    data_loader.load_data()
    X_train, X_test, y_train, y_test = data_loader.preprocess()
    data_loader.save_preprocessor()

    X_train_transformed = data_loader.preprocessor.transform(X_train)
    X_test_transformed = data_loader.preprocessor.transform(X_test)

    #Step 2
    print("\n🤖 Step 2: Training models")
    models = {
        'random_forest' : AirbnbModel('random_forest'),
        'xgboost' : AirbnbModel('xgboost'),
        'catboost': AirbnbModel('catboost')
    }
    best_model = None
    best_r2 = -float('inf')
    best_model_name = None
    
    for name, model_obj in models.items():
        print(f"\n📊 Training {name}...")
        model_obj.create_model()
        model_obj.train(X_train_transformed, y_train, X_test_transformed, y_test)
        model_obj.save_model(f'models/{name}_model.pkl')

        if model_obj.metrics['r2'] > best_r2:
            best_r2 = model_obj.metrics['r2']
            best_model = model_obj
            best_model_name = name

    #Step 3
    print("\n🏆 Step 3: Saving best model")
    print(f"✅ Best model: {best_model_name} with R² = {best_r2:.4f}")
    best_model.save_model('models/airbnb_model.pkl')

    print("\n" + "=" * 60)
    print("🎉 Training complete!")
    print(f"📁 Model saved to: models/airbnb_model.pkl")
    print(f"📁 Preprocessor saved to: artifacts/preprocessor.pkl")
    print("=" * 60)

if __name__ == "__main__":
        main()
            
