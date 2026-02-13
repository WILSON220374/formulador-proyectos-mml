import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Obtener el diccionario de Secrets
            # Usamos .to_dict() para asegurarnos de tener un objeto limpio
            cred_info = st.secrets["firebase_credentials"].to_dict()
            
            # 2. PROCESAMIENTO DE LA LLAVE
            # El error InvalidPadding ocurre si la llave no tiene los saltos de línea 
            # correctos o si le faltan los "=" al final.
            if "private_key" in cred_info:
                # Primero: Convertimos los \n de texto en saltos de línea reales
                p_key = cred_info["private_key"].replace("\\n", "\n")
                # Segundo: Quitamos espacios accidentales al inicio y al final
                cred_info["private_key"] = p_key.strip()
                
            # 3. Inicialización
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error de Certificado (Padding): {e}")
            st.stop()

# Ejecución inmediata
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # Asegurar todas tus variables de proyecto
    claves = ['integrantes', 'datos_problema', 'datos_zona', 'df_interesados', 'arbol_tarjetas', 'arbol_objetivos']
    for c in claves:
        if c not in st.session_state:
            if 'df_' in c: st.session_state[c] = pd.DataFrame()
            elif 'arbol' in c or 'integrantes' in c: st.session_state[c] = []
            else: st.session_state[c] = {}

def login(u, p):
    try:
        doc = db.collection("usuarios").document(u).get()
        if doc.exists and str(doc.to_dict().get("password")) == str(p):
            st.session_state.autenticado = True
            st.session_state.usuario_id = u
            return True
    except: pass
    return False

def guardar_datos_nube():
    if st.session_state.usuario_id:
        try:
            datos = {
                "integrantes": st.session_state.get('integrantes', []),
                "diagnostico": st.session_state.get('datos_problema', {}),
                "arbol_p": st.session_state.get('arbol_tarjetas', []),
                "arbol_o": st.session_state.get('arbol_objetivos', [])
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(datos)
            st.success("Guardado en Firebase")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
