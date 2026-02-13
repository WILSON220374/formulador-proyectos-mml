import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # Obtener los secretos
            secrets = st.secrets["firebase_credentials"]
            
            # Reconstruir el diccionario para asegurar que sea un objeto limpio
            cred_dict = {
                "type": secrets["type"],
                "project_id": secrets["project_id"],
                "private_key_id": secrets["private_key_id"],
                "private_key": secrets["private_key"].replace("\\n", "\n").strip(),
                "client_email": secrets["client_email"],
                "client_id": secrets["client_id"],
                "auth_uri": secrets["auth_uri"],
                "token_uri": secrets["token_uri"],
                "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
                "client_x509_cert_url": secrets["client_x509_cert_url"]
            }
            
            # Asegurar que la llave termine exactamente en los guiones finales
            footer = "-----END PRIVATE KEY-----"
            if footer in cred_dict["private_key"]:
                cred_dict["private_key"] = cred_dict["private_key"].split(footer)[0] + footer
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error de conexión con Firebase: {e}")
            st.stop()

# Inicialización al importar el archivo
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # --- VARIABLES ORIGINALES DEL PROYECTO ---
    if 'integrantes' not in st.session_state:
        st.session_state['integrantes'] = []
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {}
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame()
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = []
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = []

# --- LÓGICA DE LOGIN Y DATOS ---
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
            if 'integrantes' in d: st.session_state['integrantes'] = d['integrantes']
            if 'diagnostico' in d: st.session_state['datos_problema'] = d['diagnostico']
            if 'zona' in d: st.session_state['datos_zona'] = d['zona']
            if 'interesados' in d: st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
            if 'arbol_p' in d: st.session_state['arbol_tarjetas'] = d['arbol_p']
            if 'arbol_o' in d: st.session_state['arbol_objetivos'] = d['arbol_o']
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

def guardar_datos_nube():
    if st.session_state.usuario_id:
        try:
            paquete = {
                "integrantes": st.session_state['integrantes'],
                "diagnostico": st.session_state['datos_problema'],
                "zona": st.session_state['datos_zona'],
                "interesados": st.session_state['df_interesados'].to_dict(),
                "arbol_p": st.session_state['arbol_tarjetas'],
                "arbol_o": st.session_state['arbol_objetivos']
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(paquete)
            st.success("Guardado en Firebase correctamente")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
