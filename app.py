import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import datetime

# Configuración Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"
SPREADSHEET_NAME = "WMS SIT"
SHEET_NAME = "Usuarios"

# Zona horaria Costa Rica
cr_timezone = pytz.timezone("America/Costa_Rica")
hora_actual = datetime.now(cr_timezone).strftime("%d/%m/%Y %H:%M")

# Conexión a hoja de usuarios
def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# Validación de login
def validar_login(usuario, contraseña):
    try:
        sheet = get_sheet()
        users = sheet.get_all_records()
        for user in users:
            if user["Usuario"] == usuario and user["Contraseña"] == contraseña:
                return user.get("Rol", "Sin rol")
        return None
    except Exception as e:
        st.error(f"No se pudo conectar: {e}")
        return None

# Restablecer contraseña
def restablecer_contraseña(usuario, nueva_contraseña):
    try:
        sheet = get_sheet()
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        if usuario not in df["Usuario"].values:
            return False
        fila = df[df["Usuario"] == usuario].index[0] + 2
        col = data[0].index("Contraseña") + 1
        sheet.update_cell(fila, col, nueva_contraseña)
        return True
    except Exception as e:
        st.error(f"No se pudo actualizar la contraseña: {e}")
        return False

# Interfaz de login
def mostrar_login():
    st.markdown(f"""
        <div style='text-align: center;'>
            <img src='https://github.com/NNHOLDING/WMSSIT/blob/main/logo3.png?raw=true' width='220'>
            <h3 style='margin-top: 10px;'>🔐 WMS - Inicio de sesión</h3>
            <p style='font-size: 0.9em; color: gray;'>Hora local: {hora_actual}</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        st.markdown("#### Credenciales de acceso")
        col1, col2 = st.columns(2)
        with col1:
            usuario = st.text_input("Usuario", placeholder="Código o nombre")
        with col2:
            contraseña = st.text_input("Contraseña", type="password", placeholder="Clave de acceso")

        mostrar = st.checkbox("Mostrar contraseña")
        if mostrar:
            st.text_input("Contraseña visible", value=contraseña, disabled=True)

        submitted = st.form_submit_button("Ingresar")
        if submitted:
            rol = validar_login(usuario.strip(), contraseña.strip())
            if rol:
                st.session_state.logueado = True
                st.session_state.rol = rol
                st.session_state.usuario = usuario
                st.success(f"Bienvenido {usuario} - Rol: {rol}")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    st.markdown("---")
    st.markdown("#### 🔁 Restablecer contraseña")

    with st.form("reset_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            usuario_reset = st.text_input("Usuario para restablecer", placeholder="Código o nombre")
        with col2:
            nueva_pass = st.text_input("Nueva contraseña", type="password", placeholder="Nueva clave")

        reset = st.form_submit_button("Restablecer")
        if reset:
            if restablecer_contraseña(usuario_reset.strip(), nueva_pass.strip()):
                st.success("Contraseña actualizada correctamente")
            else:
                st.error("No se pudo actualizar la contraseña")

    st.markdown("""
        <hr style="margin-top: 30px; border: none; border-top: 1px solid #ccc;" />
        <div style="text-align: center; color: gray; font-size: 0.85em; margin-top: 10px;">
            Powered by NN HOLDING SOLUTIONS, Ever Be Better &copy; 2025
        </div>
    """, unsafe_allow_html=True)
