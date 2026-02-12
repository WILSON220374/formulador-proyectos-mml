import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO MAESTRO ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    .stButton button[kind="primary"] p { color: white !important; font-weight: bold !important; }
    .main .stButton button:not([kind="primary"]) p { color: #ff4b4b !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🌳 4. Árbol de Problemas")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- MEMORIA Y CONFIGURACIÓN ---
if 'arbol_tarjetas' not in st.session_state:
    st.session_state['arbol_tarjetas'] = {
        "Efectos Indirectos": [], "Efectos Directos": [], 
        "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []
    }

CONFIG = {
    "Efectos Indirectos": {"color": "#B3D9FF", "tipo": "hijo", "padre": "Efectos Directos", "y": 4},
    "Efectos Directos": {"color": "#80BFFF", "tipo": "simple", "y": 3},
    "Problema Principal": {"color": "#FFB3BA", "tipo": "simple", "y": 2},
    "Causas Directas": {"color": "#FFFFBA", "tipo": "simple", "y": 1},
    "Causas Indirectas": {"color": "#FFDFBA", "tipo": "hijo", "padre": "Causas Directas", "y": 0}
}

# --- SIDEBAR: GESTIÓN ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha_nube", clear_on_submit=True):
        texto_input = st.text_area("Descripción de la idea:")
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'].get(CONFIG[tipo_sel]["padre"], [])
            if opciones_p: padre_asociado = st.selectbox(f"Vincular a:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if padre_asociado:
                st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
            else:
                st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
            guardar_datos_nube()
            st.rerun()

    st.divider()
    
    # --- FUNCIÓN DE GENERACIÓN DE PNG (COPIA FIEL DE PANTALLA) ---
    def generar_png():
        fig, ax = plt.subplots(figsize=(20, 15)) # Lienzo más ancho para mayor claridad
        ax.set_xlim(0, 12); ax.set_ylim(-1, 9); ax.axis('off')
        
        # Título centrado
        ax.text(6, 8.5, "ÁRBOL DE PROBLEMAS", fontsize=32, fontweight='bold', ha='center', color='#1E3A8A')
        
        datos = st.session_state['arbol_tarjetas']
        
        # 1. Función interna para dibujar cajas
        def dibujar_caja(x, y, texto, color):
            txt_ajustado = "\n".join(textwrap.wrap(texto, width=22))
            rect_w, rect_h = 2.2, 0.8
            rect = plt.Rectangle((x - rect_w/2, y - rect_h/2), rect_w, rect_h, 
                                 facecolor=color, edgecolor='#333', lw=1.5, zorder=3)
            ax.add_patch(rect)
            ax.text(x, y, txt_ajustado, ha='center', va='center', fontsize=10, 
                    fontweight='bold', zorder=4, color='#31333F')

        # 2. Dibujar secciones simples (Problema y Directas)
        pos_x_directas = {} # Para alinear los hijos después
        
        # Problema Principal (Centro)
        if datos["Problema Principal"]:
            dibujar_caja(6, CONFIG["Problema Principal"]["y"]*1.5, datos["Problema Principal"][0], CONFIG["Problema Principal"]["color"])

        # Secciones con ramas (Directas e Indirectas)
        for principal in ["Efectos Directos", "Causas Directas"]:
            items = datos[principal]
            if items:
                espacio = 12 / (len(items) + 1)
                for i, p_txt in enumerate(items):
                    x_p = (i + 1) * espacio
                    pos_x_directas[p_txt] = x_p
                    dibujar_caja(x_p, CONFIG[principal]["y"]*1.5, p_txt, CONFIG[principal]["color"])
                    
                    # Buscar hijos para este padre específico
                    sec_hija = "Efectos Indirectos" if principal == "Efectos Directos" else "Causas Indirectas"
                    hijos = [h for h in datos[sec_hija] if isinstance(h, dict) and h.get("padre") == p_txt]
                    
                    if hijos:
                        # Dibujar hijos agrupados bajo su padre
                        h_y = CONFIG[sec_hija]["y"]*1.5
                        # Pequeño desplazamiento si hay varios hijos
                        h_espacio = 1.8 / (len(hijos) + 1) if len(hijos) > 1 else 0
                        for j, h_data in enumerate(hijos):
                            h_x = x_p + (j - (len(hijos)-1)/2) * 0.8
                            dibujar_caja(h_x, h_y, h_data["texto"], CONFIG[sec_hija]["color"])

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight', transparent=False, facecolor='white')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol PNG", data=generar_png(), file_name="arbol_problemas_JCFLOW.png", mime="image/png", use_container_width=True)

# --- RENDERIZADO EN PANTALLA ---
def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:15px; border-radius:10px; border-left:8px solid rgba(0,0,0,0.1); 
               color:#31333F; font-weight:500; margin-bottom:8px; min-height:85px; box-shadow: 2px 2px 5px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center; font-size:14px;">{texto}</div>"""

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"**{nombre.upper()}**")
    with col_c:
        items = st.session_state['arbol_tarjetas'].get(nombre, [])
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                guardar_datos_nube(); st.rerun()
        else: st.caption("Sección vacía")

def render_rama(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_tarjetas'].get(nombre_padre, [])
    hijos = st.session_state['arbol_tarjetas'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]
    for seccion_actual, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"**{seccion_actual.upper()}**")
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            h_del_p = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_txt]
                            for idx, h_data in enumerate(h_del_p):
                                st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{idx}"):
                                    st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data); guardar_datos_nube(); st.rerun()
                        else:
                            st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_p_{seccion_actual}_{i}"):
                                st.session_state['arbol_tarjetas'][seccion_actual].pop(i); guardar_datos_nube(); st.rerun()
            else: st.caption("Esperando datos...")

st.divider()
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")
render_simple("Problema Principal") 
st.markdown("---")
render_rama("Causas Directas", "Causas Indirectas", inversion=False)
