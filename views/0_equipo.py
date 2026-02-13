import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia de datos
inicializar_session()

# --- ESTILOS PARA FICHAS PEQUEÑAS Y HOMOGÉNEAS ---
st.markdown("""
    <style>
    .ficha-equipo {
        background-color: #f0f5ff;
        border-left: 8px solid #4F8BFF;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nombre-mediano {
        font-size: 26px !important;
        color: #1E3A8A;
        font-weight: bold;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    .detalle-pequeno {
        font-size: 16px !important;
        color: #555;
        margin-bottom: 2px;
    }
    h2 { font-size: 38px !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGO Y TÍTULO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Gestión de Equipo</h2>", unsafe_allow_html=True)

st.divider()

# --- BLOQUE 1: FICHAS VISUALES ---
if st.session_state.get('integrantes'):
    cols = st.columns(3) 
    for idx, persona in enumerate(st.session_state['integrantes']):
        with cols[idx % 3]: 
            # --- AJUSTE DE SEGURIDAD (Corrección de línea 57) ---
            nombre_raw = persona.get("Nombre Completo")
            # Forzamos conversión a string y manejamos el None de Firebase
            nombre = str(nombre_raw or "SIN NOMBRE").upper()
            
            tel_raw = persona.get("Teléfono")
            tel = str(tel_raw or "N/A")
            
            email_raw = persona.get("Correo Electrónico")
            email = str(email_raw or "N/A")
            
            if len(nombre) > 2: 
                st.markdown(f"""
                    <div class="ficha-equipo">
                        <div class="nombre-mediano">👤 {nombre}</div>
                        <div class="detalle-pequeno">📞 {tel}</div>
                        <div class="detalle-pequeno">✉️ {email}</div>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.info("No hay integrantes registrados.")

st.divider()

# --- BLOQUE 2: EDITOR ---
with st.expander("⚙️ Configuración: Agregar o Editar Integrantes"):
    integrantes_actuales = st.session_state.get('integrantes', [])
    df_equipo = pd.DataFrame(integrantes_actuales) if integrantes_actuales else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

    edited_df = st.data_editor(
        df_equipo,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_compacto",
    )

    if st.button("💾 ACTUALIZAR EQUIPO", type="primary", use_container_width=True):
        st.session_state['integrantes'] = edited_df.to_dict('records')
        guardar_datos_nube()
        st.rerun()
