import streamlit as st
import os
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- LÓGICA DE ACCESO (LOGIN) ---
if not st.session_state['autenticado']:
    
    # CSS BALANCEADO: Ni muy grande, ni desalineado
    st.markdown("""
        <style>
        /* Título Principal */
        .titulo-acceso {
            font-size: 36px !important;
            font-weight: 800 !important;
            color: #4F8BFF;
            text-align: center;
            margin-bottom: 25px;
        }
        
        /* Etiquetas de Usuario y Contraseña */
        .label-mediana {
            font-size: 20px !important;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: -15px; /* Reduce espacio con el cuadro */
            margin-left: 5px;      /* Alinea con el inicio del cuadro */
        }
        
        /* Cuadros de entrada de texto */
        input {
            font-size: 20px !important;
            height: 55px !important;
            text-align: center !important;
            border-radius: 10px !important;
        }
        
        /* Botón de Ingreso (Tamaño Proporcional) */
        div.stButton > button {
            font-size: 24px !important;
            height: 2.5em !important;
            font-weight: bold !important;
            background-color: #4F8BFF !important;
            border-radius: 12px !important;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Logo JC Flow
        if os.path.exists("unnamed.jpg"):
            st.image("unnamed.jpg", use_container_width=True)
        else:
            st.title("🏗️ JC Flow")
            
        st.markdown('<div class="titulo-acceso">Acceso Grupal - Posgrado</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            # Usuario
            st.markdown('<p class="label-mediana">USUARIO (GRUPO)</p>', unsafe_allow_html=True)
            u = st.text_input("u", label_visibility="collapsed", placeholder="Ej: grupo1")
            
            # Contraseña
            st.markdown('<p class="label-mediana">CONTRASEÑA</p>', unsafe_allow_html=True)
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
                        st.error("Credenciales incorrectas.")
                except Exception as e:
                    st.error("Error de conexión. Verifique sus Secrets.")
    st.stop()

# --- CONTINUACIÓN DEL SISTEMA (SideBar y Navegación) ---
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
            st.toast("✅ ¡Avance guardado!", icon="🚀")
    
    st.divider()
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

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
