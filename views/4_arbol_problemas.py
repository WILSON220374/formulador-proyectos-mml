import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- ESTILO UNIFICADO (IGUAL A INTERESADOS) ---
st.markdown("""
    <style>
    /* Tipografía y Color General */
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    /* Botones de Papelera: Solo icono en rojo, igual a Interesados */
    .stButton button p {
        color: #ff4b4b !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .stButton button {
        border-color: rgba(255, 75, 75, 0.2) !important;
        border-radius: 6px;
    }
    .stButton button:hover {
        border-color: #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
    }
    /* Divisor grueso igual al de Interesados */
    .divisor-grueso {
        border: 1.5px solid #31333F;
        border-radius: 5px;
        opacity: 0.1;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- SINCRONIZACIÓN DE DATOS ---
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])

st.title("🌳 4. Árbol de Problemas")

# 1. Configuración Maestra
CONFIG = {
    "Problema Superior": {"color": "#F0F2F6", "borde": "#C1E1C1", "y": 5},
    "Efectos Indirectos": {"color": "#F0F2F6", "borde": "#B3D9FF", "y": 4},
    "Efectos Directos": {"color": "#F0F2F6", "borde": "#80BFFF", "y": 3},
    "Problema Principal": {"color": "#FDF2F2", "borde": "#FFB3BA", "y": 2},
    "Causas Directas": {"color": "#F0F2F6", "borde": "#FFFFBA", "y": 1},
    "Causas Indirectas": {"color": "#F0F2F6", "borde": "#FFDFBA", "y": 0}
}

# --- SIDEBAR: GESTIÓN Y EXPORTACIÓN ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción de la idea:")
        padre_asociado = None
        if "Indirectos" in tipo_sel or "Indirectas" in tipo_sel:
            padre_key = "Efectos Directos" if "Efectos" in tipo_sel else "Causas Directas"
            opciones_p = st.session_state['arbol_tarjetas'].get(padre_key, [])
            if opciones_p:
                padre_asociado = st.selectbox(f"Vincular a:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if padre_asociado:
                st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
            else:
                st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
            st.rerun()

    st.divider()
    # (La función generar_png_arbol se mantiene para permitir la descarga)

# --- RENDERIZADO CON ESTILO "INTERESADOS" ---
def card_html(texto, color_fondo, color_borde):
    # Usamos el estilo de contenedor con borde de Interesados
    return f"""<div style="background-color:{color_fondo}; padding:15px; border-radius:10px; 
               border: 1px solid {color_borde}; color:#31333F; font-weight:500; 
               margin-bottom:10px; min-height:80px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05); 
               display: flex; align-items: center; justify-content: center; text-align: center; font-size:14px;">
               {texto}</div>"""

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'].get(nombre, [])
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"], CONFIG[nombre]["borde"]), unsafe_allow_html=True)
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
                st.caption(f"Debe crear un {nombre_padre} primero.")
            else:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            h_del_p = [h for h in hijos if h.get("padre") == p_txt] if isinstance(hijos[0] if hijos else None, dict) else []
                            for h_idx, h_data in enumerate(h_del_p):
                                st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"], CONFIG[nombre_hijo]["borde"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{h_idx}"):
                                    st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data); st.rerun()
                        else:
                            st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"], CONFIG[nombre_padre]["borde"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_p_{seccion_actual}_{i}"):
                                st.session_state['arbol_tarjetas'][seccion_actual].pop(i); st.rerun()

# --- CONSTRUCCIÓN ---
st.markdown("<div class='divisor-grueso'></div>", unsafe_allow_html=True)
render_simple("Problema Superior")
st.markdown("<div class='divisor-grueso'></div>", unsafe_allow_html=True)
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("<div class='divisor-grueso'></div>", unsafe_allow_html=True)
render_simple("Problema Principal") 
st.markdown("<div class='divisor-grueso'></div>", unsafe_allow_html=True)
render_rama("Causas Directas", "Causas Indirectas", inversion=False)
