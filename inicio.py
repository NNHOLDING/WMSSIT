import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"
SPREADSHEET_NAME = "WMS SIT"
SHEET_NAME = "Usuarios"

# Conexión a la hoja
def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
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
