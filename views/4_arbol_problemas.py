import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- REPARACIÓN DE EMERGENCIA (Si arbol_tarjetas es una lista, la convertimos en diccionario) ---
if not isinstance(st.session_state.get('arbol_tarjetas'), dict):
    st.session_state['arbol_tarjetas'] = {
        "Efectos Indirectos": [], "Efectos Directos": [], 
        "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []
    }

# --- ENCABEZADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🌳 4. Árbol de Problemas")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# Configuración de secciones
CONFIG = {
    "Efectos Indirectos": {"color": "#B3D9FF", "tipo": "hijo", "padre": "Efectos Directos", "y": 9.5},
    "Efectos Directos": {"color": "#80BFFF", "tipo": "simple", "y": 6.0},
    "Problema Principal": {"color": "#FFB3BA", "tipo": "simple", "y": 3.0},
    "Causas Directas": {"color": "#FFFFBA", "tipo": "simple", "y": 0.0},
    "Causas Indirectas": {"color": "#FFDFBA", "tipo": "hijo", "padre": "Causas Directas", "y": -3.5}
}

# --- GESTIÓN DE FICHAS (SIDEBAR) ---
with st.sidebar:
    st.header("➕ Agregar Tarjeta")
    tipo_sel = st.selectbox("Sección:", list(CONFIG.keys()))
    
    with st.form("form_arbol", clear_on_submit=True):
        texto_input = st.text_area("Descripción:", max_chars=180)
        padre_asociado = None
        
        # Ahora el .get() es seguro porque aseguramos que sea un diccionario
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'].get(CONFIG[tipo_sel]["padre"], [])
            if opciones_p:
                padre_asociado = st.selectbox("Vincular a:", opciones_p)
        
        if st.form_submit_button("Añadir al Árbol") and texto_input:
            if padre_asociado:
                st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
            else:
                st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
            guardar_datos_nube()
            st.rerun()

# --- RENDERIZADO VISUAL ---
st.info("Utilice el panel lateral para agregar o eliminar causas y efectos.")

# (Aquí sigue el resto de tu lógica de dibujo de tarjetas y render_rama)
