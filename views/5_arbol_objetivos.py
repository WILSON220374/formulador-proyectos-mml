import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# Asegurar persistencia del estado
inicializar_session()

# --- ESTILO MAESTRO UNIFICADO ---
st.markdown("""
    <style>
    /* 1. Tipografía base */
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    
    /* 2. Sidebar: Guardar (Blanco/Negrita) y Cerrar Sesión (Negro/Fino) */
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    [data-testid="stSidebar"] .stButton button:not([kind="primary"]) p {
        color: black !important;
        font-weight: normal !important;
        font-size: 1rem;
    }

    /* 3. Papeleras en Rojo */
    .main .stButton button:not([kind="primary"]) p {
        color: #ff4b4b !important;
        font-weight: bold !important;
    }
    
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 5. Árbol de Objetivos")

# 1. Configuración de Colores (IGUAL AL ÁRBOL DE PROBLEMAS)
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5, "tipo": "simple"},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "tipo": "hijo", "padre": "Fines Directos"},
    "Fines Directos": {"color": "#80BFFF", "y": 3, "tipo": "simple"},
    "Objetivo General": {"color": "#FFB3BA", "y": 2, "tipo": "simple"},
    "Medios Directos": {"color": "#FFFFBA", "y": 1, "tipo": "simple"},
    "Medios Indirectos": {"color": "#FFDFBA", "y": 0, "tipo": "hijo", "padre": "Medios Directos"}
}

# --- SIDEBAR: GESTIÓN DE OBJETIVOS (IDÉNTICO A PROBLEMAS) ---
with st.sidebar:
    st.header("➕ Gestión de Objetivos")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG_OBJ.keys()))
    
    with st.form("crear_objetivo", clear_on_submit=True):
        texto_input = st.text_area("Descripción (Redactar en positivo):")
        padre_asoc = None
        if CONFIG_OBJ[tipo_sel]["tipo"] == "hijo":
            opciones = st.session_state['arbol_objetivos'].get(CONFIG_OBJ[tipo_sel]["padre"], [])
            if opciones:
                padre_asoc = st.selectbox(f"Vincular a {CONFIG_OBJ[tipo_sel]['padre']}:", opciones)
        
        if st.form_submit_button("Añadir al Árbol") and texto_input:
            if CONFIG_OBJ[tipo_sel]["tipo"] == "hijo" and padre_asoc:
                st.session_state['arbol_objetivos'][tipo_sel].append({"texto": texto_input, "padre": padre_asoc})
            else:
                st.session_state['arbol_objetivos'][tipo_sel].append(texto_input)
            st.rerun()

    st.divider()
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {
            "Efectos Indirectos": "Fines Indirectos",
            "Efectos Directos": "Fines Directos", 
            "Problema Principal": "Objetivo General", 
            "Causas Directas": "Medios Directos", 
            "Causas Indirectas": "Medios Indirectos"
        }
        for p_sec, o_sec in mapeo.items():
            if p_sec in problemas:
                st.session_state['arbol_objetivos'][o_sec] = []
                for item in problemas[p_sec]:
                    txt = item['texto'] if isinstance(item, dict) else item
                    if isinstance(item, dict):
                        st.session_state['arbol_objetivos'][o_sec].append({"texto": txt, "padre": item['padre']})
                    else:
                        st.session_state['arbol_objetivos'][o_sec].append(txt)
        st.success("¡Datos convertidos! Fin Último se mantiene vacío.")
        st.rerun()

# --- FUNCIONES DE RENDERIZADO (IDÉNTICO A PROBLEMAS) ---

def card_html(texto, color):
    # Usamos el mismo HTML que el Árbol de Problemas para garantizar visual idéntico
    return f"""<div style="background-color:{color}; padding:15px; border-radius:10px; 
               border-left:8px solid rgba(0,0,0,0.1); color:#31333F; font-weight:500; 
               margin-bottom:8px; min-height:80px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); 
               display: flex; align-items: center; justify-content: center; text-align: center; font-size:14px;">
               {texto}</div>"""

def render_simple_obj(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_objetivos'].get(nombre, [])
        if items:
            st.markdown(card_html(items[0], CONFIG_OBJ[nombre]["color"]), unsafe_allow_html=True)
            if nombre != "Objetivo General" and st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_objetivos'][nombre] = []; st.rerun()
        else: st.caption("Sección vacía")

def render_rama_objetivos(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:30px;'>{seccion.upper()}</div>", unsafe_allow_html=True)
        with col_c:
            if not padres: st.caption(f"Cree un {nombre_padre} primero.")
            else:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    p_nombre = p_txt["texto"] if isinstance(p_txt, dict) else p_txt
                    with cols[i]:
                        if es_hijo:
                            hijos_p = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_nombre]
                            for idx, h_data in enumerate(hijos_p):
                                st.markdown(card_html(h_data["texto"], CONFIG_OBJ[nombre_hijo]["color"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"del_h_{seccion}_{i}_{idx}"):
                                    st.session_state['arbol_objetivos'][seccion].remove(h_data); st.rerun()
                        else:
                            st.markdown(card_html(p_nombre, CONFIG_OBJ[nombre_padre]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_p_{seccion}_{i}"):
                                st.session_state['arbol_objetivos'][seccion].pop(i); st.rerun()

# --- DIBUJO DEL ÁRBOL ---
st.divider()
render_simple_obj("Fin Último")
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_rama_objetivos("Fines Directos", "Fines Indirectos", inversion=True)
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_simple_obj("Objetivo General") 
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_rama_objetivos("Medios Directos", "Medios Indirectos", inversion=False)
