import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización
inicializar_session()

# --- AJUSTES DE TAMAÑO DE FUENTE (CSS) ---
st.markdown("""
    <style>
    /* Título principal de la sección */
    h2 {
        font-size: 42px !important;
        font-weight: 700 !important;
    }
    /* Cuadro de información azul */
    .stInfo {
        font-size: 20px !important;
    }
    /* Etiquetas y textos generales */
    p {
        font-size: 18px !important;
    }
    /* Botón de guardado */
    .stButton button {
        font-size: 24px !important;
        height: 3em !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DISTRIBUCIÓN VISUAL (IGUAL A LA INICIAL) ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Verificación y despliegue del logo JC Flow
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Registro de Equipo</h2>", unsafe_allow_html=True)
    st.info("Registre los integrantes para personalizar la barra lateral.")

st.divider()

# --- SECCIÓN DE TABLA DE DATOS ---
integrantes_actuales = st.session_state.get('integrantes', [])
df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

# Nota: El tamaño de letra dentro de las celdas del editor es manejado por el motor interno de Streamlit
edited_df = st.data_editor(
    df_equipo,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_equipo_v3",
    column_config={
        "Nombre Completo": st.column_config.TextColumn(help="Nombre y apellido del formulador"),
        "Teléfono": st.column_config.TextColumn(help="Contacto directo"),
        "Correo Electrónico": st.column_config.TextColumn(help="Email institucional")
    }
)

st.markdown("<br>", unsafe_allow_html=True)

# Botón de guardado con tamaño aumentado
if st.button("💾 GUARDAR INFORMACIÓN DEL EQUIPO", type="primary", use_container_width=True):
    st.session_state['integrantes'] = edited_df.to_dict('records')
    guardar_datos_nube()
    st.toast("✅ ¡Equipo guardado y actualizado!", icon="👥")
    st.rerun() # Sincroniza la lista vertical del sidebar
