
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os

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
    # Logika yang SAMA PERSIS dengan Notebook Revisi
    # Kita butuh data items juga untuk pembobotan yang tepat (agar angka match 2.26)
    
    # Hitung selisih hari
    df['delivery_diff_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    
    # Buat label kategori yang JELAS
    def categorize(days):
        if days > 0:
            return "Late Delivery"
        else:
            return "On Time Delivery"
    
    df['delivery_status'] = df['delivery_diff_days'].apply(categorize)
    
    # Hitung rata-rata
    review_score = df.groupby('delivery_status')['review_score'].mean().reset_index()
    return review_score

# --- Load Data dengan Caching & Path Fix ---
@st.cache_data
def load_data():
    # Fix Path untuk Streamlit Cloud
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'main_data.csv')
    
    df = pd.read_csv(csv_path)
    
    # Konversi ke Datetime (PENTING untuk Filter Tanggal)
    datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]
    for column in datetime_columns:
        df[column] = pd.to_datetime(df[column])
    
    # Sorting data agar filter tanggal bekerja dengan benar dari awal sampai akhir
    df.sort_values(by="order_purchase_timestamp", inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df

all_df = load_data()

# --- Filter Sidebar (Fix Konsistensi Tanggal) ---
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengunci default value ke min dan max data
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date] # Default: Select All
        )
    except ValueError:
        st.error("Mohon pilih rentang tanggal yang valid.")
        start_date = min_date
        end_date = max_date

# Filter Main DataFrame
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# --- Siapkan Dataframe untuk Visualisasi ---
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score_df = create_by_review_score_df(main_df)

# --- Header ---
st.header('Dicoding E-Commerce Dashboard :sparkles:')
st.markdown("Dashboard ini menampilkan performa penjualan dan analisis kepuasan pelanggan.")

# --- 1. Daily Orders (Metrik Utama) ---
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

# --- 2. Product Performance (Menjawab Pertanyaan 1) ---
st.subheader("Best Performing Product Category")
st.markdown("Grafik ini menjawab pertanyaan: **Kategori produk apa yang menghasilkan revenue terbesar?**")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Pastikan data ada sebelum di-plot
if not sum_order_items_df.empty:
    sns.barplot(
        x="price", 
        y="product_category_name_english",
        data=sum_order_items_df.head(5),
        palette=colors,
        ax=ax
    )
    ax.set_ylabel(None)
    ax.set_xlabel("Total Revenue (BRL)", fontsize=30)
    ax.set_title("Top 5 Categories by Revenue", loc="center", fontsize=50)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=30)
else:
    st.write("Data tidak tersedia untuk rentang waktu ini.")
    
st.pyplot(fig)

# --- 3. Customer Satisfaction (Menjawab Pertanyaan 2 - REVISI UTAMA) ---
st.subheader("Effect of Delivery Time on Customer Satisfaction")
st.markdown("Grafik ini menjawab pertanyaan: **Bagaimana keterlambatan pengiriman mempengaruhi skor ulasan pelanggan?**")

fig, ax = plt.subplots(figsize=(10, 6))

if not review_score_df.empty:
    # Plotting dengan warna yang kontras (Merah untuk telat, Hijau untuk on time)
    sns.barplot(
        x='delivery_status', 
        y='review_score', 
        data=review_score_df, 
        palette={'Late Delivery': '#e74c3c', 'On Time Delivery': '#2ecc71'}, # Warna eksplisit
        order=['On Time Delivery', 'Late Delivery'], # Mengatur urutan agar rapi
        ax=ax
    )
    
    # Judul dan Label yang JELAS (Sesuai feedback reviewer)
    ax.set_title('Average Review Score: On Time vs Late Delivery', fontsize=20)
    ax.set_xlabel("Delivery Status", fontsize=15)
    ax.set_ylabel("Average Review Score (1-5)", fontsize=15)
    ax.set_ylim(0, 5.5) # Memberi ruang untuk label angka
    
    # Menambahkan Angka di atas batang (Data Labels)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', fontsize=12, padding=3)
else:
    st.write("Data review tidak tersedia untuk rentang waktu ini.")

st.pyplot(fig)

st.caption('Copyright (c) Dicoding 2024')
