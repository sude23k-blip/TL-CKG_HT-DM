import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Dashboard Analisis CKG Kemenkes", page_icon="🏥", layout="wide"
)

st.title("🏥 Dashboard Analisis Data Cek Kesehatan Gratis (CKG)")
st.write(
    "Aplikasi interaktif untuk monitoring data CKG (Hipertensi, Diabetes, Dislipidemia, & Pengobatan)."
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
    df = pd.read_excel(uploaded_file)

  st.success("✅ Data berhasil dimuat!")

  # 2. Filter Wilayah Fleksibel (Kabupaten -> Kecamatan -> Faskes)
  st.subheader("🔍 Filter Wilayah & Faskes")

  col_f1, col_f2, col_f3 = st.columns(3)

  with col_f1:
    if "Nama Kabupaten Kota" in df.columns:
      kab_list = ["Semua"] + list(df["Nama Kabupaten Kota"].unique())
      pilih_kab = st.selectbox("Kabupaten / Kota:", options=kab_list)
      if pilih_kab != "Semua":
        df = df[df["Nama Kabupaten Kota"] == pilih_kab]

  with col_f2:
    if "Nama Kecamatan" in df.columns:
      kec_list = ["Semua"] + list(df["Nama Kecamatan"].unique())
      pilih_kec = st.selectbox("Kecamatan:", options=kec_list)
      if pilih_kec != "Semua":
        df = df[df["Nama Kecamatan"] == pilih_kec]

  with col_f3:
    if "Nama Faskes" in df.columns:
      faskes_list = ["Semua"] + list(df["Nama Faskes"].unique())
      pilih_faskes = st.selectbox("Puskesmas / Faskes:", options=faskes_list)
      if pilih_faskes != "Semua":
        df = df[df["Nama Faskes"] == pilih_faskes]

  # 3. Metrik Ringkasan Utama (Termasuk Data Pengobatan)
  st.subheader("📊 Ringkasan Kasus & Pengobatan")

  col1, col2, col3, col4 = st.columns(4)

  with col1:
    total_ht = (
        df["Jumlah Penderita Hipertensi"].sum()
        if "Jumlah Penderita Hipertensi" in df.columns
        else 0
    )
    st.metric("Total Penderita Hipertensi", f"{total_ht:,}")

  with col2:
    # Mencari kolom obat hipertensi (Biasanya kolom 'Diberikan Obat' setelah kolom HT)
    obat_ht_cols = [
        c
        for c in df.columns
        if "obat" in c.lower() and ("hipertensi" in c.lower() or "ht" in c.lower())
    ]
    # Jika tidak ketemu spesifik, kita cari kolom bernama 'Diberikan Obat'
    if not obat_ht_cols and "Diberikan Obat" in df.columns:
      obat_ht_cols = ["Diberikan Obat"]

    obat_ht = df[obat_ht_cols[0]].sum() if obat_ht_cols else 0
    st.metric("Hipertensi Diberikan Obat", f"{obat_ht:,}")

  with col3:
    total_dm = (
        df["Jumlah Penderita Diabetes"].sum()
        if "Jumlah Penderita Diabetes" in df.columns
        else 0
    )
    st.metric("Total Penderita Diabetes", f"{total_dm:,}")

  with col4:
    obat_dm_cols = [
        c
        for c in df.columns
        if "obat" in c.lower() and ("diabetes" in c.lower() or "dm" in c.lower())
    ]
    if not obat_dm_cols and "Diberikan Obat Diabetes" in df.columns:
      obat_dm_cols = ["Diberikan Obat Diabetes"]

    obat_dm = df[obat_dm_cols[0]].sum() if obat_dm_cols else 0
    st.metric("Diabetes Diberikan Obat", f"{obat_dm:,}")

  # 4. Grafik Interaktif dengan Plotly (Muncul Angka di Batang Grafik)
  if "Nama Kecamatan" in df.columns and "Jumlah Penderita Hipertensi" in df.columns:
    st.subheader("📈 Grafik Penderita Hipertensi Berdasarkan Wilayah")

    # Mengelompokkan data agar rapi di grafik
    group_col = (
        "Nama Faskes" if pilih_kec != "Semua" else "Nama Kecamatan"
    )  # Bisa dinamis ke Faskes jika kecamatan dipilih
    chart_df = (
        df.groupby(group_col)["Jumlah Penderita Hipertensi"]
        .sum()
        .reset_index()
    )

    # Membuat bar chart interaktif menggunakan Plotly yang memunculkan angka langsung di atas batang
    fig = px.bar(
        chart_df,
        x=group_col,
        y="Jumlah Penderita Hipertensi",
        text="Jumlah Penderita Hipertensi",
        color="Jumlah Penderita Hipertensi",
        color_continuous_scale="Blues",
    )
    fig.update_traces(
        texttemplate="%{text:,}", textposition="outside"
    )  # Memunculkan angka dengan format ribuan
    fig.update_layout(xaxis_tickangle=-45, height=500)

    st.plotly_chart(fig, use_container_width=True)

  # 5. Tabel Detail Data
  st.subheader("📋 Tabel Data Detail")
  st.dataframe(df)

else:
  st.warning(
      "Silakan upload file Excel laporan CKG Anda terlebih dahulu untuk"
      " melihat dashboard."
  )