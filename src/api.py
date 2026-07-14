import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import os
import json
from datetime import datetime

from src.data_loader import DataLoader
from src.model import AirbnbModel

data_loader = DataLoader()
preprocessor = data_loader.load_preprocessor('artifacts/preprocessor.pkl')

model = AirbnbModel()
model.load_model('models/airbnb_model.pkl')

with open('models/airbnb_model_metadata.json', 'r') as f:
    metadata = json.load(f)

print(f"✅ Model loaded: {metadata['model_type']}")
print(f"✅ R² Score: {metadata['metrics']['r2']:.4f}")

class PropertyFeatures(BaseModel):
    neighbourhood: str = Field(..., description="Neighborhood of the property")
    room_type: str = Field(..., description="Type of room (Entire home/apt, Private room, Shared room)")
    minimum_nights: int = Field(..., ge=1, le=365, description="Minimum number of nights")
    number_of_reviews: int = Field(..., ge=0, description="Total number of reviews")
    reviews_per_month: float = Field(..., ge=0, description="Average reviews per month")
    calculated_host_listing_count: int = Field(..., ge=1, description="Number of listings by the host")
    availability_365: int = Field(..., ge=0, le=365, description="Available days in a year")

class PredictionResponse(BaseModel):
    predicted_price: float
    price_range: str
    confidence_score: Optional[float] = None
    status: str
    timestamp: str

app = FastAPI(title = "RevNest API",
              description="Predict airbnb rental prices based on property features",
              version="1.0.0")
#For frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)  

def get_price_range(price):
    if price < 50 :
        return "Budget"
    elif price < 100:
        return "Economy"
    elif price < 200:
        return "standard"
    elif price < 300:
        return "Premium"
    else:
        return "Luxury"
    
#API endpoints
@app.get("/")
async def root():
    return {
        "message": "Airbnb Price Prediction API is running",
        "model": metadata['model_type'],
        "r2_score": metadata['metrics']['r2'],
        "endpoints": {
            "/predict": "POST - Predict price for a property",
            "/batch_predict": "POST - Predict prices for multiple properties",
            "/health": "GET - Check API health",
            "/docs": "GET - Interactive API documentation"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/predict", response_model= PredictionResponse)
async def predict(features:PropertyFeatures):
    try:
        input_df = pd.DataFrame([features.dict()])
        transformed = preprocessor.transform(input_df)
        
        prediction = model.model.predict(transformed)[0]
        prediction = float(np.round(prediction , 2))

        price_range = get_price_range(prediction)

        return PredictionResponse(
            predicted_price = prediction,
            price_range =  price_range,
            confidence_score= None,
            status = "success",
            timestamp = datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/batch_predict")
async def batch_predict(features_list: List[PropertyFeatures]):
    try:
        predictions = []
        for features in features_list:
            input_df = pd.DataFrame([features.dict()])
            transformed = preprocessor.transform(input_df)
            prediction = model.model.predict(transformed)[0]
            predictions.append(float(prediction))

        return {
            "predictions": predictions,
            "count" : len(predictions),
            "status" : "success"
        }   
    except Exception as e:
        raise HTTPException(status_code=400, detail = str(e))

@app.get("/model_info")
async def model_info():
    return {
        "model_type":metadata['model_type'],
        "metrics": metadata['metrics'],
        "training_date": metadata['training_date'],
        "feature_importance": metadata.get('feature_importance', [])
    }

#Run the app
if __name__ == "__main__":
    uvicorn.run("src.api:app" ,host = "0.0.0.0", port=8000, reload=True)
