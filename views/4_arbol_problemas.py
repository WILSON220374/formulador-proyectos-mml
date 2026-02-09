import streamlit as st

st.title("🌳 4. Árbol de Problemas (Editor con Reordenamiento)")

# 1. Configuración de Estilos y Colores
SECCIONES_CONFIG = {
    "Fin": {"color": "#C1E1C1", "icono": "🏆"},
    "Efectos Indirectos": {"color": "#B3D9FF", "icono": "🌊"},
    "Efectos Directos": {"color": "#80BFFF", "icono": "💧"},
    "Problema Central": {"color": "#FFB3BA", "icono": "📍"},
    "Causas Directas": {"color": "#FFFFBA", "icono": "🧱"},
    "Causas Indirectas": {"color": "#FFDFBA", "icono": "🌱"}
}

# --- LÓGICA DE MOVIMIENTO ---

# Mover entre secciones (Arriba/Abajo en el árbol)
def cambiar_seccion(origen, idx, destino):
    tarjeta = st.session_state['arbol_tarjetas'][origen].pop(idx)
    st.session_state['arbol_tarjetas'][destino].append(tarjeta)
    st.rerun()

# Reordenar dentro de la misma sección (Izquierda/Derecha)
def reordenar(seccion, idx, direccion):
    lista = st.session_state['arbol_tarjetas'][seccion]
    nueva_pos = idx + direccion
    if 0 <= nueva_pos < len(lista):
        lista[idx], lista[nueva_pos] = lista[nueva_pos], lista[idx]
        st.rerun()

# --- INTERFAZ DE CREACIÓN ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    with st.form("nuevo_postit", clear_on_submit=True):
        texto = st.text_area("Descripción del problema:")
        seccion_ini = st.selectbox("Ubicación inicial:", list(SECCIONES_CONFIG.keys()))
        if st.form_submit_button("Crear Tarjeta", use_container_width=True) and texto:
            st.session_state['arbol_tarjetas'][seccion_ini].append(texto)
            st.rerun()

# --- RENDERIZADO DEL ÁRBOL ---

def mostrar_bloque(nombre):
    cfg = SECCIONES_CONFIG[nombre]
    st.markdown(f"#### {cfg['icono']} {nombre}")
    
    tarjetas = st.session_state['arbol_tarjetas'][nombre]
    if not tarjetas:
        st.caption("No hay tarjetas aquí.")
    else:
        # Mostramos en 3 columnas
        cols_visuales = st.columns(3)
        for i, contenido in enumerate(tarjetas):
            with cols_visuales[i % 3]:
                # Estilo de la tarjeta
                st.markdown(f"""
                    <div style="background-color:{cfg['color']}; padding:15px; border-radius:10px; 
                         border-left:10px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
                         min-height:110px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
                        {contenido}
                    </div>
                """, unsafe_allow_html=True)
                
                # Controles de la tarjeta
                # Fila 1: Mover Izquierda / Derecha
                c_izq, c_der, c_del = st.columns([1,1,1])
                with c_izq:
                    if st.button("⬅️", key=f"L_{nombre}_{i}"):
                        reordenar(nombre, i, -1)
                with c_der:
                    if st.button("➡️", key=f"R_{nombre}_{i}"):
                        reordenar(nombre, i, 1)
                with c_del:
                    if st.button("🗑️", key=f"D_{nombre}_{i}"):
                        st.session_state['arbol_tarjetas'][nombre].pop(i)
                        st.rerun()
                
                # Fila 2: Cambiar de Sección (Nivel)
                nueva_sec = st.selectbox(
                    "Cambiar nivel:", 
                    list(SECCIONES_CONFIG.keys()),
                    index=list(SECCIONES_CONFIG.keys()).index(nombre),
                    key=f"sec_{nombre}_{i}",
                    label_visibility="collapsed"
                )
                if nueva_sec != nombre:
                    cambiar_seccion(nombre, i, nueva_sec)

st.divider()

# Dibujado en orden jerárquico solicitado
mostrar_bloque("Fin")
st.markdown("---")
mostrar_bloque("Efectos Indirectos")
mostrar_bloque("Efectos Directos")
st.markdown("---")
st.error("📍 PROBLEMA CENTRAL")
mostrar_bloque("Problema Central")
st.markdown("---")
mostrar_bloque("Causas Directas")
mostrar_bloque("Causas Indirectas")
