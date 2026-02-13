import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Extraemos los datos de Secrets
            secrets = st.secrets["firebase_credentials"]
            
            # 2. LIMPIEZA PROFUNDA DE LA LLAVE (Para evitar ASN.1 parsing error)
            raw_key = secrets["private_key"]
            
            # Eliminamos posibles comillas accidentales y normalizamos saltos de línea
            clean_key = raw_key.replace("\\n", "\n").strip()
            
            # Si la llave se pegó como una sola línea, aseguramos los encabezados correctos
            if "-----BEGIN PRIVATE KEY-----" not in clean_key:
                clean_key = "-----BEGIN PRIVATE KEY-----\n" + clean_key + "\n-----END PRIVATE KEY-----"

            # 3. Reconstrucción del diccionario de credenciales
            cred_info = {
                "type": secrets["type"],
                "project_id": secrets["project_id"],
                "private_key_id": secrets["private_key_id"],
                "private_key": clean_key,
                "client_email": secrets["client_email"],
                "client_id": secrets["client_id"],
                "auth_uri": secrets["auth_uri"],
                "token_uri": secrets["token_uri"],
                "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
                "client_x509_cert_url": secrets["client_x509_cert_url"]
            }
            
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
    
    # --- VARIABLES ORIGINALES ---
    if 'integrantes' not in st.session_state:
        st.session_state['integrantes'] = []
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {}
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame()
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = ""
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = []
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = []
    if 'lista_alternativas' not in st.session_state:
        st.session_state['lista_alternativas'] = []
    if 'df_evaluacion_alternativas' not in st.session_state:
        st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame()
    if 'ponderacion_criterios' not in st.session_state:
        st.session_state['ponderacion_criterios'] = {}
    if 'df_calificaciones' not in st.session_state:
        st.session_state['df_calificaciones'] = pd.DataFrame()

# --- LÓGICA DE LOGIN ---
def login(usuario_ingresado, clave_ingresada):
    try:
        user_ref = db.collection("usuarios").document(usuario_ingresado)
        user_doc = user_ref.get()
        if user_doc.exists:
            datos = user_doc.to_dict()
            if str(datos.get("password")) == str(clave_ingresada):
                st.session_state.autenticado = True
                st.session_state.usuario_id = usuario_ingresado
                cargar_datos_nube(usuario_ingresado)
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
            # Restauramos cada variable al session_state
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
            st.success("Progreso guardado en la nube")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
