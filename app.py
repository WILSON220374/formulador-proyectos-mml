import streamlit as st
from session_state import inicializar_session

# Configuración inicial
st.set_page_config(page_title="Formulador de Proyectos MML", layout="wide")

# Escudo anti-traductor
st.markdown("""<meta name="google" content="notranslate">""", unsafe_allow_html=True)

# Inicializar memoria
inicializar_session()

# --- NAVEGACIÓN ---
pg = st.navigation({
    "Fase I: Identificación": [
        st.Page("views/1_diagnostico.py", title="1. Diagnóstico", icon="🧐"),
        st.Page("views/2_zona.py", title="2. Zona de Estudio", icon="🗺️"),
        st.Page("views/3_interesados.py", title="3. Interesados", icon="👥"),
    ],
    "Fase II: Análisis": [
        st.Page("views/4_arbol_problemas.py", title="4. Árbol de Problemas", icon="🌳"),
        st.Page("views/5_arbol_objetivos.py", title="5. Árbol de Objetivos", icon="🎯"),
    ]
})

pg.run()
