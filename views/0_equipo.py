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
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nombre-mediano {
        font-size: 18px !important;
        color: #1E3A8A;
        font-weight: bold;
        line-height: 1.1;
        margin-bottom: 5px;
    }
    .detalle-pequeno {
        font-size: 13px !important;
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
    div[data-testid="stForm"] {
        border: 1px solid #eee;
        padding: 20px;
        border-radius: 10px;
        background-color: #fafafa;
    }
    
    /* --- HACK DEFINITIVO PARA DESACTIVAR EL CLICK EN LA IMAGEN --- */
    /* Esto hace que la imagen ignore el ratón, evitando que se agrande */
    [data-testid="stImage"] img {
        pointer-events: none;
        user-select: none;
    }
    /* Ocultamos también el botón por si acaso */
    [data-testid="StyledFullScreenButton"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECCIÓN SUPERIOR: TÍTULO Y TARJETAS (Ancho Completo)
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
    st.info("No hay equipo registrado aún. Usa el formulario de abajo.")

st.divider()

# ---------------------------------------------------------
# SECCIÓN INFERIOR: IMAGEN (IZQ) vs FORMULARIO (DER)
# ---------------------------------------------------------
col_img, col_form = st.columns([1, 1.5], gap="large")

# --- COLUMNA 1: IMAGEN (ESTÁTICA, NO CLICKEABLE) ---
with col_img:
    st.write("") 
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.info("Logo JC Flow")

# --- COLUMNA 2: FORMULARIO DE REGISTRO ---
with col_form:
    st.markdown("### 📝 Registrar Nuevo Integrante")
    
    with st.form("form_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nuevo_nombre = st.text_input("Nombre Completo *")
            nuevo_tel = st.text_input("Teléfono")
        with c2:
            nuevo_email = st.text_input("Correo Electrónico")
            st.write("") 
        
        submitted = st.form_submit_button("💾 GUARDAR INTEGRANTE", type="primary", use_container_width=True)
        
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
                st.error("⚠️ El nombre es obligatorio.")
