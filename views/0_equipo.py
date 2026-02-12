import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# Inicialización de variables globales
inicializar_session()

st.title("👥 Registro de Equipo")
st.info("Complete la tabla con la información de los integrantes. Los cambios se verán reflejados en la barra lateral.")

# 1. Cargar datos existentes
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# 2. Editor de tabla (FIX: Sin 'placeholder' para evitar errores)
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

# 3. Guardado y actualización inmediata
if st.button("💾 Guardar Datos del Equipo", type="primary", use_container_width=True):
    # Convertimos a lista de diccionarios para la nube
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Información sincronizada!", icon="👥")
    st.rerun() # Recarga para actualizar los nombres en el sidebar
