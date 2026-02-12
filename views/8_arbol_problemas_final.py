import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de persistencia
inicializar_session()

# --- ESTILO DE TARJETAS (Consistente con la P7) ---
st.markdown("""
    <style>
    div[data-testid="stTextArea"] textarea {
        background-color: #f8f9fb !important;
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }
    .stButton button:not([kind="primary"]) {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        padding: 0 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌳 8. Árbol de Problemas Final")
st.info("Poda Manual: Los cambios aquí no afectan al diagnóstico original de la Fase 4.")

CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#B3D9FF", "label": "EFECTOS INDIRECTOS"},
    "Efectos Directos": {"color": "#80BFFF", "label": "EFECTOS DIRECTOS"},
    "Problema Principal": {"color": "#FFB3BA", "label": "PROBLEMA PRINCIPAL"},
    "Causas Directas": {"color": "#FFFFBA", "label": "CAUSAS DIRECTAS"},
    "Causas Indirectas": {"color": "#FFDFBA", "label": "CAUSAS INDIRECTAS"}
}

# --- BARRA LATERAL: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar desde Paso 4", use_container_width=True):
        # Clonamos el árbol de tarjetas original
        st.session_state['arbol_problemas_final'] = copy.deepcopy(st.session_state['arbol_tarjetas'])
        guardar_datos_nube(); st.rerun()
    
    st.divider()
    
    def generar_png_problemas_final():
        fig, ax = plt.subplots(figsize=(16, 12))
        ax.set_xlim(0, 10); ax.set_ylim(-1, 7.5); ax.axis('off')
        datos = st.session_state.get('arbol_problemas_final', {})
        y_pos = {"Efectos Indirectos": 6.5, "Efectos Directos": 5.0, "Problema Principal": 3.5, 
                 "Causas Directas": 1.5, "Causas Indirectas": 0}
        
        for sec, y in y_pos.items():
            items = datos.get(sec, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            for i, it in enumerate(items):
                x = (i + 1) * espacio
                txt = it["texto"] if isinstance(it, dict) else it
                ax.add_patch(plt.Rectangle((x-1.1, y-0.35), 2.2, 0.7, facecolor=CONFIG_PROB[sec]["color"], edgecolor='#333', lw=1.2))
                ax.text(x, y, "\n".join(textwrap.wrap(txt, width=22)), ha='center', va='center', fontsize=9, fontweight='bold')
        buf = io.BytesIO(); plt.savefig(buf, format="png", dpi=300, bbox_inches='tight'); plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol Podado", generar_png_problemas_final(), "arbol_problemas_final.png", use_container_width=True)

# --- FUNCIONES DE RENDERIZADO Y ALINEACIÓN (LOGICA P7) ---

def render_poda_card(seccion, indice, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_PROB[seccion]["color"]
    with st.container():
        st.markdown(f'<div style="background-color: {color}; height: 6px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
        nuevo_texto = st.text_area(label=f"txt_{seccion}_{indice}", value=texto_actual, label_visibility="collapsed", height=90, key=f"p_edit_{seccion}_{indice}")
        
        # El botón de eliminar usa el índice exacto
        if st.button("🗑️ Eliminar", key=f"p_del_{seccion}_{indice}"):
            st.session_state['arbol_problemas_final'][seccion].pop(indice)
            guardar_datos_nube(); st.rerun()
            
        if nuevo_texto != texto_actual:
            if isinstance(item, dict): st.session_state['arbol_problemas_final'][seccion][indice]["texto"] = nuevo_texto
            else: st.session_state['arbol_problemas_final'][seccion][indice] = nuevo_texto
            guardar_datos_nube()

def mostrar_rama_poda(padre_key, hijo_key, inversion=False):
    """Alinea verticalmente las causas o efectos bajo sus padres."""
    padres = st.session_state['arbol_problemas_final'].get(padre_key, [])
    hijos = st.session_state['arbol_problemas_final'].get(hijo_key, [])
    orden = [(hijo_key, True), (padre_key, False)] if inversion else [(padre_key, False), (hijo_key, True)]
    
    for sec, es_hijo in orden:
        c1, c2 = st.columns([1, 4])
        with c1: st.markdown(f"<div style='margin-top:25px;'>**{CONFIG_PROB[sec]['label']}**</div>", unsafe_allow_html=True)
        with c2:
            if padres:
                cols = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    p_txt = p_data["texto"] if isinstance(p_data, dict) else p_data
                    with cols[i]:
                        if es_hijo:
                            # Filtramos los hijos por su padre
                            h_rel = [(idx, h) for idx, h in enumerate(hijos) if isinstance(h, dict) and h.get("padre") == p_txt]
                            for h_orig_idx, h_data in h_rel: render_poda_card(sec, h_orig_idx, h_data)
                        else: render_poda_card(sec, i, p_data)
            else: st.caption("Sin datos.")

# --- DIBUJO DE LA MESA ---
arbol_p_f = st.session_state.get('arbol_problemas_final', {})

if not arbol_p_f:
    st.warning("Árbol vacío. Use 'Importar desde Paso 4' en el menú lateral.")
else:
    st.divider()
    # Efectos (Hacia arriba: Inversión=True)
    mostrar_rama_poda("Efectos Directos", "Efectos Indirectos", inversion=True)
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    
    # Problema Central
    c1, c2 = st.columns([1, 4])
    with c1: st.markdown(f"**{CONFIG_PROB['Problema Principal']['label']}**")
    with c2: 
        if arbol_p_f.get('Problema Principal'): render_poda_card('Problema Principal', 0, arbol_p_f['Problema Principal'][0])
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    
    # Causas (Hacia abajo: Inversión=False)
    mostrar_rama_poda("Causas Directas", "Causas Indirectas", inversion=False)
