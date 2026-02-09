import streamlit as st

st.title("🌳 4. Árbol de Problemas (Jerárquico)")

# Configuración Maestra
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple"},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos"},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple"},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple"},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple"},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas"}
}

# --- SIDEBAR: GENERADOR CON ASOCIACIÓN ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    with st.form("crear_tarjeta", clear_on_submit=True):
        tipo_sel = st.selectbox("Sección:", list(CONFIG.keys()))
        texto_input = st.text_area("Descripción de la idea:")
        
        # Lógica de asociación para hijos
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_padre = st.session_state['arbol_tarjetas'][CONFIG[tipo_sel]["padre"]]
            if opciones_padre:
                padre_asociado = st.selectbox(f"Vincular a {CONFIG[tipo_sel]['padre']}:", opciones_padre)
            else:
                st.warning(f"⚠️ Primero cree un '{CONFIG[tipo_sel]['padre']}' para poder asociar este elemento.")

        if st.form_submit_button("Generar Tarjeta") and texto_input:
            # Validar límite (1 para Problema Superior/Central)
            if len(st.session_state['arbol_tarjetas'][tipo_sel]) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo":
                    if padre_asociado:
                        st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                        st.rerun()
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                    st.rerun()
            else:
                st.error("Esta sección solo permite una tarjeta principal.")

# --- RENDERIZADO CON ETIQUETAS LATERALES ---

def card_style(texto, color):
    return f"""<div style="background-color:{color}; padding:15px; border-radius:10px; 
               border-left:10px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:10px; min-height:90px; box-shadow: 2px 2px 5px #ddd;">{texto}</div>"""

def render_seccion_simple(nombre):
    col_etiqueta, col_cards = st.columns([1, 4]) # Etiquetas al lado
    with col_etiqueta:
        st.markdown(f"<br><h5 style='color:#444;'>{nombre}</h5>", unsafe_allow_html=True)
    with col_cards:
        items = st.session_state['arbol_tarjetas'][nombre]
        if not items: st.caption("Vacío")
        else:
            cols = st.columns(3)
            for i, texto in enumerate(items):
                with cols[i % 3]:
                    st.markdown(card_style(texto, CONFIG[nombre]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{nombre}_{i}"):
                        st.session_state['arbol_tarjetas'][nombre].pop(i)
                        st.rerun()

def render_seccion_hija(nombre_hijo, nombre_padre):
    col_etiqueta, col_cards = st.columns([1, 4]) # Etiquetas al lado
    with col_etiqueta:
        st.markdown(f"<br><h5 style='color:#444;'>{nombre_hijo}</h5>", unsafe_allow_html=True)
    with col_content := col_cards:
        padres = st.session_state['arbol_tarjetas'][nombre_padre]
        hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
        
        for p_idx, p_texto in enumerate(padres):
            st.markdown(f"**Vínculo con:** *{p_texto}*")
            items_vivos = [h for h in hijos if h["padre"] == p_texto]
            if items_vivos:
                sub_cols = st.columns(3)
                for h_idx, h_data in enumerate(items_vivos):
                    with sub_cols[h_idx % 3]:
                        st.markdown(card_style(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_h_{nombre_hijo}_{p_idx}_{h_idx}"):
                            # Borrar del estado global buscando el elemento exacto
                            st.session_state['arbol_tarjetas'][nombre_hijo] = [x for x in hijos if x != h_data]
                            st.rerun()
            else:
                st.caption("Sin elementos asociados aún.")
            st.divider()

# --- DIBUJO DEL ÁRBOL JERÁRQUICO ---
st.divider()
render_seccion_simple("Problema Superior")
st.markdown("---")
render_seccion_hija("Efectos Indirectos", "Efectos Directos")
render_seccion_simple("Efectos Directos")
st.markdown("---")
st.error("📍 ÁREA DEL PROBLEMA CENTRAL")
render_seccion_simple("Problema Central")
st.markdown("---")
render_seccion_simple("Causas Directas")
render_seccion_hija("Causas Indirectas", "Causas Directas")
