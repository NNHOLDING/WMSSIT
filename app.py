import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"
SPREADSHEET_NAME = "TuNombreDeHoja"  # Reemplaza con el nombre real

# Función para conectar con Google Sheets
def get_worksheet(sheet_name):
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(sheet_name)
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

# Función de login
def validar_login(usuario, contraseña):
    try:
        df_usuarios = get_worksheet("Usuarios")
        user_row = df_usuarios[(df_usuarios["Usuario"] == usuario) & (df_usuarios["Contraseña"] == contraseña)]
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
    st.title("🔐 Inicio de sesión - WMS Smart Intelligence Tools")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        rol = validar_login(usuario, contraseña)
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
    opciones = [
        "LPNs",
        "Recepción SKUs",
        "LPNs Eliminados",
        "LPNs Generados",
        "Ubicaciones",
        "Resumen de Almacenamiento",
        "Reportes por Pasillo"
    ]
    seleccion = st.sidebar.selectbox("Selecciona una hoja", opciones)

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