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

  # 2. Filter Wilayah Fleksibel (Kabupaten -> Kecamatan -> Faskes) di Bagian Atas
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
  obat_ht = df["Diberikan Obat"].sum() if "Diberikan Obat" in df.columns else 0
  persen_ht = (obat_ht / tot_ht * 100) if tot_ht > 0 else 0

  edu_ht = (
      df["Edukasi Hipertensi"].sum()
      if "Edukasi Hipertensi" in df.columns
      else 0
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
  obat_dm = (
      df["Diberikan Obat Diabetes"].sum()
      if "Diberikan Obat Diabetes" in df.columns
      else 0
  )
  persen_dm = (obat_dm / tot_dm * 100) if tot_dm > 0 else 0

  edu_dm = (
      df["Edukasi Diabetes"].sum() if "Edukasi Diabetes" in df.columns else 0
  )
  persen_edu_dm = (edu_dm / tot_dm * 100) if tot_dm > 0 else 0

  diag_ht = (
      df["Diagnosis Hipertensi"].sum()
      if "Diagnosis Hipertensi" in df.columns
      else 0
  )
  diag_dm = (
      df["Diberikan Diagnosis"].sum() if "Diberikan Diagnosis" in df.columns else 0
  )

  group_col = "Nama Faskes" if pilih_kec != "Semua" else "Nama Kecamatan"

  # ==========================================
  # 3. PEMBUATAN MENU KESAMPING (TABS)
  # ==========================================
  tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
      "📊 Ringkasan & Kasus",
      "📋 Analisis Diagnosis",
      "🗣️ Cakupan Edukasi",
      "📈 Prevalensi Wilayah",
      "🍩 Cakupan Pengobatan & Alasan",
      "📁 Tabel Data Detail",
  ])

  # --- TAB 1: RINGKASAN & GRAFIK KASUS ---
  with tab1:
    st.subheader("📊 Ringkasan Skrining, Kasus, & Pengobatan")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
      st.metric(
          "Total Penderita Hipertensi",
          f"{tot_ht:,}",
          delta=f"{prev_ht:.1f}% dari {scr_ht:,} diskrining",
      )
    with c2:
      st.metric(
          "Hipertensi Diberikan Obat",
          f"{obat_ht:,}",
          delta=f"{persen_ht:.1f}% dari penderita",
      )
    with c3:
      st.metric(
          "Total Penderita Diabetes",
          f"{tot_dm:,}",
          delta=f"{prev_dm:.1f}% dari {scr_dm:,} diskrining",
      )
    with c4:
      st.metric(
          "Diabetes Diberikan Obat",
          f"{obat_dm:,}",
          delta=f"{persen_dm:.1f}% dari penderita",
      )

    st.markdown("---")

    if "Jumlah Penderita Hipertensi" in df.columns:
      st.subheader("📈 Grafik Jumlah Penderita Hipertensi per Wilayah")
      chart_df_ht = (
          df.groupby(group_col)["Jumlah Penderita Hipertensi"].sum().reset_index()
      )
      fig_bar_ht = px.bar(
          chart_df_ht,
          x=group_col,
          y="Jumlah Penderita Hipertensi",
          text="Jumlah Penderita Hipertensi",
          color="Jumlah Penderita Hipertensi",
          color_continuous_scale="Blues",
      )
      fig_bar_ht.update_traces(texttemplate="%{text:,}", textposition="outside")
      fig_bar_ht.update_layout(xaxis_tickangle=-45, height=450)
      st.plotly_chart(fig_bar_ht, use_container_width=True)

    if "Jumlah Penderita Diabetes" in df.columns:
      st.subheader("📈 Grafik Jumlah Penderita Diabetes per Wilayah")
      chart_df_dm = (
          df.groupby(group_col)["Jumlah Penderita Diabetes"].sum().reset_index()
      )
      fig_bar_dm = px.bar(
          chart_df_dm,
          x=group_col,
          y="Jumlah Penderita Diabetes",
          text="Jumlah Penderita Diabetes",
          color="Jumlah Penderita Diabetes",
          color_continuous_scale="Greens",
      )
      fig_bar_dm.update_traces(texttemplate="%{text:,}", textposition="outside")
      fig_bar_dm.update_layout(xaxis_tickangle=-45, height=450)
      st.plotly_chart(fig_bar_dm, use_container_width=True)

  # --- TAB 2: ANALISIS DIAGNOSIS & ALASANNYA ---
  with tab2:
    st.subheader("📋 Analisis Penegakan Diagnosis (HT & DM)")
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

  # --- TAB 3: CAKUPAN EDUKASI (DENGAN PERSENTASE) ---
  with tab3:
    st.subheader("🗣️ Analisis Cakupan Pemberian Edukasi (HT & DM)")

    # Metrik Ringkasan Edukasi Berbasis Persentase
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

    col_e1, col_e2 = st.columns(2)
    with col_e1:
      st.markdown("**Grafik Jumlah Edukasi Hipertensi per Wilayah**")
      if "Edukasi Hipertensi" in df.columns and "Nama Faskes" in df.columns:
        chart_edu_ht = (
            df.groupby(group_col)["Edukasi Hipertensi"].sum().reset_index()
        )
        fig_edu_ht = px.bar(
            chart_edu_ht,
            x=group_col,
            y="Edukasi Hipertensi",
            text="Edukasi Hipertensi",
            color="Edukasi Hipertensi",
            color_continuous_scale="Blues",
        )
        fig_edu_ht.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_edu_ht.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_edu_ht, use_container_width=True)

    with col_e2:
      st.markdown("**Grafik Jumlah Edukasi Diabetes per Wilayah**")
      if "Edukasi Diabetes" in df.columns and "Nama Faskes" in df.columns:
        chart_edu_dm = (
            df.groupby(group_col)["Edukasi Diabetes"].sum().reset_index()
        )
        fig_edu_dm = px.bar(
            chart_edu_dm,
            x=group_col,
            y="Edukasi Diabetes",
            text="Edukasi Diabetes",
            color="Edukasi Diabetes",
            color_continuous_scale="Greens",
        )
        fig_edu_dm.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_edu_dm.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_edu_dm, use_container_width=True)

  # --- TAB 4: PREVALENSI PERSENTASE WILAYAH ---
  with tab4:
    st.subheader(
        "📊 Grafik Persentase (Prevalensi) Kasus dari Jumlah Diskrining per"
        " Wilayah"
    )

    if (
        "Jumlah Orang Diperiksa Tekanan Darah" in df.columns
        and "Jumlah Penderita Hipertensi" in df.columns
    ):
      st.markdown("**Persentase Penderita Hipertensi (%) dari Orang Diperiksa TD**")
      df_pct_ht = (
          df.groupby(group_col)[
              [
                  "Jumlah Penderita Hipertensi",
                  "Jumlah Orang Diperiksa Tekanan Darah",
              ]
          ]
          .sum()
          .reset_index()
      )
      df_pct_ht["Persentase HT"] = (
          df_pct_ht["Jumlah Penderita Hipertensi"]
          / df_pct_ht["Jumlah Orang Diperiksa Tekanan Darah"]
          * 100
      ).fillna(0)
      fig_pct_ht = px.bar(
          df_pct_ht,
          x=group_col,
          y="Persentase HT",
          text=df_pct_ht["Persentase HT"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase HT",
          color_continuous_scale="Teal",
      )
      fig_pct_ht.update_traces(textposition="outside")
      fig_pct_ht.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
      )
      st.plotly_chart(fig_pct_ht, use_container_width=True)

    st.markdown("---")

    if (
        "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)" in df.columns
        and "Jumlah Penderita Diabetes" in df.columns
    ):
      st.markdown(
          "**Persentase Penderita Diabetes (%) dari Orang Diperiksa Gula Darah**"
      )
      df_pct_dm = (
          df.groupby(group_col)[
              [
                  "Jumlah Penderita Diabetes",
                  "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)",
              ]
          ]
          .sum()
          .reset_index()
      )
      df_pct_dm["Persentase DM"] = (
          df_pct_dm["Jumlah Penderita Diabetes"]
          / df_pct_dm[
              "Jumlah Orang Diperiksa gula darah (Usia ≥ 18 Tahun)"
          ]
          * 100
      ).fillna(0)
      fig_pct_dm = px.bar(
          df_pct_dm,
          x=group_col,
          y="Persentase DM",
          text=df_pct_dm["Persentase DM"].apply(lambda x: f"{x:.1f}%"),
          color="Persentase DM",
          color_continuous_scale="YlOrRd",
      )
      fig_pct_dm.update_traces(textposition="outside")
      fig_pct_dm.update_layout(
          xaxis_tickangle=-45,
          height=450,
          yaxis_title="Persentase (%)",
          yaxis_ticksuffix="%",
      )
      st.plotly_chart(fig_pct_dm, use_container_width=True)

  # --- TAB 5: PENGOBATAN & ANALISIS ALASAN TIDAK DIBERI OBAT ---
  with tab5:
    st.subheader("🍩 Proporsi Pemberian Pengobatan pada Penderita")
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
    st.subheader("⚠️ Analisis Alasan Tidak Diberikan Obat")

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
        fig_als_ht.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_als_ht.update_layout(
            height=400, yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig_als_ht, use_container_width=True)
      else:
        st.info("Tidak ada data alasan.")

    st.markdown("---")

    st.markdown("**Alasan Diabetes Tidak Diberikan Obat**")
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
        fig_als_dm.update_traces(texttemplate="%{text:,}", textposition="outside")
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
      "Silakan upload file Excel laporan CKG Anda terlebih dahulu melalui"
      " tombol di atas."
  )