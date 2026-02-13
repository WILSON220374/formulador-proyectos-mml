iimport streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- BLINDAJE EXTRA CONTRA ATTRIBUTERROR ---
# Si la sesión inicializó esto como lista [], lo reparamos a diccionario {}
if not isinstance(st.session_state.get('arbol_tarjetas'), dict):
    st.session_state['arbol_tarjetas'] = {
        "Efectos Indirectos": [], "Efectos Directos": [], 
        "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []
    }

# --- ENCABEZADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🌳 4. Árbol de Problemas")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# Configuración de colores y posiciones
CONFIG = {
    "Efectos Indirectos": {"color": "#B3D9FF", "tipo": "hijo", "padre": "Efectos Directos", "y": 9.5},
    "Efectos Directos": {"color": "#80BFFF", "tipo": "simple", "y": 6.0},
    "Problema Principal": {"color": "#FFB3BA", "tipo": "simple", "y": 3.0},
    "Causas Directas": {"color": "#FFFFBA", "tipo": "simple", "y": 0.0},
    "Causas Indirectas": {"color": "#FFDFBA", "tipo": "hijo", "padre": "Causas Directas", "y": -3.5}
}

# --- SIDEBAR: GESTIÓN DE FICHAS ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha_nube", clear_on_submit=True):
        texto_input = st.text_area("Descripción (Máx 180 caracteres):", max_chars=180)
        padre_asociado = None
        
        # El .get() ahora funcionará porque aseguramos que sea un diccionario arriba
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'].get(CONFIG[tipo_sel]["padre"], [])
            if opciones_p: padre_asociado = st.selectbox(f"Vincular a:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if padre_asociado:
                st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
            else:
                st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
            guardar_datos_nube()
            st.rerun()

    st.divider()
    
    # Función para generar el PNG
    def generar_png():
        fig, ax = plt.subplots(figsize=(22, 22)) 
        ax.set_xlim(0, 10); ax.set_ylim(-8, 12); ax.axis('off')
        ax.text(5, 11, "ÁRBOL DE PROBLEMAS", fontsize=32, fontweight='bold', ha='center', color='#1E3A8A')
        
        datos = st.session_state['arbol_tarjetas']
        
        def dibujar_caja(x, y, texto, color):
            lineas = textwrap.wrap(texto, width=18)
            txt_ajustado = "\n".join(lineas[:10]) 
            n_lineas = len(lineas[:10])
            rect_h = max(1.0, 0.4 + (n_lineas * 0.25))
            rect_w = 1.8 
            f_size = 9 if n_lineas <= 5 else 7.5
            rect = plt.Rectangle((x - rect_w/2, y - rect_h/2), rect_w, rect_h, facecolor=color, edgecolor='#333', lw=1.5, zorder=3)
            ax.add_patch(rect)
            ax.text(x, y, txt_ajustado, ha='center', va='center', fontsize=f_size, fontweight='bold', zorder=4)

        if datos.get("Problema Principal"):
            dibujar_caja(5, CONFIG["Problema Principal"]["y"], datos["Problema Principal"][0], CONFIG["Problema Principal"]["color"])

        for principal in ["Efectos Directos", "Causas Directas"]:
            items = datos.get(principal, [])
            if items:
                espacio = 10 / (len(items) + 1)
                for i, p_txt in enumerate(items):
                    x_p = (i + 1) * espacio
                    y_p = CONFIG[principal]["y"]
                    dibujar_caja(x_p, y_p, p_txt, CONFIG[principal]["color"])
                    
                    sec_hija = "Efectos Indirectos" if principal == "Efectos Directos" else "Causas Indirectas"
                    hijos = [h for h in datos.get(sec_hija, []) if isinstance(h, dict) and h.get("padre") == p_txt]
                    for j, h_data in enumerate(hijos):
                        h_y = y_p + ((1 if principal == "Efectos Directos" else -1) * (j + 1) * 2.8) 
                        dibujar_caja(x_p, h_y, h_data["texto"], CONFIG[sec_hija]["color"])

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol PNG", data=generar_png(), file_name="arbol_problemas.png", mime="image/png", use_container_width=True)

# --- VISUALIZACIÓN EN PANTALLA ---
def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:15px; border-radius:10px; color:#31333F; font-weight:500; margin-bottom:8px; min-height:150px; display: flex; align-items: center; justify-content: center; text-align: center;">{texto}</div>"""

def render_rama(nombre_padre, nombre_hijo, inversion=False):
    datos = st.session_state['arbol_tarjetas']
    padres = datos.get(nombre_padre, [])
    hijos = datos.get(nombre_hijo, [])
    
    # Lógica de renderizado simplificada para evitar errores
    st.markdown(f"### {nombre_padre} y {nombre_hijo}")
    if padres:
        cols = st.columns(len(padres))
        for i, p_txt in enumerate(padres):
            with cols[i]:
                st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                if st.button("🗑️ Padre", key=f"del_p_{nombre_padre}_{i}"):
                    st.session_state['arbol_tarjetas'][nombre_padre].pop(i)
                    guardar_datos_nube(); st.rerun()
                
                # Mostrar hijos vinculados
                h_vinculados = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_txt]
                for idx, h_data in enumerate(h_vinculados):
                    st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️ Hijo", key=f"del_h_{nombre_hijo}_{i}_{idx}"):
                        st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data)
                        guardar_datos_nube(); st.rerun()

st.divider()
render_rama("Efectos Directos", "Efectos Indirectos", inversion=True)
st.divider()
# Render Problema Principal
items_p = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
if items_p:
    st.markdown(card_html(items_p[0], CONFIG["Problema Principal"]["color"]), unsafe_allow_html=True)
    if st.button("🗑️ Borrar Problema Central"):
        st.session_state['arbol_tarjetas']["Problema Principal"] = []
        guardar_datos_nube(); st.rerun()
st.divider()
render_rama("Causas Directas", "Causas Indirectas")
