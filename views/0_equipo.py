import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia de datos
inicializar_session()

# --- ESTILOS CSS REFORZADOS PARA EL INTERIOR DE LA TABLA ---
st.markdown("""
    <style>
    /* 1. Aumenta la fuente de las celdas y el texto base del editor */
    div[data-testid="stDataEditor"] {
        font-size: 30px !important; /* Ajusta este valor según prefieras */
    }

    /* 2. Aumenta la fuente específicamente en las filas de datos */
    div[data-testid="stDataEditor"] div[role="gridcell"] {
        font-size: 30px !important;
    }

    /* 3. Aumenta la fuente del campo de texto cuando estás escribiendo */
    div[data-testid="stDataEditor"] input {
        font-size: 30px !important;
        font-weight: bold !important;
    }

    /* 4. Estilos de títulos y logo JC Flow (Manteniendo proporciones) */
    h2 { font-size: 42px !important; font-weight: 700 !important; }
    .stInfo { font-size: 24px !important; }
    
    /* 5. Estilo del botón de guardado */
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
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Registro de Equipo</h2>", unsafe_allow_html=True)
    st.info("Diligencie aquí los datos de su grupo de trabajo:")

st.divider()

# --- SECCIÓN DE TABLA DE DATOS ---
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# Editor de datos con configuración de columnas
edited_df = st.data_editor(
    df_equipo,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_equipo_vFinal",
    column_config={
        "Nombre Completo": st.column_config.TextColumn(width="large"),
        "Teléfono": st.column_config.TextColumn(width="medium"),
        "Correo Electrónico": st.column_config.TextColumn(width="large")
    }
)

st.markdown("<br>", unsafe_allow_html=True)

# Sincronización con la nube
if st.button("💾 GUARDAR INFORMACIÓN DEL EQUIPO", type="primary", use_container_width=True):
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Información sincronizada!", icon="👥")
    st.rerun()
