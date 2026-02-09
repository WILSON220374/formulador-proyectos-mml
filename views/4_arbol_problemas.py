import streamlit as st

st.title("🌳 4. Árbol de Problemas (Vista de Ramas)")

# Configuración Maestra: Colores y Relaciones
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple"},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos"},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple"},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple"},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple"},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas"}
}

# --- SIDEBAR: GENERADOR DE TARJETAS (ASOCIACIÓN PREVIA) ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    # 1. Selección de Sección primero para activar lógica
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("2. Descripción de la idea:")
        
        # Lógica de asociación: Se hace ANTES de generar
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            nombre_padre = CONFIG[tipo_sel]["padre"]
            opciones_padre = st.session_state['arbol_tarjetas'][nombre_padre]
            
            if opciones_padre:
                padre_asociado = st.selectbox(f"3. Vincular a {nombre_padre}:", opciones_padre)
            else:
                st.warning(f"⚠️ No hay '{nombre_padre}' creados. Cree uno primero.")
        
        if st.form_submit_button("Generar Ficha"):
            if not texto_input:
                st.error("Por favor escriba un texto.")
            elif len(st.session_state['arbol_tarjetas'][tipo_sel]) >= CONFIG[tipo_sel]["limite"]:
                st.error("Límite de 1 tarjeta alcanzado para esta sección.")
            elif CONFIG[tipo_sel]["tipo"] == "hijo" and not padre_asociado:
                st.error("Debe seleccionar un elemento superior para asociar.")
            else:
                # Guardar según tipo
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

def render_fila_simple(nombre):
    """Para Problema Superior y Central (Etiqueta al lado)"""
    col_label, col_content = st.columns([1, 4])
    with col_label:
        st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_content:
        items = st.session_state['arbol_tarjetas'][nombre]
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                st.rerun()
        else:
            st.caption("Sección vacía")

def render_jerarquia_completa(nombre_padre, nombre_hijo, inversion_visual=False):
    """Renderiza padres e hijos alineados verticalmente"""
    col_label, col_content = st.columns([1, 4])
    with col_label:
        st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{nombre_padre.upper()} y {nombre_hijo.upper()}</div>", unsafe_allow_html=True)
    
    with col_content:
        padres = st.session_state['arbol_tarjetas'][nombre_padre]
        hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
        
        if not padres:
            st.caption(f"Cree un {nombre_padre} para ver la estructura.")
            return

        # Creamos una columna física para cada padre
        cols = st.columns(max(len(padres), 1))
        
        for i, p_texto in enumerate(padres):
            with cols[i]:
                # Si son Efectos, el orden es: Hijo (arriba) -> Padre (abajo)
                # Si son Causas, el orden es: Padre (arriba) -> Hijo (abajo)
                
                if inversion_visual: # Caso Efectos
                    # Dibujar hijos primero
                    hijos_del_padre = [h for h in hijos if h["padre"] == p_texto]
                    for h_idx, h_data in enumerate(hijos_del_padre):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_h_{nombre_hijo}_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data)
                            st.rerun()
                    # Dibujar padre después
                    st.markdown(card_html(p_texto, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                
                else: # Caso Causas (Padre arriba, hijo abajo)
                    st.markdown(card_html(p_texto, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                    # Dibujar hijos debajo
                    hijos_del_padre = [h for h in hijos if h["padre"] == p_texto]
                    for h_idx, h_data in enumerate(hijos_del_padre):
                        st.caption(f"↳ {nombre_hijo}")
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_h_{nombre_hijo}_{i}_{h_idx}"):
                            st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data)
                            st.rerun()
                
                if st.button("🗑️ Borrar Principal", key=f"del_p_{nombre_padre}_{i}"):
                    # Limpiar también hijos huérfanos
                    st.session_state['arbol_tarjetas'][nombre_hijo] = [h for h in hijos if h["padre"] != p_texto]
                    st.session_state['arbol_tarjetas'][nombre_padre].pop(i)
                    st.rerun()

# --- CONSTRUCCIÓN VISUAL DEL ÁRBOL ---
st.divider()

# 1. Problema Superior
render_fila_simple("Problema Superior")
st.markdown("---")

# 2. Efectos (Directos e Indirectos alineados verticalmente)
# Para efectos, los indirectos suelen graficarse por ENCIMA de los directos
render_jerarquia_completa("Efectos Directos", "Efectos Indirectos", inversion_visual=True)
st.markdown("---")

# 3. Problema Central
st.error("🚨 ÁREA DEL PROBLEMA CENTRAL")
render_fila_simple("Problema Central")
st.markdown("---")

# 4. Causas (Directas e Indirectas alineadas verticalmente)
# Las causas indirectas aparecen DEBAJO de las directas asociadas
render_jerarquia_completa("Causas Directas", "Causas Indirectas", inversion_visual=False)

st.divider()
if st.button("Limpiar Árbol Completo", type="primary"):
    for k in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas'][k] = []
    st.rerun()
