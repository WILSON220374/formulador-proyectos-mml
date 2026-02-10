import streamlit as st
from session_state import inicializar_session

# Configuración inicial de la página
st.set_page_config(page_title="Formulador de Proyectos MML", layout="wide")

# Escudo anti-traductor para evitar errores de interfaz
st.markdown("""<meta name="google" content="notranslate">""", unsafe_allow_html=True)

# Inicializar variables de memoria (session_state)
inicializar_session()

# --- NAVEGACIÓN ---
# Se define la estructura del menú lateral
pg = st.navigation({
    "Inicio": [
        # Nueva página para guardar y cargar archivos .json
        st.Page("views/0_proyecto.py", title="Gestión de Proyecto", icon="📁"),
    ],
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

# Ejecutar la navegación
pg.run()
