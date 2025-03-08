import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def analyze_freight_vs_rating(df, cutoff_date):
    cutoff_date = pd.to_datetime(cutoff_date)
    df_filtered = df[df["order_purchase_timestamp"] >= cutoff_date]   
    freight_rating_df = df_filtered.groupby(by="review_score").agg({
        "freight_value": ["mean", "median", "count"]
    }).reset_index()   
    freight_rating_df.columns = ["review_score", "freight_value_mean", "freight_value_median", "count"]
    return freight_rating_df

def analyze_delivery_delay_vs_rating(df, cutoff_date):
    cutoff_date = pd.to_datetime(cutoff_date)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df_filtered = df[df["order_purchase_timestamp"] >= cutoff_date]
    if "delivery_status" not in df_filtered.columns:
        raise ValueError("Kolom 'delivery_status' tidak ditemukan dalam dataframe!")
    if "review_score" in df_filtered.columns:
        delay_df = df_filtered.groupby("delivery_status")["review_score"].mean().reset_index()
        delay_df.rename(columns={"review_score": "avg_review_score"}, inplace=True)
    else:
        raise ValueError("Kolom 'review_score' tidak ditemukan dalam dataframe!")
    return delay_df


def analyze_high_value_payment_methods(df, cutoff_date):
    cutoff_date = pd.to_datetime(cutoff_date)
    df_filtered = df[df["order_purchase_timestamp"] >= cutoff_date]
    high_value_threshold = df_filtered['payment_value'].quantile(0.75)
    high_value_orders = df_filtered[df_filtered['payment_value'] > high_value_threshold]
    return high_value_orders['payment_type'].value_counts()

def analyze_geographical_distribution(df, cutoff_date):
    cutoff_date = pd.to_datetime(cutoff_date)
    df_filtered = df[df["order_purchase_timestamp"] >= cutoff_date]
    customer_distribution = df_filtered['customer_state'].value_counts()
    seller_distribution = df_filtered['seller_state'].value_counts()
    return customer_distribution, seller_distribution

all_df = pd.read_csv("data/all_data.csv")

datetime_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp"
]

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column], errors='coerce')

all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

def filter_date(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return df[(df["order_purchase_timestamp"] >= start_date) & 
              (df["order_purchase_timestamp"] <= end_date)]

st.title("Analisis Data E-Commerce")

# Sidebar untuk filter tanggal
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("Dashboard E-Commerce")
    st.markdown("---")
    st.subheader("Filter Rentang Waktu")
    date_range = st.date_input(
    label="Rentang Waktu",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date],
    key="date_range"
)

# Validasi apakah pengguna memilih rentang tanggal yang benar
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.error("Harap pilih rentang tanggal yang valid!")
    st.stop()  # Hentikan eksekusi jika rentang tanggal tidak valid

filtered_df = filter_date(all_df, start_date, end_date)

st.subheader("Pengaruh Biaya Pengiriman terhadap Rating")
freight_df = analyze_freight_vs_rating(filtered_df, start_date)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=freight_df, x="review_score", y="freight_value_mean", palette="viridis", ax=ax)
ax.set_xlabel("Review Score")
ax.set_ylabel("Rata-rata Biaya Pengiriman")
ax.set_title("Hubungan Biaya Pengiriman dengan Rating")
st.pyplot(fig)

st.subheader("Pengaruh Keterlambatan Pengiriman terhadap Rating")
delay_df = analyze_delivery_delay_vs_rating(filtered_df, start_date)
fig, ax = plt.subplots(figsize=(8, 5))
colors = ["#72BCD4", "#D3D3D3"]
sns.barplot(data=delay_df, x="delivery_status", y="avg_review_score", palette=colors, ax=ax)
ax.set_xlabel("Status Pengiriman")
ax.set_ylabel("Rata-rata Review Score")
ax.set_title("Pengaruh Keterlambatan terhadap Rating")
st.pyplot(fig)

st.subheader("Metode Pembayaran untuk Transaksi Bernilai Tinggi")
payment_counts = analyze_high_value_payment_methods(filtered_df, start_date)
fig, ax = plt.subplots(figsize=(8, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(y=payment_counts.index, x=payment_counts.values, palette="viridis", ax=ax)
ax.set_xlabel("Jumlah Pembayaran")
ax.set_ylabel("Metode Pembayaran")
ax.set_title("Metode Pembayaran untuk Transaksi Bernilai Tinggi")
st.pyplot(fig)

st.subheader("Distribusi Lokasi Pelanggan dan Penjual")
customer_dist, seller_dist = analyze_geographical_distribution(filtered_df, start_date)
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
sns.barplot(y=customer_dist.index, x=customer_dist.values, palette="viridis", ax=ax[0])
ax[0].set_xlabel("Jumlah Pelanggan")
ax[0].set_ylabel(None)
ax[0].set_title("Distribusi Lokasi Pelanggan")

sns.barplot(y=seller_dist.index, x=seller_dist.values, palette="viridis", ax=ax[1])
ax[1].set_xlabel("Jumlah Penjual")
ax[1].set_ylabel(None)
ax[1].set_title("Distribusi Lokasi Penjual")
plt.suptitle("Distribusi Lokasi Pelanggan dan Penjual", fontsize=20)
st.pyplot(fig)