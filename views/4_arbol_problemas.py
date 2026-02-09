import streamlit as st

st.title("🌳 4. Árbol de Problemas (Vista Jerárquica)")

# Configuración Maestra
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple"},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos"},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple"},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple"},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple"},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas"}
}

# --- SIDEBAR: CREADOR DE POST-ITS ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    with st.form("crear", clear_on_submit=True):
        tipo_sel = st.selectbox("Sección:", list(CONFIG.keys()))
        texto = st.text_area("Descripción:")
        
        padre_sel = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones = st.session_state['arbol_tarjetas'][CONFIG[tipo_sel]["padre"]]
            if opciones:
                padre_sel = st.selectbox(f"Asociar a {CONFIG[tipo_sel]['padre']}:", opciones)
            else:
                st.warning(f"⚠️ Cree primero un {CONFIG[tipo_sel]['padre']}")

        if st.form_submit_button("Generar") and texto:
            if len(st.session_state['arbol_tarjetas'][tipo_sel]) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo" and padre_sel:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto, "padre": padre_sel})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto)
                st.rerun()
            else:
                st.error("Límite de 1 tarjeta alcanzado.")

# --- FUNCIONES DE DISEÑO ---

def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:15px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:10px; min-height:80px; box-shadow: 2px 2px 5px #eee;">{texto}</div>"""

def render_lateral(nombre, es_hijo=False):
    col_label, col_content = st.columns([1, 4]) # Etiquetas a la IZQUIERDA
    with col_label:
        st.markdown(f"<p style='color:#666; font-weight:bold; margin-top:20px;'>{nombre.upper()}</p>", unsafe_allow_html=True)
    
    with col_content:
        if not es_hijo:
            items = st.session_state['arbol_tarjetas'][nombre]
            cols = st.columns(3)
            for i, val in enumerate(items):
                with cols[i % 3]:
                    st.markdown(card_html(val, CONFIG[nombre]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️", key=f"d_{nombre}_{i}"):
                        st.session_state['arbol_tarjetas'][nombre].pop(i)
                        st.rerun()
        else:
            # Lógica jerárquica: Agrupar hijos bajo su padre
            nombre_padre = CONFIG[nombre]["padre"]
            padres = st.session_state['arbol_tarjetas'][nombre_padre]
            hijos = st.session_state['arbol_tarjetas'][nombre]
            
            for p in padres:
                hijos_de_este_padre = [h for h in hijos if h["padre"] == p]
                if hijos_de_este_padre:
                    st.caption(f"Derivados de: {p}")
                    c_hijos = st.columns(3)
                    for idx, h in enumerate(hijos_de_este_padre):
                        with c_hijos[idx % 3]:
                            st.markdown(card_html(h["texto"], CONFIG[nombre]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"dh_{nombre}_{idx}_{p}"):
                                st.session_state['arbol_tarjetas'][nombre] = [x for x in hijos if x != h]
                                st.rerun()
            st.divider()

# --- ESTRUCTURA VISUAL DEL ÁRBOL ---
st.divider()
render_lateral("Problema Superior")
st.markdown("---")
render_lateral("Efectos Indirectos", es_hijo=True)
render_lateral("Efectos Directos")
st.markdown("---")
st.error("📍 PROBLEMA CENTRAL (Único)")
render_lateral("Problema Central")
st.markdown("---")
render_lateral("Causas Directas")
render_lateral("Causas Indirectas", es_hijo=True)
