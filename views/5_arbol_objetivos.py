import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# Asegurar persistencia del estado
inicializar_session()

# --- ESTILO MAESTRO UNIFICADO (IGUAL A PROBLEMAS) ---
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
        font-size: 1.1rem;
    }
    
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 5. Árbol de Objetivos")

# 1. Configuración de Colores (Idéntico a Problemas)
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5, "tipo": "simple"},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "tipo": "hijo", "padre": "Fines Directos"},
    "Fines Directos": {"color": "#80BFFF", "y": 3, "tipo": "simple"},
    "Objetivo General": {"color": "#FFB3BA", "y": 2, "tipo": "simple"},
    "Medios Directos": {"color": "#FFFFBA", "y": 1, "tipo": "simple"},
    "Medios Indirectos": {"color": "#FFDFBA", "y": 0, "tipo": "hijo", "padre": "Medios Directos"}
}

# --- SIDEBAR: GESTIÓN Y EXPORTACIÓN ---
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
    
    # BOTÓN ✨ TRAER DATOS
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {
            "Efectos Indirectos": "Fines Indirectos", "Efectos Directos": "Fines Directos", 
            "Problema Principal": "Objetivo General", "Causas Directas": "Medios Directos", 
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
        st.success("¡Datos convertidos!")
        st.rerun()

    st.divider()
    st.subheader("📥 Exportar Árbol")

    # FUNCIÓN DE EXPORTACIÓN PNG (SIN DISTORSIÓN)
    def generar_png_objetivos():
        fig, ax = plt.subplots(figsize=(16, 14)) 
        ax.set_xlim(0, 10); ax.set_ylim(-1, 9); ax.axis('off')
        datos = st.session_state['arbol_objetivos']
        for seccion, conf in CONFIG_OBJ.items():
            items = datos.get(seccion, [])
            if not items: continue
            n = len(items)
            ancho_caja = min(2.2, (8.5/n) - 0.3)
            espaciado = 10 / (n + 1)
            y_base = conf["y"] * 1.5 
            for i, item in enumerate(items):
                x = (i + 1) * espaciado
                texto = item["texto"] if isinstance(item, dict) else item
                txt_ajustado = "\n".join(textwrap.wrap(texto, width=22))
                num_lineas = txt_ajustado.count('\n') + 1
                alto_caja = max(0.6, num_lineas * 0.18)
                rect = plt.Rectangle((x-(ancho_caja/2), y_base-(alto_caja/2)), ancho_caja, alto_caja, 
                                     facecolor=conf["color"], edgecolor='#333333', lw=1.2, zorder=2)
                ax.add_patch(rect)
                ax.text(x, y_base, txt_ajustado, ha='center', va='center', fontsize=9, fontweight='bold', color='black', zorder=3)
                if i == 0:
                    ax.text(0.1, y_base, seccion.upper(), fontsize=7, color='#777', fontweight='bold', va='center')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight', pad_inches=0.4)
        plt.close(fig)
        return buf.getvalue()

    st.download_button(label="🖼️ Descargar PNG", data=generar_png_objetivos(), file_name="arbol_objetivos.png", mime="image/png", use_container_width=True)

# --- RENDERIZADO (ESTILO PROBLEMAS) ---

def card_html(texto, color):
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

# --- DIBUJO ---
st.divider()
render_simple_obj("Fin Último")
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_rama_objetivos("Fines Directos", "Fines Indirectos", inversion=True)
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_simple_obj("Objetivo General") 
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_rama_objetivos("Medios Directos", "Medios Indirectos", inversion=False)
