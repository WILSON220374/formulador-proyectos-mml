import streamlit as st
import os
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- LÓGICA DE ACCESO (LOGIN) ---
if not st.session_state['autenticado']:
    
    # ESTILOS CSS REFORZADOS
    st.markdown("""
        <style>
        .titulo-acceso { font-size: 45px !important; font-weight: 800 !important; color: #4F8BFF; text-align: center; margin-bottom: 20px; }
        .label-grande { font-size: 32px !important; font-weight: bold; color: #1E3A8A; margin-top: 20px; margin-bottom: 5px; }
        
        /* 1. TEXTO CENTRADO Y GRANDE EN LOS CUADROS */
        input { 
            font-size: 32px !important; 
            height: 80px !important; 
            text-align: center !important; /* <--- ESTO CENTRA EL TEXTO QUE DIGITAN */
        }
        
        /* 2. BOTÓN CON TEXTO GIGANTE E IMPACTANTE */
        div.stButton > button { 
            font-size: 42px !important; /* <--- TEXTO MUCHO MÁS GRANDE */
            height: 2.5em !important; 
            font-weight: 900 !important; 
            margin-top: 30px; 
            background-color: #4F8BFF !important; 
            color: white !important;
            border-radius: 20px !important;
        }

        /* 3. MENSAJE DE ERROR MÁS CLARO */
        .stAlert p { font-size: 22px !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Validación del logo JC Flow
        if os.path.exists("unnamed.jpg"):
            st.image("unnamed.jpg", use_container_width=True)
        else:
            st.title("🏗️ JC Flow")
            
        st.markdown('<div class="titulo-acceso">Acceso Grupal - Posgrado</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            # Campos con etiquetas manuales gigantes
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
                    st.error("Error de conexión. Revisa tus Secrets de Supabase.")
    st.stop()

# --- CONTINUACIÓN DEL CÓDIGO (SideBar y Navegación) ---
# ... (Mantiene tu lógica de integrantes y páginas del Paso 1 al 8)
