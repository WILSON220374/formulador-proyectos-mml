import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- SINCRONIZACIÓN DE LLAVES (MIGRACIÓN DE DATOS) ---
# Esto evita que se pierda la información guardada al cambiar el nombre de la sección
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        # Recuperamos el dato de 'Problema Central' si existe, o inicializamos vacío
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])

st.title("🌳 4. Árbol de Problemas (Vista Jerárquica e Imagen)")

# 1. Configuración Maestra - Se cambia la etiqueta visual a 'Problema Principal'
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple", "y": 5},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos", "y": 4},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple", "y": 3},
    "Problema Principal": {"color": "#FFB3BA", "limite": 1, "tipo": "simple", "y": 2}, # <-- CAMBIO REALIZADO
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple", "y": 1},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas", "y": 0}
}

# --- SIDEBAR: GESTIÓN Y DESCARGA ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("2. Descripción de la idea:")
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'].get(CONFIG[tipo_sel]["padre"], [])
            if opciones_p:
                padre_asociado = st.selectbox(f"3. Vincular a {CONFIG[tipo_sel]['padre']}:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if len(st.session_state['arbol_tarjetas'].get(tipo_sel, [])) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo" and padre_asociado:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()
            else:
                st.error("Límite de 1 tarjeta alcanzado.")

    st.divider()
    st.subheader("📥 Exportar Árbol")

    def generar_png_arbol():
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(-0.5, 6)
        ax.axis('off')
        datos = st.session_state['arbol_tarjetas']
        
        for seccion, conf in CONFIG.items():
            items = datos.get(seccion, [])
            if not items: continue
            n = len(items)
            espaciado = 10 / (n + 1)
            for i, item in enumerate(items):
                x = (i + 1) * espaciado
                y = conf["y"]
                texto = item["texto"] if isinstance(item, dict) else item
                rect = plt.Rectangle((x-0.8, y-0.3), 1.6, 0.6, facecolor=conf["color"], edgecolor='gray', lw=1, alpha=0.8)
                ax.add_patch(rect)
                txt_ajustado = "\n".join(textwrap.wrap(texto, width=15))
                ax.text(x, y, txt_ajustado, ha='center', va='center', fontsize=9, fontweight='bold', color='black')
                if i == 0:
                    ax.text(0.1, y, seccion.upper(), fontsize=7, color='gray', va='center', fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button(
        label="🖼️ Descargar como Imagen (PNG)",
        data=generar_png_arbol(),
        file_name="arbol_problemas.png",
        mime="image/png",
        use_container_width=True
    )

# --- FUNCIONES DE RENDERIZADO EN PANTALLA ---
def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:12px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:8px; min-height:70px; box-shadow: 2px 2px 5px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center;">
               {texto}</div>"""

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'].get(nombre, [])
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            if st.button("🗑️ Borrar", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                st.rerun()
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
            if not padres:
                st.caption(f"Cree un {nombre_padre} para activar esta fila.")
            else:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            hijos_del_padre = [h for h in hijos if h["padre"] == p_txt]
                            for h_idx, h_data in enumerate(hijos_del_padre):
                                st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{h_idx}"):
                                    st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data)
                                    st.rerun()
                        else:
                            st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                            hijos_asociados = [h for h in hijos if h["padre"] == p_txt]
                            if st.button("🗑️ Borrar Principal", key=f"del_p_{seccion_actual}_{i}"):
                                if hijos_asociados:
                                    st.error("⚠️ Borre primero los elementos indirectos.")
                                else:
                                    st.session_state['arbol_tarjetas'][seccion_actual].pop(i)
                                    st.rerun()

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
render_simple("Problema Superior")
st.markdown("---")
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")
# Llamada actualizada a 'Problema Principal'
render_simple("Problema Principal") 
st.markdown("---")
render_rama("Causas Directas", "Causas Indirectas", inversion=False)
