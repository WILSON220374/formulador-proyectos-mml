import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Extraer los secretos y convertirlos a un diccionario limpio
            # Usamos .to_dict() para evitar proxies de Streamlit
            cred_info = st.secrets["firebase_credentials"].to_dict()
            
            # 2. LIMPIEZA QUIRÚRGICA DE LA LLAVE (SOLUCIÓN AL EXTRA DATA)
            p_key = cred_info["private_key"]
            
            # Paso A: Convertir \n de texto a saltos de línea reales
            p_key = p_key.replace("\\n", "\n")
            
            # Paso B: Encontrar el inicio y fin exacto (Ignora basura antes o después)
            inicio = "-----BEGIN PRIVATE KEY-----"
            fin = "-----END PRIVATE KEY-----"
            
            if inicio in p_key and fin in p_key:
                # Cortamos la cadena para que empiece en BEGIN y termine justo en el último guion de END
                p_key = p_key[p_key.find(inicio) : p_key.find(fin) + len(fin)]
                cred_info["private_key"] = p_key
            else:
                st.error("La llave privada no tiene el formato PEM correcto (BEGIN/END).")
                st.stop()

            # 3. Inicialización oficial
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred)
            
        except Exception as e:
            st.error(f"Error de conexión con Firebase: {e}")
            st.stop()

# Ejecutar inmediatamente al importar
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    # Mantenemos todas tus variables originales
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # Inicialización de listas y diccionarios del proyecto
    for key in ['integrantes', 'datos_problema', 'datos_zona', 'arbol_tarjetas', 'arbol_objetivos']:
        if key not in st.session_state:
            st.session_state[key] = [] if 'arbol' in key or 'integrantes' in key else {}

def login(usuario, clave):
    try:
        user_ref = db.collection("usuarios").document(usuario)
        doc = user_ref.get()
        if doc.exists:
            datos = doc.to_dict()
            # Comparación de seguridad
            if str(datos.get("password")) == str(clave):
                st.session_state.autenticado = True
                st.session_state.usuario_id = usuario
                return True
    except:
        pass
    return False

def guardar_datos_nube():
    if st.session_state.usuario_id:
        try:
            # Aquí van todas las variables que quieres persistir
            paquete = {
                "integrantes": st.session_state.get('integrantes', []),
                "diagnostico": st.session_state.get('datos_problema', {}),
                "arbol_p": st.session_state.get('arbol_tarjetas', []),
                "arbol_o": st.session_state.get('arbol_objetivos', [])
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(paquete)
            st.success("✅ Sincronizado con Firebase")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
