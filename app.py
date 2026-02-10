import streamlit as st
from session_state import inicializar_session
import yaml # Para manejar las claves si usas un archivo local, o conectar a DB

# 1. Configuración de página
st.set_page_config(page_title="Formulador MML - Acceso Profesional", layout="wide")

# 2. Inicializar memoria base
inicializar_session()

# --- LÓGICA DE AUTENTICACIÓN ---
# Aquí es donde verificaríamos contra la Base de Datos
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    # PANTALLA DE LOGIN
    st.title("🏗️ Acceso al Formulador de Proyectos")
    with st.container(border=True):
        usuario = st.text_input("Usuario (Grupo/Correo)")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", type="primary", use_container_width=True):
            # Aquí pondremos la validación real con la base de datos más adelante
            if usuario == "grupo1" and password == "civil2026": # Ejemplo simple
                st.session_state['autenticado'] = True
                st.session_state['usuario_id'] = usuario
                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    
    st.info("Consulte con su profesor para obtener las credenciales de su grupo.")
    st.stop() # Detiene la ejecución aquí si no hay login

# --- SI ESTÁ AUTENTICADO, MOSTRAR LA APP ---
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

st.sidebar.write(f"👤 Conectado como: **{st.session_state['usuario_id']}**")

# Tu navegación actual
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
