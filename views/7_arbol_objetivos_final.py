import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
import os
import uuid # Sistema de Pasaportes Únicos
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos persistentes
inicializar_session()

# --- ESTILO DE TARJETAS (CORREGIDO PARA NO AFECTAR SIDEBAR) ---
st.markdown("""
    <style>
    div[data-testid="stTextArea"] textarea {
        background-color: #f8f9fb !important;
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding-top: 15px !important;
    }
    /* SOLUCIÓN: Solo los botones en el área principal (.main) serán rojos y transparentes */
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.2rem !important;
        margin-top: -15px !important;
    }
    /* Los botones de la barra lateral conservan su estilo original por defecto */
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO Y TÍTULO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🎯 7. Árbol de Objetivos Final") # Título corregido
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.info("Podado Manual: Los cambios aquí no afectan al Árbol original de la Fase 5.")

# --- FUNCIÓN DE ALTURA DINÁMICA ---
def calcular_altura_web(texto, min_h=100):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 30)
    return max(min_h, (lineas + 2) * 22)

CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"}
}

# --- HERRAMIENTA DE IMPORTACIÓN CON UUID (PASAPORTES) ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar desde Paso 5", use_container_width=True):
        datos_originales = copy.deepcopy(st.session_state.get('arbol_objetivos', {}))
        datos_con_id = {}
        for seccion, lista in datos_originales.items():
            procesados = []
            for item in lista:
                if isinstance(item, dict):
                    item['id_unico'] = str(uuid.uuid4())
                    procesados.append(item)
                else:
                    procesados.append({'texto': item, 'id_unico': str(uuid.uuid4())})
            datos_con_id[seccion] = procesados
        st.session_state['arbol_objetivos_final'] = datos_con_id
        guardar_datos_nube(); st.rerun()

# --- FUNCIÓN DE RENDERIZADO CON IDENTIDAD ÚNICA ---
def render_poda_card(seccion, item):
    id_id = item.get('id_unico', 'temp')
    texto_actual = item.get("texto", "")
    color = CONFIG_OBJ[seccion]["color"]
    
    st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    
    nuevo_texto = st.text_area(
        label=f"p_{id_id}", 
        value=texto_actual, 
        label_visibility="collapsed", 
        height=calcular_altura_web(texto_actual), 
        key=f"txt_{id_id}"
    )
    
    # Borrado por Identidad (Blindaje contra doble clic)
    if st.button("🗑️", key=f"btn_{id_id}"):
        st.session_state['arbol_objetivos_final'][seccion] = [
            x for x in st.session_state['arbol_objetivos_final'][seccion] 
            if x.get('id_unico') != id_id
        ]
        guardar_datos_nube(); st.rerun()
    
    if nuevo_texto != texto_actual:
        item["texto"] = nuevo_texto
        guardar_datos_nube()

# --- ESTRUCTURA JERÁRQUICA ---
def mostrar_seccion_simple_poda(key_interna):
    label_visual = CONFIG_OBJ[key_interna]["label"]
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"**{label_visual}**")
    with col_c:
        items = st.session_state['arbol_objetivos_final'].get(key_interna, [])
        if items: render_poda_card(key_interna, items[0])

def mostrar_rama_jerarquica_poda(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos_final'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos_final'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]
    
    for seccion_actual, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='margin-top:25px;'>**{CONFIG_OBJ[seccion_actual]['label']}**</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    p_txt = p_data.get("texto", "")
                    with cols[i]:
                        if es_hijo:
                            h_rel = [h for h in hijos if h.get("padre") == p_txt]
                            for h_data in h_rel: render_poda_card(seccion_actual, h_data)
                        else:
                            render_poda_card(seccion_actual, p_data)

# --- DIBUJO ---
arbol_f = st.session_state.get('arbol_objetivos_final', {})
if not arbol_f:
    st.warning("El árbol está vacío. Use 'Importar desde Paso 5' en la barra lateral.")
else:
    st.divider()
    mostrar_seccion_simple_poda("Fin Último")
    st.markdown("---")
    mostrar_rama_jerarquica_poda("Fines Directos", "Fines Indirectos", inversion=True)
    st.markdown("---")
    mostrar_seccion_simple_poda("Objetivo General")
    st.markdown("---")
    mostrar_rama_jerarquica_poda("Medios Directos", "Medios Indirectos", inversion=False)
