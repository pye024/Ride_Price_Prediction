import streamlit as st
import pandas as pd
import joblib
from math import radians, cos, sin, asin, sqrt
import random

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def estimate_duration(distance_km, speed_kmh=40):
    return (distance_km / speed_kmh) * 3600

ADDRESSES = {
    "Mumbai Airport": (19.0896, 72.8656),
    "Gateway of India, Mumbai": (18.9220, 72.8347),
    "Bandra-Worli Sea Link": (19.0229, 72.8177),
    "Chhatrapati Shivaji Terminus, Mumbai": (18.9402, 72.8356),
    "Marine Drive, Mumbai": (18.9432, 72.8238)
}

model = joblib.load("models/lightgbm.pkl")

st.title("Ride Fare Prediction (India)")

col1, col2 = st.columns(2)
with col1:
    Pickup_Location = st.selectbox("Pickup Location", options=list(ADDRESSES.keys()))
with col2:
    Dropoff_Location = st.selectbox("Dropoff Location", options=list(ADDRESSES.keys()))

pickup_coords = ADDRESSES[Pickup_Location]
dropoff_coords = ADDRESSES[Dropoff_Location]

Vehicle_Type = st.selectbox("Vehicle Type", ["Car", "Van"])
max_passengers = 4 if Vehicle_Type == "Car" else 9

col3, col4 = st.columns(2)
with col3:
    NUM_OF_PASSENGERS = st.slider("Number of Passengers", min_value=1, max_value=max_passengers, step=1, value=1)
with col4:
    TIP = st.slider("Tip (INR)", 0.0, max_value=1000.0, step=10.0)

SURGE_APPLIED = int(st.toggle("Surge Pricing"))

if st.button("Predict"):
    DISTANCE_TRAVELED = haversine(pickup_coords, dropoff_coords)
    TRIP_DURATION = estimate_duration(DISTANCE_TRAVELED)
    MISCELLANEOUS_FEES = round(random.uniform(2.5, 3.5), 2)

    col_distance, col_eta = st.columns(2)
    with col_distance:
        st.metric("Distance (km)", f"{DISTANCE_TRAVELED:.2f}")
    with col_eta:
        st.metric("ETA (minutes)", f"{TRIP_DURATION / 60:.1f}")

    features = [[TRIP_DURATION, DISTANCE_TRAVELED, NUM_OF_PASSENGERS, TIP, MISCELLANEOUS_FEES, SURGE_APPLIED]]
    predict = model.predict(features)

    st.success(f"The Total Fare for this Ride is: ₹{predict[0]:.2f}")
    st.info(f"Miscellaneous fees applied: ₹{MISCELLANEOUS_FEES}")
