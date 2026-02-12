import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización de variables
inicializar_session()

# --- DISTRIBUCIÓN VISUAL (IGUAL A LA INICIAL) ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Verificación y despliegue del logo
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Registro de Equipo</h2>", unsafe_allow_html=True)
    st.info("Ingrese los datos de los integrantes. Los nombres de pila se verán en la barra lateral.")

# --- SECCIÓN DE EDICIÓN DE DATOS ---
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# Editor de tabla sin parámetros que causen error
edited_df = st.data_editor(
    df_equipo,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_equipo_final",
    column_config={
        "Nombre Completo": st.column_config.TextColumn(help="Ingrese nombre y apellido"),
        "Teléfono": st.column_config.TextColumn(help="Número de contacto"),
        "Correo Electrónico": st.column_config.TextColumn(help="Correo institucional o personal")
    }
)

# Botón de guardado sincronizado
if st.button("💾 Guardar y Actualizar Equipo", type="primary", use_container_width=True):
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Información del equipo guardada!", icon="👥")
    st.rerun() # Para refrescar la lista en la barra lateral
