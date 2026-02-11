import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- MIGRACIÓN DE DATOS (SEGURIDAD) ---
if 'arbol_tarjetas' in st.session_state:
    if 'Problema Principal' not in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas']['Problema Principal'] = st.session_state['arbol_tarjetas'].pop('Problema Central', [])

st.title("🌳 4. Árbol de Problemas (Conectado)")

# 1. Configuración
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple", "y": 5},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos", "y": 4},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple", "y": 3},
    "Problema Principal": {"color": "#FFB3BA", "limite": 1, "tipo": "simple", "y": 2},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple", "y": 1},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas", "y": 0}
}

# --- SIDEBAR: GESTIÓN (Sin cambios en la lógica original) ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("2. Descripción de la idea:")
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'].get(CONFIG[tipo_sel]["padre"], [])
            if opciones_p: padre_asociado = st.selectbox(f"3. Vincular a {CONFIG[tipo_sel]['padre']}:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if len(st.session_state['arbol_tarjetas'].get(tipo_sel, [])) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo" and padre_asociado:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else: st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()
    # (Función de exportación PNG se mantiene igual)

# --- FUNCIONES DE RENDERIZADO MEJORADAS ---

def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:10px; border-radius:8px; 
               border-left:6px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin: 5px 0; min-height:60px; box-shadow: 2px 2px 4px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center; font-size:14px;">
               {texto}</div>"""

def arrow_html(direccion="abajo"):
    # Flecha visual sutil para conectar cajas
    simbolo = "↓" if direccion == "abajo" else "↑"
    return f"""<div style="text-align:center; color:#888; font-size:20px; margin:-10px 0; font-weight:bold;">{simbolo}</div>"""

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

def render_rama_conectada(nombre_padre, nombre_hijo, inversion=False):
    """Muestra padres e hijos en la misma columna con una flecha entre ellos."""
    padres = st.session_state['arbol_tarjetas'].get(nombre_padre, [])
    hijos = st.session_state['arbol_tarjetas'].get(nombre_hijo, [])

    col_l, col_c = st.columns([1, 4])
    with col_l:
        # Etiquetas laterales alineadas
        st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:20px;'>{nombre_hijo.upper() if inversion else nombre_padre.upper()}</div>", unsafe_allow_html=True)
        st.markdown("<br>"*2, unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right;'>{nombre_padre.upper() if inversion else nombre_hijo.upper()}</div>", unsafe_allow_html=True)

    with col_c:
        if not padres:
            st.caption(f"Debe crear un {nombre_padre} primero.")
            return
        
        cols = st.columns(len(padres))
        for i, p_txt in enumerate(padres):
            with cols[i]:
                hijos_del_padre = [h for h in hijos if h["padre"] == p_txt]
                
                if inversion: # EFECTOS: Indirectos (hijos) arriba, Directos (padre) abajo
                    for h_idx, h_data in enumerate(hijos_del_padre):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_h_{nombre_hijo}_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data); st.rerun()
                    
                    if hijos_del_padre: st.markdown(arrow_html("arriba"), unsafe_allow_html=True)
                    
                    st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️ Borrar Principal", key=f"del_p_{nombre_padre}_{i}"):
                        if hijos_del_padre: st.error("Borre indirectos primero")
                        else: st.session_state['arbol_tarjetas'][nombre_padre].pop(i); st.rerun()
                
                else: # CAUSAS: Directos arriba, Indirectos abajo
                    st.markdown(card_html(p_txt, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️ Borrar Principal", key=f"del_p_c_{nombre_padre}_{i}"):
                        if hijos_del_padre: st.error("Borre indirectos primero")
                        else: st.session_state['arbol_tarjetas'][nombre_padre].pop(i); st.rerun()

                    if hijos_del_padre: st.markdown(arrow_html("abajo"), unsafe_allow_html=True)

                    for h_idx, h_data in enumerate(hijos_del_padre):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_h_c_{nombre_hijo}_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data); st.rerun()

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
render_simple("Problema Superior")
st.markdown("---")
# Rama de Efectos (Conectados)
render_rama_conectada("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")
# Problema Principal
render_simple("Problema Principal")
st.markdown("---")
# Rama de Causas (Conectados)
render_rama_conectada("Causas Directas", "Causas Indirectas", inversion=False)
