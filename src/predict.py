import mlflow
import pandas as pd
import yaml
import os
from data_preprocessing import *

def load_config():
    with open("../config/params.yaml", "r") as f:
        return yaml.safe_load(f)

def load_model():
    config = load_config()
    model = mlflow.sklearn.load_model("../models/latest_model")
    return model

def predict_single(input_data):
    model = load_model()
    config = load_config()
    
    # Convert input to DataFrame
    input_df = pd.DataFrame([input_data])
    
    # Apply same preprocessing as training data
    input_df = preprocess_data(input_df, config)
    
    prediction = model.predict(input_df)
    return bool(prediction[0])

if __name__ == "__main__":
    # Test prediction
    test_data = {
        "Gender": "Male",
        "Age": 35,
        "Driving_License": 1,
        "Region_Code": 11,
        "Previously_Insured": 1,
        "Vehicle_Age": "< 1 Year",
        "Vehicle_Damage": "No",
        "Annual_Premium": 35786,
        "Policy_Sales_Channel": 152,
        "Vintage": 53
    }
    print(predict_single(test_data))