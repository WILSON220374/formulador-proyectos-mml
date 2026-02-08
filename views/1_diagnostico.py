import streamlit as st
from session_state import inicializar_session

# Configuración inicial
st.set_page_config(page_title="Formulador de Proyectos", layout="wide")
inicializar_session()

# --- DEFINICIÓN DE PÁGINAS ---

# FASE 1: Archivo real que acabamos de crear
pag_1 = st.Page("views/1_diagnostico.py", title="1. Diagnóstico y Zona", icon="📍")

# FASES 2-5: Funciones "Placeholder" (las iremos reemplazando por archivos reales paso a paso)
def p_interesados():
    st.title("👥 Fase 2: Interesados")
    st.info("Próximamente: Matriz de Interesados y Estrategias")

def p_analisis():
    st.title("🧮 Fase 3: Análisis del Problema")
    st.info("Próximamente: Matriz de Vester y Árbol de Problemas")

def p_objetivos():
    st.title("🌳 Fase 4: Objetivos y Alternativas")
    st.info("Próximamente: Árbol de Objetivos y Selección")

def p_mml():
    st.title("📋 Fase 5: Marco Lógico")
    st.info("Próximamente: Matriz 4x4 completa")

# --- MENÚ DE NAVEGACIÓN ---
pg = st.navigation({
    "Fase I: Identificación": [pag_1],
    "Fase II: Formulación": [
        st.Page(p_interesados, title="2. Interesados"),
        st.Page(p_analisis, title="3. Problemas (Vester)"),
        st.Page(p_objetivos, title="4. Objetivos"),
        st.Page(p_mml, title="5. Marco Lógico")
    ]
})

pg.run()
