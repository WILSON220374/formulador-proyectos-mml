import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia de datos
inicializar_session()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* 1. TARJETAS MÁS GRANDES Y ROBUSTAS */
    .ficha-equipo {
        background-color: #f0f5ff;
        border-left: 10px solid #4F8BFF;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.08);
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nombre-mediano {
        font-size: 24px !important;
        color: #1E3A8A;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    .detalle-pequeno {
        font-size: 15px !important;
        color: #555;
        margin-bottom: 4px;
    }
    
    .titulo-principal {
        font-size: 42px !important; 
        font-weight: 800 !important; 
        color: #4F8BFF;
        text-align: left;
        margin-bottom: 25px;
    }

    /* Estilo del formulario (Alineado y limpio) */
    div[data-testid="stForm"] {
        border: 1px solid #eee;
        padding: 20px;
        border-radius: 12px;
        background-color: #fafafa;
        margin-top: 0px; /* Asegura que empiece arriba */
    }
    
    /* --- HACK PARA IMAGEN ESTÁTICA --- */
    [data-testid="stImage"] img {
        pointer-events: none;
        user-select: none;
        border-radius: 15px; /* Bordes redondeados para que combine */
    }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECCIÓN SUPERIOR: TÍTULO Y TARJETAS
# ---------------------------------------------------------
st.markdown('<div class="titulo-principal">Gestión de Equipo</div>', unsafe_allow_html=True)

col_titulo, col_btn = st.columns([4, 1])
with col_titulo:
    st.subheader("👥 Miembros Registrados")
with col_btn:
    if st.button("↩️ Deshacer último", help="Borra el registro más reciente"):
        if st.session_state.get('integrantes'):
            st.session_state['integrantes'].pop()
            guardar_datos_nube()
            st.rerun()

integrantes_raw = st.session_state.get('integrantes', [])
integrantes_validos = [p for p in integrantes_raw if isinstance(p, dict) and p]

if integrantes_validos:
    cols = st.columns(3) 
    for idx, persona in enumerate(integrantes_validos):
        with cols[idx % 3]: 
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
    st.info("No hay equipo registrado aún.")

st.divider()

# ---------------------------------------------------------
# SECCIÓN INFERIOR: ALINEACIÓN PERFECTA (IMAGEN vs FORMULARIO)
# ---------------------------------------------------------

# Usamos columnas de relleno (0.6) a los extremos para centrar todo el bloque
# Proporción central: Imagen (1.3) vs Formulario (2.2)
col_izq_vacia, col_img, col_form, col_der_vacia = st.columns([0.6, 1.3, 2.2, 0.6], gap="medium")

# --- COLUMNA IMAGEN ---
with col_img:
    # Ajuste fino: Un pequeño espacio vacío para bajar la imagen y alinear su centro con el formulario
    st.write("") 
    st.write("") 
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.info("Logo JC Flow")

# --- COLUMNA FORMULARIO ---
with col_form:
    st.markdown("##### 📝 Registrar Nuevo Integrante")
    
    with st.form("form_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nuevo_nombre = st.text_input("Nombre *")
            nuevo_tel = st.text_input("Teléfono")
        with c2:
            nuevo_email = st.text_input("Email")
            st.write("") 
        
        submitted = st.form_submit_button("💾 GUARDAR", type="primary", use_container_width=True)
        
        if submitted:
            if nuevo_nombre:
                nuevo_integrante = {
                    "Nombre Completo": nuevo_nombre,
                    "Teléfono": nuevo_tel,
                    "Correo Electrónico": nuevo_email
                }
                
                if 'integrantes' not in st.session_state:
                    st.session_state['integrantes'] = []
                
                st.session_state['integrantes'].append(nuevo_integrante)
                guardar_datos_nube()
                st.toast(f"✅ {nuevo_nombre} agregado correctamente")
                st.rerun()
            else:
                st.error("⚠️ Nombre obligatorio.")
