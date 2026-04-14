
import pandas as pd
import streamlit as st
import re

# Page config
st.set_page_config(page_title="Eco Advisor", layout="wide")

# Load data
data = pd.read_csv("products.csv")

# Header
st.title("🌱 Sustainable Shopping Advisor")
st.markdown("### Smart Eco-Friendly Product Recommendations 🌍")

# Sidebar
st.sidebar.header("🔍 Smart Filters")

category = st.sidebar.selectbox("Category", data["Category"].unique())
budget = st.sidebar.slider("Budget (₹)", 100, 5000, 1000)
search = st.sidebar.text_input("Search Product")

eco_filter = st.sidebar.checkbox("High Eco Score (>=7)")
organic_filter = st.sidebar.checkbox("Only Organic")

# Filtering
if search:
    filtered = data[data["Name"].str.contains(search, case=False, na=False)]
    filtered = filtered[filtered["Price"] <= budget]
else:
    filtered = data[(data["Category"] == category) & (data["Price"] <= budget)]

if eco_filter:
    filtered = filtered[filtered["EcoScore"] >= 7]

if organic_filter:
    filtered = filtered[filtered["Organic"] == "Yes"]

# Helper functions
def reason(row):
    r = []
    if row["EcoScore"] >= 8:
        r.append("🌱 Highly Sustainable")
    if row["Organic"] == "Yes":
        r.append("🌿 Organic")
    if row["Recyclable"] == "Yes":
        r.append("♻️ Recyclable")
    return " | ".join(r)

def eco_badge(score):
    if score >= 8:
        return "🟢 Eco Friendly"
    elif score >= 5:
        return "🟡 Moderate"
    else:
        return "🔴 Not Eco"

# Score system
filtered["Score"] = (filtered["EcoScore"] * 0.7) + ((5000 - filtered["Price"]) * 0.3 / 5000)
result = filtered.sort_values(by="Score", ascending=False)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Products", len(filtered))
col2.metric("Avg Eco Score", round(filtered["EcoScore"].mean(), 1) if not filtered.empty else 0)
col3.metric("Best Score", round(result["Score"].max(), 2) if not result.empty else 0)

st.markdown("---")

# Product UI
st.subheader("🌟 Top Recommendations")
cols = st.columns(3)

for idx, (_, row) in enumerate(result.head(9).iterrows()):
    with cols[idx % 3]:
        st.markdown(f"""
        <div style="border-radius:20px;padding:20px;margin:10px 0;
        box-shadow:0 6px 15px rgba(0,0,0,0.1);background-color:#ffffff;">
        <h4>🛍️ {row['Name']}</h4>
        <p><b>{eco_badge(row['EcoScore'])}</b></p>
        <p>⭐ Rating: {row.get('Rating', 'N/A')}</p>
        <p>💰 ₹{row['Price']}</p>
        <p>🌱 Eco Score: {row['EcoScore']}</p>
        <p>✅ {reason(row)}</p>
        </div>
        """, unsafe_allow_html=True)

# Analytics
st.markdown("---")
st.subheader("📊 Insights")

col1, col2 = st.columns(2)

with col1:
    st.write("Eco Score Distribution")
    st.bar_chart(data["EcoScore"])

with col2:
    st.write("Category Distribution")
    st.bar_chart(data["Category"].value_counts())

# 🤖 SMART CHATBOT
st.markdown("---")
st.subheader("🤖 Smart Eco Chatbot")

user_input = st.text_input("Ask (e.g., organic shampoo under 300)")

if user_input:
    query = user_input.lower()
    words = query.split()

    # Conversation
    if any(x in query for x in ["hi", "hello", "hey"]):
        st.success("👋 Hello! Ask me for eco-friendly product suggestions 🌱")

    elif "thank" in query:
        st.success("😊 You're welcome!")

    else:
        filtered_chat = data.copy()

        # Price
        price_match = re.findall(r'\d+', query)
        if price_match:
            max_price = int(price_match[0])
            filtered_chat = filtered_chat[filtered_chat["Price"] <= max_price]

        # Intent
        if "organic" in query:
            filtered_chat = filtered_chat[filtered_chat["Organic"] == "Yes"]

        if "eco" in query or "sustainable" in query:
            filtered_chat = filtered_chat[filtered_chat["EcoScore"] >= 7]

        # Category detect
        detected_category = None
        for cat in data["Category"].unique():
            if cat.lower() in query:
                filtered_chat = filtered_chat[filtered_chat["Category"] == cat]
                detected_category = cat

        # Keyword match
        matched = pd.DataFrame()
        for word in words:
            temp = filtered_chat[
                filtered_chat["Name"].str.contains(word, case=False, na=False)
            ]
            matched = pd.concat([matched, temp])

        matched = matched.drop_duplicates()

        # ✅ FOUND
        if not matched.empty:
            matched["Score"] = (matched["EcoScore"] * 0.7) + ((5000 - matched["Price"]) * 0.3 / 5000)
            matched = matched.sort_values(by="Score", ascending=False)

            st.success("✅ Here are the best matches:")

            for i, row in matched.head(3).iterrows():
                st.markdown(f"""
                **🛍️ {row['Name']}**  
                💰 ₹{row['Price']} | 🌱 Eco: {row['EcoScore']}
                """)

        # ❌ NOT FOUND (FIXED)
        else:
            st.error("❌ This product is not available right now.")

            # 🔥 SMART CATEGORY MAPPING
            category_map = {
                "shoes": "Clothes",
                "shirt": "Clothes",
                "tshirt": "Clothes",
                "jeans": "Clothes",
                "soap": "Personal Care",
                "shampoo": "Personal Care",
                "toothpaste": "Personal Care",
                "cleaner": "Home Care",
                "detergent": "Home Care",
                "dish": "Home Care"
            }

            detected_fallback_category = None

            for word in words:
                if word in category_map:
                    detected_fallback_category = category_map[word]

            if detected_fallback_category:
                fallback = data[data["Category"] == detected_fallback_category]
            else:
                fallback = data.copy()

            fallback = fallback.sort_values(by="EcoScore", ascending=False)

            st.info("👉 Showing similar eco-friendly alternatives:")

            for i, row in fallback.head(3).iterrows():
                st.markdown(f"""
                **🛍️ {row['Name']}**  
                💰 ₹{row['Price']} | 🌱 Eco: {row['EcoScore']}
                """)

# Footer
st.markdown("---")
st.caption("🌍 Built for Sustainable Future | AI-based Eco Recommendation System")
