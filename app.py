import pandas as pd
import streamlit as st
import re

# Page config
st.set_page_config(page_title="Eco Advisor", layout="wide")

# Load data
data = pd.read_csv("products.csv")

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

# Filtering logic
if search:
    filtered = data[data["Name"].str.contains(search, case=False, na=False)]
    filtered = filtered[filtered["Price"] <= budget]
else:
    filtered = data[(data["Category"] == category) & (data["Price"] <= budget)]

if eco_filter:
    filtered = filtered[filtered["EcoScore"] >= 7]

if organic_filter:
    filtered = filtered[filtered["Organic"] == "Yes"]

# Score system
filtered["Score"] = (filtered["EcoScore"] * 0.7) + ((5000 - filtered["Price"]) * 0.3 / 5000)
result = filtered.sort_values(by="Score", ascending=False)

# Display products
st.subheader("🌟 Top Recommendations")
for i, row in result.head(10).iterrows():
    st.markdown(f"""
    **🛍️ {row['Name']}**  
    💰 ₹{row['Price']} | 🌱 Eco Score: {row['EcoScore']}  
    ⭐ Rating: {row.get('Rating', 'N/A')}
    """)

# Charts
st.markdown("---")
st.subheader("📊 Insights")
st.bar_chart(data["EcoScore"])
st.bar_chart(data["Category"].value_counts())

# 🤖 ULTRA SMART CHATBOT
st.markdown("---")
st.subheader("🤖 Smart Eco Chatbot")

user_input = st.text_input("Ask (e.g., tshirt, eco soap under 200, gift ideas)")

if user_input:
    query = user_input.lower()

    # Friendly replies
    if any(x in query for x in ["hi", "hello", "hey"]):
        st.success("👋 Hello! Ask me for eco-friendly products 🌱")

    elif "thank" in query:
        st.success("😊 You're welcome!")

    else:
        filtered_chat = data.copy()

        # Price detection
        price_match = re.findall(r'\d+', query)
        if price_match:
            max_price = int(price_match[0])
            filtered_chat = filtered_chat[filtered_chat["Price"] <= max_price]

        # Eco filters
        if "eco" in query or "sustainable" in query:
            filtered_chat = filtered_chat[filtered_chat["EcoScore"] >= 7]

        if "organic" in query:
            filtered_chat = filtered_chat[filtered_chat["Organic"] == "Yes"]

        # 🔥 SMART CATEGORY HANDLING
        if any(x in query for x in ["tshirt", "t shirt", "shirt", "tee"]):
            filtered_chat = filtered_chat[filtered_chat["Category"] == "Clothes"]

        elif any(x in query for x in ["shoes", "shoe", "sneakers"]):
            filtered_chat = filtered_chat[filtered_chat["Category"] == "Clothes"]

        elif any(x in query for x in ["soap", "body wash", "cleanser"]):
            filtered_chat = filtered_chat[filtered_chat["Category"] == "Personal Care"]

        elif any(x in query for x in ["cleaner", "detergent", "dish"]):
            filtered_chat = filtered_chat[filtered_chat["Category"] == "Home Care"]

        # 🎁 GIFT LOGIC
        if "gift" in query:
            gift_items = data[
                (data["EcoScore"] >= 7) &
                (data["Price"] <= 1000)
            ].sort_values(by="EcoScore", ascending=False)

            st.success("🎁 Best Eco-Friendly Gift Ideas:")

            for i, row in gift_items.head(3).iterrows():
                st.markdown(f"""
                **🎁 {row['Name']}**  
                💰 ₹{row['Price']} | 🌱 Eco: {row['EcoScore']}
                """)
        else:
            # 🔍 Match by name
            matched = filtered_chat[
                filtered_chat["Name"].str.contains(query, case=False, na=False)
            ]

            # ✅ FOUND
            if not matched.empty:
                matched = matched.sort_values(by="EcoScore", ascending=False)

                st.success("✅ Best matches:")

                for i, row in matched.head(3).iterrows():
                    st.markdown(f"""
                    **🛍️ {row['Name']}**  
                    💰 ₹{row['Price']} | 🌱 Eco: {row['EcoScore']}
                    """)

            # ❌ NOT FOUND
            else:
                st.error("❌ Product not found")

                fallback = filtered_chat.sort_values(by="EcoScore", ascending=False)

                st.info("👉 Showing similar eco-friendly products:")

                for i, row in fallback.head(3).iterrows():
                    st.markdown(f"""
                    **🛍️ {row['Name']}**  
                    💰 ₹{row['Price']} | 🌱 Eco: {row['EcoScore']}
                    """)

# Footer
st.markdown("---")
st.caption("🌍 AI-Based Sustainable Shopping Advisor")
