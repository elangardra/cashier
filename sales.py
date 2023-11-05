import streamlit as st
from firebase_admin import db
from firebase_init import firebase_app
import pandas as pd
from datetime import datetime

# Streamlit UI untuk Pelanggan
st.title("Pilih Produk")

# Tampilkan kategori dan produk yang tersedia
kategori_produk = db.reference('products').get()
if kategori_produk:
    kategori_terpilih = st.selectbox("Pilih Kategori", list(kategori_produk.keys()))

    if kategori_terpilih:
        st.header(f"Produk dalam Kategori {kategori_terpilih}")
        produk_dalam_kategori = kategori_produk[kategori_terpilih]
        for nama_produk, info_produk in produk_dalam_kategori.items():
            st.write(f"**{nama_produk}**")
            st.write(f"Harga: Rp {info_produk['Harga']:.0f}")
            st.write(f"Stok Tersedia: {info_produk['Stok']}")

            jumlah = st.number_input("Jumlah Pembelian", min_value=0, max_value=info_produk['Stok'], key=nama_produk)

            if jumlah > 0:
                if st.button(f"Beli {jumlah} {nama_produk}"):
                    # Kurangi stok setelah pembelian
                    stok_baru = info_produk['Stok'] - jumlah
                    referensi_produk = db.reference(f'products/{kategori_terpilih}/{nama_produk}')
                    referensi_produk.update({'Stok': stok_baru})

                    # Hitung total harga pembelian
                    total_harga = info_produk['Harga'] * jumlah

                    # Simpan informasi pembelian ke Firebase untuk membuat faktur
                    referensi_pembelian = db.reference('purchases')
                    data_pembelian = {
                        'Invoice': len(referensi_pembelian.get()) + 1 if referensi_pembelian.get() else 1,
                        'Tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Kategori': kategori_terpilih,
                        'Nama Produk': nama_produk,
                        'Jumlah': jumlah,
                        'Harga': info_produk['Harga'],
                        'Total Harga': total_harga
                    }
                    referensi_pembelian.push(data_pembelian)

                    st.success(f"Anda telah membeli {jumlah} {nama_produk}.")

# Tampilkan faktur
st.header("Faktur Pembelian")
data_faktur = db.reference('purchases').get()
if data_faktur:
    faktur_df = pd.DataFrame(data_faktur).T
    st.write("Faktur Anda:")
    st.dataframe(faktur_df)
else:
    st.warning("Belum ada pembelian yang dilakukan.")
