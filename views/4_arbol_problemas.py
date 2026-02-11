import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- MIGRACIÓN Y SEGURIDAD ---
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])

st.title("🌳 4. Árbol de Problemas (Conexiones Reforzadas)")

# 1. Configuración
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple", "y": 5},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos", "y": 4},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple", "y": 3},
    "Problema Principal": {"color": "#FFB3BA", "limite": 1, "tipo": "simple", "y": 2},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple", "y": 1},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas", "y": 0}
}

# --- SIDEBAR (Gestión de Fichas) ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("1. Sección:", list(CONFIG.keys()))
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("2. Descripción:")
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'].get(CONFIG[tipo_sel]["padre"], [])
            if opciones_p: padre_asociado = st.selectbox(f"Vincular a:", opciones_p)
        if st.form_submit_button("Generar") and texto_input:
            st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado} if CONFIG[tipo_sel]["tipo"] == "hijo" else texto_input)
            st.rerun()

# --- FUNCIONES DE DISEÑO (NUEVAS FLECHAS LARGAS) ---

def card_html(texto, color):
    # Reducimos el margen vertical para facilitar la conexión
    return f"""<div style="background-color:{color}; padding:10px; border-radius:8px; 
               border-left:6px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin: 0; min-height:60px; box-shadow: 2px 2px 4px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center; font-size:13px;">
               {texto}</div>"""

def arrow_html(direccion="arriba"):
    # Conector vertical largo con punta de flecha
    color = "#888"
    if direccion == "arriba":
        return f"""
        <div style="display: flex; flex-direction: column; align-items: center; margin: -10px 0 -10px 0;">
            <div style="font-size: 10px; color: {color}; margin-bottom: -4px;">▲</div>
            <div style="width: 2px; height: 50px; background-color: {color};"></div>
        </div>
        """
    else:
        return f"""
        <div style="display: flex; flex-direction: column; align-items: center; margin: -10px 0 -10px 0;">
            <div style="width: 2px; height: 50px; background-color: {color};"></div>
            <div style="font-size: 10px; color: {color}; margin-top: -4px;">▼</div>
        </div>
        """

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:15px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'].get(nombre, [])
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            if nombre != "Problema Principal" and st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []; st.rerun()
        else: st.caption("Vacío")

def render_rama_conectada(nombre_directo, nombre_indirecto, efectos=False):
    directos = st.session_state['arbol_tarjetas'].get(nombre_directo, [])
    indirectos = st.session_state['arbol_tarjetas'].get(nombre_indirecto, [])

    col_l, col_c = st.columns([1, 4])
    with col_l:
        # Etiquetas alineadas a las cajas
        st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:20px;'>{nombre_indirecto.upper() if efectos else nombre_directo.upper()}</div>", unsafe_allow_html=True)
        st.markdown("<br>"*4, unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right;'>{nombre_directo.upper() if efectos else nombre_indirecto.upper()}</div>", unsafe_allow_html=True)

    with col_c:
        if not directos:
            st.caption(f"Cree un {nombre_directo} primero.")
            return
        
        cols = st.columns(len(directos))
        for i, p_txt in enumerate(directos):
            with cols[i]:
                hijos = [h for h in indirectos if h["padre"] == p_txt]
                if efectos: # EFECTOS (Hijos ARRIBA -> Flecha ↑ -> Padre ABAJO)
                    for h_idx, h_data in enumerate(hijos):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_indirecto]["color"]), unsafe_allow_html=True)
                        if st.button("ｘ", key=f"del_h_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_indirecto].remove(h_data); st.rerun()
                    
                    if hijos: st.markdown(arrow_html("arriba"), unsafe_allow_html=True)
                    
                    st.markdown(card_html(p_txt, CONFIG[nombre_directo]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️ Borrar", key=f"del_p_{i}"):
                        if hijos: st.error("Borre indirectos primero")
                        else: st.session_state['arbol_tarjetas'][nombre_directo].pop(i); st.rerun()
                
                else: # CAUSAS (Padre ARRIBA -> Flecha ↓ -> Hijos ABAJO)
                    st.markdown(card_html(p_txt, CONFIG[nombre_directo]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️ Borrar", key=f"del_p_c_{i}"):
                        if hijos: st.error("Borre indirectos primero")
                        else: st.session_state['arbol_tarjetas'][nombre_directo].pop(i); st.rerun()

                    if hijos: st.markdown(arrow_html("abajo"), unsafe_allow_html=True)

                    for h_idx, h_data in enumerate(hijos):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_indirecto]["color"]), unsafe_allow_html=True)
                        if st.button("ｘ", key=f"del_h_c_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_indirecto].remove(h_data); st.rerun()

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
render_simple("Problema Superior")
# Conector largo hacia efectos
st.markdown(arrow_html("arriba"), unsafe_allow_html=True)

render_rama_conectada("Efectos Directos", "Efectos Indirectos", efectos=True)

# Conector de color hacia el Problema Principal
st.markdown("""<div style="display: flex; justify-content: center; margin: -10px 0;"><div style="width: 2px; height: 50px; background-color: #e57373;"></div></div>""", unsafe_allow_html=True)

render_simple("Problema Principal")

# Conector largo hacia causas
st.markdown(arrow_html("abajo"), unsafe_allow_html=True)

render_rama_conectada("Causas Directas", "Causas Indirectas", efectos=False)
