import pandas as pd
from datetime import datetime
import streamlit as st
from google_sheets import get_lpn_sheet

def show_disponibles():
    sheet = get_lpn_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    st.subheader("📦 LPNs disponibles con filtros")

    estados = df["Estado"].unique().tolist()
    bodegas = df["Bodega"].unique().tolist()
    fechas = pd.to_datetime(df["Fecha creación"])

    col1, col2, col3 = st.columns(3)
    estado_sel = col1.selectbox("Filtrar por estado", ["Todos"] + estados)
    bodega_sel = col2.selectbox("Filtrar por bodega", ["Todas"] + bodegas)
    fecha_rango = col3.date_input("Filtrar por fecha", value=(fechas.min(), fechas.max()))

    filtro_df = df.copy()
    if estado_sel != "Todos":
        filtro_df = filtro_df[filtro_df["Estado"] == estado_sel]
    if bodega_sel != "Todas":
        filtro_df = filtro_df[filtro_df["Bodega"] == bodega_sel]
    if isinstance(fecha_rango, tuple) and len(fecha_rango) == 2:
        fecha_inicio, fecha_fin = fecha_rango
        filtro_df["Fecha creación"] = pd.to_datetime(filtro_df["Fecha creación"])
        filtro_df = filtro_df[
            (filtro_df["Fecha creación"] >= pd.to_datetime(fecha_inicio)) &
            (filtro_df["Fecha creación"] <= pd.to_datetime(fecha_fin))
        ]

    st.markdown("### 📄 Resultados paginados")
    page_size = st.selectbox("Registros por página", [10, 25, 50], index=0)
    total_rows = len(filtro_df)
    total_pages = (total_rows - 1) // page_size + 1

    if "page" not in st.session_state:
        st.session_state.page = 1

    col_pag1, _, col_pag3 = st.columns([1, 2, 1])
    if col_pag1.button("⬅️ Anterior") and st.session_state.page > 1:
        st.session_state.page -= 1
    if col_pag3.button("Siguiente ➡️") and st.session_state.page < total_pages:
        st.session_state.page += 1

    start_idx = (st.session_state.page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_df = filtro_df.iloc[start_idx:end_idx]

    st.write(f"Página {st.session_state.page} de {total_pages}")
    st.dataframe(paginated_df, use_container_width=True)

    if not paginated_df.empty:
        tipo_actual = "IB" if "IB" in paginated_df["Número LPN"].iloc[0] else "OB"
        fecha_actual = datetime.now().strftime("%Y%m%d")
        nombre_archivo = f"{tipo_actual}_lpns_pagina_{st.session_state.page}_{fecha_actual}.csv"
        csv = paginated_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📤 Exportar CSV de esta página",
            data=csv,
            file_name=nombre_archivo,
            mime="text/csv"
        )