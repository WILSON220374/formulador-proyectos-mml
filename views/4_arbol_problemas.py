import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- ESTILO MAESTRO: HOMOGENIZADO CON INTERESADOS ---
st.markdown("""
    <style>
    /* 1. Tipografía y color general igual a Interesados */
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    
    /* 2. Botón de Guardar (Primario): Texto blanco SIEMPRE visible */
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* 3. Botones de Papelera: Solo icono en rojo, sin texto */
    .stButton button:not([kind="primary"]) p {
        color: #ff4b4b !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* 4. Bordes de botones sutiles */
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SINCRONIZACIÓN Y MIGRACIÓN DE DATOS ---
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        # Aseguramos que los datos se muevan al nuevo nombre de sección
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])

st.title("🌳 4. Árbol de Problemas")

# Configuración de Colores basada en componentes de Interesados
CONFIG = {
    "Problema Superior": {"tipo": "success", "y": 5}, # Verde
    "Efectos Indirectos": {"tipo": "info", "y": 4},    # Azul claro
    "Efectos Directos": {"tipo": "info", "y": 3},     # Azul claro
    "Problema Principal": {"tipo": "error", "y": 2},  # Rojo/Rosa
    "Causas Directas": {"tipo": "warning", "y": 1},   # Amarillo
    "Causas Indirectas": {"tipo": "light", "y": 0}    # Gris neutro
}

# --- SIDEBAR: GESTIÓN DE FICHAS ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha_arbol", clear_on_submit=True):
        texto_input = st.text_area("Descripción de la idea:")
        padre_asociado = None
        # Lógica de vinculación para hijos
        if "Indirecto" in tipo_sel or "Indirecta" in tipo_sel:
            padre_key = "Efectos Directos" if "Efectos" in tipo_sel else "Causas Directas"
            opciones_p = st.session_state['arbol_tarjetas'].get(padre_key, [])
            if opciones_p:
                padre_asociado = st.selectbox(f"Vincular a {padre_key}:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if padre_asociado:
                st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
            else:
                st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
            st.rerun()

# --- FUNCIONES DE RENDERIZADO (MODELO INTERESADOS) ---

def render_card(texto, tipo):
    """Renderiza una tarjeta usando contenedores y alertas como en Interesados"""
    with st.container(border=True):
        if tipo == "success": st.success(texto)
        elif tipo == "info": st.info(texto)
        elif tipo == "error": st.error(texto)
        elif tipo == "warning": st.warning(texto)
        else: st.write(texto)

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'].get(nombre, [])
        if items:
            render_card(items[0], CONFIG[nombre]["tipo"])
            if nombre != "Problema Principal" and st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []; st.rerun()
        else: st.caption("Sección vacía")

def render_rama(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_tarjetas'].get(nombre_padre, [])
    hijos = st.session_state['arbol_tarjetas'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion_actual, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:30px;'>{seccion_actual.upper()}</div>", unsafe_allow_html=True)
        with col_c:
            if not padres:
                st.caption(f"Cree un {nombre_padre} primero.")
            else:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            h_del_p = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_txt]
                            for idx, h_data in enumerate(h_del_p):
                                render_card(h_data["texto"], CONFIG[nombre_hijo]["tipo"])
                                if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{idx}"):
                                    st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data); st.rerun()
                        else:
                            render_card(p_txt, CONFIG[nombre_padre]["tipo"])
                            if st.button("🗑️", key=f"del_p_{seccion_actual}_{i}"):
                                h_asoc = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_txt]
                                if h_asoc: st.error("Borre indirectos primero")
                                else: st.session_state['arbol_tarjetas'][seccion_actual].pop(i); st.rerun()

# --- CONSTRUCCIÓN DEL ÁRBOL ---
# Divisor igual al de Interesados
DIV_MAESTRO = "<hr style='border: 1.5px solid #31333F; border-radius: 5px; opacity: 0.1; margin: 20px 0;'>"

st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_simple("Problema Superior")
st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_simple("Problema Principal") 
st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_rama("Causas Directas", "Causas Indirectas", inversion=False)
