import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
# Importación de funciones de persistencia
from session_state import inicializar_session, guardar_datos_nube

# --- PERSISTENCIA TOTAL: CARGA DATOS AL ABRIR LA PESTAÑA ---
inicializar_session()

# --- ESTILO MAESTRO UNIFICADO ---
st.markdown("""
    <style>
    /* 1. Tipografía general */
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    
    /* 2. Botón de Guardar (Primario): Texto blanco siempre visible */
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* 3. Papeleras en el área central: Rojo y negrita */
    .main .stButton button:not([kind="primary"]) p {
        color: #ff4b4b !important;
        font-weight: bold !important;
        font-size: 1.1rem;
    }

    /* 4. Botón Cerrar Sesión (Sidebar): Negro y sin negrilla */
    [data-testid="stSidebar"] .stButton button:not([kind="primary"]) p {
        color: black !important;
        font-weight: normal !important;
        font-size: 1rem;
    }
    
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SINCRONIZACIÓN Y MIGRACIÓN ---
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])
    if 'Problema Superior' in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas'].pop('Problema Superior')

st.title("🌳 4. Árbol de Problemas")

# Configuración Maestra de Secciones y Colores
CONFIG = {
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos", "y": 4},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple", "y": 3},
    "Problema Principal": {"color": "#FFB3BA", "limite": 1, "tipo": "simple", "y": 2},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple", "y": 1},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas", "y": 0}
}

# --- SIDEBAR: GESTIÓN Y EXPORTACIÓN ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción de la idea:")
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'].get(CONFIG[tipo_sel]["padre"], [])
            if opciones_p:
                padre_asociado = st.selectbox(f"Vincular a {CONFIG[tipo_sel]['padre']}:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if len(st.session_state['arbol_tarjetas'].get(tipo_sel, [])) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo" and padre_asociado:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                
                # AUTO-GUARDADO: Sincroniza con la nube inmediatamente
                guardar_datos_nube()
                st.rerun()

    st.divider()
    st.subheader("📥 Exportar Árbol")

    def generar_png_arbol():
        fig, ax = plt.subplots(figsize=(16, 12)) 
        ax.set_xlim(0, 10); ax.set_ylim(-1, 7.5); ax.axis('off')
        datos = st.session_state['arbol_tarjetas']
        for seccion, conf in CONFIG.items():
            items_raw = datos.get(seccion, [])
            # Filtrado para que el PNG sea idéntico a la pantalla
            if conf["tipo"] == "hijo":
                padres_ref = datos.get(conf["padre"], [])
                items = [h for h in items_raw if isinstance(h, dict) and h.get("padre") in padres_ref]
            else:
                items = items_raw
                
            if not items: continue
            n = len(items)
            espaciado = 10 / (n + 1)
            y_base = conf["y"] * 1.5 
            for i, item in enumerate(items):
                x = (i + 1) * espaciado
                texto = item["texto"] if isinstance(item, dict) else item
                txt_ajustado = "\n".join(textwrap.wrap(texto, width=22))
                num_lineas = txt_ajustado.count('\n') + 1
                rect = plt.Rectangle((x-1.1, y_base-0.4), 2.2, max(0.6, num_lineas * 0.18), 
                                     facecolor=conf["color"], edgecolor='#333333', lw=1.2)
                ax.add_patch(rect)
                ax.text(x, y_base, txt_ajustado, ha='center', va='center', fontsize=9, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button(label="🖼️ Descargar Árbol (PNG)", data=generar_png_arbol(), file_name="arbol_final.png", mime="image/png", use_container_width=True)

# --- RENDERIZADO EN PANTALLA ---
def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:15px; border-radius:10px; 
               border-left:8px solid rgba(0,0,0,0.1); color:#31333F; font-weight:500; 
               margin-bottom:8px; min-height:75px; box-shadow: 2px 2px 5px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center; font-size:14px;">
               {texto}</div>"""

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'].get(nombre, [])
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            # Botón de borrado restaurado para el Problema Principal
            if st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                guardar_datos_nube(); st.rerun()
        else: st.caption("Sección vacía")

def render_rama(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_tarjetas'].get(nombre_padre, [])
    hijos = st.session_state['arbol_tarjetas'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion_actual, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{seccion_actual.upper()}</div>", unsafe_allow_html=True)
        with col_c:
            if not padres and not es_hijo:
                st.caption(f"Debe crear un {nombre_padre} primero.")
            elif padres:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            h_del_p = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_txt]
                            for h_idx, h_data in enumerate(h_del_p):
                                st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{h_idx}"):
                                    st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data)
                                    guardar_datos_nube(); st.rerun()
                        else:
                            st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_p_{seccion_actual}_{i}"):
                                h_asoc = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_txt]
                                if h_asoc: st.error("Borre indirectos primero")
                                else: 
                                    st.session_state['arbol_tarjetas'][seccion_actual].pop(i)
                                    guardar_datos_nube(); st.rerun()
    
    # SECCIÓN DE LIMPIEZA: Para eliminar fichas sin padre (fantasmas como la letra 'a')
    huerfanos = [h for h in hijos if not isinstance(h, dict) or h.get("padre") not in padres]
    if huerfanos:
        with st.expander("⚠️ Fichas sin vínculo (Limpiar Fantasmas)"):
            for h in huerfanos:
                txt = h["texto"] if isinstance(h, dict) else h
                st.write(f"- {txt}")
                if st.button(f"Eliminar fantasma: {txt[:20]}...", key=f"clean_{txt}"):
                    st.session_state['arbol_tarjetas'][nombre_hijo].remove(h)
                    guardar_datos_nube(); st.rerun()

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")
render_simple("Problema Principal") 
st.markdown("---")
render_rama("Causas Directas", "Causas Indirectas", inversion=False)
