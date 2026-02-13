import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import re

def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Obtener los secretos
            s = st.secrets["firebase_credentials"]
            
            # 2. LIMPIEZA QUIRÚRGICA DE LA LLAVE
            raw_key = s["private_key"]
            
            # Eliminamos cualquier carácter que no deba estar en una llave PEM 
            # (dejamos solo letras, números, +, /, =, -, y saltos de línea)
            # Esto elimina el guion bajo (_) que está causando el error 95
            clean_key = raw_key.replace("\\n", "\n")
            
            # Extraemos solo el bloque base64 entre los encabezados si existen
            # o limpiamos los guiones bajos del bloque central
            if "-----BEGIN PRIVATE KEY-----" in clean_key:
                parts = clean_key.split("-----")
                # La parte [2] es el contenido Base64
                header = "-----BEGIN PRIVATE KEY-----"
                footer = "-----END PRIVATE KEY-----"
                content = parts[2].strip().replace("_", "/").replace("-", "+")
                # Reconstruimos el PEM perfecto
                final_key = f"{header}\n{content}\n{footer}"
            else:
                # Si no tiene encabezados, los ponemos y limpiamos el cuerpo
                content = clean_key.strip().replace("_", "/").replace("-", "+")
                final_key = f"-----BEGIN PRIVATE KEY-----\n{content}\n-----END PRIVATE KEY-----"

            # 3. Creación del diccionario para Firebase
            cred_info = {
                "type": s["type"],
                "project_id": s["project_id"],
                "private_key_id": s["private_key_id"],
                "private_key": final_key,
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
            st.error(f"Error crítico de certificado (Byte 95): {e}")
            st.stop()

# Inicializar Base de Datos
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    # Inicialización de variables de sesión (árbol, diagnóstico, etc.)
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # Aseguramos que existan todas tus variables de proyecto
    for key in ['integrantes', 'datos_problema', 'datos_zona', 'arbol_tarjetas', 'arbol_objetivos']:
        if key not in st.session_state:
            st.session_state[key] = [] if 'arbol' in key or 'integrantes' in key else {}

def login(usuario, clave):
    try:
        user_ref = db.collection("usuarios").document(usuario)
        doc = user_ref.get()
        if doc.exists and str(doc.to_dict().get("password")) == str(clave):
            st.session_state.autenticado = True
            st.session_state.usuario_id = usuario
            return True
    except:
        pass
    return False

def guardar_datos_nube():
    if st.session_state.usuario_id:
        try:
            datos = {
                "diagnostico": st.session_state['datos_problema'],
                "arbol_p": st.session_state['arbol_tarjetas'],
                "arbol_o": st.session_state['arbol_objetivos']
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(datos)
            st.success("Sincronizado con Firebase")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
