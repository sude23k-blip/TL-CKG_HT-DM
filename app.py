import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman Web (Layout Wide agar leluasa)
st.set_page_config(
    page_title="Dashboard Analisis Tata Laksana HT dan DM CKG Dinkes Pangkep",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Dashboard Analisis Data Tata Laksana HT dan DM CKG Dinkes Pangkep")
st.write(
    "Aplikasi portal monitoring data skrining CKG, cakupan diagnosis, pengobatan,"
    " edukasi, dan analisis klinis."
)

# --- BAGIAN OTOMATIS LOAD FILE DEFAULT & UPLOAD BARU ---
default_file_path = "data_default.xlsx"

# Widget uploader (tetap disediakan sebagai opsi jika ingin mengganti data)
uploaded_file = st.file_uploader(
    "📁 Upload file Excel laporan CKG baru (Opsional - Jika ingin mengganti data"
    " default)",
    type=["xlsx", "csv"],
)

data_loaded = False
df_raw = None

if uploaded_file is not None:
  # Jika user meng-upload file baru
  try:
    df_raw = pd.read_excel(uploaded_file, sheet_name="Data Agregat CKG")
    st.success("✅ Menggunakan data dari file yang baru di-upload!")
    data_loaded = True
  except:
    try:
      df_raw = pd.read_excel(uploaded_file)
      st.success("✅ Menggunakan data dari file yang baru di-upload!")
      data_loaded = True
    except Exception as e:
      st.error(f"Gagal membaca file yang di-upload: {e}")

elif os.path.exists(default_file_path):
  # Jika belum upload, otomatis baca file default dari sistem/GitHub
  try:
    # Coba baca sheet spesifik dulu
    df_raw = pd.read_excel(default_file_path, sheet_name="Data Agregat CKG")
    st.info("ℹ️ Menampilkan data default dari sistem (`data_default.xlsx`).")
    data_loaded = True
  except Exception as e_sheet:
    try:
      # Jika sheet "Data Agregat CKG" tidak ditemukan, baca sheet pertama secara otomatis
      df_raw = pd.read_excel(default_file_path, sheet_name=0)
      st.info(
          "ℹ️ Menampilkan data default dari sheet pertama `data_default.xlsx`."
      )
      data_loaded = True
    except Exception as e:
      st.error(
          f"Gagal membaca file default sistem. Detail error: {e_sheet} / {e}"
      )
else:
  st.warning(
      "⚠️ File data default (`data_default.xlsx`) tidak ditemukan di repository"
      " GitHub. Silakan pastikan file tersebut sudah di-upload ke repository"
      " sejajar dengan `app.py`, atau upload melalui tombol di atas."
  )

# Lanjutkan proses jika data berhasil dimuat (baik secara otomatis maupun upload)
if data_loaded and df_raw is not None:
  # Simpan salinan asli untuk grafik per kecamatan yang ingin ditampilkan utuh
  df_original = df_raw.copy()

  # 2. Filter Wilayah Fleksibel (Kabupaten -> Kecamatan -> Faskes) di Bagian Atas
  st.subheader("🔍 Filter Wilayah & Faskes")
  col_f1, col_f2, col_f3 = st.columns(3)

  with col_f1:
    if "Nama Kabupaten Kota" in df_raw.columns:
      kab_list = ["Semua"] + list(df_raw["Nama Kabupaten Kota"].unique())
      pilih_kab = st.selectbox("Kabupaten / Kota:", options=kab_list)
      if pilih_kab != "Semua":
        df_raw = df_raw[df_raw["Nama Kabupaten Kota"] == pilih_kab]
        df_original = df_original[
            df_original["Nama Kabupaten Kota"] == pilih_kab
        ]

  with col_f2:
    if "Nama Kecamatan" in df_raw.columns:
      kec_list = ["Semua"] + list(df_raw["Nama Kecamatan"].unique())
      pilih_kec = st.selectbox("Kecamatan:", options=kec_list)
      if pilih_kec != "Semua":
        df_raw = df_raw[df_raw["Nama Kecamatan"] == pilih_kec]

  with col_f3:
    if "Nama Faskes" in df_raw.columns:
      faskes_list = ["Semua"] + list(df_raw["Nama Faskes"].unique())
      pilih_faskes = st.selectbox("Puskesmas / Faskes:", options=faskes_list)
      if pilih_faskes != "Semua":
        df_raw = df_raw[df_raw["Nama Faskes"] == pilih_faskes]

  # Gunakan df_raw sebagai dataframe utama untuk analisis
  df = df_raw

  st.markdown("---")

  # --- PERHITUNGAN VARIABEL UTAMA ---
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
  prev_ht = (tot_ht / scr_ht * 100) if scr_ht > 0 else 0

  diag_ht = (
      df["Diagnosis Hipertensi"].sum()
      if "Diagnosis Hipertensi" in df.columns
      else 0
  )
  persen_diag_ht = (diag_ht / tot_ht * 100) if tot_ht > 0 else 0

  obat_ht = df["Diberikan Obat"].sum() if "Diberikan Obat" in df.columns else 0
  # Pembagi diubah dari tot_ht menjadi diag_ht (penderita terdiagnosis)
  persen_ht = (obat_ht / diag_ht * 100) if diag_ht > 0 else 0

  edu_ht = (
      df["Edukasi Hipertensi"].sum() if "Edukasi Hipertensi" in df.columns else 0
  )
  persen_edu_ht = (edu_ht / tot_ht * 100) if tot_ht > 0 else 0

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
  prev_dm = (tot_dm / scr_dm * 100) if scr_dm > 0 else 0

  diag_dm = (
      df["Diberikan Diagnosis"].sum() if "Diberikan Diagnosis" in df.columns else 0
  )
  persen_diag_dm = (diag_dm / tot_dm * 100) if tot_dm > 0 else 0

  obat_dm = (
      df["Diberikan Obat Diabetes"].sum()
      if "Diberikan Obat Diabetes" in df.columns
      else 0
  )
  # Pembagi diubah dari tot_dm menjadi diag_dm (penderita terdiagnosis)
  persen_dm = (obat_dm / diag_dm * 100) if diag_dm > 0 else 0

  edu_dm = (
      df["Edukasi Diabetes"].sum() if "Edukasi Diabetes" in df.columns else 0
  )
  persen_edu_dm = (edu_dm / tot_dm * 100) if tot_dm > 0 else 0

  # ==========================================
  # 3. PEMBUATAN MENU KESAMPING (TABS)
  # ==========================================
  tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
      "📊 Ringkasan & Kasus",
      "📋 Analisis Diagnosis",
      "🗣️ Cakupan Edukasi",
      "📈 Prevalensi Wilayah",
      "💊 Cakupan Pengobatan & Alasan",
      "📁 Tabel Data Detail",
  ])

  # --- TAB 1: RINGKASAN & GRAFIK KASUS ---
  with tab1:
    st.subheader("📊 Ringkasan Skrining, Kasus, Diagnosis, & Pengobatan")

    # Baris 1: Hipertensi
    st.markdown("##### 🔹 Ringkasan Hipertensi (HT)")
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
      st.metric(
          "Total Penderita Hipertensi",
          f"{tot_ht:,}",
          delta=f"{prev_ht:.1f}% dari {scr_ht:,} diskrining",
      )
    with mc2:
      st.metric(
          "Hipertensi Diberikan Diagnosis",
          f"{diag_ht:,}",
          delta=f"{persen_diag_ht:.1f}% dari penderita",
      )
    with mc3:
      st.metric(
          "Hipertensi Diberikan Obat",
          f"{obat_ht:,}",
          delta=f"{persen_ht:.1f}% dari penderita terdiagnosis ({diag_ht:,})",
      )

    st.markdown("")

    # Baris 2: Diabetes
    st.markdown("##### 🔹 Ringkasan Diabetes Melitus (DM)")
    mc4, mc5, mc6 = st.columns(3)
    with mc4:
      st.metric(
          "Total Penderita Diabetes",
          f"{tot_dm:,}",
          delta=f"{prev_dm:.1f}% dari {scr_dm:,} diskrining",
      )
    with mc5:
      st.metric(
          "Diabetes Diberikan Diagnosis",
          f"{diag_dm:,}",
          delta=f"{persen_diag_dm:.1f}% dari penderita",
      )
    with mc6:
      st.metric(
          "Diabetes Diberikan Obat",
          f"{obat_dm:,}",
          delta=f"{persen_dm:.1f}% dari penderita terdiagnosis ({diag_dm:,})",
      )

    st.markdown("---")

    # Grafik Penderita HT Berdasarkan Kecamatan (Urut Tertinggi ke Terendah)
    if "Jumlah Penderita Hipertensi" in df.columns and "Nama Kecamatan" in df.columns:
      st.subheader("📈 Grafik Penderita Hipertensi Berdasarkan Kecamatan")
      chart_kec_ht = (
          df.groupby("Nama Kecamatan")["Jumlah Penderita Hipertensi"]
          .sum()
          .reset_index()
          .sort_values(by="Jumlah Penderita Hipertensi", ascending=False)
      )
      fig_kec_ht = px.bar(
          chart_kec_ht,
          x="Nama Kecamatan",
          y="Jumlah Penderita Hipertensi",
          text="Jumlah Penderita Hipertensi",
          color="Jumlah Penderita Hipertensi",
          color_continuous_scale="Blues",
      )
      fig_kec_ht.update_traces(texttemplate="%{text:,}", textposition="outside")
      fig_kec_ht.update_layout(
          xaxis_tickangle=-45,
          height=400,
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_kec_ht, use_container_width=True)

    # Grafik Penderita DM Berdasarkan Kecamatan (Urut Tertinggi ke Terendah)
    if "Jumlah Penderita Diabetes" in df.columns and "Nama Kecamatan" in df.columns:
      st.subheader("📈 Grafik Penderita Diabetes Berdasarkan Kecamatan")
      chart_kec_dm = (
          df.groupby("Nama Kecamatan")["Jumlah Penderita Diabetes"]
          .sum()
          .reset_index()
          .sort_values(by="Jumlah Penderita Diabetes", ascending=False)
      )
      fig_kec_dm = px.bar(
          chart_kec_dm,
          x="Nama Kecamatan",
          y="Jumlah Penderita Diabetes",
          text="Jumlah Penderita Diabetes",
          color="Jumlah Penderita Diabetes",
          color_continuous_scale="Oranges",
      )
      fig_kec_dm.update_traces(texttemplate="%{text:,}", textposition="outside")
      fig_kec_dm.update_layout(
          xaxis_tickangle=-45,
          height=400,
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_kec_dm, use_container_width=True)

    st.markdown("---")

    # Grafik Rinci HT Per PKM (Urut Tertinggi ke Terendah)
    if "Jumlah Penderita Hipertensi" in df.columns and "Nama Faskes" in df.columns:
      st.subheader("🏥 Grafik Rinci Penderita Hipertensi Per Puskesmas (PKM)")
      chart_pkm_ht = (
          df.groupby("Nama Faskes")["Jumlah Penderita Hipertensi"]
          .sum()
          .reset_index()
          .sort_values(by="Jumlah Penderita Hipertensi", ascending=False)
      )
      fig_pkm_ht = px.bar(
          chart_pkm_ht,
          x="Nama Faskes",
          y="Jumlah Penderita Hipertensi",
          text="Jumlah Penderita Hipertensi",
          color="Jumlah Penderita Hipertensi",
          color_continuous_scale="PuBu",
      )
      fig_pkm_ht.update_traces(texttemplate="%{text:,}", textposition="outside")
      fig_pkm_ht.update_layout(
          xaxis_tickangle=-45,
          height=450,
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_pkm_ht, use_container_width=True)

    st.markdown("---")

    # Grafik Rinci DM Per PKM (Urut Tertinggi ke Terendah)
    if "Jumlah Penderita Diabetes" in df.columns and "Nama Faskes" in df.columns:
      st.subheader("🏥 Grafik Rinci Penderita Diabetes Per Puskesmas (PKM)")
      chart_pkm_dm = (
          df.groupby("Nama Faskes")["Jumlah Penderita Diabetes"]
          .sum()
          .reset_index()
          .sort_values(by="Jumlah Penderita Diabetes", ascending=False)
      )
      fig_pkm_dm = px.bar(
          chart_pkm_dm,
          x="Nama Faskes",
          y="Jumlah Penderita Diabetes",
          text="Jumlah Penderita Diabetes",
          color="Jumlah Penderita Diabetes",
          color_continuous_scale="Greens",
      )
      fig_pkm_dm.update_traces(texttemplate="%{text:,}", textposition="outside")
      fig_pkm_dm.update_layout(
          xaxis_tickangle=-45,
          height=450,
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_pkm_dm, use_container_width=True)

  # --- TAB 2: ANALISIS DIAGNOSIS ---
  with tab2:
    st.subheader(
        "📋 Analisis Penegakan Diagnosis (HT & DM) & Persentase Per PKM"
    )
    col_d1, col_d2 = st.columns(2)

    with col_d1:
      st.markdown(
          f"**Hipertensi: Penderita ({tot_ht:,}) vs Diberikan Diagnosis"
          f" ({diag_ht:,})**"
      )
      sisa_diag_ht = max(0, tot_ht - diag_ht)
      df_pie_diag_ht = pd.DataFrame(
          {
              "Status Diagnosis": [
                  "Diberikan Diagnosis",
                  "Belum/Tidak Diberikan",
              ],
              "Jumlah": [diag_ht, sisa_diag_ht],
          }
      )
      fig_pie_diag_ht = px.pie(
          df_pie_diag_ht,
          names="Status Diagnosis",
          values="Jumlah",
          hole=0.4,
          color_discrete_sequence=["#004c6d", "#c1f0f6"],
      )
      fig_pie_diag_ht.update_traces(textinfo="percent+value")
      st.plotly_chart(fig_pie_diag_ht, use_container_width=True)

    with col_d2:
      st.markdown(
          f"**Diabetes: Penderita ({tot_dm:,}) vs Diberikan Diagnosis"
          f" ({diag_dm:,})**"
      )
      sisa_diag_dm = max(0, tot_dm - diag_dm)
      df_pie_diag_dm = pd.DataFrame(
          {
              "Status Diagnosis": [
                  "Diberikan Diagnosis",
                  "Belum/Tidak Diberikan",
              ],
              "Jumlah": [diag_dm, sisa_diag_dm],
          }
      )
      fig_pie_diag_dm = px.pie(
          df_pie_diag_dm,
          names="Status Diagnosis",
          values="Jumlah",
          hole=0.4,
          color_discrete_sequence=["#38b000", "#ccff33"],
      )
      fig_pie_diag_dm.update_traces(textinfo="percent+value")
      st.plotly_chart(fig_pie_diag_dm, use_container_width=True)

    st.markdown("---")
    st.subheader(
        "📊 Grafik Persentase Diagnosis (%) dari Total Penderita Per Puskesmas"
    )

    # Persentase Diagnosis HT Per PKM (Urut Tertinggi ke Terendah)
    if (
        "Diagnosis Hipertensi" in df.columns
        and "Jumlah Penderita Hipertensi" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown("**Persentase Diagnosis Hipertensi (%) Per Puskesmas**")
      df_diag_pkm_ht = (
          df.groupby("Nama Faskes")[
              ["Diagnosis Hipertensi", "Jumlah Penderita Hipertensi"]
          ]
          .sum()
          .reset_index()
      )
      df_diag_pkm_ht["Persentase Diag HT"] = (
          df_diag_pkm_ht["Diagnosis Hipertensi"]
          / df_diag_pkm_ht["Jumlah Penderita Hipertensi"]
          * 100
      ).fillna(0)
      df_diag_pkm_ht = df_diag_pkm_ht.sort_values(
          by="Persentase Diag HT", ascending=False
      )

      fig_diag_pkm_ht = px.bar(
          df_diag_pkm_ht,
          x="Nama Faskes",
          y="Persentase Diag HT",
          text=df_diag_pkm_ht["Persentase Diag HT"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase Diag HT",
          color_continuous_scale="Blues",
      )
      fig_diag_pkm_ht.update_traces(textposition="outside")
      fig_diag_pkm_ht.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_diag_pkm_ht, use_container_width=True)

    st.markdown("---")

    # Persentase Diagnosis DM Per PKM (Urut Tertinggi ke Terendah)
    if (
        "Diberikan Diagnosis" in df.columns
        and "Jumlah Penderita Diabetes" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown("**Persentase Diagnosis Diabetes (%) Per Puskesmas**")
      df_diag_pkm_dm = (
          df.groupby("Nama Faskes")[
              ["Diberikan Diagnosis", "Jumlah Penderita Diabetes"]
          ]
          .sum()
          .reset_index()
      )
      df_diag_pkm_dm["Persentase Diag DM"] = (
          df_diag_pkm_dm["Diberikan Diagnosis"]
          / df_diag_pkm_dm["Jumlah Penderita Diabetes"]
          * 100
      ).fillna(0)
      df_diag_pkm_dm = df_diag_pkm_dm.sort_values(
          by="Persentase Diag DM", ascending=False
      )

      fig_diag_pkm_dm = px.bar(
          df_diag_pkm_dm,
          x="Nama Faskes",
          y="Persentase Diag DM",
          text=df_diag_pkm_dm["Persentase Diag DM"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase Diag DM",
          color_continuous_scale="Greens",
      )
      fig_diag_pkm_dm.update_traces(textposition="outside")
      fig_diag_pkm_dm.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_diag_pkm_dm, use_container_width=True)

    st.markdown("---")
    st.markdown("### ⚠️ Analisis Alasan Tidak Diberikan Diagnosis")
    col_al_d1, col_al_d2 = st.columns(2)

    with col_al_d1:
      st.markdown("*Alasan Hipertensi Tidak Diberikan Diagnosis:*")
      cols_als_diag_ht = [
          c
          for c in df.columns
          if "Alasan Tidak Diberikan Diagnosis Hipertensi" in c
      ]
      if cols_als_diag_ht:
        sum_als_diag_ht = df[cols_als_diag_ht].sum().reset_index()
        sum_als_diag_ht.columns = ["Alasan", "Jumlah"]
        sum_als_diag_ht["Alasan"] = sum_als_diag_ht["Alasan"].str.replace(
            "Alasan Tidak Diberikan Diagnosis Hipertensi - ", ""
        )
        sum_als_diag_ht = sum_als_diag_ht[sum_als_diag_ht["Jumlah"] > 0]
        if not sum_als_diag_ht.empty:
          fig_als_diag_ht = px.bar(
              sum_als_diag_ht,
              x="Jumlah",
              y="Alasan",
              orientation="h",
              text="Jumlah",
              color="Jumlah",
              color_continuous_scale="Purples",
          )
          fig_als_diag_ht.update_traces(
              texttemplate="%{text:,}", textposition="outside"
          )
          fig_als_diag_ht.update_layout(
              height=350, yaxis={"categoryorder": "total ascending"}
          )
          st.plotly_chart(fig_als_diag_ht, use_container_width=True)
        else:
          st.info("Tidak ada data alasan.")

    with col_al_d2:
      st.markdown("*Alasan Diabetes Tidak Diberikan Diagnosis:*")
      cols_als_diag_dm = [
          c
          for c in df.columns
          if "Alasan Tidak Diberikan Diagnosis Diabetes" in c
      ]
      if cols_als_diag_dm:
        sum_als_diag_dm = df[cols_als_diag_dm].sum().reset_index()
        sum_als_diag_dm.columns = ["Alasan", "Jumlah"]
        sum_als_diag_dm["Alasan"] = sum_als_diag_dm["Alasan"].str.replace(
            "Alasan Tidak Diberikan Diagnosis Diabetes - ", ""
        )
        sum_als_diag_dm = sum_als_diag_dm[sum_als_diag_dm["Jumlah"] > 0]
        if not sum_als_diag_dm.empty:
          fig_als_diag_dm = px.bar(
              sum_als_diag_dm,
              x="Jumlah",
              y="Alasan",
              orientation="h",
              text="Jumlah",
              color="Jumlah",
              color_continuous_scale="YlGn",
          )
          fig_als_diag_dm.update_traces(
              texttemplate="%{text:,}", textposition="outside"
          )
          fig_als_diag_dm.update_layout(
              height=350, yaxis={"categoryorder": "total ascending"}
          )
          st.plotly_chart(fig_als_diag_dm, use_container_width=True)
        else:
          st.info("Tidak ada data alasan.")

  # --- TAB 3: CAKUPAN EDUKASI ---
  with tab3:
    st.subheader(
        "🗣️ Analisis Cakupan Pemberian Edukasi (% dari Penderita) Per Puskesmas"
    )

    ce1, ce2 = st.columns(2)
    with ce1:
      st.metric(
          "Edukasi Hipertensi",
          f"{edu_ht:,} Orang",
          delta=f"{persen_edu_ht:.1f}% dari total penderita ({tot_ht:,})",
      )
    with ce2:
      st.metric(
          "Edukasi Diabetes",
          f"{edu_dm:,} Orang",
          delta=f"{persen_edu_dm:.1f}% dari total penderita ({tot_dm:,})",
      )

    st.markdown("---")

    # Persentase Edukasi HT Per PKM (Urut Tertinggi ke Terendah)
    if (
        "Edukasi Hipertensi" in df.columns
        and "Jumlah Penderita Hipertensi" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown(
          "**Persentase Edukasi Hipertensi (%) Per Puskesmas (PKM)**"
      )
      df_edu_pkm_ht = (
          df.groupby("Nama Faskes")[
              ["Edukasi Hipertensi", "Jumlah Penderita Hipertensi"]
          ]
          .sum()
          .reset_index()
      )
      df_edu_pkm_ht["Persentase Edukasi HT"] = (
          df_edu_pkm_ht["Edukasi Hipertensi"]
          / df_edu_pkm_ht["Jumlah Penderita Hipertensi"]
          * 100
      ).fillna(0)
      df_edu_pkm_ht = df_edu_pkm_ht.sort_values(
          by="Persentase Edukasi HT", ascending=False
      )

      fig_edu_pkm_ht = px.bar(
          df_edu_pkm_ht,
          x="Nama Faskes",
          y="Persentase Edukasi HT",
          text=df_edu_pkm_ht["Persentase Edukasi HT"].apply(
              lambda x: f"{x:.1f}%"
          ),
          color="Persentase Edukasi HT",
          color_continuous_scale="Blues",
      )
      fig_edu_pkm_ht.update_traces(textposition="outside")
      fig_edu_pkm_ht.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_edu_pkm_ht, use_container_width=True)

    st.markdown("---")

    # Persentase Edukasi DM Per PKM (Urut Tertinggi ke Terendah)
    if (
        "Edukasi Diabetes" in df.columns
        and "Jumlah Penderita Diabetes" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown(
          "**Persentase Edukasi Diabetes (%) Per Puskesmas (PKM)**"
      )
      df_edu_pkm_dm = (
          df.groupby("Nama Faskes")[
              ["Edukasi Diabetes", "Jumlah Penderita Diabetes"]
          ]
          .sum()
          .reset_index()
      )
      df_edu_pkm_dm["Persentase Edukasi DM"] = (
          df_edu_pkm_dm["Edukasi Diabetes"]
          / df_edu_pkm_dm["Jumlah Penderita Diabetes"]
          * 100
      ).fillna(0)
      df_edu_pkm_dm = df_edu_pkm_dm.sort_values(
          by="Persentase Edukasi DM", ascending=False
      )

      fig_edu_pkm_dm = px.bar(
          df_edu_pkm_dm,
          x="Nama Faskes",
          y="Persentase Edukasi DM",
          text=df_edu_pkm_dm["Persentase Edukasi DM"].apply(
              lambda x: f"{x:.1f}%"
          ),
          color="Persentase Edukasi DM",
          color_continuous_scale="Greens",
      )
      fig_edu_pkm_dm.update_traces(textposition="outside")
      fig_edu_pkm_dm.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_edu_pkm_dm, use_container_width=True)

  # --- TAB 4: PREVALENSI PERSENTASE (KECAMATAN & PKM MENGGUNAKAN DF_ORIGINAL) ---
  with tab4:
    st.subheader(
        "📊 Grafik Prevalensi Kasus dari Jumlah Diskrining (Berdasarkan Kecamatan"
        " & Per Puskesmas)"
    )

    # 1. Prevalensi Hipertensi per Kecamatan (Urut Tertinggi ke Terendah)
    if (
        "Jumlah Orang Diperiksa Tekanan Darah" in df_original.columns
        and "Jumlah Penderita Hipertensi" in df_original.columns
        and "Nama Kecamatan" in df_original.columns
    ):
      st.markdown(
          "**1. Persentase Penderita Hipertensi (%) Berdasarkan Kecamatan**"
      )
      df_kec_pct_ht = (
          df_original.groupby("Nama Kecamatan")[
              [
                  "Jumlah Penderita Hipertensi",
                  "Jumlah Orang Diperiksa Tekanan Darah",
              ]
          ]
          .sum()
          .reset_index()
      )
      df_kec_pct_ht["Persentase HT"] = (
          df_kec_pct_ht["Jumlah Penderita Hipertensi"]
          / df_kec_pct_ht["Jumlah Orang Diperiksa Tekanan Darah"]
          * 100
      ).fillna(0)
      df_kec_pct_ht = df_kec_pct_ht.sort_values(
          by="Persentase HT", ascending=False
      )

      fig_kec_pct_ht = px.bar(
          df_kec_pct_ht,
          x="Nama Kecamatan",
          y="Persentase HT",
          text=df_kec_pct_ht["Persentase HT"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase HT",
          color_continuous_scale="Teal",
      )
      fig_kec_pct_ht.update_traces(textposition="outside")
      fig_kec_pct_ht.update_layout(
          xaxis_tickangle=-45,
          height=420,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_kec_pct_ht, use_container_width=True)

    st.markdown("---")

    # 2. Prevalensi Hipertensi per Puskesmas (PKM) (Urut Tertinggi ke Terendah)
    if (
        "Jumlah Orang Diperiksa Tekanan Darah" in df.columns
        and "Jumlah Penderita Hipertensi" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown(
          "**2. Persentase Penderita Hipertensi (%) Per Puskesmas (PKM)**"
      )
      df_pkm_pct_ht = (
          df.groupby("Nama Faskes")[
              [
                  "Jumlah Penderita Hipertensi",
                  "Jumlah Orang Diperiksa Tekanan Darah",
              ]
          ]
          .sum()
          .reset_index()
      )
      df_pkm_pct_ht["Persentase HT"] = (
          df_pkm_pct_ht["Jumlah Penderita Hipertensi"]
          / df_pkm_pct_ht["Jumlah Orang Diperiksa Tekanan Darah"]
          * 100
      ).fillna(0)
      df_pkm_pct_ht = df_pkm_pct_ht.sort_values(
          by="Persentase HT", ascending=False
      )

      fig_pkm_pct_ht = px.bar(
          df_pkm_pct_ht,
          x="Nama Faskes",
          y="Persentase HT",
          text=df_pkm_pct_ht["Persentase HT"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase HT",
          color_continuous_scale="Darkmint",
      )
      fig_pkm_pct_ht.update_traces(textposition="outside")
      fig_pkm_pct_ht.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_pkm_pct_ht, use_container_width=True)

    st.markdown("---")

    # 3. Prevalensi Diabetes per Kecamatan (Urut Tertinggi ke Terendah)
    if (
        "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)" in df_original.columns
        and "Jumlah Penderita Diabetes" in df_original.columns
        and "Nama Kecamatan" in df_original.columns
    ):
      st.markdown(
          "**3. Persentase Penderita Diabetes (%) Berdasarkan Kecamatan**"
      )
      df_kec_pct_dm = (
          df_original.groupby("Nama Kecamatan")[
              [
                  "Jumlah Penderita Diabetes",
                  "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)",
              ]
          ]
          .sum()
          .reset_index()
      )
      df_kec_pct_dm["Persentase DM"] = (
          df_kec_pct_dm["Jumlah Penderita Diabetes"]
          / df_kec_pct_dm[
              "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)"
          ]
          * 100
      ).fillna(0)
      df_kec_pct_dm = df_kec_pct_dm.sort_values(
          by="Persentase DM", ascending=False
      )

      fig_kec_pct_dm = px.bar(
          df_kec_pct_dm,
          x="Nama Kecamatan",
          y="Persentase DM",
          text=df_kec_pct_dm["Persentase DM"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase DM",
          color_continuous_scale="YlOrRd",
      )
      fig_kec_pct_dm.update_traces(textposition="outside")
      fig_kec_pct_dm.update_layout(
          xaxis_tickangle=-45,
          height=420,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_kec_pct_dm, use_container_width=True)

    st.markdown("---")

    # 4. Prevalensi Diabetes per Puskesmas (PKM) (Urut Tertinggi ke Terendah)
    if (
        "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)" in df.columns
        and "Jumlah Penderita Diabetes" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown(
          "**4. Persentase Penderita Diabetes (%) Per Puskesmas (PKM)**"
      )
      df_pkm_pct_dm = (
          df.groupby("Nama Faskes")[
              [
                  "Jumlah Penderita Diabetes",
                  "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)",
              ]
          ]
          .sum()
          .reset_index()
      )
      df_pkm_pct_dm["Persentase DM"] = (
          df_pkm_pct_dm["Jumlah Penderita Diabetes"]
          / df_pkm_pct_dm[
              "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)"
          ]
          * 100
      ).fillna(0)
      df_pkm_pct_dm = df_pkm_pct_dm.sort_values(
          by="Persentase DM", ascending=False
      )

      fig_pkm_pct_dm = px.bar(
          df_pkm_pct_dm,
          x="Nama Faskes",
          y="Persentase DM",
          text=df_pkm_pct_dm["Persentase DM"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase DM",
          color_continuous_scale="Oranges",
      )
      fig_pkm_pct_dm.update_traces(textposition="outside")
      fig_pkm_pct_dm.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_pkm_pct_dm, use_container_width=True)

  # --- TAB 5: CAKUPAN PENGOBATAN & ALASAN ---
  with tab5:
    st.subheader(
        "💊 Proporsi & Persentase Cakupan Pengobatan Penderita Per Puskesmas"
    )
    col_pie1, col_pie2 = st.columns(2)

    with col_pie1:
      st.markdown("**Hipertensi (Diberi Obat vs Belum/Tidak)**")
      sisa_ht = max(0, tot_ht - obat_ht)
      df_pie_ht = pd.DataFrame(
          {
              "Status": ["Diberikan Obat", "Belum/Tidak Diberikan"],
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
      st.markdown("**Diabetes (Diberi Obat vs Belum/Tidak)**")
      sisa_dm = max(0, tot_dm - obat_dm)
      df_pie_dm = pd.DataFrame(
          {
              "Status": ["Diberikan Obat", "Belum/Tidak Diberikan"],
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

    st.markdown("---")
    st.subheader(
        "📊 Grafik Persentase Pemberian Obat (%) dari Total Penderita Per"
        " Puskesmas"
    )

    # Persentase Pengobatan HT Per PKM (Urut Tertinggi ke Terendah)
    if (
        "Diberikan Obat" in df.columns
        and "Jumlah Penderita Hipertensi" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown("**Persentase Pengobatan Hipertensi (%) Per Puskesmas**")
      df_obat_pkm_ht = (
          df.groupby("Nama Faskes")[
              ["Diberikan Obat", "Jumlah Penderita Hipertensi"]
          ]
          .sum()
          .reset_index()
      )
      df_obat_pkm_ht["Persentase Obat HT"] = (
          df_obat_pkm_ht["Diberikan Obat"]
          / df_obat_pkm_ht["Jumlah Penderita Hipertensi"]
          * 100
      ).fillna(0)
      df_obat_pkm_ht = df_obat_pkm_ht.sort_values(
          by="Persentase Obat HT", ascending=False
      )

      fig_obat_pkm_ht = px.bar(
          df_obat_pkm_ht,
          x="Nama Faskes",
          y="Persentase Obat HT",
          text=df_obat_pkm_ht["Persentase Obat HT"].apply(
              lambda x: f"{x:.1f}%"
          ),
          color="Persentase Obat HT",
          color_continuous_scale="Blues",
      )
      fig_obat_pkm_ht.update_traces(textposition="outside")
      fig_obat_pkm_ht.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_obat_pkm_ht, use_container_width=True)

    st.markdown("---")

    # Persentase Pengobatan DM Per PKM (Urut Tertinggi ke Terendah)
    if (
        "Diberikan Obat Diabetes" in df.columns
        and "Jumlah Penderita Diabetes" in df.columns
        and "Nama Faskes" in df.columns
    ):
      st.markdown("**Persentase Pengobatan Diabetes (%) Per Puskesmas**")
      df_obat_pkm_dm = (
          df.groupby("Nama Faskes")[
              ["Diberikan Obat Diabetes", "Jumlah Penderita Diabetes"]
          ]
          .sum()
          .reset_index()
      )
      df_obat_pkm_dm["Persentase Obat DM"] = (
          df_obat_pkm_dm["Diberikan Obat Diabetes"]
          / df_obat_pkm_dm["Jumlah Penderita Diabetes"]
          * 100
      ).fillna(0)
      df_obat_pkm_dm = df_obat_pkm_dm.sort_values(
          by="Persentase Obat DM", ascending=False
      )

      fig_obat_pkm_dm = px.bar(
          df_obat_pkm_dm,
          x="Nama Faskes",
          y="Persentase Obat DM",
          text=df_obat_pkm_dm["Persentase Obat DM"].apply(
              lambda x: f"{x:.1f}%"
          ),
          color="Persentase Obat DM",
          color_continuous_scale="Greens",
      )
      fig_obat_pkm_dm.update_traces(textposition="outside")
      fig_obat_pkm_dm.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
          xaxis={"categoryorder": "total descending"},
      )
      st.plotly_chart(fig_obat_pkm_dm, use_container_width=True)

    st.markdown("---")
    st.subheader("⚠️ Analisis Alasan Tidak Diberikan Obat")

    col_al_o1, col_al_o2 = st.columns(2)
    with col_al_o1:
      st.markdown("**Alasan Hipertensi Tidak Diberikan Obat**")
      cols_alasan_ht = [
          c for c in df.columns if "Alasan Tidak Diberikan Obat Hipertensi" in c
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
          fig_als_ht.update_traces(
              texttemplate="%{text:,}", textposition="outside"
          )
          fig_als_ht.update_layout(
              height=400, yaxis={"categoryorder": "total ascending"}
          )
          st.plotly_chart(fig_als_ht, use_container_width=True)
        else:
          st.info("Tidak ada data alasan.")

    with col_al_o2:
      st.markdown("**Alasan Diabetes Melitus Tidak Diberikan Obat**")
      cols_alasan_dm = [
          c for c in df.columns if "Alasan Tidak Diberikan Obat Diabetes" in c
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
          fig_als_dm.update_traces(
              texttemplate="%{text:,}", textposition="outside"
          )
          fig_als_dm.update_layout(
              height=400, yaxis={"categoryorder": "total ascending"}
          )
          st.plotly_chart(fig_als_dm, use_container_width=True)
        else:
          st.info("Tidak ada data alasan.")

  # --- TAB 6: TABEL DETAIL ---
  with tab6:
    st.subheader("📋 Tabel Data Detail Laporan")
    st.dataframe(df, use_container_width=True)

else:
  st.warning(
      "⚠️ File `data_default.xlsx` belum terbaca otomatis. Silakan pastikan file"
      " tersebut sudah di-commit/push ke repository GitHub Anda sejajar dengan"
      " file `app.py`, atau gunakan tombol upload di atas untuk memasukkan"
      " data secara manual."
  )
