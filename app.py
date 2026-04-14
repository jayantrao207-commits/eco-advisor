
import pandas as pd
import streamlit as st
import re
import random

st.set_page_config(page_title="Eco Advisor", layout="wide")

# Load CSV safely
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

# 🌟 GRID UI
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

# 🤖 SMART CHATBOT
st.markdown("---")
st.subheader("🤖 Smart Eco Chatbot")

user_input = st.text_input("Ask (e.g., tshirt, gift, living room decor)")

if user_input:
    query = user_input.lower()

    # 🧠 Intent detection
    intent = None

    if any(x in query for x in ["tshirt", "t shirt", "shirt"]):
        intent = "tshirt"

    elif "clothes" in query or "wear" in query:
        intent = "clothes"

    elif any(x in query for x in ["soap", "shampoo", "toothpaste"]):
        intent = "personal"

    elif any(x in query for x in ["cleaner", "detergent"]):
        intent = "home"

    elif "gift" in query:
        intent = "gift"

    elif any(x in query for x in ["living room", "decor", "decoration", "aesthetic", "home decor"]):
        intent = "decor"

    # 💰 price detection
    price_match = re.findall(r'\d+', query)
    max_price = int(price_match[0]) if price_match else None

    # 🎯 RESPONSE

    if intent == "tshirt":
        result_chat = data[
            (data["Category"] == "Clothes") &
            (data["Name_clean"].str.contains("shirt"))
        ]

    elif intent == "clothes":
        result_chat = data[data["Category"] == "Clothes"]

    elif intent == "personal":
        result_chat = data[data["Category"] == "Personal Care"]

    elif intent == "home":
        result_chat = data[data["Category"] == "Home Care"]

    # 🎁 SMART GIFT SYSTEM
    elif intent == "gift":

        if "shown_products" not in st.session_state:
            st.session_state.shown_products = set()

        gift_pool = data[
            (data["EcoScore"] >= 7) &
            (data["Price"] <= 1500)
        ]

        gift_pool = gift_pool[
            ~gift_pool["Name_clean"].str.contains("bag|brush")
        ]

        gift_pool = gift_pool[
            ~gift_pool["Name"].isin(st.session_state.shown_products)
        ]

        result_list = []

        for cat in gift_pool["Category"].unique():
            cat_items = gift_pool[gift_pool["Category"] == cat]

            if not cat_items.empty:
                item = cat_items.sample(1)
                result_list.append(item)

                st.session_state.shown_products.add(item.iloc[0]["Name"])

        if result_list:
            result_chat = pd.concat(result_list)
        else:
            st.warning("⚠️ Resetting suggestions...")
            st.session_state.shown_products = set()
            result_chat = gift_pool.sample(min(3, len(gift_pool)))

    # 🏠 DECOR INTENT (NEW 🔥)
    elif intent == "decor":

        result_chat = data[
            (data["Category"] == "Home Care") &
            (data["EcoScore"] >= 6)
        ]

        # remove useless items
        result_chat = result_chat[
            ~result_chat["Name_clean"].str.contains("detergent|cleaner|soap|bag")
        ]

        if result_chat.empty:
            st.info("✨ Here are some eco-friendly decor ideas:")

            decor_ideas = [
                "🌿 Indoor Plants",
                "🕯️ Scented Candles",
                "🪵 Wooden Decor Items",
                "🖼️ Wall Art / Paintings",
                "🪑 Minimalist Furniture",
                "💡 Warm Lighting Lamps"
            ]

            for idea in decor_ideas:
                st.markdown(f"- {idea}")

    else:
        result_chat = data[
            data["Name_clean"].str.contains(query, na=False)
        ]

    # apply price filter
    if 'result_chat' in locals() and result_chat is not None:
        if max_price:
            result_chat = result_chat[result_chat["Price"] <= max_price]

        if not result_chat.empty:
            result_chat = result_chat.sort_values(by="EcoScore", ascending=False)

            st.success("✅ Recommended for you:")

            for _, row in result_chat.head(4).iterrows():
                st.markdown(f"""
                **🛍️ {row['Name']}**  
                💰 ₹{row['Price']} | 🌱 Eco: {row['EcoScore']}
                """)
        else:
            st.warning("⚠️ No good match found")
