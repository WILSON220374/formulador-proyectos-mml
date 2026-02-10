import streamlit as st
from session_state import inicializar_session, conectar_db, cargar_datos_nube

st.set_page_config(page_title="Formulador Proyectos MML", layout="wide")
inicializar_session()

# --- INTERFAZ DE LOGIN ---
if not st.session_state['autenticado']:
    st.title("🏗️ Formulador de Proyectos")
    st.markdown("### Acceso Grupal - Posgrado")
    with st.container(border=True):
        u = st.text_input("Usuario (Grupo)")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True, type="primary"):
            try:
                db = conectar_db()
                # Verificar credenciales en Supabase
                res = db.table("proyectos").select("*").eq("user_id", u).eq("password", p).execute()
                if res.data:
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_id'] = u
                    cargar_datos_nube(u) # Cargar progreso previo
                    st.rerun()
                else:
                    st.error("Usuario o contraseña no válidos.")
            except Exception as e:
                st.error("Error de conexión. Revisa tus Secrets de Supabase.")
    st.stop()

# --- MENÚ DE NAVEGACIÓN ---
with st.sidebar:
    st.write(f"👷 Grupo: **{st.session_state['usuario_id']}**")
    if st.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

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
