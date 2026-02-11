import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# Inicialización de seguridad
inicializar_session()

st.title("🌳 4. Árbol de Problemas")

# --- RECUPERACIÓN DEL PROBLEMA CENTRAL ---
# Traemos el texto validado desde la Hoja 1
datos_p = st.session_state.get('datos_problema', {})
texto_problema = datos_p.get('problema_central', "No se ha definido el problema en la Fase 1.")

# --- DISEÑO DEL TRONCO (PROBLEMA CENTRAL) ---
# Eliminamos el banner superior y dejamos solo la tarjeta central
st.markdown("<br>", unsafe_allow_html=True) # Espacio estético

col_etiqueta, col_caja = st.columns([1, 4])

with col_etiqueta:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**PROBLEMA CENTRAL**")

with col_caja:
    # Caja estilizada en color rosa suave para el Problema Central
    st.markdown(
        f"""
        <div style="
            background-color: #f8bcbc; 
            padding: 25px; 
            border-radius: 10px; 
            border: 2px solid #e57373;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            color: #333;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        ">
            {texto_problema}
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- BOTÓN DE LIMPIEZA (OPCIONAL) ---
st.markdown("###")
col_btn, _ = st.columns([1, 4])
with col_btn:
    if st.button("🗑️ Borrar", use_container_width=True):
        # Esta acción solo limpia la visualización temporal, no borra el diagnóstico
        st.warning("Para modificar el Problema Central, regrese a la hoja '1. Diagnóstico'.")

# --- DIVISOR PARA CAUSAS Y EFECTOS ---
st.divider()
st.subheader("🌿 Estructura del Árbol")
st.info("Utilice las secciones siguientes para desglosar los Efectos (Ramas) y las Causas (Raíces).")

# Aquí continuaría la lógica de tus tarjetas dinámicas para causas y efectos
