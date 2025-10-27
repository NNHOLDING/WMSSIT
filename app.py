import streamlit as st
import pandas as pd
import pytz
from datetime import datetime

from inicio import mostrar_login
from google_sheets import get_sheet, generate_lpns
from utils import show_disponibles

# 🌎 Zona horaria Costa Rica
cr_timezone = pytz.timezone("America/Costa_Rica")
hora_actual = datetime.now(cr_timezone).strftime("%d/%m/%Y %H:%M")

# ⚙️ Configuración de página
st.set_page_config(page_title="WMS SIT", page_icon="📦", layout="wide")

# 🧠 Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state.update({"logueado": False, "rol": "", "usuario": "", "bodega": ""})

# 🔐 Pantalla de login
if not st.session_state.logueado:
    mostrar_login()

# 🧾 Interfaz principal
else:
    st.sidebar.header("📁 Módulos disponibles")
    hojas = [
        "LPNs", "Recepción SKUs", "LPNs Eliminados", "LPNs Generados",
        "Ubicaciones", "Resumen de Almacenamiento", "Reportes por Pasillo"
    ]
    seleccion = st.sidebar.selectbox("Selecciona una hoja", hojas)

    st.markdown(f"### 📄 {seleccion}")
    st.caption(f"🕒 {hora_actual} &nbsp;&nbsp; 👤 {st.session_state.usuario} &nbsp;&nbsp; 🔐 {st.session_state.rol}")

    # 🧾 Módulo especial para generación y visualización de LPNs
    if seleccion == "LPNs Generados":
        if st.session_state.rol == "Admin":
            st.subheader("🧾 Generar LPNs")
            with st.form("form_lpn"):
                tipo_etiqueta = st.selectbox("Tipo de etiqueta", ["Etiquetas IB", "Etiquetas OB"])
                cantidad = st.number_input("Cantidad a generar", min_value=1, step=1)
                submitted = st.form_submit_button("Generar")

                if submitted:
                    usuario = st.session_state.get("usuario")
                    bodega = st.session_state.get("bodega")
                    if usuario and bodega:
                        nuevos = generate_lpns(cantidad, usuario, bodega, tipo_etiqueta)
                        st.success(f"{len(nuevos)} LPNs generados exitosamente.")
                        st.dataframe(pd.DataFrame(nuevos, columns=["Número LPN", "Fecha creación", "Creado por", "Estado", "Bodega"]))
                    else:
                        st.error("Usuario o bodega no definidos en sesión.")
        else:
            st.info("Solo los usuarios con rol Admin pueden generar LPNs.")

        # 📦 Mostrar grilla con filtros y exportación
        show_disponibles()

    # 📊 Visualización genérica para otras hojas
    else:
        try:
            df = get_sheet(seleccion)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo cargar la hoja '{seleccion}': {e}")

    # 🔚 Cierre de sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.update({"logueado": False, "rol": "", "usuario": "", "bodega": ""})
        st.rerun()

# 🖋️ Footer institucional
st.markdown("""
<hr style="margin-top: 40px; border: none; border-top: 1px solid #ccc;" />
<div style="text-align: center; color: gray; font-size: 0.85em; margin-top: 10px;">
    Powered by NN HOLDING SOLUTIONS, Ever Be Better &copy; 2025
</div>
""", unsafe_allow_html=True)
