import streamlit as st
from session_state import inicializar_session

# 1. Configuración inicial
st.set_page_config(page_title="Formulación de Proyectos", layout="wide")

# 2. Cargar memoria (OBLIGATORIO antes de cualquier cosa)
inicializar_session()

# 3. Definir páginas vacías por ahora (Placeholders)
def pag_diagnostico():
    st.title("📍 1. Diagnóstico")
    st.info("Aquí irán los formularios de la hoja 'DIAGNÓSTICO PREVIO'")
    # Prueba de memoria para ver si funciona
    nombre = st.text_input("Nombre del Proyecto", value=st.session_state['datos_proyecto']['nombre'])
    st.session_state['datos_proyecto']['nombre'] = nombre

def pag_interesados():
    st.title("👥 2. Interesados")
    st.write("Matriz de análisis de involucrados")

def pag_vester():
    st.title("🧮 3. Matriz de Vester")
    st.write("Análisis de problemas activos y pasivos")

def pag_arboles():
    st.title("🌳 4. Árboles")
    st.write("Árbol de Problemas y Objetivos")

def pag_mml():
    st.title("📋 5. Marco Lógico")
    st.write("Matriz 4x4 final")

# 4. Crear el menú de navegación lateral
pg = st.navigation({
    "Fase I: Identificación":,
    "Fase II: Planificación": [
        st.Page(pag_mml, title="Matriz de Marco Lógico"),
    ]
})

pg.run()
