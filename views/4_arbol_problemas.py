import streamlit as st

st.title("🌳 4. Árbol de Problemas (Editor Dinámico)")

# Configuración Maestra de Colores y Secciones
SECCIONES_CONFIG = {
    "Fin": {"color": "#C1E1C1", "icono": "🏆"},
    "Efectos Indirectos": {"color": "#B3D9FF", "icono": "🌊"},
    "Efectos Directos": {"color": "#80BFFF", "icono": "💧"},
    "Problema Central": {"color": "#FFB3BA", "icono": "📍"},
    "Causas Directas": {"color": "#FFFFBA", "icono": "🧱"},
    "Causas Indirectas": {"color": "#FFDFBA", "icono": "🌱"}
}

# --- 1. GENERADOR DE TARJETAS (POST-ITS) ---
with st.sidebar:
    st.header("➕ Nueva Tarjeta")
    with st.form("crear_tarjeta", clear_on_submit=True):
        nuevo_texto = st.text_area("Descripción del problema/idea:", placeholder="Escriba aquí...")
        nueva_seccion = st.selectbox("Seleccione la Sección inicial:", list(SECCIONES_CONFIG.keys()))
        
        submit = st.form_submit_state = st.form_submit_button("Generar Post-it", use_container_width=True)
        
        if submit and nuevo_texto:
            # Guardamos un diccionario con el texto y su sección actual
            st.session_state['arbol_tarjetas'][nueva_seccion].append(nuevo_texto)
            st.success(f"Tarjeta añadida a {nueva_seccion}")
            st.rerun()

# --- 2. LÓGICA DE MOVIMIENTO ENTRE SECCIONES ---
def mover_tarjeta(seccion_origen, indice, nueva_seccion_destino):
    # Extraer la tarjeta de la sección actual
    contenido = st.session_state['arbol_tarjetas'][seccion_origen].pop(indice)
    # Insertarla en la nueva sección
    st.session_state['arbol_tarjetas'][nueva_seccion_destino].append(contenido)
    st.rerun()

# --- 3. FUNCIÓN PARA DIBUJAR LAS TARJETAS DINÁMICAS ---
def renderizar_bloque(nombre_seccion):
    config = SECCIONES_CONFIG[nombre_seccion]
    st.markdown(f"#### {config['icono']} {nombre_seccion}")
    
    lista_tarjetas = st.session_state['arbol_tarjetas'][nombre_seccion]
    
    if not lista_tarjetas:
        st.caption("Arrastre o cree tarjetas para esta sección.")
    else:
        # Mostramos las tarjetas en un grid de 3 columnas
        cols_tarjetas = st.columns(3)
        for idx, texto in enumerate(lista_tarjetas):
            with cols_tarjetas[idx % 3]:
                # Contenedor visual de la tarjeta
                st.markdown(f"""
                    <div style="background-color:{config['color']}; padding:15px; 
                         border-radius:8px; border-left:10px solid rgba(0,0,0,0.1); 
                         color:black; font-weight:500; min-height:100px; box-shadow: 2px 2px 5px #eeeeee;">
                        {texto}
                    </div>
                """, unsafe_allow_html=True)
                
                # Controles de la tarjeta (Mover y Eliminar)
                c1, c2 = st.columns([3, 1])
                with c1:
                    # El "espacio" para cambiar de sección que pediste
                    nuevo_destino = st.selectbox(
                        "Mover a:", 
                        list(SECCIONES_CONFIG.keys()), 
                        index=list(SECCIONES_CONFIG.keys()).index(nombre_seccion),
                        key=f"move_{nombre_seccion}_{idx}",
                        label_visibility="collapsed"
                    )
                    if nuevo_destino != nombre_seccion:
                        mover_tarjeta(nombre_seccion, idx, nuevo_destino)
                with c2:
                    if st.button("🗑️", key=f"del_{nombre_seccion}_{idx}"):
                        st.session_state['arbol_tarjetas'][nombre_seccion].pop(idx)
                        st.rerun()

# --- 4. ESTRUCTURA VISUAL DEL ÁRBOL (JERARQUÍA MML) ---
st.divider()

# Nivel Superior: Fines y Efectos
renderizar_bloque("Fin")
st.markdown("---")
renderizar_bloque("Efectos Indirectos")
renderizar_bloque("Efectos Directos")

# Centro: Problema
st.markdown("---")
st.error("🚨 ÁREA DEL PROBLEMA CENTRAL")
renderizar_bloque("Problema Central")
st.markdown("---")

# Base: Causas
renderizar_bloque("Causas Directas")
renderizar_bloque("Causas Indirectas")
