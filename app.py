import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuración Google Sheets
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "WMS SIT"
SHEET_USUARIOS = "Usuarios"

# Conexión usando st.secrets
def get_worksheet(sheet_name):
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(sheet_name)
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

# Autenticación
def validar_login(usuario, contraseña):
    try:
        df_usuarios = get_worksheet(SHEET_USUARIOS)
        user_row = df_usuarios[
            (df_usuarios["Usuario"] == usuario) & (df_usuarios["Contraseña"] == contraseña)
        ]
        if not user_row.empty:
            return user_row.iloc[0]["Rol"]
        else:
            return None
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

# Configuración de página
st.set_page_config(page_title="WMS SIT", layout="wide")

# Estado de sesión
if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.rol = ""
    st.session_state.usuario = ""

# Login
if not st.session_state.logueado:
    st.title("🔐 Inicio de sesión - WMS SIT")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        rol = validar_login(usuario.strip(), contraseña.strip())
        if rol:
            st.session_state.logueado = True
            st.session_state.rol = rol
            st.session_state.usuario = usuario
            st.success(f"Bienvenido {usuario} - Rol: {rol}")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# Menú principal
if st.session_state.logueado:
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
    try:
        df = get_worksheet(seleccion)
        st.dataframe(df)
    except Exception as e:
        st.error(f"No se pudo cargar la hoja '{seleccion}': {e}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logueado = False
        st.session_state.rol = ""
        st.session_state.usuario = ""
        st.rerun()
