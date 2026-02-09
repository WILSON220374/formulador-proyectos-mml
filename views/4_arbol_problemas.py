import streamlit as st

st.title("🌳 4. Árbol de Problemas (Reglas MML Activas)")

# Configuración de Estilos y Restricciones
# Definimos cuáles secciones son de "Tarjeta Única"
SECCIONES_CONFIG = {
    "Fin": {"color": "#C1E1C1", "icono": "🏆", "limite": 1},
    "Efectos Indirectos": {"color": "#B3D9FF", "icono": "🌊", "limite": 99},
    "Efectos Directos": {"color": "#80BFFF", "icono": "💧", "limite": 99},
    "Problema Central": {"color": "#FFB3BA", "icono": "📍", "limite": 1},
    "Causas Directas": {"color": "#FFFFBA", "icono": "🧱", "limite": 99},
    "Causas Indirectas": {"color": "#FFDFBA", "icono": "🌱", "limite": 99}
}

# --- LÓGICA DE VALIDACIÓN Y MOVIMIENTO ---

def cambiar_seccion(origen, idx, destino):
    # Validar si el destino ya alcanzó su límite (Para Fin y Problema Central)
    if len(st.session_state['arbol_tarjetas'][destino]) >= SECCIONES_CONFIG[destino]["limite"]:
        st.toast(f"❌ La sección '{destino}' solo permite una tarjeta.", icon="🚫")
    else:
        tarjeta = st.session_state['arbol_tarjetas'][origen].pop(idx)
        st.session_state['arbol_tarjetas'][destino].append(tarjeta)
        st.rerun()

def reordenar(seccion, idx, direccion):
    lista = st.session_state['arbol_tarjetas'][seccion]
    nueva_pos = idx + direccion
    if 0 <= nueva_pos < len(lista):
        lista[idx], lista[nueva_pos] = lista[nueva_pos], lista[idx]
        st.rerun()

# --- INTERFAZ DE CREACIÓN EN SIDEBAR ---
with st.sidebar:
    st.header("➕ Nuevo Post-it")
    with st.form("nuevo_postit", clear_on_submit=True):
        texto = st.text_area("Descripción del problema:")
        seccion_ini = st.selectbox("Ubicación inicial:", list(SECCIONES_CONFIG.keys()))
        
        enviar = st.form_submit_button("Crear Tarjeta", use_container_width=True)
        
        if enviar and texto:
            # Validación de límite al crear
            actuales = len(st.session_state['arbol_tarjetas'][seccion_ini])
            limite = SECCIONES_CONFIG[seccion_ini]["limite"]
            
            if actuales < limite:
                st.session_state['arbol_tarjetas'][seccion_ini].append(texto)
                st.rerun()
            else:
                st.error(f"La sección '{seccion_ini}' ya tiene el máximo permitido (1).")

# --- RENDERIZADO DEL ÁRBOL ---

def mostrar_bloque(nombre):
    cfg = SECCIONES_CONFIG[nombre]
    st.markdown(f"#### {cfg['icono']} {nombre}")
    
    tarjetas = st.session_state['arbol_tarjetas'][nombre]
    if not tarjetas:
        st.caption("Sección vacía.")
    else:
        # Mostramos en columnas
        cols_visuales = st.columns(3)
        for i, contenido in enumerate(tarjetas):
            with cols_visuales[i % 3]:
                st.markdown(f"""
                    <div style="background-color:{cfg['color']}; padding:15px; border-radius:10px; 
                         border-left:10px solid rgba(0,0,0,0.1); color:black; font-weight:500; 
                         min-height:110px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
                        {contenido}
                    </div>
                """, unsafe_allow_html=True)
                
                # Fila de Reordenamiento y Eliminación
                c_izq, c_der, c_del = st.columns([1,1,1])
                with c_izq:
                    if st.button("⬅️", key=f"L_{nombre}_{i}"): reordenar(nombre, i, -1)
                with c_der:
                    if st.button("➡️", key=f"R_{nombre}_{i}"): reordenar(nombre, i, 1)
                with c_del:
                    if st.button("🗑️", key=f"D_{nombre}_{i}"):
                        st.session_state['arbol_tarjetas'][nombre].pop(i)
                        st.rerun()
                
                # Selector para mover de nivel (Cambio de color y sección)
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

# Dibujado del Árbol con jerarquía estricta
mostrar_bloque("Fin")
st.markdown("---")
mostrar_bloque("Efectos Indirectos")
mostrar_bloque("Efectos Directos")
st.markdown("---")
st.error("🚨 PROBLEMA CENTRAL (Único)")
mostrar_bloque("Problema Central")
st.markdown("---")
mostrar_bloque("Causas Directas")
mostrar_bloque("Causas Indirectas")
