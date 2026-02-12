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

# --- SIDEBAR: GESTIÓN Y EXPORTACIÓN ---
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
    
    # --- FUNCIÓN DE GENERACIÓN DE PNG MEJORADA ---
    def generar_png():
        fig, ax = plt.subplots(figsize=(18, 14)) # Lienzo más grande
        ax.set_xlim(0, 10); ax.set_ylim(-1, 8.5); ax.axis('off')
        
        # 1. Título del Árbol en el PNG
        ax.text(5, 8, "ÁRBOL DE PROBLEMAS", fontsize=28, fontweight='bold', ha='center', color='#1E3A8A')
        
        datos = st.session_state['arbol_tarjetas']
        for sec, conf in CONFIG.items():
            items_raw = datos.get(sec, [])
            items = [h for h in items_raw if isinstance(h, dict) and h.get("padre") in datos.get(conf["padre"], [])] if conf["tipo"] == "hijo" else items_raw
            if not items: continue
            
            espacio = 10 / (len(items) + 1)
            for i, item in enumerate(items):
                x = (i + 1) * espacio
                txt = item["texto"] if isinstance(item, dict) else item
                
                # Ajuste de texto centrado y proporcional
                txt_ajustado = "\n".join(textwrap.wrap(txt, width=20))
                
                # Rectángulo más robusto para evitar desbordes
                rect_w, rect_h = 2.4, 0.9
                rect = plt.Rectangle((x - (rect_w/2), (conf["y"]*1.5) - (rect_h/2)), 
                                     rect_w, rect_h, facecolor=conf["color"], 
                                     edgecolor='#333', lw=1.5, zorder=2)
                ax.add_patch(rect)
                
                # Texto centrado vertical y horizontalmente
                ax.text(x, conf["y"]*1.5, txt_ajustado, ha='center', va='center', 
                        fontsize=10, fontweight='bold', zorder=3, color='#31333F')
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol PNG", data=generar_png(), file_name="arbol_problemas.png", mime="image/png", use_container_width=True)

# --- DIBUJO DEL ÁRBOL EN PANTALLA ---
# (Se mantiene tu lógica de renderizado por columnas que ya funciona bien)
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
