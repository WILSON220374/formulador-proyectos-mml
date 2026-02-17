import streamlit as st
from session_state import inicializar_session

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="JCFlow - Formulador de Proyectos", layout="wide")

# Inicializamos la sesión globalmente
inicializar_session()

# --- DEFINICIÓN DE PÁGINAS ---
# Configuración
p_equipo = st.Page("views/0_equipo.py", title="Equipo de Trabajo", icon="👥")
p_proyecto = st.Page("views/0_proyecto.py", title="Datos del Proyecto", icon="📁")

# Fase I
p_diagnostico = st.Page("views/1_diagnostico.py", title="1. Diagnóstico", icon="🎯")
p_zona = st.Page("views/2_zona.py", title="2. Zona de Estudio", icon="🗺️")
p_interesados = st.Page("views/3_interesados.py", title="3. Interesados", icon="🤝")

# Fase II
p_arbol_p = st.Page("views/4_arbol_problemas.py", title="4. Árbol de Problemas", icon="🌳")
p_arbol_o = st.Page("views/5_arbol_objetivos.py", title="5. Árbol de Objetivos", icon="🎯")
p_alternativas = st.Page("views/6_alternativas.py", title="6. Alternativas", icon="⚖️")

# Fase III
p_obj_fin = st.Page("views/7_arbol_objetivos_final.py", title="7. Objetivos Final", icon="✅")
p_prob_fin = st.Page("views/8_arbol_problemas_final.py", title="8. Problemas Final", icon="🌲")
p_desc_zona = st.Page("views/9_descripcion_zona.py", title="9. Desc. Zona", icon="📍")
p_desc_prob = st.Page("views/10_descripcion_problema.py", title="10. Desc. Problema", icon="📝")

# --- NAVEGACIÓN ACTUALIZADA ---
pg = st.navigation({
    "Configuración": [p_equipo, p_proyecto],
    "Fase I: Identificación": [p_diagnostico, p_zona, p_interesados],
    "Fase II: Definición de problemas y objetivos": [p_arbol_p, p_arbol_o, p_alternativas],
    "Fase III: Análisis del problema": [p_obj_fin, p_prob_fin, p_desc_zona, p_desc_prob]
})

pg.run()
