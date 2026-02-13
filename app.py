import streamlit as st
import os
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube, login

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- LÓGICA DE ACCESO (LOGIN) ---
if not st.session_state.get('autenticado', False):
    
    # Mantenemos tu CSS original para el diseño del login
    st.markdown("""
        <style>
        .titulo-acceso {
            font-size: 38px !important;
            font-weight: 800 !important;
            color: #4F8BFF;
            text-align: center;
            margin-bottom: 20px;
        }
        .label-mediana {
            font-size: 22px !important;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 8px !important;
            margin-top: 15px !important;
            margin-left: 5px;
            display: block;
        }
        input {
            font-size: 22px !important;
            height: 60px !important;
            text-align: center !important;
            border-radius: 12px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<p class="titulo-acceso">🚀 ACCESO AL FORMULADOR</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<label class="label-mediana">👤 Nombre del Grupo</label>', unsafe_allow_html=True)
        usuario = st.text_input("usuario", label_visibility="collapsed", placeholder="Ej: grupo1")
        
        st.markdown('<label class="label-mediana">🔑 Contraseña</label>', unsafe_allow_html=True)
        clave = st.text_input("clave", type="password", label_visibility="collapsed", placeholder="••••••••")
        
        st.write("")
        if st.button("INGRESAR AL PROYECTO", use_container_width=True, type="primary"):
            if login(usuario, clave):
                st.success("¡Acceso correcto!")
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Verifica el nombre del grupo y la clave.")
    st.stop()

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    st.title("🛠️ PANEL DE CONTROL")
    st.info(f"**Grupo:** {st.session_state.get('usuario_id', 'Invitado')}")
    
    # --- CORRECCIÓN CRÍTICA AQUÍ ---
    # Mostramos integrantes del equipo con protección contra valores nulos
    integrantes = st.session_state.get('integrantes', [])
    if integrantes:
        for persona in integrantes:
            if persona and isinstance(persona, dict):
                # Usamos .get() y verificamos que no sea None antes de usar .strip()
                nombre_raw = persona.get("Nombre Completo")
                nombre_full = nombre_raw.strip() if nombre_raw else ""
                
                if nombre_full:
                    # Extraemos solo el primer nombre en mayúsculas
                    nombre_pila = nombre_full.split()[0].upper()
                    st.markdown(f"**👤 {nombre_pila}**")
                else:
                    st.write("👤 *Integrante sin nombre*")
    
    st.divider()
    
    # Botón de guardado para Firebase
    if st.button("☁️ GUARDAR TODO EN NUBE", use_container_width=True, type="primary"):
        guardar_datos_nube()
        st.toast("✅ Avance guardado en Firebase", icon="🚀")
    
    st.divider()
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.session_state['usuario_id'] = None
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
    ]
})

pg.run()
