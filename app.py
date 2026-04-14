import pandas as pd
import streamlit as st

# Load dataset
data = pd.read_csv("products.csv")

# Title
st.title("🌱 Sustainable Shopping Advisor")

# User Inputs
category = st.selectbox("Select Category", data["Category"].unique())
budget = st.slider("Select Budget", 100, 5000, 1000)

# Filter data
filtered = data[(data["Category"] == category) & (data["Price"] <= budget)]

# Show results
st.subheader("Recommended Products")
st.write(filtered)