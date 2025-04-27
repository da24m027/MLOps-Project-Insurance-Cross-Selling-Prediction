from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
from datetime import datetime
import json
import os
from src.predict import predict_single

app = FastAPI(title="Insurance Cross-Selling Prediction")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# In-memory database (in production, you'd use a real database)
class CustomerDatabase:
    def __init__(self):
        self.customers = []
        self.load_data()
        
    def load_data(self):
        # Load existing data if file exists
        if os.path.exists("customer_data.json"):
            try:
                with open("customer_data.json", "r") as f:
                    self.customers = json.load(f)
            except:
                self.customers = []
    
    def save_data(self):
        with open("customer_data.json", "w") as f:
            json.dump(self.customers, f)
    
    def add_customer(self, customer_data):
        self.customers.append(customer_data)
        self.save_data()
    
    def get_all_customers(self):
        return self.customers
    
    def get_positive_predictions(self):
        return [c for c in self.customers if c["prediction"] == True]

db = CustomerDatabase()

# Pydantic models
class CustomerInput(BaseModel):
    name: str
    mobile: str
    age: int
    gender: str
    driving_license: int
    region_code: float
    previously_insured: int
    vehicle_age: str
    vehicle_damage: str
    annual_premium: float
    policy_sales_channel: float
    vintage: int

class CustomerResponse(BaseModel):
    name: str
    mobile: str
    prediction: bool
    timestamp: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(customer: CustomerInput):
    # Prepare input data for model
    input_data = {
        "Gender": customer.gender,
        "Age": customer.age,
        "Driving_License": customer.driving_license,
        "Region_Code": customer.region_code,
        "Previously_Insured": customer.previously_insured,
        "Vehicle_Age": customer.vehicle_age,
        "Vehicle_Damage": customer.vehicle_damage,
        "Annual_Premium": customer.annual_premium,
        "Policy_Sales_Channel": customer.policy_sales_channel,
        "Vintage": customer.vintage
    }
    
    # Make prediction
    prediction = predict_single(input_data)
    
    # Store customer data
    customer_entry = {
        'name': customer.name,
        'mobile': customer.mobile,
        'prediction': prediction,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'data': input_data
    }
    
    db.add_customer(customer_entry)
    
    return {"success": True, "prediction": prediction}

@app.get("/customers", response_model=List[CustomerResponse])
async def get_customers():
    customers = db.get_all_customers()
    return [{
        "name": c["name"],
        "mobile": c["mobile"],
        "prediction": c["prediction"],
        "timestamp": c["timestamp"]
    } for c in customers]

@app.get("/positive-customers", response_model=List[CustomerResponse])
async def get_positive_customers():
    customers = db.get_positive_predictions()
    return [{
        "name": c["name"],
        "mobile": c["mobile"],
        "prediction": c["prediction"],
        "timestamp": c["timestamp"]
    } for c in customers]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)