
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

sns.set(style='dark')

# --- 1. Load Data ---
@st.cache_data
def load_data():
    # Menggunakan path absolut agar aman di Streamlit Cloud
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'main_data.csv')

    # Load data
    df = pd.read_csv(csv_path)

    # Konversi kolom ke datetime
    datetime_cols = ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col])

    # Sorting
    df.sort_values(by="order_purchase_timestamp", inplace=True)
    return df

# Load semua data
all_df = load_data()

# --- 2. Sidebar Filter ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Data")

    # Ambil Min & Max Date
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()

    # Input Tanggal
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        st.error("Mohon pilih rentang tanggal yang valid.")
        st.stop()

# Filter Main DF
main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

# --- 3. Header Dashboard ---
st.title('Dicoding E-Commerce Dashboard :sparkles:')
st.markdown("""
Dashboard ini menganalisis dua hal utama:
1. **Produk Terlaris** berdasarkan total pendapatan.
2. **Kepuasan Pelanggan** berdasarkan ketepatan waktu pengiriman.
""")

# --- 4. Visualisasi 1: Produk Terlaris (Revenue) ---
st.subheader("1. Kategori Produk dengan Pendapatan Tertinggi")

# Hitung data (Gunakan semua item untuk Revenue agar akurat)
sum_order_items_df = main_df.groupby("product_category_name_english").price.sum().sort_values(ascending=False).head(5).reset_index()

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

if not sum_order_items_df.empty:
    sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df, palette=colors, ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel("Total Revenue", fontsize=12)
    ax.set_title("Top 5 Kategori Berdasarkan Revenue", loc="center", fontsize=15)
    ax.tick_params(axis='y', labelsize=12)
else:
    st.warning("Data tidak tersedia untuk rentang tanggal ini.")

st.pyplot(fig)

# --- 5. Visualisasi 2: Pengiriman vs Review ---
st.subheader("2. Dampak Keterlambatan Pengiriman terhadap Review")

# KUNCI PERUBAHAN LOGIKA DI SINI
plot_df = main_df.copy()

# 1. Filter status delivered DULU
plot_df = plot_df[plot_df['order_status'] == 'delivered']

# 2. Drop NA SEBELUM drop duplicates agar data bersih
plot_df.dropna(subset=['order_delivered_customer_date', 'order_estimated_delivery_date', 'review_score'], inplace=True)

# 3. Hitung selisih hari (Tanpa Normalize, agar On Time 4.21)
plot_df['delivery_diff_days'] = (plot_df['order_delivered_customer_date'] - plot_df['order_estimated_delivery_date']).dt.days
plot_df['delivery_status'] = plot_df['delivery_diff_days'].apply(lambda x: 'Late Delivery' if x > 0 else 'On Time Delivery')

# 4. Hapus Duplikat Order ID (Agar setiap order dihitung 1x)
# Ini yang membuat skor On Time menjadi ~4.21 dan Late menjadi ~2.26
unique_orders_df = plot_df.drop_duplicates(subset='order_id', keep='first')

# Hitung rata-rata
review_score_df = unique_orders_df.groupby('delivery_status')['review_score'].mean().reset_index()

# Plot
fig, ax = plt.subplots(figsize=(8, 5))

if not review_score_df.empty:
    sns.barplot(
        x='delivery_status',
        y='review_score',
        data=review_score_df,
        palette={'Late Delivery': '#e74c3c', 'On Time Delivery': '#2ecc71'},
        order=['On Time Delivery', 'Late Delivery'],
        ax=ax
    )

    ax.set_title('Rata-rata Skor Review (Per Order)', fontsize=15)
    ax.set_xlabel(None)
    ax.set_ylabel("Skor (1-5)", fontsize=12)
    ax.set_ylim(0, 5.5)

    # Label angka
    for container in ax.containers:
        # Jika hasilnya 2.26xxxx, %.2f akan membulatkan sesuai standar.
        # Jika data Anda persis, ini akan muncul 2.26.
        ax.bar_label(container, fmt='%.2f', padding=3)
else:
    st.warning("Data review tidak tersedia untuk rentang tanggal ini.")

st.pyplot(fig)

st.caption('Copyright (c) Dicoding 2026')
