import streamlit as st
from firebase_admin import db
from firebase_init import firebase_app
import pandas as pd
import plotly.express as px

# Format number as Indonesian Rupiah (IDR)
def format_currency(number):
    return f'Rp {number:,.0f}'

# Streamlit UI untuk Admin Panel
st.title("Panel Admin")

# Formulir input untuk menambahkan produk
kategori = st.text_input("Kategori")
nama_produk = st.text_input("Nama Produk")
harga = st.number_input("Harga (dalam IDR)", value=0.0)
stok = st.number_input("Stok", value=0)

if st.button("Tambahkan Produk"):
    # Validasi input dan tambahkan data ke Firebase
    if kategori and nama_produk and harga >= 0 and stok >= 0:
        ref = db.reference(f'products/{kategori}/{nama_produk}')
        ref.set({
            'Harga': harga,
            'Stok': stok
        })
        st.success("Produk berhasil ditambahkan")
    else:
        st.error("Input tidak valid. Harap periksa nilai input.")

# Tampilkan daftar pembelian sebagai faktur
st.header("Faktur Pembelian")
data_faktur = db.reference('purchases').get()
if data_faktur:
    faktur_df = pd.DataFrame(data_faktur).T
    st.write("Daftar Pembelian:")
    st.dataframe(faktur_df)
else:
    st.warning("Belum ada pembelian yang dilakukan.")

# Buat dasbor penjualan menggunakan Plotly Express
st.header("Dasbor Penjualan")

if data_faktur:
    faktur_df['Tanggal'] = pd.to_datetime(faktur_df['Tanggal'])

    # Buat grafik garis pendapatan harian
    pendapatan_harian = faktur_df.groupby(faktur_df['Tanggal'].dt.date)['Total Harga'].sum().reset_index()
    pendapatan_harian['Total Harga'] = pendapatan_harian['Total Harga'].apply(format_currency)
    fig1 = px.line(pendapatan_harian, x='Tanggal', y='Total Harga', title='Pendapatan Harian')

    # Buat grafik batang total produk terjual per produk
    produk_terjual = faktur_df.groupby('Nama Produk')['Jumlah'].sum().reset_index()
    fig2 = px.bar(produk_terjual, x='Nama Produk', y='Jumlah', title='Total Produk Terjual per Produk')

    # Buat grafik batang total pendapatan per bulan
    faktur_df['BulanTahun'] = faktur_df['Tanggal'].dt.strftime('%Y-%m')
    pendapatan_bulanan = faktur_df.groupby('BulanTahun')['Total Harga'].sum().reset_index()
    pendapatan_bulanan['Total Harga'] = pendapatan_bulanan['Total Harga'].apply(format_currency)
    fig3 = px.bar(pendapatan_bulanan, x='BulanTahun', y='Total Harga', title='Pendapatan Bulanan')

    # Temukan produk dengan jumlah pembelian terbanyak
    produk_terbanyak_dibeli = produk_terjual.sort_values(by='Jumlah', ascending=False).iloc[0]['Nama Produk']

    # Tampilkan grafik dan produk dengan jumlah pembelian terbanyak
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
    st.write(f"Produk yang paling banyak dibeli: {produk_terbanyak_dibeli}")
else:
    st.warning("Tidak ada data pembelian yang tersedia.")
