import streamlit as st
from google_sheets import generate_lpns
from utils import show_disponibles
import pandas as pd

st.set_page_config(page_title="Gestión de LPNs", layout="wide")

def formulario_generacion():
    st.subheader("🧾 Generar LPNs")
    with st.form("form_lpn"):
        tipo_etiqueta = st.selectbox("Tipo de etiqueta", ["Etiquetas IB", "Etiquetas OB"])
        cantidad = st.number_input("Cantidad a generar", min_value=1, step=1)
        submitted = st.form_submit_button("Generar")

        if submitted:
            if cantidad > 0:
                usuario = st.session_state.get("usuario")
                bodega = st.session_state.get("bodega")
                if usuario and bodega:
                    nuevos = generate_lpns(cantidad, usuario, bodega, tipo_etiqueta)
                    st.success(f"{len(nuevos)} LPNs generados exitosamente.")
                    st.write("Últimos LPNs generados:")
                    st.dataframe(pd.DataFrame(nuevos, columns=["Número LPN", "Fecha creación", "Creado por", "Estado", "Bodega"]))
                else:
                    st.error("Usuario o bodega no definidos en sesión.")
            else:
                st.warning("La cantidad debe ser mayor a cero.")

def interfaz_admin():
    if st.session_state.get("rol") == "Admin":
        formulario_generacion()
    else:
        st.info("Solo los usuarios con rol Admin pueden generar LPNs.")

interfaz_admin()
show_disponibles()