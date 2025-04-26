import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import yaml
import os
import time
import psutil
from datetime import datetime

def load_config():
    with open("config/params.yaml", "r") as f:
        return yaml.safe_load(f)

def log_system_metrics(run):
    """Log system metrics to MLflow"""
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    mlflow.log_metric("cpu_usage", cpu_percent)
    mlflow.log_metric("memory_usage", memory_percent)

def main():
    config = load_config()
    
    # Load data
    train_df = pd.read_csv("data/processed/train_processed.csv")
    val_df = pd.read_csv("data/processed/val_processed.csv")
    
    # Separate features and target
    X_train = train_df.drop(columns=[config['base']['target_col']])
    y_train = train_df[config['base']['target_col']]
    X_val = val_df.drop(columns=[config['base']['target_col']])
    y_val = val_df[config['base']['target_col']]
    
    # MLflow setup
    mlflow.set_tracking_uri(config['mlflow']['tracking_uri'])
    mlflow.set_experiment(config['mlflow']['experiment_name'])
    
    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_params(config['model_params'])
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=config['model_params']['n_estimators'],
            max_depth=config['model_params']['max_depth'],
            random_state=config['base']['random_state']
        )
        
        start_time = time.time()
        model.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        # Predict and evaluate
        y_pred = model.predict(X_val)
        
        accuracy = accuracy_score(y_val, y_pred)
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("training_time", training_time)
        
        # Log system metrics periodically during training
        for _ in range(5):  # Sample 5 times during training
            log_system_metrics(run)
            time.sleep(1)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Save model locally
        os.makedirs("models", exist_ok=True)
        mlflow.sklearn.save_model(model, "models/latest_model")

if __name__ == "__main__":
    main()