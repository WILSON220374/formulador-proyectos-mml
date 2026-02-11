import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- ESTILO MAESTRO: HOMOGENIZADO CON INTERESADOS Y AJUSTE DE SIDEBAR ---
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
    
    /* 3. Botones de la Main Area (Papeleras): Rojo y Negrita */
    .main .stButton button:not([kind="primary"]) p {
        color: #ff4b4b !important;
        font-weight: bold !important;
        font-size: 1.1rem;
    }

    /* 4. Botones de la Sidebar (Cerrar Sesión): Negro y sin negrilla */
    [data-testid="stSidebar"] .stButton button:not([kind="primary"]) p {
        color: black !important;
        font-weight: normal !important;
        font-size: 1rem;
    }
    
    /* 5. Bordes de botones sutiles */
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

# 1. Configuración de Colores
CONFIG = {
    "Problema Superior": {"bg": "#d4edda", "border": "#c3e6cb", "y": 5},
    "Efectos Indirectos": {"bg": "#d1ecf1", "border": "#bee5eb", "y": 4},
    "Efectos Directos": {"bg": "#cfe2ff", "border": "#b6d4fe", "y": 3},
    "Problema Principal": {"bg": "#f8d7da", "border": "#f5c6cb", "y": 2},
    "Causas Directas": {"bg": "#fff3cd", "border": "#ffeeba", "y": 1},
    "Causas Indirectas": {"bg": "#fefefe", "border": "#dee2e6", "y": 0}
}

# --- SIDEBAR: GESTIÓN DE FICHAS ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha_arbol", clear_on_submit=True):
        texto_input = st.text_area("Descripción de la idea:")
        padre_asociado = None
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

# --- FUNCIONES DE RENDERIZADO (ESTILO INTERESADOS COMPLETADO) ---

def card_html(texto, bg, border):
    # Función completada para evitar el SyntaxError
    return f"""<div style="background-color:{bg}; padding:15px; border-radius:10px; 
               border: 1px solid {border}; color:#31333F; font-weight:500; 
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
            st.markdown(card_html(items[0], CONFIG[nombre]["bg"], CONFIG[nombre]["border"]), unsafe_allow_html=True)
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
                                st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["bg"], CONFIG[nombre_hijo]["border"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{idx}"):
                                    st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data); st.rerun()
                        else:
                            st.markdown(card_html(p_txt, CONFIG[nombre_padre]["bg"], CONFIG[nombre_padre]["border"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_p_{seccion_actual}_{i}"):
                                h_asoc = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_txt]
                                if h_asoc: st.error("Borre indirectos primero")
                                else: st.session_state['arbol_tarjetas'][seccion_actual].pop(i); st.rerun()

# --- CONSTRUCCIÓN DEL ÁRBOL ---
DIV_MAESTRO = "<hr style='border: 1.5px solid #31333F; border-radius: 5px; opacity: 0.1; margin: 20px 0;'>"

st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_simple("Problema Superior")
st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_simple("Problema Principal") 
st.markdown(DIV_MAESTRO, unsafe_allow_html=True)
render_rama("Causas Directas", "Causas Indirectas", inversion=False)
