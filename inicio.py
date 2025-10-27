import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# Configuración Google Sheets
SPREADSHEET_NAME = "WMS SIT"
SHEET_NAME = "Usuarios"

# Conexión a la hoja usando st.secrets
def get_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

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

        fila = df[df["Usuario"] == usuario].index[0] + 2  # +2 por encabezado y base 1
        col = data[0].index("Contraseña") + 1
        sheet.update_cell(fila, col, nueva_contraseña)
        return True
    except Exception as e:
        st.error(f"No se pudo actualizar la contraseña: {e}")
        return False

# Interfaz de login
def mostrar_login():
    # Estilo para campos centrados y compactos
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 20px;
        }
        .login-container input {
            width: 100% !important;
            padding: 8px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .login-container button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.image("https://github.com/NNHOLDING/WMSSIT/blob/main/logo3.png?raw=true", width=180)
    st.markdown("<h4 style='text-align: center;'>🔐 WMS - Inicio de sesión</h4>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario", key="usuario")
    contraseña = st.text_input("Contraseña", type="password", key="contraseña")

    mostrar = st.checkbox("Mostrar contraseña")
    if mostrar:
        st.text_input("Contraseña visible", value=contraseña, disabled=True)

    if st.button("Iniciar sesión"):
        rol = validar_login(usuario.strip(), contraseña.strip())
        if rol:
            st.session_state.logueado = True
            st.session_state.rol = rol
            st.session_state.usuario = usuario
            st.success(f"Bienvenido {usuario}\nRol: {rol}")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.markdown("---")
    st.markdown("<h5 style='text-align: center;'>🔁 Restablecer contraseña</h5>", unsafe_allow_html=True)

    usuario_reset = st.text_input("Usuario para restablecer", key="usuario_reset")
    nueva_pass = st.text_input("Nueva contraseña", type="password", key="nueva_pass")

    if st.button("Restablecer"):
        if restablecer_contraseña(usuario_reset.strip(), nueva_pass.strip()):
            st.success("Contraseña actualizada correctamente")
        else:
            st.error("No se pudo actualizar la contraseña")

    st.markdown("</div>", unsafe_allow_html=True)
