import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# Inicializar sesión para asegurar que existan las variables
inicializar_session()

st.title("👥 Registro de Equipo")
st.info("Ingrese los datos de los integrantes. El sistema extraerá el primer nombre para la barra lateral.")

# 1. Cargar o inicializar la lista de integrantes
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# 2. Editor interactivo de datos
edited_df = st.data_editor(
    df_equipo,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_equipo",
    column_config={
        "Nombre Completo": st.column_config.TextColumn(placeholder="Ej: Juan Pérez"),
        "Teléfono": st.column_config.TextColumn(placeholder="Ej: +57 300..."),
        "Correo Electrónico": st.column_config.TextColumn(placeholder="juan@ejemplo.com")
    }
)

# 3. Botón para guardar y actualizar la barra lateral
if st.button("💾 Guardar y Actualizar Barra Lateral", type="primary", use_container_width=True):
    # Convertir el DataFrame editado de vuelta a lista de diccionarios
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Equipo actualizado con éxito!", icon="👥")
    st.rerun() # Recarga para aplicar los cambios en el sidebar
