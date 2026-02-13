import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Convertir Secrets a diccionario limpio
            secrets = st.secrets["firebase_credentials"]
            cred_info = {k: v for k, v in secrets.items()}
            
            # 2. LIMPIEZA TOTAL DE LLAVE
            # Convertimos los \n de texto en saltos de línea reales
            raw_key = cred_info["private_key"].replace("\\n", "\n").strip()
            
            # Buscamos el final oficial y cortamos CUALQUIER cosa que venga después
            footer = "-----END PRIVATE KEY-----"
            if footer in raw_key:
                raw_key = raw_key.split(footer)[0] + footer
            
            cred_info["private_key"] = raw_key
            
            # 3. Inicializar
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error de conexión con Firebase: {e}")
            st.stop()

# Inicialización automática
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # Inicialización de tus variables de proyecto
    if 'integrantes' not in st.session_state:
        st.session_state['integrantes'] = []
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    # ... inicializa el resto de tus variables (zona, interesados, etc.) aquí ...

def login(usuario, clave):
    try:
        user_ref = db.collection("usuarios").document(usuario)
        doc = user_ref.get()
        if doc.exists:
            datos = doc.to_dict()
            if str(datos.get("password")) == str(clave):
                st.session_state.autenticado = True
                st.session_state.usuario_id = usuario
                cargar_datos_nube(usuario)
                return True
    except Exception as e:
        st.error(f"Error al validar usuario: {e}")
    return False

def cargar_datos_nube(user_id):
    try:
        doc_ref = db.collection("proyectos").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            d = doc.to_dict()
            # Actualiza tus variables de sesión con los datos de Firebase
            if 'integrantes' in d: st.session_state['integrantes'] = d['integrantes']
            if 'diagnostico' in d: st.session_state['datos_problema'] = d['diagnostico']
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

def guardar_datos_nube():
    if st.session_state.usuario_id:
        try:
            paquete = {
                "integrantes": st.session_state['integrantes'],
                "diagnostico": st.session_state['datos_problema']
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(paquete)
            st.success("Sincronizado con Firebase")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
