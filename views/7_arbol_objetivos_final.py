import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
import os # <--- Necesario para cargar el logo
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos persistentes
inicializar_session()

# --- ESTILO DE TARJETAS (CENTRADO Y PAPELERA LIMPIA) ---
st.markdown("""
    <style>
    div[data-testid="stTextArea"] textarea {
        background-color: #f8f9fb !important;
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding-top: 10px !important;
    }
    /* Estilo para que la papelera se vea roja y centrada */
    .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.2rem !important;
        margin-top: -10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1 y 2. ENCABEZADO CON LOGO Y TÍTULO SOLICITADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")

with col_titulo:
    st.title("🎯 7. Árbol de Objetivos Final") # Título actualizado

with col_logo:
    # Traemos la imagen 'unnamed-1.jpg' igual que en la Hoja 1
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.info("Podado Manual: Los cambios aquí no afectan al Árbol original de la Fase 5.")

CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"}
}

# --- 3. FUNCIÓN DE ELIMINACIÓN (CALLBACK DE SEGURIDAD) ---
def eliminar_tarjeta_final(seccion, indice):
    """
    Borra el elemento exacto usando su posición en la lista original.
    Se ejecuta antes de renderizar la página para evitar errores de índice.
    """
    st.session_state['arbol_objetivos_final'][seccion].pop(indice)
    guardar_datos_nube()

# --- FUNCIÓN DE RENDERIZADO DE TARJETAS ---
def render_poda_card(seccion, indice, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_OBJ[seccion]["color"]
    
    with st.container():
        st.markdown(f'<div style="background-color: {color}; height: 6px; border-radius: 10px 10px 0 0; margin-bottom: 0px;"></div>', unsafe_allow_html=True)
        
        # Área de edición
        nuevo_texto = st.text_area(
            label=f"p_{seccion}_{indice}", 
            value=texto_actual, 
            label_visibility="collapsed", 
            height=90, 
            key=f"txt_{seccion}_{indice}"
        )
        
        # BOTÓN DE BORRADO CON CALLBACK: Garantiza borrar la tarjeta correcta
        st.button("🗑️", key=f"btn_del_{seccion}_{indice}", on_click=eliminar_tarjeta_final, args=(seccion, indice))
            
        if nuevo_texto != texto_actual:
            if isinstance(item, dict): 
                st.session_state['arbol_objetivos_final'][seccion][indice]["texto"] = nuevo_texto
            else: 
                st.session_state['arbol_objetivos_final'][seccion][indice] = nuevo_texto
            guardar_datos_nube()

# --- FUNCIONES DE ESTRUCTURA ---
def mostrar_seccion_simple_poda(key_interna):
    label_visual = CONFIG_OBJ[key_interna]["label"]
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"**{label_visual}**")
    with col_c:
        items = st.session_state['arbol_objetivos_final'].get(key_interna, [])
        if items: render_poda_card(key_interna, 0, items[0])
        else: st.caption("Vacío.")

def mostrar_rama_jerarquica_poda(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos_final'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos_final'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]
    
    for seccion_actual, es_hijo in orden:
        label_visual = CONFIG_OBJ[seccion_actual]["label"]
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='margin-top:25px;'>**{label_visual}**</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    p_txt = p_data["texto"] if isinstance(p_data, dict) else p_data
                    with cols[i]:
                        if es_hijo:
                            h_rel = [(idx, h) for idx, h in enumerate(hijos) if isinstance(h, dict) and h.get("padre") == p_txt]
                            for h_idx_orig, h_data in h_rel: render_poda_card(seccion_actual, h_idx_orig, h_data)
                        else: render_poda_card(seccion_actual, i, p_data)
            else: st.caption(f"Defina {nombre_padre} primero.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar desde Paso 5", use_container_width=True):
        st.session_state['arbol_objetivos_final'] = copy.deepcopy(st.session_state['arbol_objetivos'])
        guardar_datos_nube(); st.rerun()

# --- DIBUJO DEL ÁRBOL ---
arbol_f = st.session_state.get('arbol_objetivos_final', {})

if not arbol_f:
    st.warning("El árbol está vacío. Use 'Importar desde Paso 5' en la barra lateral.")
else:
    st.divider()
    mostrar_seccion_simple_poda("Fin Último")
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    mostrar_rama_jerarquica_poda("Fines Directos", "Fines Indirectos", inversion=True)
    st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    mostrar_seccion_simple_poda("Objetivo General")
    st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    mostrar_rama_jerarquica_poda("Medios Directos", "Medios Indirectos", inversion=False)
