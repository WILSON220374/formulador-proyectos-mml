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

    /* Estética de Tarjetas */
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
    
    /* Estilo para Huérfanos */
    .huerfano-box {
        border: 2px dashed #ff4b4b;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: #fff5f5;
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

# --- CONFIGURACIÓN DE NIVELES Y ETIQUETAS ---
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN\nÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES\nINDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES\nDIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO\nGENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS\nESPECÍFICOS"}, 
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"} 
}

# --- MOTOR DE DIBUJO (FILTRADO: SOLO CONECTADOS) ---
def generar_grafo_objetivos():
    datos = st.session_state.get('arbol_objetivos', {})
    if not any(datos.values()): return None
    
    dot = graphviz.Digraph(format='png')
    dot.attr(label='ÁRBOL DE OBJETIVOS', labelloc='t', fontsize='35', fontname='Arial Bold', fontcolor='#333333')
    dot.attr(dpi='300', rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')
    dot.attr('node', fontsize='18', fontcolor='#31333F', fontname='Arial Bold', style='filled', color='none', margin='0.6,0.4', shape='box')
    
    def limpiar(t, w=45): return "\n".join(textwrap.wrap(str(t).upper(), width=w))

    # ETIQUETAS LATERALES
    etiquetas = ["L_FU", "L_FI", "L_FD", "L_OG", "L_MD", "L_MI"]
    tipos = ["Fin Último", "Fines Indirectos", "Fines Directos", "Objetivo General", "Medios Directos", "Medios Indirectos"]
    
    for id_e, tipo in zip(etiquetas, tipos):
        conf = CONFIG_OBJ[tipo]
        dot.node(id_
