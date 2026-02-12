import streamlit as st
import os # <--- IMPORTANTE: Esta línea es clave para que la app no se rompa
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- LÓGICA DE ACCESO (LOGIN) ---
if not st.session_state['autenticado']:
    
    # ESTILOS CSS PARA EL ACCESO GIGANTE
    st.markdown("""
        <style>
        /* Título central */
        .titulo-acceso { font-size: 45px !important; font-weight: 800 !important; color: #4F8BFF; text-align: center; margin-bottom: 20px; }
        
        /* Nuestras nuevas etiquetas manuales */
        .label-grande { font-size: 32px !important; font-weight: bold; color: #1E3A8A; margin-top: 20px; margin-bottom: 5px; }
        
        /* Texto dentro de los cuadros */
        input { font-size: 26px !important; height: 75px !important; }
        
        /* Botón de ingreso */
        .stButton button { font-size: 32px !important; height: 3.5em !important; font-weight: bold !important; margin-top: 30px; background-color: #4F8BFF !important; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Validación de seguridad para el logo
        if os.path.exists("unnamed.jpg"):
            st.image("unnamed.jpg", use_container_width=True)
        else:
            st.title("🏗️ JC Flow")
            
        st.markdown('<div class="titulo-acceso">Acceso Grupal - Posgrado</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            # SOLUCIÓN: Usamos etiquetas manuales y ocultamos las originales
            st.markdown('<p class="label-grande">USUARIO (GRUPO)</p>', unsafe_allow_html=True)
            u = st.text_input("u", label_visibility="collapsed")
            
            st.markdown('<p class="label-grande">CONTRASEÑA</p>', unsafe_allow_html=True)
            p = st.text_input("p", type="password", label_visibility="collapsed")
            
            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
                try:
                    db = conectar_db()
                    res = db.table("proyectos").select("*").eq("user_id", u).eq("password", p).execute()
                    if res.data:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_id'] = u
                        cargar_datos_nube(u)
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas. Verifique usuario y contraseña.")
                except Exception as e:
                    st.error("Error de conexión con la base de datos.")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header(f"👷 {st.session_state['usuario_id']}")
    
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
    "Configuración": [st.Page("views/0_equipo.py", title="Equipo", icon="👥")],
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
