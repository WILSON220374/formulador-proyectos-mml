import streamlit as st
import graphviz
import os
import uuid
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia y Memoria
inicializar_session()

# --- ESTILO GLOBAL ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        border: none !important;           
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #000 !important;
        min-height: 100px !important;
    }

    [data-testid="stImage"] img { border-radius: 12px; pointer-events: none; }
    button[title="View fullscreen"] { display: none !important; }
    
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.3rem !important;
        margin-top: -15px !important;
        position: relative;
        z-index: 2;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🎯 5. Árbol de Objetivos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Transformación de problemas en estados positivos y medios para alcanzarlos.</div>', unsafe_allow_html=True)
    
    hay_datos = any(st.session_state.get('arbol_objetivos', {}).values())
    progreso = 1.0 if hay_datos else 0.0
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- CONFIGURACIÓN DE COLORES ---
CONFIG_OBJ = {
    "Fin Último":       {"color": "#27AE60", "font_color": "white", "label": "FIN\nÚLTIMO"},
    "Fines Indirectos": {"color": "#154360", "font_color": "white", "label": "FINES\nINDIRECTOS"},
    "Fines Directos":   {"color": "#1F618D", "font_color": "white", "label": "FINES\nDIRECTOS"},
    "Objetivo General": {"color": "#C0392B", "font_color": "white", "label": "OBJETIVO\nGENERAL"},
    "Medios Directos":  {"color": "#F1C40F", "font_color": "black", "label": "OBJETIVOS\nESPECÍFICOS"},
    "Medios Indirectos":{"color": "#D35400", "font_color": "white", "label": "ACTIVIDADES"}
}

# --- PILOTO AUTOMÁTICO DE LIMPIEZA ---
if hay_datos:
    datos = st.session_state['arbol_objetivos']
    cambios_realizados = False
    
    padres_validos_fi = [p['texto'] for p in datos.get("Fines Directos", [])]
    fines_indirectos_limpios = [h for h in datos.get("Fines Indirectos", []) if h.get('padre') in padres_validos_fi]
