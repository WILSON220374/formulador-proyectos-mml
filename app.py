import streamlit as st
import os
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Acceso", layout="wide")
inicializar_session()

# --- LÓGICA DE ACCESO (LOGIN) ---
if not st.session_state['autenticado']:
    
    st.markdown("""
        <style>
        /* 1. LAS ETIQUETAS (Usuario y Contraseña) - ¡ESTO ES LO QUE BUSCABAS! */
        div[data-testid="stWidgetLabel"] p {
            font-size: 30px !important; /* Tamaño de la palabra Usuario/Contraseña */
            font-weight: bold !important;
            color: #1E3A8A !important;
            margin-bottom: 10px !important;
        }

        /* 2. EL TEXTO DENTRO DE LOS CUADROS */
        input[data-testid="stWidgetInputElement"] {
            font-size: 26px !important; /* Tamaño de lo que el usuario escribe */
            height: 70px !important;   /* Cuadro más alto */
        }

        /* 3. EL TÍTULO AZUL */
        .titulo-acceso {
            font-size: 45px !important;
            font-weight: 800 !important;
            color: #4F8BFF;
            text-align: center;
            margin-top: 15px;
            margin-bottom: 15px;
        }

        /* 4. EL BOTÓN DE INGRESO */
        .stButton button {
            font-size: 30px !important;
            height: 3.5em !important;
            background-color: #4F8BFF !important;
            font-weight: bold !important;
            margin-top: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if os.path.exists("unnamed.jpg"):
            st.image("unnamed.jpg", use_container_width=True)
        else:
            st.title("🏗️ JC Flow")
            
        st.markdown('<div class="titulo-acceso">Acceso Grupal - Posgrado</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            # Aquí el sistema usará las reglas de arriba para que se vean GIGANTES
            u = st.text_input("Usuario (Grupo)")
            p = st.text_input("Contraseña", type="password")
            
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
                        st.error("Credenciales incorrectas.")
                except Exception as e:
                    st.error("Error de conexión.")
    st.stop()

# --- CONTINUACIÓN DEL CÓDIGO (Navegación y Sidebar) ---
# (Aquí va el resto de tu código de navegación que ya tienes funcionando)
