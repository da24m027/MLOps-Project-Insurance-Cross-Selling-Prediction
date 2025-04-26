import streamlit as st
import pandas as pd
from predict import predict_single
import time

# Initialize session state for customer data
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = pd.DataFrame(columns=['Name', 'Mobile', 'Prediction', 'Timestamp'])

st.title("Insurance Cross-Selling Prediction")

# Input form
with st.form("customer_form"):
    st.write("Customer Information")
    name = st.text_input("Name")
    mobile = st.text_input("Mobile Number")
    
    # Add all other features
    Age = st.number_input("Age", min_value=18, max_value=100)
    Gender = st.selectbox("Gender", ["Male", "Female"])
    Driving_License = st.selectbox("Driving License", [0, 1])
    Region_Code = st.number_input("Region_Code")
    Previously_Insured = st.selectbox("Previously Insured", [0, 1])
    Vehicle_Age = st.selectbox("Vehicle Age", ["< 1 Year", "1-2 Year", "> 2 Years"])
    Vehicle_Damage = st.selectbox("Vehicle Damage", ["Yes", "No"])
    Annual_Premium = st.number_input("Annual Premium")
    Policy_Sales_Channel = st.number_input("Policy Sales Channel")
    Vintage = st.number_input("Vintage")
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        # Prepare input data for model
        input_data = {
            "Gender": Gender,
            "Age": Age,
            "Driving_License": Driving_License,
            "Region_Code": Region_Code,
            "Previously_Insured": Previously_Insured,
            "Vehicle_Age": Vehicle_Age,
            "Vehicle_Damage": Vehicle_Damage,
            "Annual_Premium": Annual_Premium,
            "Policy_Sales_Channel": Policy_Sales_Channel,
            "Vintage": Vintage
        }
        
        # Make prediction
        prediction = predict_single(input_data)
        
        # Store customer data
        new_entry = pd.DataFrame([{
            'Name': name,
            'Mobile': mobile,
            'Prediction': prediction,
            'Timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        st.session_state.customer_data = pd.concat(
            [st.session_state.customer_data, new_entry], 
            ignore_index=True
        )

# Display positive predictions
st.subheader("Customers Likely to Purchase (Cross-Sell Opportunities)")
positive_cases = st.session_state.customer_data[
    st.session_state.customer_data['Prediction'] == True
]
st.dataframe(positive_cases[['Name', 'Mobile', 'Timestamp']])

# Optionally display all entries
if st.checkbox("Show all entries"):
    st.dataframe(st.session_state.customer_data)