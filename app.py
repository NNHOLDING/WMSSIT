import streamlit as st
from inicio import mostrar_login, get_sheet
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import datetime

# Zona horaria Costa Rica
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
    st.image("https://github.com/NNHOLDING/WMSSIT/blob/main/logo3.png?raw=true", use_column_width=True)
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
    st.markdown(f"👤 Usuario: **{st.session_state.usuario}** &nbsp;&nbsp;&nbsp; 🔐 Rol: **{st.session_state.rol}**")

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

# Footer institucional
st.markdown("""
    <hr style="margin-top: 50px; border: none; border-top: 1px solid #ccc;" />
    <div style="text-align: center; color: gray; font-size: 0.9em; margin-top: 20px;">
        Powered by NN HOLDING SOLUTIONS, Ever Be Better &copy; 2025, Todos los derechos reservados
    </div>
""", unsafe_allow_html=True)
