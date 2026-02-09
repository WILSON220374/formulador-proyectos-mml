import streamlit as st
from session_state import inicializar_session

# Configuración inicial
st.set_page_config(page_title="Formulador de Proyectos", layout="wide")

# --- ESCUDO ANTI-TRADUCTOR ---
st.markdown(
    """
    <meta name="google" content="notranslate">
    <style>
    .goog-te-banner-frame {display: none!important;}
        body {translate: no!important;}
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializar memoria
inicializar_session()

# --- DEFINICIÓN DE PÁGINAS ---

# FASE 1: Identificación (Archivos reales)
pag_1 = st.Page("views/1_diagnostico.py", title="1. Diagnóstico del Problema", icon="🤕")
pag_2 = st.Page("views/2_zona.py", title="2. Caracterización de la Zona", icon="🗺️")
# CORRECCIÓN: Ahora apunta al archivo físico en la carpeta views
pag_3 = st.Page("views/3_interesados.py", title="3. Interesados", icon="👥")

# FASES SIGUIENTES (Placeholders para las que aún no tienen archivo .py)
def p_vester():
    st.title("🧮 4. Matriz de Vester")
    st.info("🚧 Próximamente: Votación automática.")

def p_arboles():
    st.title("🌳 5. Árboles")
    st.info("🚧 Próximamente: Diagramas.")

def p_mml():
    st.title("📋 6. Marco Lógico")
    st.info("🚧 Próximamente: Matriz.")

# --- MENÚ DE NAVEGACIÓN ---
pg = st.navigation({
    "Fase I: Identificación": [
        pag_1, 
        pag_2, 
        pag_3  # Cargando el archivo real corregido
    ],
    "Fase II: Análisis y Estrategia": [
        st.Page(p_vester, title="4. Matriz de Vester", icon="🧮"),
        st.Page(p_arboles, title="5. Árboles", icon="🌳"),
        st.Page(p_mml, title="6. Marco Lógico", icon="📋")
    ]
})

pg.run()
