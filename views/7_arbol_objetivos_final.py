import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos persistentes
inicializar_session()

# --- ESTILO DE TARJETAS (Consistente con la P5) ---
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

st.title("🎯 7. Árbol de Objetivos Final")
st.info("Podado Manual: Los cambios aquí no afectan al Árbol original de la Fase 5.")

CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"}
}

# --- BARRA LATERAL: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar desde Paso 5", use_container_width=True):
        # Clonamos el árbol original para la mesa de poda
        st.session_state['arbol_objetivos_final'] = copy.deepcopy(st.session_state['arbol_objetivos'])
        guardar_datos_nube(); st.rerun()
    
    st.divider()
    
    def generar_png_final():
        fig, ax = plt.subplots(figsize=(16, 14))
        ax.set_xlim(0, 10); ax.set_ylim(-1, 8.5); ax.axis('off')
        datos = st.session_state.get('arbol_objetivos_final', {})
        y_pos = {"Fin Último": 7.5, "Fines Indirectos": 6.0, "Fines Directos": 4.5, 
                 "Objetivo General": 3.0, "Medios Directos": 1.5, "Medios Indirectos": 0}
        
        for sec, y_base in y_pos.items():
            items = datos.get(sec, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            for i, item in enumerate(items):
                x = (i + 1) * espacio
                txt = item["texto"] if isinstance(item, dict) else item
                ax.add_patch(plt.Rectangle((x-1.1, y_base-0.35), 2.2, 0.7, facecolor=CONFIG_OBJ[sec]["color"], edgecolor='#333', lw=1.2))
                ax.text(x, y_base, "\n".join(textwrap.wrap(txt, width=22)), ha='center', va='center', fontsize=8, fontweight='bold')
        buf = io.BytesIO(); plt.savefig(buf, format="png", dpi=300, bbox_inches='tight'); plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol Final", data=generar_png_final(), file_name="arbol_objetivos_final.png", use_container_width=True)

# --- FUNCIÓN DE RENDERIZADO CON VÍNCULOS Y ELIMINACIÓN ---

def render_poda_card(seccion, indice, item):
    """Renderiza una tarjeta con opción de edición y eliminación."""
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_OBJ[seccion]["color"]
    
    with st.container():
        st.markdown(f'<div style="background-color: {color}; height: 6px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
        # Edición de texto
        nuevo_texto = st.text_area(label=f"p_{seccion}_{indice}", value=texto_actual, label_visibility="collapsed", height=90, key=f"txt_{seccion}_{indice}")
        
        # Botón de Poda (Eliminar) - FIX: Usamos el índice actual de la lista para evitar errores de alineación
        if st.button("🗑️ Eliminar", key=f"btn_del_{seccion}_{indice}"):
            st.session_state['arbol_objetivos_final'][seccion].pop(indice)
            guardar_datos_nube(); st.rerun()
        
        if nuevo_texto != texto_actual:
            if isinstance(item, dict): st.session_state['arbol_objetivos_final'][seccion][indice]["texto"] = nuevo_texto
            else: st.session_state['arbol_objetivos_final'][seccion][indice] = nuevo_texto
            guardar_datos_nube()

# --- LÓGICA DE RAMAS JERÁRQUICAS (SOLUCIÓN ALINEACIÓN) ---

def mostrar_seccion_simple_poda(key_interna):
    label_visual = CONFIG_OBJ[key_interna]["label"]
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"**{label_visual}**")
    with col_c:
        items = st.session_state['arbol_objetivos_final'].get(key_interna, [])
        if items: render_poda_card(key_interna, 0, items[0])
        else: st.caption("Vacío.")

def mostrar_rama_jerarquica_poda(nombre_padre, nombre_hijo, inversion=False):
    """Alinea hijos debajo de sus padres usando columnas, igual que en la P5."""
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
                            # Filtramos los hijos que pertenecen a este padre específico
                            h_relacionados = [(idx, h) for idx, h in enumerate(hijos) 
                                              if isinstance(h, dict) and h.get("padre") == p_txt]
                            for h_idx_orig, h_data in h_relacionados:
                                render_poda_card(seccion_actual, h_idx_orig, h_data)
                        else:
                            render_poda_card(seccion_actual, i, p_data)
            else: st.caption(f"Defina {nombre_padre} primero.")

# --- DIBUJO DEL ÁRBOL ---
arbol_f = st.session_state.get('arbol_objetivos_final', {})

if not arbol_f:
    st.warning("El árbol está vacío. Use 'Importar desde Paso 5' en la barra lateral.")
else:
    st.divider()
    mostrar_seccion_simple_poda("Fin Último")
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    
    # Fines: Alineación jerárquica
    mostrar_rama_jerarquica_poda("Fines Directos", "Fines Indirectos", inversion=True)
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    
    mostrar_seccion_simple_poda("Objetivo General")
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    
    # Medios/Actividades: Alineación jerárquica
    mostrar_rama_jerarquica_poda("Medios Directos", "Medios Indirectos", inversion=False)
