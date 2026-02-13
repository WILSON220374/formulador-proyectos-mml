import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Extraer los datos de Secrets
            s = st.secrets["firebase_credentials"]
            
            # 2. EL ASESINO DE "EXTRA DATA": 
            # Limpiamos la llave y forzamos a que termine EXACTAMENTE en los guiones
            raw_key = s["private_key"].replace("\\n", "\n").strip()
            
            footer = "-----END PRIVATE KEY-----"
            if footer in raw_key:
                # Esto corta cualquier espacio o salto de línea que haya después del footer
                clean_key = raw_key.split(footer)[0] + footer
            else:
                clean_key = raw_key

            # 3. Reconstrucción manual del objeto para evitar metadatos de Streamlit
            cred_info = {
                "type": s["type"],
                "project_id": s["project_id"],
                "private_key_id": s["private_key_id"],
                "private_key": clean_key,
                "client_email": s["client_email"],
                "client_id": s["client_id"],
                "auth_uri": s["auth_uri"],
                "token_uri": s["token_uri"],
                "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
                "client_x509_cert_url": s["client_x509_cert_url"]
            }
            
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error de conexión con Firebase: {e}")
            st.stop()

# Ejecución de seguridad
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # --- VARIABLES DE TU PROYECTO ---
    vars_proyecto = [
        'integrantes', 'datos_problema', 'datos_zona', 'df_interesados',
        'analisis_participantes', 'arbol_tarjetas', 'arbol_objetivos',
        'lista_alternativas', 'df_evaluacion_alternativas', 
        'df_relaciones_objetivos', 'ponderacion_criterios', 'df_calificaciones'
    ]
    for v in vars_proyecto:
        if v not in st.session_state:
            if 'df_' in v: st.session_state[v] = pd.DataFrame()
            elif 'datos_' in v: st.session_state[v] = {}
            elif 'lista_' in v or 'arbol_' in v: st.session_state[v] = []
            else: st.session_state[v] = ""

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
            for key, value in d.items():
                if key in st.session_state:
                    if isinstance(value, dict) and 'columns' in value: # Es un DataFrame
                        st.session_state[key] = pd.DataFrame(value)
                    else:
                        st.session_state[key] = value
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

def guardar_datos_nube():
    if st.session_state.usuario_id:
        try:
            paquete = {
                "integrantes": st.session_state.get('integrantes', []),
                "diagnostico": st.session_state.get('datos_problema', {}),
                "zona": st.session_state.get('datos_zona', {}),
                "interesados": st.session_state.get('df_interesados', pd.DataFrame()).to_dict(),
                "arbol_p": st.session_state.get('arbol_tarjetas', []),
                "arbol_o": st.session_state.get('arbol_objetivos', [])
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(paquete)
            st.success("Progreso guardado en Firebase")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
