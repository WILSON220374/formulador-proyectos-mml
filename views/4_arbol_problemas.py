import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- ESTILO MAESTRO: HOMOGENIZADO CON INTERESADOS ---
st.markdown("""
    <style>
    /* 1. Tipografía igual a Interesados */
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    
    /* 2. Botón de Guardar (Primario): Texto blanco SIEMPRE visible */
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* 3. Botones de Papelera (Normales): Solo icono en rojo */
    .stButton button:not([kind="primary"]) p {
        color: #ff4b4b !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* 4. Bordes de botones sutiles como en Interesados */
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SINCRONIZACIÓN DE DATOS ---
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])

st.title("🌳 4. Árbol de Problemas")

# 1. Configuración de Colores (Basada en st.info, st.success, etc. de Interesados)
CONFIG = {
    "Problema Superior": {"bg": "#d4edda", "border": "#c3e6cb", "y": 5}, # Success (Verde)
    "Efectos Indirectos": {"bg": "#d1ecf1", "border": "#bee5eb", "y": 4}, # Info (Azul claro)
    "Efectos Directos": {"bg": "#cfe2ff", "border": "#b6d4fe", "y": 3},   # Primario suave
    "Problema Principal": {"bg": "#f8d7da", "border": "#f5c6cb", "y": 2}, # Error (Rojo suave)
    "Causas Directas": {"bg": "#fff3cd", "border": "#ffeeba", "y": 1},   # Warning (Amarillo)
    "Causas Indirectas": {"bg": "#fefefe", "border": "#dee2e6", "y": 0}   # Gris neutro
}

# --- SIDEBAR: GESTIÓN Y EXPORTACIÓN ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción de la idea:")
        padre_asociado = None
        if "Indirecto" in tipo_sel or "Indirecta" in tipo_sel:
            padre_key = "Efectos Directos" if "Efectos" in tipo_sel else "Causas Directas"
            opciones_p = st.session_state['arbol_tarjetas'].get(padre_key, [])
            if opciones_p:
                padre_asociado = st.selectbox(f"Vincular a {padre_key}:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if len(st.session_state['arbol_tarjetas'].get(tipo_sel, [])) < 99:
                if padre_asociado:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()

# --- FUNCIONES DE RENDERIZADO (IGUAL A INTERESADOS) ---

def card_html(texto, bg, border
