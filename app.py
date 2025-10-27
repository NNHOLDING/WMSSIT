import streamlit as st
from inicio import mostrar_login, get_sheet
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import datetime

# Configuración de zona horaria Costa Rica
cr_timezone = pytz.timezone("America/Costa_Rica")
hora_actual = datetime.now(cr_timezone).strftime("%d/%m/%Y %H:%M")

# Configuración de página
st.set_page_config(
    page_title="WMS SIT",
    page_icon="📦",
    layout="wide"
)

# Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.rol = ""
    st.session_state.usuario = ""

# Mostrar login si no está autenticado
if not st.session_state.logueado:
    # Mostrar logo
    st.image("https://drive.google.com/uc?export=view&id=1CgMBkG3rUwWOE9OodfBN1Tjinrl0vMOh", use_column_width=True)
    mostrar_login()

# Mostrar contenido si está autenticado
else:
    st.sidebar.title("📁 Módulos disponibles")
    hojas_disponibles = [
        "LPNs",
        "Recepción SKUs",
        "LPNs Eliminados",
        "LPNs Generados",
        "Ubicaciones",
        "Resumen de Almacenamiento",
        "Reportes por Pasillo"
    ]
    seleccion = st.sidebar.selectbox("Selecciona una hoja", hojas_disponibles)

    st.title(f"📄 Datos de: {seleccion}")
    st.caption(f"🕒 Hora local: {hora_actual}")

    # Conexión a la hoja seleccionada
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    CREDS_FILE = "credentials.json"
    SPREADSHEET_NAME = "WMS SIT"

    def get_hoja(nombre):
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME).worksheet(nombre)
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        return df

    try:
        df = get_hoja(seleccion)
        st.dataframe(df)
    except Exception as e:
        st.error(f"No se pudo cargar la hoja '{seleccion}': {e}")

    # Cierre de sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logueado = False
        st.session_state.rol = ""
        st.session_state.usuario = ""
        st.rerun()
