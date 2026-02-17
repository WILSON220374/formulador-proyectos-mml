import streamlit as st
from session_state import inicializar_session

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="JCFlow - Formulador de Proyectos", layout="wide")

# Inicializamos la sesión globalmente
inicializar_session()

# --- DEFINICIÓN DE PÁGINAS (VOLUMEN 1: IDENTIFICACIÓN Y PERFIL) ---
# Módulo 0: Configuración Inicial
intro = st.Page("views/0_proyecto.py", title="Datos del Proyecto", icon="📁")
p_team = st.Page("views/0_equipo.py", title="Equipo de Trabajo", icon="👥")

# Módulo 1: Diagnóstico y Situación Actual
p1 = st.Page("views/1_diagnostico.py", title="1. Diagnóstico", icon="jh")
p2 = st.Page("views/2_zona.py", title="2. Zona de Estudio", icon="🗺️")
p3 = st.Page("views/3_interesados.py", title="3. Interesados", icon="🤝")

# Módulo 2: Estructuración del Problema y Objetivos
p4 = st.Page("views/4_arbol_problemas.py", title="4. Árbol de Problemas", icon="🌳")
p5 = st.Page("views/5_arbol_objetivos.py", title="5. Árbol de Objetivos", icon="🎯")
p6 = st.Page("views/6_alternativas.py", title="6. Alternativas", icon="⚖️")

# Módulo 3: Definición Técnica (El "Corazón" de la MML)
p7 = st.Page("views/7_arbol_objetivos_final.py", title="7. Objetivos Final", icon="✅")
p8 = st.Page("views/8_arbol_problemas_final.py", title="8. Problemas Final", icon="🌲")
p9 = st.Page("views/9_descripcion_zona.py", title="9. Desc. Zona", icon="📍")
p10 = st.Page("views/10_descripcion_problema.py", title="10. Desc. Problema", icon="📝")

# --- NAVEGACIÓN Y RUTAS ---
pg = st.navigation({
    "Configuración": [intro, p_team],
    "Fase I: Identificación": [p1, p2, p3],
    "Fase II: Definición de problemas y objetivos": [p4, p5, p6],
    "Fase III: Análisis del problema": [p7, p8, p9, p10]
})

pg.run()
