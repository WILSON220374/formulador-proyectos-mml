import streamlit as st

st.title("🌳 4. Árbol de Problemas (Jerarquía y Validación)")

# 1. Configuración de Estilos y Colores
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple"},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos"},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple"},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple"},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple"},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas"}
}

# --- SIDEBAR: GENERADOR Y HERRAMIENTAS ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("2. Descripción de la idea:")
        
        # Asociación previa para elementos indirectos
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'][CONFIG[tipo_sel]["padre"]]
            if opciones_p:
                padre_asociado = st.selectbox(f"3. Vincular a {CONFIG[tipo_sel]['padre']}:", opciones_p)
            else:
                st.warning(f"⚠️ Primero cree un {CONFIG[tipo_sel]['padre']}.")

        if st.form_submit_button("Generar Ficha") and texto_input:
            if len(st.session_state['arbol_tarjetas'][tipo_sel]) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo" and padre_asociado:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()
            else:
                st.error("Límite de 1 tarjeta alcanzado para esta sección.")

    st.divider()
    
    # 2. BOTÓN DE DESCARGA (Para Impresión)
    st.subheader("📥 Exportar Árbol")
    def generar_texto_reporte():
        datos = st.session_state['arbol_tarjetas']
        reporte = "REPORTE TÉCNICO: ÁRBOL DE PROBLEMAS\n" + "="*40 + "\n"
        for sec, items in datos.items():
            reporte += f"\n{sec.upper()}:\n"
            if not items:
                reporte += "- (Sección vacía)\n"
            else:
                for i, item in enumerate(items):
                    if isinstance(item, dict):
                        reporte += f"  {i+1}. {item['texto']} [Asociado a: {item['padre']}]\n"
                    else:
                        reporte += f"  {i+1}. {item}\n"
        return reporte

    st.download_button(
        label="📄 Descargar Reporte (.txt)",
        data=generar_texto_reporte(),
        file_name="arbol_problemas.txt",
        mime="text/plain",
        use_container_width=True
    )

# --- FUNCIONES DE RENDERIZADO ---

def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:12px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:8px; min-height:70px; box-shadow: 2px 2px 5px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center;">
               {texto}</div>"""

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'][nombre]
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            if st.button("🗑️ Borrar", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                st.rerun()
        else:
            st.caption("Sección vacía")

def render_rama(nombre_padre, nombre_hijo, inversion=False):
    """Renderiza alineado verticalmente con validación de borrado."""
    padres = st.session_state['arbol_tarjetas'][nombre_padre]
    hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
    
    # Definir orden de filas para Efectos (Hijo arriba) o Causas (Padre arriba)
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion_actual, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{seccion_actual.upper()}</div>", unsafe_allow_html=True)
        with col_c:
            if not padres:
                st.caption(f"Cree un {nombre_padre} para activar esta fila.")
            else:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            hijos_del_padre = [h for h in hijos if h["padre"] == p_txt]
                            for h_
