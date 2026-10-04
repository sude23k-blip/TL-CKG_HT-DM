import pandas as pd
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Dashboard Analisis CKG Kemenkes", page_icon="🏥", layout="wide"
)

st.title("🏥 Dashboard Analisis Data Cek Kesehatan Gratis (CKG)")
st.write(
    "Aplikasi web interaktif untuk memonitoring data agregat CKG (Hipertensi, Diabetes, Dislipidemia, dan Kesehatan Gigi)."
)

# 1. Upload File Excel ASIK Kemenkes
uploaded_file = st.file_uploader(
    "Upload file Excel laporan CKG Kemenkes (.xlsx)", type=["xlsx", "csv"]
)

if uploaded_file is not None:
  # Membaca file
  try:
    df = pd.read_excel(uploaded_file, sheet_name="Data Agregat CKG")
  except:
    df = pd.read_excel(uploaded_file)  # Kalau sheet name berbeda

  st.success("✅ Data berhasil dimuat!")

  # Menampilkan ringkasan ukuran data
  st.info(
      f"Total Baris Data Faskes: {df.shape[0]} | Total Kolom Variabel:"
      f" {df.shape[1]}"
  )

  # 2. Filter Interaktif Berdasarkan Wilayah (Kabupaten/Kota)
  if "Nama Kabupaten Kota" in df.columns:
    st.subheader("🔍 Filter Wilayah")
    kab_list = ["Semua Kabupaten/Kota"] + list(df["Nama Kabupaten Kota"].unique())
    pilih_kab = st.selectbox("Pilih Kabupaten / Kota:", options=kab_list)

    if pilih_kab != "Semua Kabupaten/Kota":
      df_filtered = df[df["Nama Kabupaten Kota"] == pilih_kab]
    else:
      df_filtered = df
  else:
    df_filtered = df

  # 3. Metrik Ringkasan Utama
  st.subheader("📊 Ringkasan Kasus Utama (Total)")

  col1, col2, col3, col4 = st.columns(4)

  with col1:
    if "Jumlah Peserta Hadir Usia 18 Tahun" in df_filtered.columns:
      total_peserta_18 = df_filtered["Jumlah Peserta Hadir Usia 18 Tahun"].sum()
      st.metric("Peserta Hadir Usia ≥18 Thn", f"{total_peserta_18:,}")

  with col2:
    if "Jumlah Penderita Hipertensi" in df_filtered.columns:
      total_ht = df_filtered["Jumlah Penderita Hipertensi"].sum()
      st.metric("Penderita Hipertensi", f"{total_ht:,}")

  with col3:
    if "Jumlah Penderita Diabetes" in df_filtered.columns:
      total_dm = df_filtered["Jumlah Penderita Diabetes"].sum()
      st.metric("Penderita Diabetes", f"{total_dm:,}")

  with col4:
    if "Jumlah Peserta Dislipidemia" in df_filtered.columns:
      total_lipid = df_filtered["Jumlah Peserta Dislipidemia"].sum()
      st.metric("Kasus Dislipidemia", f"{total_lipid:,}")

  # 4. Tabel Detail Data Faskes
  st.subheader("📋 Detail Data per Faskes")
  st.dataframe(df_filtered)

  # 5. Visualisasi Sederhana (Contoh: Grafik Kasus Berdasarkan Kecamatan)
  if "Nama Kecamatan" in df_filtered.columns and "Jumlah Penderita Hipertensi" in df_filtered.columns:
    st.subheader("📈 Perbandingan Penderita Hipertensi per Kecamatan")
    chart_data = (
        df_filtered.groupby("Nama Kecamatan")["Jumlah Penderita Hipertensi"]
        .sum()
        .reset_index()
    )
    chart_data = chart_data.set_index("Nama Kecamatan")
    st.bar_chart(chart_data)

else:
  st.warning(
      "Silakan upload file Excel laporan CKG Anda terlebih dahulu untuk"
      " melihat dashboard."
  )