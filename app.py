import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Eco Advisor", layout="wide")

# Load data safely
try:
    data = pd.read_csv("products.csv")
except:
    data = pd.read_csv("products.csv", on_bad_lines='skip')

# Clean names
data["Name_clean"] = data["Name"].str.lower().str.replace("-", " ")

# Title
st.title("🌱 Sustainable Shopping Advisor")
st.markdown("### Smart Eco-Friendly Product Recommendations 🌍")

# Sidebar
st.sidebar.header("🔍 Filters")

category = st.sidebar.selectbox("Category", data["Category"].unique())
budget = st.sidebar.slider("Budget (₹)", 100, 5000, 1000)
search = st.sidebar.text_input("Search Product")

eco_filter = st.sidebar.checkbox("High Eco Score (>=7)")
organic_filter = st.sidebar.checkbox("Only Organic")

# Filtering
if search:
    filtered = data[data["Name_clean"].str.contains(search.lower(), na=False)]
    filtered = filtered[filtered["Price"] <= budget]
else:
    filtered = data[(data["Category"] == category) & (data["Price"] <= budget)]

if eco_filter:
    filtered = filtered[filtered["EcoScore"] >= 7]

if organic_filter:
    filtered = filtered[filtered["Organic"] == "Yes"]

# Score
filtered["Score"] = (filtered["EcoScore"] * 0.7) + ((5000 - filtered["Price"]) * 0.3 / 5000)
result = filtered.sort_values(by="Score", ascending=False)

# 🔥 GRID UI
st.subheader("🌟 Top Recommendations")
cols = st.columns(3)

for i, (_, row) in enumerate(result.head(9).iterrows()):
    with cols[i % 3]:
        st.markdown(f"""
        ### 🛍️ {row['Name']}
        💰 ₹{row['Price']}  
        🌱 Eco: {row['EcoScore']}  
        ⭐ {row.get('Rating', 'N/A')}
        """)

# Charts
st.markdown("---")
st.subheader("📊 Insights")
st.bar_chart(data["EcoScore"])
st.bar_chart(data["Category"].value_counts())

# 🤖 CHATBOT
st.markdown("---")
st.subheader("🤖 Smart Eco Chatbot")

user_input = st.text_input("Ask (e.g., tshirt, soap, gift)")

if user_input:
    query = user_input.lower().replace("-", " ")

    # greetings
    if any(x in query for x in ["hi", "hello", "hey"]):
        st.success("👋 Hello! Ask me for eco-friendly products")

    elif "thank" in query:
        st.success("😊 You're welcome!")

    else:
        # 🎯 EXACT TSHIRT LOGIC
        if any(x in query for x in ["tshirt", "t shirt", "shirt", "tee"]):
            matched = data[
                (data["Category"] == "Clothes") &
                (data["Name_clean"].str.contains("shirt"))
            ]

        # 🧼 Personal care
        elif any(x in query for x in ["soap", "shampoo", "toothpaste"]):
            matched = data[data["Category"] == "Personal Care"]

        # 🏠 Home
        elif any(x in query for x in ["cleaner", "detergent"]):
            matched = data[data["Category"] == "Home Care"]

        # 🎁 Gift
        elif "gift" in query:
            matched = data[
                (data["EcoScore"] >= 7) &
                (data["Price"] <= 1000)
            ]

        # 🔍 General search
        else:
            matched = data[
                data["Name_clean"].str.contains(query, na=False)
            ]

        # ❗ If nothing found
        if matched.empty:
            st.error("❌ No exact product found in dataset")
        else:
            matched = matched.sort_values(by="EcoScore", ascending=False)

            st.success("✅ Results:")

            for _, row in matched.head(3).iterrows():
                st.markdown(f"""
                **🛍️ {row['Name']}**  
                💰 ₹{row['Price']} | 🌱 Eco: {row['EcoScore']}
                """)

# Footer
st.markdown("---")
st.caption("🌍 AI-Based Sustainable Shopping Advisor")

