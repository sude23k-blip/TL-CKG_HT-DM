import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Dashboard Analisis CKG Kemenkes", page_icon="🏥", layout="wide"
)

st.title("🏥 Dashboard Analisis Data Cek Kesehatan Gratis (CKG)")
st.write(
    "Aplikasi interaktif untuk monitoring data skrining CKG, cakupan pengobatan, dan analisis alasan klinis."
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

  # 3. Metrik Ringkasan Utama
  st.subheader("📊 Ringkasan Skrining, Kasus, & Pengobatan")

  col1, col2, col3, col4 = st.columns(4)

  with col1:
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
        "Total Penderita Hipertensi",
        f"{tot_ht:,}",
        delta=f"Diskrining: {scr_ht:,}",
    )

  with col2:
    obat_ht = df["Diberikan Obat"].sum() if "Diberikan Obat" in df.columns else 0
    persen_ht = (obat_ht / tot_ht * 100) if tot_ht > 0 else 0
    st.metric(
        "Hipertensi Diberikan Obat",
        f"{obat_ht:,}",
        delta=f"{persen_ht:.1f}% dari penderita",
    )

  with col3:
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
        "Total Penderita Diabetes",
        f"{tot_dm:,}",
        delta=f"Diskrining: {scr_dm:,}",
    )

  with col4:
    obat_dm = (
        df["Diberikan Obat Diabetes"].sum()
        if "Diberikan Obat Diabetes" in df.columns
        else 0
    )
    persen_dm = (obat_dm / tot_dm * 100) if tot_dm > 0 else 0
    st.metric(
        "Diabetes Diberikan Obat",
        f"{obat_dm:,}",
        delta=f"{persen_dm:.1f}% dari penderita",
    )

  # 4. Grafik Batang Penderita Hipertensi per Wilayah
  if "Jumlah Penderita Hipertensi" in df.columns:
    st.subheader("📈 Grafik Penderita Hipertensi Berdasarkan Wilayah")
    group_col = "Nama Faskes" if pilih_kec != "Semua" else "Nama Kecamatan"
    chart_df = df.groupby(group_col)["Jumlah Penderita Hipertensi"].sum().reset_index()

    fig_bar = px.bar(
        chart_df,
        x=group_col,
        y="Jumlah Penderita Hipertensi",
        text="Jumlah Penderita Hipertensi",
        color="Jumlah Penderita Hipertensi",
        color_continuous_scale="Blues",
    )
    fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig_bar.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_bar, use_container_width=True)

  # 5. Grafik Lingkaran (Pie Chart) Perbandingan Pengobatan HT & DM
  st.subheader("🍩 Proporsi Pemberian Pengobatan pada Penderita")
  col_pie1, col_pie2 = st.columns(2)

  with col_pie1:
    st.markdown("**Hipertensi (Diberi Obat vs Belum/Tidak Diberikan)**")
    sisa_ht = max(0, tot_ht - obat_ht)
    df_pie_ht = pd.DataFrame(
        {
            "Status": ["Diberikan Obat", "Belum/Tidak Diberikan Obat"],
            "Jumlah": [obat_ht, sisa_ht],
        }
    )
    fig_pie_ht = px.pie(
        df_pie_ht,
        names="Status",
        values="Jumlah",
        hole=0.4,
        color_discrete_sequence=["#1f77b4", "#aec7e8"],
    )
    fig_pie_ht.update_traces(textinfo="percent+value")
    st.plotly_chart(fig_pie_ht, use_container_width=True)

  with col_pie2:
    st.markdown("**Diabetes (Diberi Obat vs Belum/Tidak Diberikan)**")
    sisa_dm = max(0, tot_dm - obat_dm)
    df_pie_dm = pd.DataFrame(
        {
            "Status": ["Diberikan Obat", "Belum/Tidak Diberikan Obat"],
            "Jumlah": [obat_dm, sisa_dm],
        }
    )
    fig_pie_dm = px.pie(
        df_pie_dm,
        names="Status",
        values="Jumlah",
        hole=0.4,
        color_discrete_sequence=["#2ca02c", "#98df8a"],
    )
    fig_pie_dm.update_traces(textinfo="percent+value")
    st.plotly_chart(fig_pie_dm, use_container_width=True)

  # 6. Grafik Alasan Tidak Diberikan Obat (HT & DM)
  st.subheader("⚠️ Analisis Alasan Tidak Diberikan Obat")
  col_alasan1, col_alasan2 = st.columns(2)

  with col_alasan1:
    st.markdown("**Alasan Hipertensi Tidak Diberikan Obat**")
    cols_alasan_ht = [
        c
        for c in df.columns
        if "Alasan Tidak Diberikan Obat Hipertensi" in c
    ]
    if cols_alasan_ht:
      sum_alasan_ht = df[cols_alasan_ht].sum().reset_index()
      sum_alasan_ht.columns = ["Alasan", "Jumlah"]
      sum_alasan_ht["Alasan"] = sum_alasan_ht["Alasan"].str.replace(
          "Alasan Tidak Diberikan Obat Hipertensi - ", ""
      )
      sum_alasan_ht = sum_alasan_ht[sum_alasan_ht["Jumlah"] > 0]

      if not sum_alasan_ht.empty:
        fig_als_ht = px.bar(
            sum_alasan_ht,
            x="Jumlah",
            y="Alasan",
            orientation="h",
            text="Jumlah",
            color="Jumlah",
            color_continuous_scale="Reds",
        )
        fig_als_ht.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_als_ht.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_als_ht, use_container_width=True)
      else:
        st.info("Tidak ada data alasan tidak diberikan obat hipertensi.")

  with col_alasan2:
    st.markdown("**Alasan Diabetes Tidak Diberikan Obat**")
    cols_alasan_dm = [
        c
        for c in df.columns
        if "Alasan Tidak Diberikan Obat Diabetes" in c
    ]
    if cols_alasan_dm:
      sum_alasan_dm = df[cols_alasan_dm].sum().reset_index()
      sum_alasan_dm.columns = ["Alasan", "Jumlah"]
      sum_alasan_dm["Alasan"] = sum_alasan_dm["Alasan"].str.replace(
          "Alasan Tidak Diberikan Obat Diabetes - ", ""
      )
      sum_alasan_dm = sum_alasan_dm[sum_alasan_dm["Jumlah"] > 0]

      if not sum_alasan_dm.empty:
        fig_als_dm = px.bar(
            sum_alasan_dm,
            x="Jumlah",
            y="Alasan",
            orientation="h",
            text="Jumlah",
            color="Jumlah",
            color_continuous_scale="Oranges",
        )
        fig_als_dm.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_als_dm.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_als_dm, use_container_width=True)
      else:
        st.info("Tidak ada data alasan tidak diberikan obat diabetes.")

  # 7. Tabel Detail Data
  st.subheader("📋 Tabel Data Detail")
  st.dataframe(df)

else:
  st.warning(
      "Silakan upload file Excel laporan CKG Anda terlebih dahulu untuk"
      " melihat dashboard."
  )