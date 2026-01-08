
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# --- Helper Functions ---
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").price.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_by_review_score_df(df):
    # Logika Delivery vs Review
    df['delivery_diff_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    df['delivery_status'] = df['delivery_diff_days'].apply(lambda x: 'Late' if x > 0 else 'On Time')
    review_score = df.groupby('delivery_status')['review_score'].mean().reset_index()
    return review_score

# --- Load Data ---
all_df = pd.read_csv("main_data.csv") # Load data lokal
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])
all_df['order_delivered_customer_date'] = pd.to_datetime(all_df['order_delivered_customer_date'])
all_df['order_estimated_delivery_date'] = pd.to_datetime(all_df['order_estimated_delivery_date'])

all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

# --- Filter Sidebar ---
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan (Opsional)
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# --- Siapkan Dataframe ---
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score_df = create_by_review_score_df(main_df)

# --- Header ---
st.header('Dicoding E-Commerce Dashboard :sparkles:')

# --- 1. Daily Orders ---
st.subheader('Daily Orders')
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR') 
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_purchase_timestamp"], daily_orders_df["order_count"], marker='o', linewidth=2, color="#90CAF9")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# --- 2. Product Performance ---
st.subheader("Best Performing Product Category")
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="price", 
    y="product_category_name_english",
    data=sum_order_items_df.head(5),
    palette=colors,
    ax=ax
)
ax.set_ylabel(None)
ax.set_xlabel("Revenue", fontsize=30)
ax.set_title("Top 5 Categories by Revenue", loc="center", fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)
st.pyplot(fig)

# --- 3. Customer Satisfaction ---
st.subheader("Delivery Time vs Review Score")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='delivery_status', y='review_score', data=review_score_df, palette=['#e74c3c', '#2ecc71'], ax=ax)
ax.set_title('Impact of Late Delivery on Satisfaction', fontsize=20)
ax.bar_label(ax.containers[0], fmt='%.2f')
st.pyplot(fig)

st.caption('Copyright (c) Dicoding 2024')
