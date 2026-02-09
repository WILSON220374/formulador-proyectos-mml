import streamlit as st

st.title("🌳 4. Árbol de Problemas (Vista de Ramas Alineadas)")

# Configuración Maestra: Colores y Relaciones
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple"},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos"},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple"},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple"},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple"},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas"}
}

# --- SIDEBAR: GENERADOR DE TARJETAS ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("2. Descripción de la idea:")
        
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
                if CONFIG[tipo_sel]["tipo"] == "hijo":
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()

# --- FUNCIONES DE RENDERIZADO ---
def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:12px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:8px; min-height:70px; box-shadow: 2px 2px 5px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center;">
               {texto}</div>"""

def render_fila_simple(nombre):
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
    """Renderiza padres e hijos con etiquetas separadas pero alineación vertical de columnas."""
    padres = st.session_state['arbol_tarjetas'][nombre_padre]
    hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
    
    if not padres:
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='text-align:right; color:#999;'>{nombre_padre.upper()}</div>", unsafe_allow_html=True)
        with col_c: st.caption(f"Cree un {nombre_padre} para activar esta rama.")
        return

    # Definir el orden de las etiquetas y el contenido según si es Efecto (invertido) o Causa
    secciones_orden = [nombre_hijo, nombre_padre] if inversion_visual else [nombre_padre, nombre_hijo]

    for seccion_actual in secciones_orden:
        col_label, col_content = st.columns([1, 4])
        with col_label:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{seccion_actual.upper()}</div>", unsafe_allow_html=True)
        
        with col_content:
            # Creamos una columna física por cada padre para mantener la alineación vertical
            cols = st.columns(len(padres))
            for i, p_texto in enumerate(padres):
                with cols[i]:
                    if seccion_actual == nombre_hijo:
                        # Dibujar hijos asociados a este padre
                        hijos_especificos = [h for h in hijos if h["padre"] == p_texto]
                        for h_idx, h_data in enumerate(hijos_especificos):
                            st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_h_{nombre_hijo}_{i}_{h_idx}"):
                                st.session_state['arbol_tarjetas'][nombre_hijo].remove(h_data)
                                st.rerun()
                    else:
                        # Dibujar el padre
                        st.markdown(card_html(p_texto, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️ Borrar Principal", key=f"del_p_{nombre_padre}_{i}"):
                            st.session_state['arbol_tarjetas'][nombre_hijo] = [h for h in hijos if h["padre"] != p_texto]
                            st.session_state['arbol_tarjetas'][nombre_padre].pop(i)
                            st.rerun()

# --- CONSTRUCCIÓN VISUAL DEL ÁRBOL ---
st.divider()

# 1. Problema Superior
render_fila_simple("Problema Superior")
st.markdown("---")

# 2. Rama de Efectos: Indirectos arriba, Directos abajo (Jerarquía MML)
render_jerarquia_completa("Efectos Directos", "Efectos Indirectos", inversion_visual=True)
st.markdown("---")

# 3. Problema Central
st.error("🚨 ÁREA DEL PROBLEMA CENTRAL")
render_fila_simple("Problema Central")
st.markdown("---")

# 4. Rama de Causas: Directas arriba, Indirectas abajo (Jerarquía MML)
render_jerarquia_completa("Causas Directas", "Causas Indirectas", inversion_visual=False)

st.divider()
if st.button("Limpiar Árbol Completo", type="primary"):
    for k in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas'][k] = []
    st.rerun()
