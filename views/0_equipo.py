import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización
inicializar_session()

st.title("👥 Registro de Equipo")
st.info("Ingrese los datos de los integrantes. El sistema extraerá el primer nombre para mostrarlo en la barra lateral.")

# 2. Cargar lista de integrantes
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# 3. Editor de tabla (AJUSTADO: Sin 'placeholder' para evitar TypeError)
edited_df = st.data_editor(
    df_equipo,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_equipo",
    column_config={
        "Nombre Completo": st.column_config.TextColumn(help="Ej: Juan Pérez"),
        "Teléfono": st.column_config.TextColumn(help="Ej: +57 300..."),
        "Correo Electrónico": st.column_config.TextColumn(help="juan@ejemplo.com")
    }
)

# 4. Botón de guardado y sincronización
if st.button("💾 Guardar y Actualizar Barra Lateral", type="primary", use_container_width=True):
    # Guardamos los datos como lista de diccionarios
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Equipo actualizado!", icon="👥")
    st.rerun() # Esto actualiza inmediatamente el sidebar
