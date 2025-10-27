import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from google_sheets import generate_lpns, show_disponibles, get_sheet

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
    from inicio import mostrar_login
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

    # 🧾 FORMULARIO DE GENERACIÓN (solo para Admin)
    if seleccion == "LPNs Generados":
        if st.session_state.get("rol") == "Admin":
            st.subheader("🧾 Generar LPNs")
            with st.form("form_lpn"):
                tipo_etiqueta = st.selectbox("Tipo de etiqueta", ["Etiquetas IB", "Etiquetas OB"])
                cantidad = st.number_input("Cantidad a generar", min_value=1, step=1)
                submitted = st.form_submit_button("Generar")
                if submitted:
                    if cantidad > 0:
                        if "usuario" in st.session_state and "bodega" in st.session_state:
                            nuevos = generate_lpns(cantidad, st.session_state.usuario, st.session_state.bodega, tipo_etiqueta)
                            st.success(f"{len(nuevos)} LPNs generados exitosamente.")
                            st.dataframe(pd.DataFrame(nuevos, columns=["Número LPN", "Fecha creación", "Creado por", "Estado", "Bodega"]))
                        else:
                            st.error("Usuario o bodega no definidos en sesión.")
                    else:
                        st.warning("La cantidad debe ser mayor a cero.")
        else:
            st.info("Solo los usuarios con rol Admin pueden generar LPNs.")

        # 📦 GRILLA CON FILTROS Y PAGINACIÓN (visible para todos)
        show_disponibles()

    else:
        try:
            df = get_sheet(seleccion)
            if df.empty:
                st.warning(f"La hoja '{seleccion}' está vacía o no tiene registros.")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo cargar la hoja '{seleccion}': {e}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.update({"logueado": False, "rol": "", "usuario": ""})
        st.rerun()

# 🖋️ Footer institucional (siempre visible)
st.markdown("""
<hr style="margin-top: 40px; border: none; border-top: 1px solid #ccc;" />
<div style="text-align: center; color: gray; font-size: 0.85em; margin-top: 10px;">
    Powered by NN HOLDING SOLUTIONS, Ever Be Better &copy; 2025
</div>
""", unsafe_allow_html=True)
