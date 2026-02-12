import streamlit as st
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- LÓGICA DE ACCESO (LOGIN) ---
if not st.session_state['autenticado']:
    # Centrado del Logo y Títulos
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Mostramos el logo cargado
        st.image("unnamed.jpg", use_container_width=True)
        st.markdown("<h2 style='text-align: center; color: #4F8BFF;'>Acceso Grupal - Posgrado</h2>", unsafe_allow_html=True)
        
        # Contenedor del formulario de ingreso
        with st.container(border=True):
            u = st.text_input("Usuario (Grupo)")
            p = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar al Sistema", use_container_width=True, type="primary"):
                try:
                    db = conectar_db()
                    # Verificar credenciales en Supabase
                    res = db.table("proyectos").select("*").eq("user_id", u).eq("password", p).execute()
                    if res.data:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_id'] = u
                        cargar_datos_nube(u) # Recuperar avance previo
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
                except Exception as e:
                    st.error("Error de conexión. Revisa tus Secrets de Supabase.")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header(f"👷 {st.session_state['usuario_id']}")
    
    # Visualización en forma de lista de los integrantes
    integrantes = st.session_state.get('integrantes', [])
    if integrantes:
        for persona in integrantes:
            nombre_full = persona.get("Nombre Completo", "").strip()
            if nombre_full:
                nombre_pila = nombre_full.split()[0].upper()
                st.markdown(f"**👤 {nombre_pila}**")
            
    st.divider()
    
    if st.button("☁️ GUARDAR TODO EN NUBE", use_container_width=True, type="primary"):
        with st.spinner("Sincronizando..."):
            guardar_datos_nube()
            st.toast("✅ ¡Todo tu avance ha sido guardado!", icon="🚀")
    
    st.divider()
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

# --- NAVEGACIÓN ---
pg = st.navigation({
    "Configuración": [
        st.Page("views/0_equipo.py", title="Equipo", icon="👥"),
    ],
    "Fase I: Identificación": [
        st.Page("views/1_diagnostico.py", title="1. Diagnóstico", icon="🧐"),
        st.Page("views/2_zona.py", title="2. Zona de Estudio", icon="🗺️"),
        st.Page("views/3_interesados.py", title="3. Interesados", icon="👥"),
    ],
    "Fase II: Análisis": [
        st.Page("views/4_arbol_problemas.py", title="4. Árbol de Problemas", icon="🌳"),
        st.Page("views/5_arbol_objetivos.py", title="5. Árbol de Objetivos", icon="🎯"),
        st.Page("views/6_alternativas.py", title="6. Análisis de Alternativas", icon="⚖️"),
        st.Page("views/7_arbol_objetivos_final.py", title="7. Árbol de Objetivos Final", icon="🚀"),
        st.Page("views/8_arbol_problemas_final.py", title="8. Árbol de Problemas Final", icon="🌳"),
    ]
})

pg.run()
