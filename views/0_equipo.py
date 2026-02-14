import streamlit as st
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
    /* Estilo para el formulario limpio */
    div[data-testid="stForm"] {
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 10px;
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- LAYOUT: IMAGEN IZQUIERDA | GESTIÓN DERECHA ---
col_img, col_contenido = st.columns([1, 2], gap="large")

# --- COLUMNA 1: SOLO IMAGEN ---
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.info("Logo JC Flow")

# --- COLUMNA 2: GESTIÓN DE EQUIPO ---
with col_contenido:
    st.markdown('<div class="titulo-principal">Gestión de Equipo</div>', unsafe_allow_html=True)

    # --- BLOQUE 1: FORMULARIO DE REGISTRO (REEMPLAZA A LA TABLA) ---
    st.subheader("📝 Registrar Nuevo Integrante")
    
    with st.form("form_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nuevo_nombre = st.text_input("Nombre Completo *")
            nuevo_tel = st.text_input("Teléfono")
        with c2:
            nuevo_email = st.text_input("Correo Electrónico")
            # Espacio vacío para alinear
            st.write("") 
        
        # Botón de envío que ocupa todo el ancho
        submitted = st.form_submit_button("💾 GUARDAR INTEGRANTE", type="primary", use_container_width=True)
        
        if submitted:
            if nuevo_nombre:
                # Crear el nuevo integrante
                nuevo_integrante = {
                    "Nombre Completo": nuevo_nombre,
                    "Teléfono": nuevo_tel,
                    "Correo Electrónico": nuevo_email
                }
                
                # Agregar a la lista en sesión
                if 'integrantes' not in st.session_state:
                    st.session_state['integrantes'] = []
                
                st.session_state['integrantes'].append(nuevo_integrante)
                
                # Guardar en Supabase inmediatamente
                guardar_datos_nube()
                st.toast(f"✅ {nuevo_nombre} agregado correctamente")
                st.rerun()
            else:
                st.error("⚠️ El nombre es obligatorio.")

    st.divider()

    # --- BLOQUE 2: FICHAS VISUALES (SOLO LECTURA) ---
    st.subheader("👥 Equipo Actual")
    
    integrantes_raw = st.session_state.get('integrantes', [])
    integrantes_validos = [p for p in integrantes_raw if isinstance(p, dict) and p]

    if integrantes_validos:
        # Botón pequeño para borrar el último (por si se equivocan)
        if st.button("↩️ Deshacer último registro", help="Borra el último integrante agregado"):
            st.session_state['integrantes'].pop()
            guardar_datos_nube()
            st.rerun()

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
        st.info("Aún no hay integrantes. Usa el formulario de arriba para registrarte.")
