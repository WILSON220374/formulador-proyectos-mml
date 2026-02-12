import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia de datos
inicializar_session()

# --- ESTILOS CSS PARA AMPLIAR EL INTERIOR DE LA TABLA ---
st.markdown("""
    <style>
    /* 1. Aumenta la fuente de TODO el contenido dentro del editor de datos */
    [data-testid="stDataEditor"] div {
        font-size: 48px !important;
    }

    /* 2. Aumenta la fuente específicamente cuando se está escribiendo en la celda */
    [data-testid="stDataEditor"] input {
        font-size: 24px !important;
    }

    /* 3. Estilos de títulos y logo JC Flow */
    h2 { font-size: 42px !important; font-weight: 700 !important; }
    .stInfo { font-size: 24px !important; }
    
    /* 4. Estilo del botón de guardado destacado */
    .stButton button {
        font-size: 26px !important;
        height: 3em !important;
        border-radius: 15px !important;
        background-color: #4F8BFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DISTRIBUCIÓN VISUAL JC FLOW ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Verificación del archivo de logo
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Registro de Equipo</h2>", unsafe_allow_html=True)
    st.info("Diligencie aquí los datos de su grupo de trabajo:")

st.divider()

# --- SECCIÓN DE TABLA DE DATOS (Interior del Registro) ---
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# Editor de datos configurado para el tamaño de letra grande
edited_df = st.data_editor(
    df_equipo,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_equipo_v5",
    column_config={
        "Nombre Completo": st.column_config.TextColumn(width="large"),
        "Teléfono": st.column_config.TextColumn(width="medium"),
        "Correo Electrónico": st.column_config.TextColumn(width="large")
    }
)

st.markdown("<br>", unsafe_allow_html=True)

# Sincronización con la nube al guardar
if st.button("💾 GUARDAR INFORMACIÓN DEL EQUIPO", type="primary", use_container_width=True):
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Información sincronizada con éxito!", icon="👥")
    st.rerun() # Actualiza el sidebar con los nombres de pila
