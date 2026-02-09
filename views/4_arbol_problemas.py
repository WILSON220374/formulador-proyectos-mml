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

# --- SIDEBAR: GENERADOR DE TARJETAS (ASOCIACIÓN PREVIA MEJORADA) ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    # Paso 1: Selección de sección fuera del form para actualizar opciones de 'padre'
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        # Paso 2: Asociación (Se pregunta ANTES de escribir el texto)
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            nombre_padre = CONFIG[tipo_sel]["padre"]
            opciones_padre = st.session_state['arbol_tarjetas'][nombre_padre]
            
            if opciones_padre:
                padre_asociado = st.selectbox(f"2. Vincular a {nombre_padre}:", opciones_padre)
            else:
                st.warning(f"⚠️ Primero debe crear un '{nombre_padre}'.")
        
        # Paso 3: Descripción
        texto_input = st.text_area("3. Descripción de la idea:")
        
        if st.form_submit_button("Generar Ficha"):
            if not texto_input:
                st.error("Por favor, escriba un texto.")
            elif len(st.session_state['arbol_tarjetas'][tipo_sel]) >= CONFIG[tipo_sel]["limite"]:
                st.error("Esta sección solo permite 1 tarjeta.")
            elif CONFIG[tipo_sel]["tipo"] == "hijo" and not padre_asociado:
                st.error("Debe asociar esta ficha a un elemento superior.")
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

def render_rama_jerarquica(nombre_padre, nombre_hijo, inversion=False):
    """Renderiza Directos e Indirectos en filas separadas para evitar que floten"""
    padres = st.session_state['arbol_tarjetas'][nombre_padre]
    hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
    
    if not padres:
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='text-align:right; color:#999;'>{nombre_padre.upper()}</div>", unsafe_allow_html=True)
        with col_c: st.caption(f"Cree un {nombre_padre} para activar esta sección.")
        return

    # Definir orden de filas: Para Efectos, Indirecto va arriba. Para Causas, Directo va arriba.
    orden_filas = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion_actual, es_hijo in orden_filas:
        col_label, col_content = st.columns([1, 4])
        with col_label:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{seccion_actual.upper()}</div>", unsafe_allow_html=True)
        
        with col_content:
            # Crear el mismo número de columnas que padres existen para alinear verticalmente
            cols = st.columns(len(padres))
            for i, p_texto in enumerate(padres):
                with cols[i]:
                    if es_hijo:
                        # Filtrar y mostrar hijos asociados a este padre específico
                        hijos_del_padre = [h for h in hijos if h["padre"] == p_texto]
                        for h_idx, h_data in enumerate(hijos_del_padre):
                            st.markdown(card_html(h_data["texto"], CONFIG[nombre_hijo]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_h_{seccion_actual}_{i}_{h_idx}"):
                                st.session_state['arbol_tarjetas'][seccion_actual].remove(h_data)
                                st.rerun()
                    else:
                        # Mostrar el padre
                        st.markdown(card_html(p_texto, CONFIG[nombre_padre]["color"]), unsafe_allow_html=True)
                        if st.button("🗑️ Borrar Principal", key=f"del_p_{seccion_actual}_{i}"):
                            # Al borrar el padre, se limpian sus hijos asociados
                            st.session_state['arbol_tarjetas'][nombre_hijo] = [h for h in hijos if h["padre"] != p_texto]
                            st.session_state['arbol_tarjetas'][seccion_actual].pop(i)
                            st.rerun()

# --- CONSTRUCCIÓN VISUAL DEL ÁRBOL ---
st.divider()

# 1. Problema Superior
render_simple("Problema Superior")
st.markdown("---")

# 2. Rama de Efectos: Indirectos (Arriba) -> Directos (Abajo)
render_rama_jerarquica("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")

# 3. Problema Central
st.error("📍 ÁREA DEL PROBLEMA CENTRAL")
render_simple("Problema Central")
st.markdown("---")

# 4. Rama de Causas: Directas (Arriba) -> Indirectas (Abajo)
render_rama_jerarquica("Causas Directas", "Causas Indirectas", inversion=False)

st.divider()
if st.button("Limpiar Árbol Completo", type="primary"):
    for k in st.session_state['arbol_tarjetas']:
        st.session_state['arbol_tarjetas'][k] = []
    st.rerun()
