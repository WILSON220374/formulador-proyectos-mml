import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos persistentes
inicializar_session()

# --- ESTILO DE TARJETAS (CENTRADO Y PAPELERA ATÓMICA) ---
st.markdown("""
    <style>
    div[data-testid="stTextArea"] textarea {
        background-color: #f8f9fb !important;
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding-top: 15px !important;
    }
    .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.2rem !important;
        margin-top: -15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO Y TÍTULO SOLICITADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")

with col_titulo:
    st.title("🎯 7. Árbol de Objetivos Final") # Ajuste 2: Título final

with col_logo:
    # Ajuste 1: Traemos la imagen 'unnamed-1.jpg'
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.info("Podado Manual: Los cambios aquí no afectan al Árbol original de la Fase 5.")

CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"}
}

# --- FUNCIÓN DE BORRADO SEGURO (CALLBACK) ---
def eliminar_item_poda(seccion, indice):
    """Elimina el elemento exacto antes de que Streamlit refresque los índices."""
    st.session_state['arbol_objetivos_final'][seccion].pop(indice)
    guardar_datos_nube()

# --- FUNCIÓN DE RENDERIZADO DE TARJETAS ---
def render_poda_card(seccion, indice, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_OBJ[seccion]["color"]
    
    with st.container():
        st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0; margin-bottom: 0px;"></div>', unsafe_allow_html=True)
        
        nuevo_texto = st.text_area(
            label=f"p_{seccion}_{indice}", value=texto_actual, 
            label_visibility="collapsed", height=90, key=f"txt_{seccion}_{indice}"
        )
        
        # Ajuste 3: Papelera con on_click para evitar borrar el último elemento
        st.button("🗑️", key=f"btn_del_{seccion}_{indice}", on_click=eliminar_item_poda, args=(seccion, indice))
            
        if nuevo_texto != texto_actual:
            if isinstance(item, dict): st.session_state['arbol_objetivos_final'][seccion][indice]["texto"] = nuevo_texto
            else: st.session_state['arbol_objetivos_final'][seccion][indice] = nuevo_texto
            guardar_datos_nube()

# --- MOTOR DE EXPORTACIÓN (ESPACIADO ELÁSTICO) ---
def generar_png_final():
    fig, ax = plt.subplots(figsize=(22, 24))
    ax.set_xlim(0, 10); ax.set_ylim(-8, 14); ax.axis('off')
    ax.text(5, 13, "ÁRBOL DE OBJETIVOS FINAL", fontsize=28, fontweight='bold', ha='center', color='#1E3A8A')
    
    datos = st.session_state.get('arbol_objetivos_final', {})
    Y_LEVELS = {"Fin Último": 11.0, "Fines Indirectos": 9.0, "Fines Directos": 6.5, "Objetivo General": 4.0, "Medios Directos": 1.5, "Medios Indirectos": -2.0}
    stacks = {}

    def dibujar_caja(x, y, texto, color):
        lineas = textwrap.wrap(texto, width=18)
        txt_ajustado = "\n".join(lineas[:10])
        n_lineas = len(lineas[:10])
        rect_h = max(1.0, 0.4 + (n_lineas * 0.28))
        rect_w = 1.8
        ax.add_patch(plt.Rectangle((x-rect_w/2, y-rect_h/2), rect_w, rect_h, facecolor=color, edgecolor='#333', lw=1.5, zorder=3))
        ax.text(x, y, txt_ajustado, ha='center', va='center', fontsize=9, fontweight='bold', zorder=4)
        return rect_h

    # Lógica de distribución similar a Hoja 4 para fidelidad total
    m_dir = datos.get("Medios Directos", [])
    pos_x_medios = {(m['texto'] if isinstance(m, dict) else m): (i+1)*(10/(len(m_dir)+1)) for i, m in enumerate(m_dir)}
    f_dir = datos.get("Fines Directos", [])
    pos_x_fines = {(f['texto'] if isinstance(f, dict) else f): (i+1)*(10/(len(f_dir)+1)) for i, f in enumerate(f_dir)}

    for sec, y_base in Y_LEVELS.items():
        items = datos.get(sec, [])
        for it in items:
            txt = it["texto"] if isinstance(it, dict) else it
            if sec in ["Fin Último", "Objetivo General"]: x = 5.0
            elif sec == "Medios Directos": x = pos_x_medios.get(txt, 5.0)
            elif sec == "Fines Directos": x = pos_x_fines.get(txt, 5.0)
            elif sec == "Medios Indirectos": x = pos_x_medios.get(it.get("padre") if isinstance(it, dict) else None, 5.0)
            elif sec == "Fines Indirectos": x = pos_x_fines.get(it.get("padre") if isinstance(it, dict) else None, 5.0)
            
            offset = stacks.get((sec, x), 0)
            current_y = y_base - offset if "Medios" in sec else y_base + offset
            h_caja = dibujar_caja(x, current_y, txt, CONFIG_OBJ[sec]["color"])
            stacks[(sec, x)] = offset + h_caja + 0.5

    buf = io.BytesIO(); plt.savefig(buf, format="png", dpi=300, bbox_inches='tight'); plt.close(fig)
    return buf.getvalue()

# --- SIDEBAR Y ESTRUCTURA ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar desde Paso 5", use_container_width=True):
        st.session_state['arbol_objetivos_final'] = copy.deepcopy(st.session_state['arbol_objetivos'])
        guardar_datos_nube(); st.rerun()
    st.download_button("🖼️ Descargar Árbol Final", data=generar_png_final(), file_name="arbol_objetivos_final.png", use_container_width=True)

# --- FUNCIONES DE ESTRUCTURA (Respetando tu lógica) ---
def mostrar_seccion_simple_poda(key_interna):
    label_visual = CONFIG_OBJ[key_interna]["label"]
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"**{label_visual}**")
    with col_c:
        items = st.session_state['arbol_objetivos_final'].get(key_interna, [])
        if items: render_poda_card(key_interna, 0, items[0])

def mostrar_rama_jerarquica_poda(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos_final'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos_final'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]
    for seccion_actual, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='margin-top:25px;'>**{CONFIG_OBJ[seccion_actual]['label']}**</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    p_txt = p_data["texto"] if isinstance(p_data, dict) else p_data
                    with cols[i]:
                        if es_hijo:
                            h_rel = [(idx, h) for idx, h in enumerate(hijos) if isinstance(h, dict) and h.get("padre") == p_txt]
                            for h_idx_orig, h_data in h_rel: render_poda_card(seccion_actual, h_idx_orig, h_data)
                        else: render_poda_card(seccion_actual, i, p_data)

# --- DIBUJO ---
arbol_f = st.session_state.get('arbol_objetivos_final', {})
if not arbol_f:
    st.warning("Use 'Importar desde Paso 5' en la barra lateral.")
else:
    st.divider()
    mostrar_seccion_simple_poda("Fin Último")
    st.markdown("---")
    mostrar_rama_jerarquica_poda("Fines Directos", "Fines Indirectos", inversion=True)
    st.markdown("---")
    mostrar_seccion_simple_poda("Objetivo General")
    st.markdown("---")
    mostrar_rama_jerarquica_poda("Medios Directos", "Medios Indirectos", inversion=False)
