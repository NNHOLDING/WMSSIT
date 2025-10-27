import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# Configuración Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"
SPREADSHEET_NAME = "WMS SIT"
SHEET_LPN = "LPNs generados"

# Función para conectar con hoja LPNs
def get_lpn_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_LPN)
    return sheet

# Obtener último consecutivo por tipo
def get_last_lpn(sheet, tipo):
    data = sheet.col_values(1)[1:] # Ignorar encabezado
    prefix = "IB" if tipo == "Etiquetas IB" else "OB"
    data = [d for d in data if d.startswith(prefix)]
    if not data:
        return 0
    last = data[-1]
    return int(last[-6:]) # Extraer últimos 6 dígitos

# Generar LPNs
def generate_lpns(cantidad, usuario, bodega, tipo):
    sheet = get_lpn_sheet()
    last = get_last_lpn(sheet, tipo)
    nuevos = []
    for i in range(1, cantidad + 1):
        consecutivo = str(last + i).zfill(6)
        prefix = "IB" if tipo == "Etiquetas IB" else "OB"
        lpn = f"{prefix}{bodega}506{consecutivo}"
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevos.append([lpn, fecha, usuario, "Disponible", bodega])
    sheet.append_rows(nuevos)
    return nuevos

# Mostrar grilla con filtros y paginación
def show_disponibles():
    sheet = get_lpn_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    st.subheader("📦 LPNs disponibles con filtros")

    estados = df["Estado"].unique().tolist()
    bodegas = df["Bodega"].unique().tolist()
    fechas = pd.to_datetime(df["Fecha creación"])

    col1, col2, col3 = st.columns(3)

    with col1:
        estado_sel = st.selectbox("Filtrar por estado", ["Todos"] + estados)

    with col2:
        bodega_sel = st.selectbox("Filtrar por bodega", ["Todas"] + bodegas)

    with col3:
        fecha_rango = st.date_input("Filtrar por fecha", value=(fechas.min(), fechas.max()))

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

    # PAGINACIÓN
    st.markdown("### 📄 Resultados paginados")
    page_size = st.selectbox("Registros por página", [10, 25, 50], index=0)
    total_rows = len(filtro_df)
    total_pages = (total_rows - 1) // page_size + 1

    if "page" not in st.session_state:
        st.session_state.page = 1

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    with col_pag1:
        if st.button("⬅️ Anterior") and st.session_state.page > 1:
            st.session_state.page -= 1
    with col_pag3:
        if st.button("Siguiente ➡️") and st.session_state.page < total_pages:
            st.session_state.page += 1

    start_idx = (st.session_state.page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_df = filtro_df.iloc[start_idx:end_idx]

    st.write(f"Página {st.session_state.page} de {total_pages}")
    st.dataframe(paginated_df, use_container_width=True)

    # Exportar CSV solo de la página actual
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

# 🧾 FORMULARIO DE GENERACIÓN (solo para Admin)
if st.session_state.get("rol") == "Admin":
    st.subheader("🧾 Generar LPNs")

    with st.form("form_lpn"):
        tipo_etiqueta = st.selectbox("Tipo de etiqueta", ["Etiquetas IB", "Etiquetas OB"])
        cantidad = st.number_input("Cantidad a generar", min_value=1, step=1)
        submitted = st.form_submit_button("Generar")

        if submitted:
            if cantidad > 0:
                if "usuario" in st.session_state and "bodega" in st.session_state:
                    nuevos = generate_lpns(cantidad, st.session_state.usuario, st.session_state.bodega, tipo_etiqueta)
                    st.success(f"{len(nuevos)} LPNs generados exitosamente.")
                    st.write("Últimos LPNs generados:")
                    st.dataframe(pd.DataFrame(nuevos, columns=["Número LPN", "Fecha creación", "Creado por", "Estado", "Bodega"]))
                else:
                    st.error("Usuario o bodega no definidos en sesión.")
            else:
                st.warning("La cantidad debe ser mayor a cero.")
else:
    st.info("Solo los usuarios con rol Admin pueden generar LPNs.")

# 📦 GRILLA CON FILTROS Y PAGINACIÓN (visible para todos)
show_disponibles()
