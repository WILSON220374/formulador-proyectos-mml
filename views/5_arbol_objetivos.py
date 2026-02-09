import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

st.title("🎯 5. Árbol de Objetivos (Fines y Medios)")

# Configuración Maestra de Objetivos
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5, "tipo": "simple", "limite": 1},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "tipo": "hijo", "padre": "Fines Directos", "limite": 99},
    "Fines Directos": {"color": "#80BFFF", "y": 3, "tipo": "simple", "limite": 99},
    "Objetivo General": {"color": "#D1C4E9", "y": 2, "tipo": "simple", "limite": 1},
    "Medios Directos": {"color": "#FFF9C4", "y": 1, "tipo": "simple", "limite": 99},
    "Medios Indirectos": {"color": "#FFE0B2", "y": 0, "tipo": "hijo", "padre": "Medios Directos", "limite": 99}
}

# --- SIDEBAR: TRANSFORMACIÓN Y EXPORTACIÓN ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    # Botón de Mapeo Automático
    if st.button("✨ Generar desde Problemas", use_container_width=True):
        problemas = st.session_state['arbol_tarjetas']
        mapeo = {
            "Problema Superior": "Fin Último", "Efectos Indirectos": "Fines Indirectos",
            "Efectos Directos": "Fines Directos", "Problema Central": "Objetivo General",
            "Causas Directas": "Medios Directos", "Causas Indirectas": "Medios Indirectos"
        }
        for p_sec, o_sec in mapeo.items():
            st.session_state['arbol_objetivos'][o_sec] = []
            for item in problemas[p_sec]:
                if isinstance(item, dict):
                    st.session_state['arbol_objetivos'][o_sec].append({"texto": f"Lograr: {item['texto']}", "padre": f"Lograr: {item['padre']}"})
                else:
                    st.session_state['arbol_objetivos'][o_sec].append(f"Alcanzar: {item}")
        st.rerun()

    st.divider()

    # Función para generar la Imagen PNG profesional
    def exportar_objetivos_png():
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10); ax.set_ylim(-0.5, 6); ax.axis('off')
        datos = st.session_state['arbol_objetivos']
        for sec, conf in CONFIG_OBJ.items():
            items = datos[sec]
            if not items: continue
            espacio = 10 / (len(items) + 1)
            for i, item in enumerate(items):
                x = (i + 1) * espacio
                txt = item["texto"] if isinstance(item, dict) else item
                rect = plt.Rectangle((x-0.7, conf["y"]-0.25), 1.4, 0.5, facecolor=conf["color"], edgecolor='black', lw=0.5)
                ax.add_patch(rect)
                txt_wrap = "\n".join(textwrap.wrap(txt, width=15))
                ax.text(x, conf["y"], txt_wrap, ha='center', va='center', fontsize=8, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Imagen (PNG)", data=exportar_objetivos_png(), file_name="arbol_objetivos.png", mime="image/png", use_container_width=True)

# --- FUNCIONES DE RENDERIZADO (ALINEACIÓN VERTICAL) ---
def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:12px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:8px; min-height:70px; display: flex; align-items: center; 
               justify-content: center; text-align: center; box-shadow: 2px 2px 5px #eee;">
               {texto}</div>"""

def render_rama_objetivos(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos'][nombre_padre]
    hijos = st.session_state['arbol_objetivos'][nombre_hijo]
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{seccion.upper()}</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            hijos_p = [h for h in hijos if h["padre"] == (p_txt["texto"] if isinstance(p_txt, dict) else p_txt)]
                            for h_idx, h_data in enumerate(hijos_p):
                                st.markdown(card_html(h_data["texto"], CONFIG_OBJ[seccion]["color"]), unsafe_allow_html=True)
                        else:
                            st.markdown(card_html(p_txt["texto"] if isinstance(p_txt, dict) else p_txt, CONFIG_OBJ[seccion]["color"]), unsafe_allow_html=True)
            else: st.caption("Esperando datos...")

def render_simple_obj(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_objetivos'][nombre]
        if items: st.markdown(card_html(items[0], CONFIG_OBJ[nombre]["color"]), unsafe_allow_html=True)
        else: st.caption("Sección vacía")

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
render_simple_obj("Fin Último")
st.markdown("---")
render_rama_objetivos("Fines Directos", "Fines Indirectos", inversion=True)
st.markdown("---")
st.success("🎯 OBJETIVO GENERAL")
render_simple_obj("Objetivo General")
st.markdown("---")
render_rama_objetivos("Medios Directos", "Medios Indirectos", inversion=False)
