import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia: Carga datos al abrir la pestaña
inicializar_session()

# --- ESTILO MAESTRO: TARJETAS EDITABLES CON COLOR TOTAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* HACER TRANSPARENTE EL EDITOR DE TEXTO: Para que se vea el color de la tarjeta detrás */
    div[data-testid="stTextArea"] {
        background-color: transparent !important;
    }
    div[data-testid="stTextArea"] textarea {
        background-color: transparent !important;
        color: #31333F !important;
        border: none !important;
        box-shadow: none !important;
        padding: 10px !important;
        font-weight: 500 !important;
        text-align: center !important;
        font-size: 14px !important;
    }
    div[data-baseweb="textarea"] {
        background-color: transparent !important;
        border: none !important;
    }

    /* Diseño de la tarjeta editable (Idéntico a Problemas) */
    .editable-card {
        border-radius: 10px;
        border-left: 8px solid rgba(0,0,0,0.1);
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 5. Árbol de Objetivos")

# Configuración de Colores y Posiciones
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4},
    "Fines Directos": {"color": "#80BFFF", "y": 3},
    "Objetivo General": {"color": "#FFB3BA", "y": 2},
    "Medios Directos": {"color": "#FFFFBA", "y": 1},
    "Medios Indirectos": {"color": "#FFDFBA", "y": 0}
}

# --- SIDEBAR: HERRAMIENTAS EXCLUSIVAS (Sin Generar Fichas) ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    # Botón para traer datos desde el Árbol de Problemas
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {
            "Efectos Indirectos": "Fines Indirectos",
            "Efectos Directos": "Fines Directos", 
            "Problema Principal": "Objetivo General", 
            "Causas Directas": "Medios Directos", 
            "Causas Indirectas": "Medios Indirectos"
        }
        # Limpiar objetivos previos para evitar duplicados
        for k in CONFIG_OBJ: st.session_state['arbol_objetivos'][k] = []
        
        # Mapear datos negativos a sus contenedores de objetivos
        for p_sec, o_sec in mapeo.items():
            if p_sec in problemas:
                for item in problemas[p_sec]:
                    txt = item['texto'] if isinstance(item, dict) else item
                    if isinstance(item, dict):
                        st.session_state['arbol_objetivos'][o_sec].append({"texto": txt, "padre": item['padre']})
                    else:
                        st.session_state['arbol_objetivos'][o_sec].append(txt)
        
        # El Fin Último es el único que no viene de problemas, lo inicializamos vacío
        if not st.session_state['arbol_objetivos']["Fin Último"]:
            st.session_state['arbol_objetivos']["Fin Último"] = ["Redactar aquí el Impacto Final Positivo"]
            
        guardar_datos_nube()
        st.success("¡Datos convertidos! Redacte en positivo sobre las tarjetas.")
        st.rerun()

    st.divider()

    # Función de exportación PNG
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

# --- FUNCIÓN DE RENDERIZADO DE TARJETAS EDITABLES ---

def render_editable_card(seccion, indice, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_OBJ[seccion]["color"]
    
    # Tarjeta con color y editor transparente integrado
    st.markdown(f'<div class="editable-card" style="background-color:{color};">', unsafe_allow_html=True)
    nuevo_texto = st.text_area(
        f"edit_{seccion}_{indice}", 
        value=texto_actual, 
        label_visibility="collapsed", 
        key=f"area_{seccion}_{indice}"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Si detectamos cambio al perder el foco, guardamos en la nube
    if nuevo_texto != texto_actual:
        if isinstance(item, dict):
            st.session_state['arbol_objetivos'][seccion][indice]["texto"] = nuevo_texto
        else:
            st.session_state['arbol_objetivos'][seccion][indice] = nuevo_texto
        guardar_datos_nube()
        st.rerun()

# --- DIBUJO DEL ÁRBOL ---

def mostrar_seccion_objetivos(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_objetivos'].get(nombre, [])
        if items:
            cols = st.columns(len(items))
            for i, item in enumerate(items):
                with cols[i]:
                    render_editable_card(nombre, i, item)
        else:
            st.caption("Sección vacía. Use el panel lateral para traer los datos.")

st.divider()
mostrar_seccion_objetivos("Fin Último")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.3;'>", unsafe_allow_html=True)
mostrar_seccion_objetivos("Fines Indirectos")
mostrar_seccion_objetivos("Fines Directos")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.3;'>", unsafe_allow_html=True)
mostrar_seccion_objetivos("Objetivo General")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.3;'>", unsafe_allow_html=True)
mostrar_seccion_objetivos("Medios Directos")
mostrar_seccion_objetivos("Medios Indirectos")
