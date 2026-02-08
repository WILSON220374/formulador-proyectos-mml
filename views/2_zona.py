import streamlit as st

st.header("2. Caracterización de la Zona de Estudio")
st.info("Ingrese los datos correspondientes a la hoja 'DESCRIPCIÓN GENERAL DE LA ZONA'.")

# Recuperar memoria
if 'datos_zona' not in st.session_state:
    st.session_state['datos_zona'] = {}

datos = st.session_state['datos_zona']

with st.form("form_zona"):
    # --- SECCIÓN 1: POBLACIÓN ---
    st.subheader("👥 Análisis de Población")
    c1, c2, c3 = st.columns(3)
    pob_total = c1.number_input("Población Total", min_value=0, value=datos.get('pob_total', 0))
    pob_urbana = c2.number_input("Urbana", min_value=0, value=datos.get('pob_urbana', 0))
    pob_rural = c3.number_input("Rural", min_value=0, value=datos.get('pob_rural', 0))

    # --- SECCIÓN 2: TERRITORIO ---
    st.divider()
    st.subheader("🗺️ Territorio y Geografía")
    
    ubicacion = st.text_input("Ubicación exacta del problema:", value=datos.get('ubicacion', ""))
    
    col_a, col_b = st.columns(2)
    with col_a:
        limites = st.text_area("Límites Geográficos:", value=datos.get('limites', ""), height=100)
    with col_b:
        economia = st.text_area("Principal Actividad Económica:", value=datos.get('economia', ""), height=100)

    # --- SECCIÓN 3: ACCESIBILIDAD ---
    st.divider()
    st.subheader("🛣️ Accesibilidad")
    vias = st.text_area("Estado de vías y transporte:", value=datos.get('vias', ""))

    # Guardar
    if st.form_submit_button("💾 Guardar Datos de la Zona"):
        st.session_state['datos_zona']['pob_total'] = pob_total
        st.session_state['datos_zona']['pob_urbana'] = pob_urbana
        st.session_state['datos_zona']['pob_rural'] = pob_rural
        st.session_state['datos_zona']['ubicacion'] = ubicacion
        st.session_state['datos_zona']['limites'] = limites
        st.session_state['datos_zona']['economia'] = economia
        st.session_state['datos_zona']['vias'] = vias
        st.success("✅ Información de la zona guardada.")
