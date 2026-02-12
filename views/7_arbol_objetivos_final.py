import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

st.title("🎯 7. Árbol de Objetivos Final")
st.info("Utilice esta mesa de trabajo para 'podar' el árbol y dejar únicamente los componentes definitivos.")

CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5, "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "y": 3, "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "y": 2, "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "y": 1, "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "y": 0, "label": "ACTIVIDADES"}
}

# --- BARRA LATERAL: CONTROL DE PODA ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar desde Paso 5", use_container_width=True):
        st.session_state['arbol_objetivos_final'] = copy.deepcopy(st.session_state['arbol_objetivos'])
        guardar_datos_nube(); st.rerun()
    
    st.divider()
    
    def generar_png_podado():
        fig, ax = plt.subplots(figsize=(16, 14))
        ax.set_xlim(0, 10); ax.set_ylim(-1, 8.5); ax.axis('off')
        datos = st.session_state['arbol_objetivos_final']
        for sec, conf in CONFIG_OBJ.items():
            items = datos.get(sec, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            for i, item in enumerate(items):
                x, y_base = (i + 1) * espacio, conf["y"] * 1.5 
                txt = item["texto"] if isinstance(item, dict) else item
                ax.add_patch(plt.Rectangle((x-1.1, y_base-0.4), 2.2, 0.7, facecolor=conf["color"], edgecolor='#333', lw=1.2))
                ax.text(x, y_base, "\n".join(textwrap.wrap(txt, width=22)), ha='center', va='center', fontsize=8, fontweight='bold')
        buf = io.BytesIO(); plt.savefig(buf, format="png", dpi=300, bbox_inches='tight'); plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol Podado", data=generar_png_podado(), file_name="arbol_final_podado.png", use_container_width=True)

# --- RENDERIZADO INTERACTIVO ---
def render_poda_card(seccion, indice, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    st.markdown(f'<div style="background-color: {CONFIG_OBJ[seccion]["color"]}; height: 6px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    nuevo_texto = st.text_area(label=f"p_{seccion}_{indice}", value=texto_actual, label_visibility="collapsed", height=80, key=f"f_edit_{seccion}_{indice}")
    
    if st.button("🗑️ Eliminar", key=f"del_f_{seccion}_{indice}"):
        st.session_state['arbol_objetivos_final'][seccion].pop(indice)
        guardar_datos_nube(); st.rerun()
    
    if nuevo_texto != texto_actual:
        if isinstance(item, dict): st.session_state['arbol_objetivos_final'][seccion][indice]["texto"] = nuevo_texto
        else: st.session_state['arbol_objetivos_final'][seccion][indice] = nuevo_texto
        guardar_datos_nube()

# --- DIBUJO DE LA MESA DE TRABAJO ---
arbol_f = st.session_state.get('arbol_objetivos_final', {})
if not arbol_f:
    st.warning("Árbol vacío. Use 'Importar desde Paso 5' en el menú lateral.")
else:
    for nivel, conf in CONFIG_OBJ.items():
        st.markdown(f"#### {conf['label']}")
        items = arbol_f.get(nivel, [])
        if items:
            cols = st.columns(len(items) if len(items) > 0 else 1)
            for i, item in enumerate(items):
                with cols[i]: render_poda_card(nivel, i, item)
        st.divider()
