import streamlit as st
import os
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- PURIFICACIÓN DE RAÍZ ---
if 'integrantes' in st.session_state and isinstance(st.session_state['integrantes'], list):
    st.session_state['integrantes'] = [p for p in st.session_state['integrantes'] if p is not None and isinstance(p, dict)]

# --- ESTILOS CSS GLOBALES (SOLO TÍTULOS DE FASE EN NEGRILLA) ---
st.markdown("""
    <style>
    /* Selecciona específicamente los títulos de las secciones en el menú lateral */
    div[data-testid="stSidebarNavItems"] > ul > li > div > span {
        font-weight: 900 !important;
        color: #1E3A8A !important;
        font-size: 14px !important;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE ACCESO (LOGIN) - IMAGEN IZQUIERDA / FORMULARIO DERECHA ---
if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        .titulo-acceso { 
            font-size: 32px !important; 
            font-weight: 800 !important; 
            color: #1E3A8A;
            margin-bottom: 2px;
        }
        .subtitulo-acceso {
            font-size: 16px !important;
            color: #666;
            margin-bottom: 25px;
        }
        div[data-testid="stForm"] {
            border: 1px solid #e0e7ff !important;
            padding: 30px !important;
            border-radius: 15px !important;
            background-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

    col_img, col_login = st.columns([1.2, 1], gap="large")
    
    with col_img:
        st.write("") # Espaciador
        if os.path.exists("unnamed.jpg"):
            st.image("unnamed.jpg", use_container_width=True)
        else:
            st.info("Logo JCFlow")

    with col_login:
        st.markdown('<p class="titulo-acceso">Asistente JCFlow</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitulo-acceso">Gestión de proyectos bajo Metodología de Marco Lógico.</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_id = st.text_input("ID del Proyecto", placeholder="Ingrese el código de su grupo...")
            btn_acceder = st.form_submit_button("INGRESAR AL SISTEMA", type="primary", use_container_width=True)
            
            if btn_acceder:
                if user_id:
                    st.session_state['usuario_id'] = user_id
                    cargar_datos_nube()
                    st.session_state['autenticado'] = True
                    st.rerun()
                else:
                    st.error("Por favor, ingrese un ID válido.")
    st.stop()

# --- SIDEBAR (CONFIGURACIÓN Y CERRAR SESIÓN) ---
with st.sidebar:
    st.markdown(f"### 🚀 Proyecto: **{st.session_state.get('usuario_id', 'N/A')}**")
    st.write("---")
    if st.button("💾 Sincronizar Nube", use_container_width=True, type="primary"):
        guardar_datos_nube()
        st.toast("✅ Avance guardado", icon="🚀")
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

# --- DEFINICIÓN DE PÁGINAS POR SECCIONES ---
pg = st.navigation({
    "Configuración": [
        st.Page("views/0_equipo.py", title="Equipo", icon="👥")
    ],
    "Fase I: Identificación": [
        st.Page("views/1_diagnostico.py", title="1. Diagnóstico", icon="🧐"),
        st.Page("views/2_zona.py", title="2. Zona de Estudio", icon="🗺️"),
        st.Page("views/3_interesados.py", title="3. Interesados", icon="👥"),
    ],
    "Fase II: Definición de problemas y objetivos": [
        st.Page("views/4_arbol_problemas.py", title="4. Árbol de Problemas", icon="🌳"),
        st.Page("views/5_arbol_objetivos.py", title="5. Árbol de Objetivos", icon="🎯"),
        st.Page("views/6_alternativas.py", title="6. Análisis de Alternativas", icon="⚖️"),
        st.Page("views/7_arbol_objetivos_final.py", title="7. Árbol de Objetivos Final", icon="✅"),
        st.Page("views/8_arbol_problemas_final.py", title="8. Árbol de Problemas Final", icon="📉"),
    ],
    "Fase III: Estructuración": [
        st.Page("views/9_descripcion_zona.py", title="9. Descripción de la Zona", icon="🏘️"),
        st.Page("views/10_descripcion_problema.py", title="10. Descripción del Problema", icon="📝"),
    ],
    "Fase IV: Análisis de Objetivos": [
        st.Page("views/11_indicadores.py", title="11. Indicadores", icon="📈"),
    ]
})

pg.run()
