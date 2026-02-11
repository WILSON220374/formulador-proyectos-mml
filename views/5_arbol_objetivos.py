import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
# Persistencia: Carga datos de la nube al iniciar
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

# --- ESTILO: CENTRADO TOTAL Y FRANJA DELGADA ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* CENTRADO DEL TEXTO Y ESTILO DE TARJETA GRIS */
    div[data-testid="stTextArea"] textarea {
        background-color: #f0f2f6 !important; /* Gris estándar de Streamlit */
        border-radius: 0 0 10px 10px !important;
        border: 1px solid #e6e9ef !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #31333F !important;
        
        /* Centrado horizontal y vertical */
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding-top: 25px !important; /* Ajuste para centrar visualmente el texto */
    }
    
    /* Eliminar contornos de enfoque */
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #d0d4dc !important;
    }

    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 5. Árbol de Objetivos")

# Configuración Maestra de Colores
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4},
    "Fines Directos": {"color": "#80BFFF", "y": 3},
    "Objetivo General": {"color": "#FFB3BA", "y": 2},
    "Medios Directos": {"color": "#FFFFBA", "y": 1},
    "Medios Indirectos": {"color": "#FFDFBA", "y": 0}
}

# --- SIDEBAR: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    # Importación con filtro (Sin fichas fantasmas)
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {
            "Efectos Indirectos": "Fines Indirectos",
            "Efectos Directos": "Fines Directos", 
            "Problema Principal": "Objetivo General", 
            "Causas Directas": "Medios Directos", 
            "Causas Indirectas": "Medios Indirectos"
        }
        
        for k in CONFIG_OBJ: st.session_state['arbol_objetivos'][k] = []
        
        for p_sec, o_sec in mapeo.items():
            items_raw = problemas.get(p_sec, [])
            for item in items_raw:
                txt = item['texto'] if isinstance(item, dict) else item
                if isinstance(txt, str) and len(txt.strip()) > 2:
                    if isinstance(item, dict):
                        st.session_state['arbol_objetivos'][o_sec].append({"texto": txt.upper(), "padre": item['padre']})
                    else:
                        st.session_state['arbol_objetivos'][o_sec].append(txt.upper())
        
        if not st.session_state['arbol_objetivos']["Fin Último"]:
            st.session_state['arbol_objetivos']["Fin Último"] = ["MEJORAR LA CALIDAD DE VIDA"]
            
        guardar_datos_nube()
        st.success("¡Datos importados!")
        st.rerun()

    st.divider()

    def generar_png_objetivos():
        fig, ax = plt.subplots(figsize=(16, 14))
        ax.set_xlim(0, 10); ax.set_ylim(-1, 8.5); ax.axis('off')
        datos = st.session_state['arbol_objetivos']
        for sec, conf in CONFIG_OBJ.items():
            items = datos.get(sec, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            y_base = conf["y"] * 1.5 
            for i, item in enumerate(items):
                x = (i + 1) * espacio
                txt = item["texto"] if isinstance(item, dict) else item
                rect = plt.Rectangle((x-1.1, y_base-0.4), 2.2, 0.7, facecolor=conf["color"], edgecolor='#333', lw=1.2)
                ax.add_patch(rect)
                txt_wrap = "\n".join(textwrap.wrap(txt, width=22))
                ax.text(x, y_base, txt_wrap, ha='center', va='center', fontsize=9, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol (PNG)", data=generar_png_objetivos(), file_name="arbol_objetivos.png", mime="image/png", use_container_width=True)

# --- FUNCIÓN DE TARJETA CON TEXTO CENTRADO ---

def render_objective_card(seccion, indice, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_OBJ[seccion]["color"]
    
    # 1. Franja de color delgada (6px)
    st.markdown(f"""
        <div style="background-color: {color}; height: 6px; border-radius: 10px 10px 0 0; margin-bottom: 0px;"></div>
    """, unsafe_allow_html=True)
    
    # 2. Tarjeta gris de edición con texto centrado
    nuevo_texto = st.text_area(
        label=f"edit_{seccion}_{indice}",
        value=texto_actual,
        label_visibility="collapsed",
        key=f"area_{seccion}_{indice}",
        height=90
    )
    
    if nuevo_texto != texto_actual:
        if isinstance(item, dict):
            st.session_state['arbol_objetivos'][seccion][indice]["texto"] = nuevo_texto
        else:
            st.session_state['arbol_objetivos'][seccion][indice] = nuevo_texto
        guardar_datos_nube()
        st.rerun()

def mostrar_seccion(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_objetivos'].get(nombre, [])
        if items:
            cols = st.columns(len(items))
            for i, item in enumerate(items):
                with cols[i]:
                    render_objective_card(nombre, i, item)
        else:
            st.caption("Sección vacía.")

# --- CONSTRUCCIÓN ---
st.divider()
mostrar_seccion("Fin Último")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
mostrar_seccion("Fines Indirectos")
mostrar_seccion("Fines Directos")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
mostrar_seccion("Objetivo General")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
mostrar_seccion("Medios Directos")
mostrar_seccion("Medios Indirectos")
