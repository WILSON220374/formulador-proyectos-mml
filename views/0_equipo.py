import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia de datos
inicializar_session()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* 1. TARJETAS MÁS GRANDES */
    .ficha-equipo {
        background-color: #f0f5ff;
        border-left: 10px solid #4F8BFF; /* Borde más grueso */
        padding: 20px; /* Más relleno */
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.08);
        height: 160px; /* AUMENTADO DE 120px A 160px */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nombre-mediano {
        font-size: 24px !important; /* AUMENTADO DE 18px A 24px */
        color: #1E3A8A;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    .detalle-pequeno {
        font-size: 15px !important; /* AUMENTADO DE 13px A 15px */
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

    /* Estilo del formulario (más compacto visualmente) */
    div[data-testid="stForm"] {
        border: 1px solid #eee;
        padding: 15px;
        border-radius: 12px;
        background-color: #fafafa;
    }
    
    /* --- HACK PARA DESACTIVAR EL CLICK EN LA IMAGEN --- */
    [data-testid="stImage"] img {
        pointer-events: none;
        user-select: none;
    }
    [data-testid="StyledFullScreenButton"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECCIÓN SUPERIOR: TÍTULO Y TARJETAS (MÁS GRANDES)
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
    # Mantenemos 3 columnas pero el CSS las hace ver más robustas
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
# SECCIÓN INFERIOR: IMAGEN Y FORMULARIO (MÁS PEQUEÑOS Y CENTRADOS)
# ---------------------------------------------------------
# Usamos columnas vacías a los lados (0.5 y 0.5) para "comprimir" el contenido en el centro
col_izq_vacia, col_img, col_form, col_der_vacia = st.columns([0.5, 1.5, 2.5, 0.5])

# --- COLUMNA IMAGEN (Reducida visualmente por las columnas laterales) ---
with col_img:
    st.markdown("<br>", unsafe_allow_html=True) # Un pequeño espacio arriba para alinear
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    else:
        st.info("Logo JC Flow")

# --- COLUMNA FORMULARIO (Reducida visualmente) ---
with col_form:
    st.markdown("##### 📝 Registrar Nuevo Integrante") # Título un poco más pequeño (h5)
    
    with st.form("form_registro", clear_on_submit=True):
        # Campos apilados para que el formulario sea más estrecho y alto, o en columnas compactas
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
