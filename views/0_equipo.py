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

# --- LOGO Y TÍTULO JC FLOW ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.title("🏗️ JC Flow")
    st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Gestión de Equipo</h2>", unsafe_allow_html=True)

st.divider()

# --- BLOQUE 1: FICHAS VISUALES ---
if st.session_state['integrantes']:
    cols = st.columns(3) 
    # Filtramos para asegurar que solo procesamos diccionarios válidos
    lista_valida = [p for p in st.session_state['integrantes'] if isinstance(p, dict)]
    
    for idx, persona in enumerate(lista_valida):
        with cols[idx % 3]: 
            nombre = persona.get("Nombre Completo", "").upper()
            tel = persona.get("Teléfono", "N/A")
            email = persona.get("Correo Electrónico", "N/A")
            
            if len(nombre.strip()) > 0: 
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

# --- BLOQUE 2: EDITOR OCULTO ---
with st.expander("⚙️ Configuración: Agregar o Editar Integrantes"):
    integrantes_actuales = st.session_state.get('integrantes', [])
    # Limpiamos nulos antes de cargar en el DataFrame para evitar filas fantasma
    integrantes_limpios = [p for p in integrantes_actuales if isinstance(p, dict) and any(p.values())]
    
    df_equipo = pd.DataFrame(integrantes_limpios) if integrantes_limpios else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

    edited_df = st.data_editor(
        df_equipo,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_compacto",
    )

    if st.button("💾 ACTUALIZAR EQUIPO", type="primary", use_container_width=True):
        # Convertimos a diccionario y guardamos
        st.session_state['integrantes'] = edited_df.to_dict('records')
        guardar_datos_nube()
        st.rerun()
