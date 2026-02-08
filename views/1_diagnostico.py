import streamlit as st

# Título de la Hoja
st.header("1. Diagnóstico del Problema")
st.info("Diligencie la información correspondiente al DIAGNÓSTICO PREVIO")

# Recuperamos el espacio de memoria que creamos en el paso anterior
if 'datos_problema' not in st.session_state:
    st.session_state['datos_problema'] = {}

datos = st.session_state['datos_problema']

# --- FORMULARIO DE DIAGNÓSTICO ---
with st.form("form_diagnostico"):
    # Pregunta 1
    st.markdown("### 1. ¿En qué consiste la situación problema?")
    problema = st.text_area(
        "Describa la carencia o déficit principal:",
        value=datos.get('problema_central', ""),
        height=100,
        placeholder="Ejemplo: Mal estado de la vía que comunica..."
    )

    col1, col2 = st.columns(2)
    
    with col1:
        # Pregunta 2
        st.markdown("### 2. ¿Cómo se manifiesta?")
        sintomas = st.text_area(
            "Síntomas y efectos visibles:",
            value=datos.get('sintomas', ""),
            height=150
        )

    with col2:
        # Pregunta 3
        st.markdown("### 3. Causas Inmediatas")
        causas = st.text_area(
            "¿Cuáles son las causas directas?",
            value=datos.get('causas_inmediatas', ""),
            height=150
        )

    # Pregunta 4
    st.markdown("### 4. Factores Agravantes")
    agravantes = st.text_area(
        "¿Qué otros factores empeoran la situación?",
        value=datos.get('factores_agravantes', "")
    )

    # Botón de Guardado
    guardar = st.form_submit_button("💾 Guardar Diagnóstico")

    if guardar:
        # Guardamos en la memoria del sistema
        st.session_state['datos_problema']['problema_central'] = problema
        st.session_state['datos_problema']['sintomas'] = sintomas
        st.session_state['datos_problema']['causas_inmediatas'] = causas
        st.session_state['datos_problema']['factores_agravantes'] = agravantes
        st.success("✅ Diagnóstico guardado correctamente.")
