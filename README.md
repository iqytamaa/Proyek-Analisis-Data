%%writefile submission/README.md

# Proyek Analisis Data: E-Commerce Public Dataset

Proyek ini bertujuan untuk menganalisis data e-commerce dari Olist (Brazil) untuk mengungkap wawasan bisnis seputar performa produk dan kepuasan pelanggan, serta menyajikannya dalam bentuk dashboard interaktif.

## 📂 Struktur Proyek

- **dashboard/** : Berisi file utama `dashboard.py` dan data hasil olahan `main_data.csv`.
- **data/** : Berisi dataset mentah (raw data) dalam format .csv.
- **notebook.ipynb** : File Jupyter Notebook yang mencakup seluruh proses analisis (Data Wrangling, EDA, Visualization).
- **README.md** : Dokumentasi proyek (file ini).
- **requirements.txt** : Daftar library Python yang diperlukan.

## 🔧 Cara Menjalankan Dashboard

### 1. Setup Environment

Pastikan Python sudah terinstal di komputer Anda.

**Cara 1: Menggunakan Anaconda**

```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt

**Cara 2: Menggunakan Terminal/Shell**
pip install -r requirements.txt

**Menjalankan Streamlit**
streamlit run dashboard/dashboard.py
```
