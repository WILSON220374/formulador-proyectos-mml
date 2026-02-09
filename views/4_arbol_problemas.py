import streamlit as st

st.title("🌳 4. Árbol de Problemas (Validación y Reporte)")

# Configuración Maestra
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
    st.header("➕ Gestión del Árbol")
    
    # 1. Crear Tarjetas
    tipo_sel = st.selectbox("Sección:", list(CONFIG.keys()))
    with st.form("crear_ficha", clear_on_submit=True):
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'][CONFIG[tipo_sel]["padre"]]
            if opciones_p:
                padre_asociado = st.selectbox(f"Vincular a {CONFIG[tipo_sel]['padre']}:", opciones_p)
            else:
                st.warning(f"Cree un {CONFIG[tipo_sel]['padre']} primero.")
        
        texto_input = st.text_area("Descripción:")
        if st.form_submit_button("Generar Ficha") and texto_input:
            if len(st.session_state['arbol_tarjetas'][tipo_sel]) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo" and padre_asociado:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()
            else:
                st.error("Límite de 1 tarjeta alcanzado.")

    st.divider()
    
    # 2. Validación Técnica
    if st.button("✅ Validar Consistencia Técnica", use_container_width=True):
        errores = []
        arbol = st.session_state['arbol_tarjetas']
        
        if not arbol["Problema Superior"]: errores.append("Falta el Problema Superior.")
        if not arbol["Problema Central"]: errores.append("Falta el Problema Central.")
        if not arbol["Causas Directas"]: errores.append("Debe tener al menos una Causa Directa.")
        if not arbol["Efectos Directos"]: errores.append("Debe tener al menos un Efecto Directo.")
        
        if errores:
            for err in errores: st.error(err)
        else:
            st.success("¡Árbol técnicamente consistente!")

    # 3. Opción de Descarga
    st.subheader("📥 Exportar Reporte")
    
    def generar_reporte():
        arbol = st.session_state['arbol_tarjetas']
        lineas = ["REPORTE TÉCNICO: ÁRBOL DE PROBLEMAS\n" + "="*40 + "\n"]
        
        for sec in list(CONFIG.keys()):
            lineas.append(f"\n[{sec.upper()}]")
            items = arbol[sec]
            if not items:
                lineas.append("- Sin registros.")
            else:
                for idx, item in enumerate(items):
                    if isinstance(item, dict):
                        lineas.append(f"{idx+1}. {item['texto']} (Asociado a: {item['padre']})")
                    else:
                        lineas.append(f"{idx+1}. {item}")
        return "\n".join(lineas)

    st.download_button(
        label="📄 Descargar para Impresión",
        data=generar_reporte(),
        file_name="arbol_problemas_reporte.txt",
        mime="text/plain",
        use_container_width=True
    )

# --- FUNCIONES DE RENDERIZADO VISUAL ---

def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:12px; border-radius:8px; 
               border-left:8px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
               margin-bottom:8px; min-height:70px; box-shadow: 2px 2px 5px #eee; 
               display: flex; align-items: center; justify-content: center; text-align: center;">
               {texto}</div>"""

def render_jerarquia(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_tarjetas'][nombre_padre]
    hijos = st.session_state['arbol_tarjetas'][nombre_hijo]
    
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{seccion.upper()}</div>", unsafe_allow_html=True)
        with col_content := col_c:
            if not padres:
                st.caption(f"Esperando {nombre_padre}...")
            else:
                cols = st.columns(len(padres))
                for i, p_txt in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            for h in [h for h in hijos if h["padre"] == p_txt]:
                                st.markdown(card_html(h["texto"], CONFIG[seccion]["color"]), unsafe_allow_html=True)
                                if st.button("🗑️", key=f"d_{seccion}_{i}_{h['texto'][:5]}"):
                                    st.session_state['arbol_tarjetas'][seccion].remove(h)
                                    st.rerun()
                        else:
                            st.markdown(card_html(p_txt, CONFIG[seccion]["color"]), unsafe_allow_html=True)
                            if st.button("🗑️ Borrar", key=f"dp_{seccion}_{i}"):
                                st.session_state['arbol_tarjetas'][nombre_hijo] = [h for h in hijos if h["padre"] != p_txt]
                                st.session_state['arbol_tarjetas'][seccion].pop(i)
                                st.rerun()

def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'][nombre]
        if items:
            st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
            if st.button("🗑️", key=f"ds_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                st.rerun()
        else: st.caption("Vacío")

# --- DIBUJO DEL ÁRBOL ---
st.divider()
render_simple("Problema Superior")
st.markdown("---")
render_jerarquia("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")
st.error("📍 PROBLEMA CENTRAL")
render_simple("Problema Central")
st.markdown("---")
render_jerarquia("Causas Directas", "Causas Indirectas", inversion=False)
