import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
# 1. Persistencia: Carga datos de la nube al iniciar
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

# --- ESTILO: CENTRADO TOTAL Y FRANJA DELGADA (6px) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* CENTRADO DEL TEXTO Y ESTILO DE TARJETA GRIS */
    div[data-testid="stTextArea"] textarea {
        background-color: #f0f2f6 !important;
        border-radius: 0 0 10px 10px !important;
        border: 1px solid #e6e9ef !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #31333F !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding-top: 25px !important; 
    }
    
    div[data-testid="stTextArea"] textarea:focus { border-color: #d0d4dc !important; }
    .stButton button[kind="primary"] p { color: white !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 5. Árbol de Objetivos")

# Configuración Maestra con nuevos nombres
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5, "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "y": 3, "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "y": 2, "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "y": 1, "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "y": 0, "label": "ACTIVIDADES"}
}

# --- SIDEBAR: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
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
                        st.session_state['arbol_objetivos'][o_sec].append({"texto": txt.upper(), "padre": item['padre'].upper()})
                    else:
                        st.session_state['arbol_objetivos'][o_sec].append(txt.upper())
        
        if not st.session_state['arbol_objetivos']["Fin Último"]:
            st.session_state['arbol_objetivos']["Fin Último"] = ["MEJORAR LA CALIDAD DE VIDA"]
            
        guardar_datos_nube()
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
                ax.text(x, y_base, txt_wrap, ha='center', va='center', fontsize=8, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol (PNG)", data=generar_png_objetivos(), file_name="arbol_objetivos.png", mime="image/png", use_container_width=True)

# --- FUNCIÓN DE RENDERIZADO CON VÍNCULOS INTELIGENTES ---

def render_objective_card(seccion, indice_global, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_OBJ[seccion]["color"]
    
    st.markdown(f'<div style="background-color: {color}; height: 6px; border-radius: 10px 10px 0 0; margin-bottom: 0px;"></div>', unsafe_allow_html=True)
    
    nuevo_texto = st.text_area(label=f"edit_{seccion}_{indice_global}", value=texto_actual, label_visibility="collapsed", key=f"area_{seccion}_{indice_global}", height=90)
    
    if nuevo_texto != texto_actual:
        # 1. Actualizamos el texto de la tarjeta actual
        if isinstance(item, dict):
            st.session_state['arbol_objetivos'][seccion][indice_global]["texto"] = nuevo_texto
        else:
            st.session_state['arbol_objetivos'][seccion][indice_global] = nuevo_texto
        
        # 2. CASCADA: Si editamos un PADRE, actualizamos el vínculo de sus HIJOS
        relaciones = {"Fines Directos": "Fines Indirectos", "Medios Directos": "Medios Indirectos"}
        if seccion in relaciones:
            seccion_hija = relaciones[seccion]
            for h in st.session_state['arbol_objetivos'][seccion_hija]:
                if isinstance(h, dict) and h.get("padre") == texto_actual:
                    h["padre"] = nuevo_texto
        
        guardar_datos_nube()
        st.rerun()

# --- FUNCIONES DE ESTRUCTURA JERÁRQUICA ---

def mostrar_seccion_simple(key_interna):
    label_visual = CONFIG_OBJ[key_interna]["label"]
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{label_visual}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_objetivos'].get(key_interna, [])
        if items: render_objective_card(key_interna, 0, items[0])
        else: st.caption("Sección vacía.")

def mostrar_rama_jerarquica(nombre_padre, nombre_hijo, inversion=False):
    """Muestra padres e hijos alineados verticalmente por columnas"""
    padres = st.session_state['arbol_objetivos'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion_actual, es_hijo in orden:
        label_visual = CONFIG_OBJ[seccion_actual]["label"]
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{label_visual}</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    p_txt = p_data["texto"] if isinstance(p_data, dict) else p_data
                    with cols[i]:
                        if es_hijo:
                            # Filtramos los hijos que pertenecen a este padre específico
                            h_relacionados = [(idx, h) for idx, h in enumerate(hijos) 
                                              if isinstance(h, dict) and h.get("padre") == p_txt]
                            for h_idx_orig, h_data in h_relacionados:
                                render_objective_card(seccion_actual, h_idx_orig, h_data)
                        else:
                            render_objective_card(seccion_actual, i, p_data)
            else: st.caption(f"Debe definir {nombre_padre} primero.")

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
mostrar_seccion_simple("Fin Último")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
# Nivel Fines: Indirectos arriba, Directos abajo
mostrar_rama_jerarquica("Fines Directos", "Fines Indirectos", inversion=True)
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
mostrar_seccion_simple("Objetivo General")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
# Nivel Medios: Objetivos Específicos arriba, Actividades abajo
mostrar_rama_jerarquica("Medios Directos", "Medios Indirectos", inversion=False)
