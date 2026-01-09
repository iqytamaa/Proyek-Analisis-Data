
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

# --- 2. Sidebar Filter (FIX KONSISTENSI TANGGAL) ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Data")
    
    # Ambil Min & Max Date
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()
    
    # Input Tanggal (Default: Ambil Semua Data)
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

# --- LOGIKA FILTER UTAMA ---
# Kita filter berdasarkan kolom 'date' saja (abaikan jam/menit)
# Ini kunci agar konsisten antara Lokal (WIB) dan Cloud (UTC)
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

# Hitung data
sum_order_items_df = main_df.groupby("product_category_name_english").price.sum().sort_values(ascending=False).head(5).reset_index()

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Cek data kosong
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

# Hitung selisih hari & status
# Gunakan .copy() agar tidak muncul warning SettingWithCopy
plot_df = main_df.copy()
plot_df['delivery_diff_days'] = (plot_df['order_delivered_customer_date'] - plot_df['order_estimated_delivery_date']).dt.days
plot_df['delivery_status'] = plot_df['delivery_diff_days'].apply(lambda x: 'Late Delivery' if x > 0 else 'On Time Delivery')

# Hitung rata-rata review
review_score_df = plot_df.groupby('delivery_status')['review_score'].mean().reset_index()

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

    ax.set_title('Rata-rata Skor Review', fontsize=15)
    ax.set_xlabel(None)
    ax.set_ylabel("Skor (1-5)", fontsize=12)
    ax.set_ylim(0, 5.5)

    # Label angka di atas batang (VISUALISASI JELAS)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', padding=3)
else:
    st.warning("Data review tidak tersedia untuk rentang tanggal ini.")

st.pyplot(fig)

st.caption('Copyright (c) Dicoding 2024')
