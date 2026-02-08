import streamlit as st
from session_state import inicializar_session

# Configuración inicial
st.set_page_config(page_title="Formulador de Proyectos", layout="wide")

# --- ESCUDO ANTI-TRADUCTOR (Previene el error 'removeChild') ---
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

# FASE 1: Diagnóstico (Archivos reales)
pag_1 = st.Page("views/1_diagnostico.py", title="1. Diagnóstico y Zona", icon="📍")

# FASE 2: Interesados
pag_2 = st.Page("views/2_interesados.py", title="2. Análisis de Interesados", icon="👥")

# FASE 3: Matriz de Vester (El que acabamos de crear)
pag_3 = st.Page("views/3_vester.py", title="3. Matriz de Vester", icon="🧮")

# FASES 4-5: Placeholders (Funciones temporales)
def p_objetivos():
    st.title("🌳 Fase 4: Objetivos")
    st.info("Próximamente: Árboles de Objetivos y Alternativas")

def p_mml():
    st.title("📋 Fase 5: Marco Lógico")
    st.info("Próximamente: Matriz de Marco Lógico 4x4")

# --- MENÚ DE NAVEGACIÓN (Aquí estaba el error, ahora está corregido) ---
pg = st.navigation({
    "Fase I: Identificación": [pag_1, pag_2],
    "Fase II: Análisis y Estrategia": [
        pag_3, 
        st.Page(p_objetivos, title="4. Objetivos"),
        st.Page(p_mml, title="5. Marco Lógico")
    ]
})

pg.run()
