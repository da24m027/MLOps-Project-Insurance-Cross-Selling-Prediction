import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import yaml
import os

def load_config():
    with open("config/params.yaml", "r") as f:
        params = yaml.safe_load(f)
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return params, config

def clean_column_names(df):
    """Clean and standardize column names"""
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '')
    return df

def preprocess_data(df, params):
    """Main preprocessing function"""
    
    # 1. Clean column names
    df = clean_column_names(df)
    
    # 2. Map Vehicle_Age to numerical values
    df['Vehicle_Age'] = df['Vehicle_Age'].map(params['preprocessing']['vehicle_age_mapping'])
    
    # 3. Convert categorical features
    df['Vehicle_Damage'] = df['Vehicle_Damage'].map({'Yes': 1, 'No': 0})
    df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})
    
    # 4. Create age groups
    age_bins = params['feature_engineering']['age_bins']
    age_labels = params['feature_engineering']['age_labels']
    df['Age_Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)
    
    # 5. Create premium groups
    premium_bins = params['feature_engineering']['premium_bins']
    premium_labels = params['feature_engineering']['premium_labels']
    df['Premium_Group'] = pd.cut(df['Annual_Premium'], bins=premium_bins, labels=premium_labels, right=False)
    
    # 6. Drop unnecessary columns
    df = df.drop(columns=params['preprocessing']['features_to_drop'], errors='ignore')
    
    return df

def main():
    params, config = load_config()
    
    # Load data
    train_df = pd.read_csv(config['data_paths']['raw']['train'])
    test_df = pd.read_csv(config['data_paths']['raw']['test'])
    
    # Preprocess data
    train_df = preprocess_data(train_df, params)
    test_df = preprocess_data(test_df, params)
    
    # Split train into train and validation
    train_data, val_data = train_test_split(
        train_df, 
        test_size=params['data_split']['val_size'],
        random_state=params['base']['random_state'],
        stratify=train_df[params['base']['target_col']]
    )
    
    # Save processed data
    os.makedirs("data/processed", exist_ok=True)
    train_data.to_csv(config['data_paths']['processed']['train'], index=False)
    val_data.to_csv(config['data_paths']['processed']['val'], index=False)
    test_df.to_csv(config['data_paths']['processed']['test'], index=False)

if __name__ == "__main__":
    main()