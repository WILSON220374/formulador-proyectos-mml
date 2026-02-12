import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia de datos
inicializar_session()

# --- ESTILOS PARA LAS FICHAS GIGANTES ---
st.markdown("""
    <style>
    .ficha-equipo {
        background-color: #f0f5ff;
        border-left: 10px solid #4F8BFF;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .nombre-gigante {
        font-size: 40px !important;
        color: #1E3A8A;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .detalle-gigante {
        font-size: 22px !important;
        color: #555;
    }
    h2 { font-size: 42px !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGO Y TÍTULO JC FLOW ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Gestión de Equipo</h2>", unsafe_allow_html=True)

st.divider()

# --- BLOQUE 1: FICHAS VISUALES (MUESTRA LOS DATOS GRANDES) ---
if st.session_state['integrantes']:
    # Solo mostramos las fichas si hay gente registrada
    cols = st.columns(2) 
    for idx, persona in enumerate(st.session_state['integrantes']):
        with cols[idx % 2]: 
            nombre = persona.get("Nombre Completo", "").upper()
            tel = persona.get("Teléfono", "N/A")
            email = persona.get("Correo Electrónico", "N/A")
            
            if len(nombre) > 2: 
                st.markdown(f"""
                    <div class="ficha-equipo">
                        <div class="nombre-gigante">👤 {nombre}</div>
                        <div class="detalle-gigante">📞 {tel}</div>
                        <div class="detalle-gigante">✉️ {email}</div>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.info("No hay integrantes registrados. Use el panel de edición inferior para empezar.")

st.divider()

# --- BLOQUE 2: EDITOR OCULTO (SOLO PARA CAMBIOS) ---
with st.expander("⚙️ Configuración: Agregar o Editar Integrantes"):
    st.write("Diligencie la tabla para actualizar las fichas visuales.")
    
    integrantes_actuales = st.session_state.get('integrantes', [])
    df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

    edited_df = st.data_editor(
        df_equipo,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_oculto",
        column_config={
            "Nombre Completo": st.column_config.TextColumn(width="large"),
            "Teléfono": st.column_config.TextColumn(width="medium"),
            "Correo Electrónico": st.column_config.TextColumn(width="large")
        }
    )

    if st.button("💾 ACTUALIZAR EQUIPO", type="primary", use_container_width=True):
        st.session_state['integrantes'] = edited_df.to_dict('records')
        guardar_datos_nube()
        st.rerun() # Para actualizar las fichas y el sidebar
