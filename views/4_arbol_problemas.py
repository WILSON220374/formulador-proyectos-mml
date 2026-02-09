import streamlit as st

st.title("🌳 4. Árbol de Problemas (Jerárquico)")

# Configuración de Colores y Límites
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple"},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos"},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple"},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple"},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple"},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas"}
}

# --- SIDEBAR: GENERADOR DINÁMICO ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    with st.form("crear_tarjeta", clear_on_submit=True):
        tipo_sel = st.selectbox("Sección:", list(CONFIG.keys()))
        texto_input = st.text_area("Descripción:")
        
        # Lógica para preguntar por el padre si es indirecto
        padre_sel = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            padres_disponibles = st.session_state['arbol_tarjetas'][CONFIG[tipo_sel]["padre"]]
            if padres_disponibles:
                padre_sel = st.selectbox(f"Asociar a {CONFIG[tipo_sel]['padre']}:", padres_disponibles)
            else:
                st.warning(f"Primero cree un(a) {CONFIG[tipo_sel]['padre']}.")

        if st.form_submit_button("Generar") and texto_input:
            if len(st.session_state['arbol_tarjetas'][tipo_sel]) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo":
                    if padre_sel:
                        st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_sel})
                        st.rerun()
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                    st.rerun()
            else:
                st.error("Límite alcanzado para esta sección (1).")

# --- FUNCIONES DE RENDERIZADO ---

def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:12px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:8px; min-height:80px; box-shadow: 2px 2px 5px #eee;">{texto}</div>"""

def mostrar_seccion_simple(nombre):
    col_label, col_content = st.columns([1, 4])
    with col_label:
        st.markdown(f"<br><b style='color:#555;'>{nombre.upper()}</b>", unsafe_allow_html=True)
    with col_content:
        items = st.session_state['arbol_tarjetas'][nombre]
        cols = st.columns(3)
        for i, texto in enumerate(items):
            with cols[i % 3]:
                st.markdown(card_html(texto, CONFIG[nombre]["color"]), unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{nombre}_{i}"):
                    st.session_state['arbol_tarjetas'][nombre].pop(i)
                    st.rerun()

def mostrar_seccion_hija(nombre_hijo, nombre_padre):
    col_label, col_content = st.columns([1, 4])
    with col_label:
        st.markdown(f"<br><b style='color:#555;'>{nombre_hijo.upper()}</b>", unsafe_allow_html=True)
    with col_content:
        padres = st.session_state['arbol_tarjetas'][nombre_padre]
        hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
        
        for p_idx, p_texto in enumerate(padres):
            st.caption(f"Vinculados a: {p_texto}")
            items_vivos = [h for h in hijos if h["padre"] == p_texto]
            if items_vivos:
                sub_cols = st.columns(3)
                for h_idx, h_data in enumerate(items_vivos):
                    with sub_cols[h_idx % 3]:
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_{nombre_hijo}_{p_idx}_{h_idx}"):
                            # Buscar el índice real en la lista completa para borrar
                            real_idx = next(i for i, v in enumerate(hijos) if v == h_data)
                            st.session_state['arbol_tarjetas'][nombre_hijo].pop(real_idx)
                            st.rerun()
            else:
                st.caption("No hay tarjetas asociadas.")
            st.divider()

# --- DIBUJO DEL ÁRBOL ---
st.divider()
mostrar_seccion_simple("Problema Superior")
st.markdown("---")
mostrar_seccion_hija("Efectos Indirectos", "Efectos Directos")
mostrar_seccion_simple("Efectos Directos")
st.markdown("---")
st.error("📍 PROBLEMA CENTRAL (Único)")
mostrar_seccion_simple("Problema Central")
st.markdown("---")
mostrar_seccion_simple("Causas Directas")
mostrar_seccion_hija("Causas Indirectas", "Causas Directas")
