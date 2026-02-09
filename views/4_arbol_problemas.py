import streamlit as st

st.title("🌳 4. Árbol de Problemas")

# Configuración de Colores Estilo Post-it por sección
COLORES = {
    "Fin": "#C1E1C1",              # Verde claro
    "Efectos Indirectos": "#B3D9FF", # Azul muy claro
    "Efectos Directos": "#80BFFF",   # Azul claro
    "Problema Central": "#FFB3BA",   # Rosa/Rojo (Problema)
    "Causas Directas": "#FFFFBA",    # Amarillo
    "Causas Indirectas": "#FFDFBA"   # Naranja claro
}

# --- FORMULARIO DE CREACIÓN ---
with st.container(border=True):
    st.subheader("📝 Generador de Tarjetas")
    c1, c2 = st.columns([2, 1])
    with c1:
        texto = st.text_input("Escriba la idea o problema:", key="input_tarjeta", placeholder="Ej: Alta tasa de desempleo")
    with c2:
        tipo = st.selectbox("¿A qué sección corresponde?", list(COLORES.keys()))
    
    if st.button("Agregar al Árbol", use_container_width=True):
        if texto:
            st.session_state['arbol_tarjetas'][tipo].append(texto)
            st.rerun()

# --- FUNCIÓN PARA RENDERIZAR LAS TARJETAS ---
def dibujar_seccion(titulo):
    st.markdown(f"#### {titulo}")
    items = st.session_state['arbol_tarjetas'][titulo]
    
    if not items:
        st.caption("Aún no hay tarjetas en esta sección.")
    else:
        cols = st.columns(3)
        for idx, contenido in enumerate(items):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div style="background-color:{COLORES[titulo]}; padding:15px; 
                         border-radius:10px; border-left:8px solid rgba(0,0,0,0.1); 
                         margin-bottom:10px; color:black; font-weight:500; min-height:80px;">
                        {contenido}
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Eliminar", key=f"btn_{titulo}_{idx}"):
                    st.session_state['arbol_tarjetas'][titulo].pop(idx)
                    st.rerun()

st.divider()

# Orden jerárquico visual (Top-Down)
dibujar_seccion("Fin")
st.markdown("⬇️")
dibujar_seccion("Efectos Indirectos")
dibujar_seccion("Efectos Directos")
st.markdown("---")
st.error("📍 PROBLEMA CENTRAL")
dibujar_seccion("Problema Central")
st.markdown("---")
st.markdown("⬆️")
dibujar_seccion("Causas Directas")
dibujar_seccion("Causas Indirectas")
