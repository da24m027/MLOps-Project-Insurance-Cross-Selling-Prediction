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
import time
from prometheus_client import Counter, Histogram, Gauge, multiprocess, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.predict import predict_single

# Initialize FastAPI
app = FastAPI(title="Insurance Cross-Selling Prediction")

# Prometheus metrics
REGISTRY = CollectorRegistry(auto_describe=True)
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests', 
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Latency', 
    ['method', 'endpoint'],
    registry=REGISTRY
)
PREDICTIONS_TOTAL = Counter(
    'predictions_total', 
    'Total number of predictions made',
    ['result'],
    registry=REGISTRY
)
POSITIVE_PREDICTIONS_GAUGE = Gauge(
    'positive_predictions_count',
    'Number of customers likely to purchase insurance',
    registry=REGISTRY
)

# Middleware for tracking request metrics
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Record request latency and count
        duration = time.time() - start_time
        endpoint = request.url.path
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status_code=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
        
        return response

# Add middleware
app.add_middleware(PrometheusMiddleware)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# In-memory database (in production, you'd use a real database)
class CustomerDatabase:
    def __init__(self):
        self.customers = []
        self.data_file = "customer_data.json"
        self.load_data()
        
    def load_data(self):
        # Create the data directory if it doesn't exist
        #os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Load existing data if file exists
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.customers = json.load(f)
            except:
                self.customers = []
                
        # Update the positive predictions gauge
        positive_count = len([c for c in self.customers if c.get("prediction", False)])
        POSITIVE_PREDICTIONS_GAUGE.set(positive_count)
    
    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.customers, f)
    
    def add_customer(self, customer_data):
        self.customers.append(customer_data)
        
        # Update the positive predictions gauge
        positive_count = len([c for c in self.customers if c.get("prediction", False)])
        POSITIVE_PREDICTIONS_GAUGE.set(positive_count)
        
        self.save_data()
    
    def get_all_customers(self):
        return self.customers
    
    def get_positive_predictions(self):
        return [c for c in self.customers if c.get("prediction", False)]

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
    
    # Increment prediction counter
    if prediction:
        PREDICTIONS_TOTAL.labels(result="positive").inc()
    else:
        PREDICTIONS_TOTAL.labels(result="negative").inc()
    
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

# Expose metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)