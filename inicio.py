import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(
    page_title="Smart Intelligence Tools",
    page_icon="https://github.com/NNHOLDING/marcas_sit/raw/main/sitfavicon.ico",
    layout="centered"
)

# Configuración Google Sheets
SPREADSHEET_NAME = "WMS SIT"
SHEET_NAME = "Usuarios"

def get_sheet():
    creds_dict = json.loads(st.secrets["google"]["credentials"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

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

def mostrar_login():
    st.markdown("<div style='max-width: 400px; margin: auto;'>", unsafe_allow_html=True)

    st.image("https://github.com/NNHOLDING/WMSSIT/blob/main/logo3.png?raw=true", use_container_width=True)
    st.title("🔐 WMS - Inicio de sesión")

    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")

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
    st.subheader("🔁 Restablecer contraseña")

    usuario_reset = st.text_input("Usuario para restablecer")
    nueva_pass = st.text_input("Nueva contraseña", type="password")

    if st.button("Restablecer"):
        if restablecer_contraseña(usuario_reset.strip(), nueva_pass.strip()):
            st.success("Contraseña actualizada correctamente")
        else:
            st.error("No se pudo actualizar la contraseña")

    st.markdown("</div>", unsafe_allow_html=True)

    # Footer institucional
    st.markdown("""
        <hr style="margin-top: 50px; border: none; border-top: 1px solid #ccc;" />
        <div style="text-align: center; color: gray; font-size: 0.9em; margin-top: 20px;">
            Powered by NN HOLDING SOLUTIONS, Ever Be Better &copy; 2025, Todos los derechos reservados
        </div>
    """, unsafe_allow_html=True)
