import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización
inicializar_session()

# --- ESTILOS CSS PARA AMPLIAR DATOS DILIGENCIADOS ---
st.markdown("""
    <style>
    /* 1. Aumentar tamaño de la letra que se escribe en las celdas */
    input {
        font-size: 22px !important;
        font-weight: 500 !important;
    }
    
    /* 2. Intentar forzar el tamaño en el contenedor del editor */
    [data-testid="stDataEditor"] {
        font-size: 20px !important;
    }

    /* 3. Títulos y avisos (manteniendo el estilo anterior) */
    h2 { font-size: 40px !important; font-weight: 700 !important; }
    .stInfo { font-size: 22px !important; }
    
    /* 4. Botón de guardado gigante */
    .stButton button {
        font-size: 26px !important;
        height: 3.5em !important;
        background-color: #4F8BFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DISTRIBUCIÓN VISUAL JC FLOW ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Registro de Equipo</h2>", unsafe_allow_html=True)
    st.info("Escriba aquí los datos de su grupo de trabajo:")

st.divider()

# --- SECCIÓN DE TABLA DE DATOS ---
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# Editor de datos con configuración de columnas
edited_df = st.data_editor(
    df_equipo,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_equipo_v4",
    column_config={
        "Nombre Completo": st.column_config.TextColumn(width="large"),
        "Teléfono": st.column_config.TextColumn(width="medium"),
        "Correo Electrónico": st.column_config.TextColumn(width="large")
    }
)

st.markdown("<br>", unsafe_allow_html=True)

# Botón de guardado con sincronización
if st.button("💾 GUARDAR DATOS DEL GRUPO", type="primary", use_container_width=True):
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Datos del equipo guardados!", icon="👥")
    st.rerun() # Para actualizar la lista en el sidebar
