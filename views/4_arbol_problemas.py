import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- SINCRONIZACIÓN Y MIGRACIÓN ---
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        # Migramos los datos de 'Central' a 'Principal' para no perder información
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])

st.title("🌳 4. Árbol de Problemas (Vista Jerárquica)")

# 1. Configuración Maestra
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple", "y": 5},
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
                st.rerun()

    st.divider()
    st.subheader("📥 Exportar Árbol")

    # FUNCIÓN CON AJUSTE AUTOMÁTICO DE ESPACIADO
    def generar_png_arbol():
        # Aumentamos el tamaño y la escala vertical para evitar solapamientos
        fig, ax = plt.subplots(figsize=(16, 14)) 
        ax.set_xlim(0, 10)
        ax.set_ylim(-1, 9) # Más espacio vertical
        ax.axis('off')
        datos = st.session_state['arbol_tarjetas']
        
        for seccion, conf in CONFIG.items():
            items = datos.get(seccion, [])
            if not items: continue
            
            n = len(items)
            # Cálculo de ancho dinámico para dejar un hueco entre cajas
            ancho_max_fila = 8.5 / n
            ancho_caja = min(2.2, ancho_max_fila - 0.3)
            espaciado = 10 / (n + 1)
            
            # Multiplicamos Y por 1.5 para separar las filas físicamente
            y_base = conf["y"] * 1.5 
            
            for i, item in enumerate(items):
                x = (i + 1) * espaciado
                texto = item["texto"] if isinstance(item, dict) else item
                
                # Envoltura de texto más estrecha para que las cajas no sean tan anchas
                txt_ajustado = "\n".join(textwrap.wrap(texto, width=22))
                num_lineas = txt_ajustado.count('\n') + 1
                alto_caja = max(0.6, num_lineas * 0.18)
                
                # Dibujo de la caja
                rect = plt.Rectangle((x-(ancho_caja/2), y_base-(alto_caja/2)), 
                                     ancho_caja, alto_caja, 
                                     facecolor=conf["color"], edgecolor='#333333', lw=1.2, zorder=2)
                ax.add_patch(rect)
                
                # Texto con tamaño adaptado
                ax.text(x, y_base, txt_ajustado, ha='center', va='center', 
                        fontsize=9, fontweight='bold', color='black', zorder=3)
                
                if i == 0:
                    ax.text(0.1, y_base, seccion.upper(), fontsize=7, color='#777', fontweight='bold', va='center')

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight', pad_inches=0.4)
        plt.close(fig)
        return buf.getvalue()

    st.download_button(label="🖼️ Descargar Árbol (PNG)", data=generar_png_arbol(), file_name="arbol_ajustado.png", mime="image/png", use_container_width=True)

# --- RENDERIZADO EN PANTALLA ---
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
            if nombre != "Problema Principal" and st.button("🗑️ Borrar", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []; st.rerun()
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
                st.caption(f"Debe crear un {nombre_padre} primero.")
            else:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            h_del_p = [h for h in hijos if h["padre"] == p_txt]
                            for h_idx, h_data in enumerate(h_del_p):
                                st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{h_idx}"):
                                    st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data); st.rerun()
                        else:
                            st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️ Borrar", key=f"del_p_{seccion_actual}_{i}"):
                                h_asociados = [h for h in hijos if h["padre"] == p_txt]
                                if h_asociados: st.error("Borre indirectos primero")
                                else: st.session_state['arbol_tarjetas'][seccion_actual].pop(i); st.rerun()

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
render_simple("Problema Superior")
st.markdown("---")
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")
render_simple("Problema Principal") 
st.markdown("---")
render_rama("Causas Directas", "Causas Indirectas", inversion=False)
