import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de persistencia
inicializar_session()

# --- ESTILO DE TARJETAS ---
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
st.info("Poda Manual: Los cambios aquí son definitivos para su Matriz de Marco Lógico.")

CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#B3D9FF", "label": "EFECTOS INDIRECTOS"},
    "Efectos Directos": {"color": "#80BFFF", "label": "EFECTOS DIRECTOS"},
    "Problema Principal": {"color": "#FFB3BA", "label": "PROBLEMA PRINCIPAL"},
    "Causas Directas": {"color": "#FFFFBA", "label": "CAUSAS DIRECTAS"},
    "Causas Indirectas": {"color": "#FFDFBA", "label": "CAUSAS INDIRECTAS"}
}

# --- FUNCIÓN DE VALIDACIÓN ESTRICTA (PARA EVITAR LETRAS SUELTAS) ---
def es_valido(item):
    if not item: return False
    txt = item["texto"] if isinstance(item, dict) else str(item)
    return len(txt.strip()) > 3 # Solo acepta textos con más de 3 letras

# --- BARRA LATERAL: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas de Limpieza")
    
    if st.button("♻️ Importar desde Paso 4", use_container_width=True):
        st.session_state['arbol_problemas_final'] = copy.deepcopy(st.session_state['arbol_tarjetas'])
        guardar_datos_nube(); st.rerun()

    # NUEVO: Botón para purgar letras intrusas de la base de datos
    if st.button("🧹 Limpiar Memoria (Borrar Letras)", use_container_width=True, type="primary"):
        for sec in st.session_state['arbol_problemas_final']:
            st.session_state['arbol_problemas_final'][sec] = [
                it for it in st.session_state['arbol_problemas_final'][sec] if es_valido(it)
            ]
        guardar_datos_nube(); st.toast("¡Memoria purgada de letras intrusas!"); st.rerun()
    
    st.divider()
    
    def generar_png_problemas_limpio():
        fig, ax = plt.subplots(figsize=(18, 16))
        ax.set_xlim(0, 10); ax.set_ylim(-3, 11); ax.axis('off')
        datos = st.session_state.get('arbol_problemas_final', {})
        
        # 1. Mapeo de X solo con elementos válidos
        c_dir = [c for c in datos.get("Causas Directas", []) if es_valido(c)]
        esp_c = 10 / (len(c_dir) + 1) if c_dir else 5.0
        pos_x_causas = { (c['texto'] if isinstance(c, dict) else c): (i+1)*esp_c for i, c in enumerate(c_dir) }

        e_dir = [e for e in datos.get("Efectos Directos", []) if es_valido(e)]
        esp_e = 10 / (len(e_dir) + 1) if e_dir else 5.0
        pos_x_efectos = { (e['texto'] if isinstance(e, dict) else e): (i+1)*esp_e for i, e in enumerate(e_dir) }

        Y_LEVELS = {"Efectos Indirectos": 9.5, "Efectos Directos": 8.0, "Problema Principal": 5.0, "Causas Directas": 2.5, "Causas Indirectas": 1.0}
        stacks = {}

        for sec, y_base in Y_LEVELS.items():
            items = [it for it in datos.get(sec, []) if es_valido(it)]
            for it in items:
                txt = it["texto"] if isinstance(it, dict) else it
                x = 5.0
                if sec == "Causas Directas": x = pos_x_causas.get(txt, 5.0)
                elif sec == "Efectos Directos": x = pos_x_efectos.get(txt, 5.0)
                elif sec in ["Causas Indirectas", "Efectos Indirectos"]:
                    p_txt = it.get("padre") if isinstance(it, dict) else None
                    # Sincronización estricta con el padre
                    x = pos_x_causas.get(p_txt) if sec == "Causas Indirectas" else pos_x_efectos.get(p_txt)
                    if x is None: continue # Esto elimina las letras huérfanas en el PNG

                current_y = y_base
                if sec in ["Causas Indirectas", "Efectos Indirectos"]:
                    offset = stacks.get((sec, x), 0)
                    current_y = y_base - offset if sec == "Causas Indirectas" else y_base + offset
                    stacks[(sec, x)] = offset + 1.3

                ax.add_patch(plt.Rectangle((x-1.15, current_y-0.5), 2.3, 1.0, facecolor=CONFIG_PROB[sec]["color"], edgecolor='#333', lw=1.5))
                ax.text(x, current_y, "\n".join(textwrap.wrap(txt, width=22)), ha='center', va='center', fontsize=9, fontweight='bold')
        
        buf = io.BytesIO(); plt.savefig(buf, format="png", dpi=300, bbox_inches='tight'); plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol Final Limpio", generar_png_problemas_limpio(), "arbol_problemas_final.png", use_container_width=True)

# --- FUNCIONES DE RENDERIZADO (LOGICA DE PANTALLA) ---

def render_poda_card(seccion, indice, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_PROB[seccion]["color"]
    with st.container():
        st.markdown(f'<div style="background-color: {color}; height: 6px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
        nuevo_texto = st.text_area(label=f"txt_{seccion}_{indice}", value=texto_actual, label_visibility="collapsed", height=90, key=f"p_edit_{seccion}_{indice}")
        
        if st.button("🗑️ Eliminar", key=f"p_del_{seccion}_{indice}"):
            st.session_state['arbol_problemas_final'][seccion].pop(indice)
            guardar_datos_nube(); st.rerun()
            
        if nuevo_texto != texto_actual:
            if isinstance(item, dict): st.session_state['arbol_problemas_final'][seccion][indice]["texto"] = nuevo_texto.strip()
            else: st.session_state['arbol_problemas_final'][seccion][indice] = nuevo_texto.strip()
            guardar_datos_nube()

def mostrar_rama_poda(padre_key, hijo_key, inversion=False):
    # Solo mostramos lo que es válido en pantalla
    padres = [p for p in st.session_state['arbol_problemas_final'].get(padre_key, []) if es_valido(p)]
    hijos = [h for h in st.session_state['arbol_problemas_final'].get(hijo_key, []) if es_valido(h)]
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
                            h_rel = [(idx, h) for idx, h in enumerate(hijos) if isinstance(h, dict) and h.get("padre") == p_txt]
                            for _, h_data in h_rel:
                                # Buscamos el índice original para el render
                                idx_orig = next(i for i, x in enumerate(st.session_state['arbol_problemas_final'][sec]) if x == h_data)
                                render_poda_card(sec, idx_orig, h_data)
                        else:
                            idx_orig = next(i for i, x in enumerate(st.session_state['arbol_problemas_final'][padre_key]) if x == p_data)
                            render_poda_card(sec, idx_orig, p_data)
            else: st.caption("Sin datos.")

# --- DIBUJO DE LA MESA ---
arbol_p_f = st.session_state.get('arbol_problemas_final', {})

if not arbol_p_f:
    st.warning("Árbol vacío. Use 'Importar desde Paso 4' en el menú lateral.")
else:
    st.divider()
    mostrar_rama_poda("Efectos Directos", "Efectos Indirectos", inversion=True)
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 4])
    with c1: st.markdown(f"**{CONFIG_PROB['Problema Principal']['label']}**")
    with c2: 
        if arbol_p_f.get('Problema Principal') and es_valido(arbol_p_f['Problema Principal'][0]):
            render_poda_card('Problema Principal', 0, arbol_p_f['Problema Principal'][0])
    st.markdown("<hr style='border: 1px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
    
    mostrar_rama_poda("Causas Directas", "Causas Indirectas", inversion=False)
