import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Dashboard Analisis CKG Kemenkes", page_icon="🏥", layout="wide"
)

st.title("🏥 Dashboard Analisis Data Cek Kesehatan Gratis (CKG)")
st.write(
    "Aplikasi interaktif untuk monitoring data skrining CKG (Hipertensi, Diabetes, Dislipidemia, & Pengobatan)."
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

  # 3. Metrik Ringkasan Utama (Jumlah Skrining, Kasus, & Pengobatan)
  st.subheader("📊 Ringkasan Skrining, Kasus, & Pengobatan")

  col1, col2, col3, col4 = st.columns(4)

  with col1:
    # Jumlah Diskrining Tekanan Darah
    scr_ht = (
        df["Jumlah Orang Diperiksa Tekanan Darah"].sum()
        if "Jumlah Orang Diperiksa Tekanan Darah" in df.columns
        else 0
    )
    tot_ht = (
        df["Jumlah Penderita Hipertensi"].sum()
        if "Jumlah Penderita Hipertensi" in df.columns
        else 0
    )
    st.metric(
        "Skrining & Penderita Hipertensi",
        f"{tot_ht:,}",
        delta=f"Diskrining: {scr_ht:,}",
    )

  with col2:
    # Hipertensi Berobat (Diberikan Obat)
    obat_ht = df["Diberikan Obat"].sum() if "Diberikan Obat" in df.columns else 0
    st.metric("Hipertensi Diberikan Obat", f"{obat_ht:,}")

  with col3:
    # Jumlah Diskrining Gula Darah / Diabetes
    scr_dm = (
        df["Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)"].sum()
        if "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)" in df.columns
        else 0
    )
    tot_dm = (
        df["Jumlah Penderita Diabetes"].sum()
        if "Jumlah Penderita Diabetes" in df.columns
        else 0
    )
    st.metric(
        "Skrining & Penderita Diabetes",
        f"{tot_dm:,}",
        delta=f"Diskrining: {scr_dm:,}",
    )

  with col4:
    # Diabetes Berobat (Diberikan Obat Diabetes)
    obat_dm = (
        df["Diberikan Obat Diabetes"].sum()
        if "Diberikan Obat Diabetes" in df.columns
        else 0
    )
    st.metric("Diabetes Diberikan Obat", f"{obat_dm:,}")

  # 4. Grafik Interaktif dengan Plotly (Muncul Angka di Batang Grafik)
  if "Jumlah Penderita Hipertensi" in df.columns:
    st.subheader("📈 Grafik Penderita Hipertensi Berdasarkan Wilayah")

    # Menentukan kelompok sumbu X berdasarkan filter yang aktif
    if pilih_faskes != "Semua":
      group_col = "Nama Faskes"
    elif pilih_kec != "Semua":
      group_col = "Nama Faskes"
    else:
      group_col = "Nama Kecamatan"

    chart_df = df.groupby(group_col)["Jumlah Penderita Hipertensi"].sum().reset_index()

    # Membuat bar chart interaktif dengan Plotly
    fig = px.bar(
        chart_df,
        x=group_col,
        y="Jumlah Penderita Hipertensi",
        text="Jumlah Penderita Hipertensi",
        color="Jumlah Penderita Hipertensi",
        color_continuous_scale="Blues",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title=group_col,
        yaxis_title="Jumlah Penderita",
    )

    st.plotly_chart(fig, use_container_width=True)

  # 5. Tabel Detail Data
  st.subheader("📋 Tabel Data Detail")
  st.dataframe(df)

else:
  st.warning(
      "Silakan upload file Excel laporan CKG Anda terlebih dahulu untuk"
      " melihat dashboard."
  )
