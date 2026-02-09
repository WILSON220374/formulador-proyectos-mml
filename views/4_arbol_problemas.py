import streamlit as st

st.title("🌳 4. Árbol de Problemas (Jerarquía de Ramas)")

# Configuración Maestra: Colores y Relaciones
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple"},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos"},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple"},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple"},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple"},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas"}
}

# --- SIDEBAR: GENERADOR DE TARJETAS (FLUJO CORREGIDO) ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    # 1. Selección de Sección (Define la lógica del formulario)
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        # 2. Asociación (Se pregunta ANTES de generar según requerimiento)
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            nombre_padre = CONFIG[tipo_sel]["padre"]
            opciones_padre = st.session_state['arbol_tarjetas'][nombre_padre]
            
            if opciones_padre:
                padre_asociado = st.selectbox(f"2. Vincular a {nombre_padre}:", opciones_padre)
            else:
                st.warning(f"⚠️ Primero cree un '{nombre_padre}'.")
        
        # 3. Contenido
        texto_input = st.text_area("3. Descripción de la idea:")
        
        if st.form_submit_button("Generar Ficha"):
            if not texto_input:
                st.error("Escriba un texto para la ficha.")
            elif len(st.session_state['arbol_tarjetas'][tipo_sel]) >= CONFIG[tipo_sel]["limite"]:
                st.error("Sección limitada a 1 tarjeta.")
            elif CONFIG[tipo_sel]["tipo"] == "hijo" and not padre_asociado:
                st.error("Debe seleccionar un elemento superior para asociar.")
            else:
                if CONFIG[tipo_sel]["tipo"] == "hijo":
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()

# --- FUNCIONES DE RENDERIZADO VISUAL ---

def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:12px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:8px; min-height:70px; box-shadow: 2px 2px 5px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center;">
               {texto}</div>"""

def render_simple(nombre):
    col_label, col_content = st.columns([1, 4])
    with col_label:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_content:
        items = st.session_state['arbol_tarjetas'][nombre]
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                st.rerun()
        else:
            st.caption("Sección vacía")

def render_ramas(nombre_padre, nombre_hijo, inversion=False):
    """Separa etiquetas pero mantiene alineación de columnas"""
    # Etiquetas separadas a la izquierda
    col_label, col_content = st.columns([1, 4])
    
    with col_label:
        # Se muestran ambos nombres pero con espacio para identificar niveles
        if inversion: # Efectos
            st.markdown(f"<div style='color:#666; text-align:right; margin-bottom:100px;'>{nombre_hijo.upper()}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right;'>{nombre_padre.upper()}</div>", unsafe_allow_html=True)
        else: # Causas
            st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-bottom:60px;'>{nombre_padre.upper()}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#666; text-align:right;'>{nombre_hijo.upper()}</div>", unsafe_allow_html=True)
            
    with col_content:
        padres = st.session_state['arbol_tarjetas'][nombre_padre]
        hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
        
        if not padres:
            st.caption(f"Cree un {nombre_padre} para activar esta rama.")
            return

        # Una columna por cada padre para alineación vertical
        cols = st.columns(len(padres))
        for i, p_texto in enumerate(padres):
            with cols[i]:
                hijos_del_padre = [h for h in hijos if h["padre"] == p_texto]
                
                if inversion: # EFECTOS: Indirectos (arriba) -> Directos (abajo)
                    for h_idx, h_data in enumerate(hijos_del_padre):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"h_{nombre_hijo}_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data)
                            st.rerun()
                    st.markdown(card_html(p_texto, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                
                else: # CAUSAS: Directas (arriba) -> Indirectas (abajo)
                    st.markdown(card_html(p_texto, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                    for h_idx, h_data in enumerate(hijos_del_padre):
                        st.caption(f"↳ {nombre_hijo}")
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"h_{nombre_hijo}_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data)
                            st.rerun()

                if st.button("🗑️ Borrar Principal", key=f"p_{nombre_padre}_{i}"):
                    st.session_state['arbol_tarjetas'][nombre_hijo] = [h for h in hijos if h["padre"] != p_texto]
                    st.session_state['arbol_tarjetas'][nombre_padre].pop(i)
                    st.rerun()

# --- DIBUJO DEL ÁRBOL ---
st.divider()

# 1. Problema Superior
render_simple("Problema Superior")
st.markdown("---")

# 2. Rama de Efectos (Indirectos encima de Directos)
render_ramas("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")

# 3. Problema Central
st.error("📍 ÁREA DEL PROBLEMA CENTRAL")
render_simple("Problema Central")
st.markdown("---")

# 4. Rama de Causas (Directas encima de Indirectas)
render_ramas("Causas Directas", "Causas Indirectas", inversion=False)

st.divider()
if st.button("Limpiar Árbol Completo", type="primary"):
    for k in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas'][k] = []
    st.rerun()
