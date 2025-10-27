import streamlit as st
from inicio import mostrar_login
from google_sheets import get_sheet
import pandas as pd
import pytz
from datetime import datetime

# 🌎 Zona horaria Costa Rica
cr_timezone = pytz.timezone("America/Costa_Rica")
hora_actual = datetime.now(cr_timezone).strftime("%d/%m/%Y %H:%M")

# ⚙️ Configuración de página
st.set_page_config(page_title="WMS SIT", page_icon="📦", layout="wide")

# 🧠 Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state.update({"logueado": False, "rol": "", "usuario": ""})

# 🔐 Pantalla de login
if not st.session_state.logueado:
    mostrar_login()

# 🧾 Interfaz principal
else:
    st.sidebar.header("📁 Módulos")
    hojas = [
        "LPNs", "Recepción SKUs", "LPNs Eliminados", "LPNs Generados",
        "Ubicaciones", "Resumen de Almacenamiento", "Reportes por Pasillo"
    ]
    seleccion = st.sidebar.selectbox("Selecciona una hoja", hojas)

    st.markdown(f"### 📄 {seleccion}")
    st.caption(f"🕒 {hora_actual} &nbsp;&nbsp; 👤 {st.session_state.usuario} &nbsp;&nbsp; 🔐 {st.session_state.rol}")

    try:
        df = get_sheet(seleccion)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar la hoja '{seleccion}': {e}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.update({"logueado": False, "rol": "", "usuario": ""})
        st.rerun()

# 🖋️ Footer institucional
st.markdown("""
<hr style="margin-top: 40px; border: none; border-top: 1px solid #ccc;" />
<div style="text-align: center; color: gray; font-size: 0.85em; margin-top: 10px;">
    Powered by NN HOLDING SOLUTIONS, Ever Be Better &copy; 2025
</div>
""", unsafe_allow_html=True)
