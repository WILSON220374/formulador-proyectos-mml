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

# --- BLOQUE 1: FICHAS VISUALES CON FILTRO DE SEGURIDAD ---
# Filtramos la lista para ignorar nulos antes de intentar dibujarlos
integrantes_raw = st.session_state.get('integrantes', [])
integrantes_validos = [p for p in integrantes_raw if isinstance(p, dict) and p]

if integrantes_validos:
    cols = st.columns(3) 
    for idx, persona in enumerate(integrantes_validos):
        with cols[idx % 3]: 
            # Doble verificación para evitar el AttributeError
            nombre = persona.get("Nombre Completo", "SIN NOMBRE").upper()
            tel = persona.get("Teléfono", "N/A")
            email = persona.get("Correo Electrónico", "N/A")
            
            if len(nombre) > 2: 
                st.markdown(f"""
                    <div class="ficha-equipo">
                        <div class="nombre-mediano">👤 {nombre}</div>
                        <div class="detalle-pequeno">📞 {tel}</div>
                        <div class="detalle-pequeno">✉️ {email}</div>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.info("No hay integrantes registrados o los datos están vacíos.")

st.divider()

# --- BLOQUE 2: EDITOR CON LIMPIEZA AL GUARDAR ---
with st.expander("⚙️ Configuración: Agregar o Editar Integrantes"):
    # Limpiamos los datos antes de cargarlos en el editor para que no aparezcan filas nulas
    df_equipo = pd.DataFrame(integrantes_validos) if integrantes_validos else pd.DataFrame(columns=["Nombre Completo", "Teléfono", "Correo Electrónico"])

    edited_df = st.data_editor(
        df_equipo,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_compacto",
    )

    if st.button("💾 ACTUALIZAR EQUIPO", type="primary", use_container_width=True):
        # Convertimos a diccionario y eliminamos filas que estén totalmente vacías o sean nulas
        lista_nueva = edited_df.to_dict('records')
        st.session_state['integrantes'] = [r for r in lista_nueva if any(str(v).strip() for v in r.values() if v is not None)]
        
        guardar_datos_nube()
        st.success("¡Equipo actualizado y base de datos limpia!")
        st.rerun()
