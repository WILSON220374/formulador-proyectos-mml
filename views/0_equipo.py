import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia de datos
inicializar_session()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .ficha-equipo {
        background-color: #f0f5ff;
        border-left: 8px solid #4F8BFF;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nombre-mediano {
        font-size: 22px !important;
        color: #1E3A8A;
        font-weight: bold;
        line-height: 1.1;
        margin-bottom: 5px;
    }
    .detalle-pequeno {
        font-size: 14px !important;
        color: #555;
        margin-bottom: 2px;
    }
    .titulo-principal {
        font-size: 38px !important; 
        font-weight: 800 !important; 
        color: #4F8BFF;
        text-align: left;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- LAYOUT: IMAGEN IZQUIERDA | GESTIÓN DERECHA ---
col_img, col_contenido = st.columns([1, 2], gap="large")

# --- COLUMNA 1: SOLO IMAGEN (Sin textos extra) ---
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.info("Logo JC Flow")

# --- COLUMNA 2: GESTIÓN DE EQUIPO ---
with col_contenido:
    st.markdown('<div class="titulo-principal">Gestión de Equipo</div>', unsafe_allow_html=True)

    # --- BLOQUE 1: FICHAS VISUALES (Tus tarjetas azules) ---
    integrantes_raw = st.session_state.get('integrantes', [])
    integrantes_validos = [p for p in integrantes_raw if isinstance(p, dict) and p]

    if integrantes_validos:
        # Usamos 2 columnas internas para organizar las tarjetas
        cols = st.columns(2) 
        for idx, persona in enumerate(integrantes_validos):
            with cols[idx % 2]: 
                try:
                    nombre_raw = persona.get("Nombre Completo") or "SIN NOMBRE"
                    nombre = str(nombre_raw).upper()
                    tel = persona.get("Teléfono") or "N/A"
                    email = persona.get("Correo Electrónico") or "N/A"
                    
                    st.markdown(f"""
                        <div class="ficha-equipo">
                            <div class="nombre-mediano">👤 {nombre}</div>
                            <div class="detalle-pequeno">📞 {tel}</div>
                            <div class="detalle-pequeno">✉️ {email}</div>
                        </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    continue
    else:
        st.info("No hay integrantes registrados aún.")

    st.divider()

    # --- BLOQUE 2: EDITOR (Tu tabla funcional) ---
    st.subheader("⚙️ Agregar o Editar Integrantes")
    
    columnas_orden = ["Nombre Completo", "Teléfono", "Correo Electrónico"]
    
    if integrantes_validos:
        df_equipo = pd.DataFrame(integrantes_validos)
        for col in columnas_orden:
            if col not in df_equipo.columns:
                df_equipo[col] = ""
        df_equipo = df_equipo.reindex(columns=columnas_orden)
    else:
        df_equipo = pd.DataFrame(columns=columnas_orden)

    edited_df = st.data_editor(
        df_equipo,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_compacto",
    )

    if st.button("💾 GUARDAR CAMBIOS", type="primary", use_container_width=True):
        if edited_df is not None:
            lista_nueva = edited_df.to_dict('records')
            # Limpiamos filas vacías
            st.session_state['integrantes'] = [
                r for r in lista_nueva 
                if r and any(str(v).strip() for v in r.values() if v is not None)
            ]
            
            guardar_datos_nube()
            st.toast("✅ Equipo actualizado correctamente")
            st.rerun()
