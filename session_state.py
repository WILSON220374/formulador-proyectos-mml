import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import re

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Extraer los datos de Secrets
            s = st.secrets["firebase_credentials"]
            raw_key = s["private_key"]

            # 2. FILTRO ANTI-CORRUPCIÓN (ASCII ONLY)
            # Esto elimina el byte 195 (Ã) y cualquier otro símbolo invisible
            # Solo deja caracteres básicos de teclado
            clean_text = "".join(c for c in raw_key if ord(c) < 128)
            
            # Normalizamos saltos de línea que vienen como texto
            clean_text = clean_text.replace("\\n", "\n")

            # 3. EXTRACCIÓN QUIRÚRGICA DEL CUERPO DE LA LLAVE
            # Buscamos solo lo que está entre los guiones para limpiar el medio
            if "BEGIN PRIVATE KEY" in clean_text:
                # Extraemos el bloque central (Base64)
                # Eliminamos cualquier guion bajo (_) o espacios que se colaron
                pattern = r"-----BEGIN PRIVATE KEY-----(.*)-----END PRIVATE KEY-----"
                match = re.search(pattern, clean_text, re.DOTALL)
                
                if match:
                    cuerpo_base64 = match.group(1).strip()
                    # Limpiamos el cuerpo de caracteres ilegales (como guiones bajos o espacios)
                    cuerpo_base64 = cuerpo_base64.replace("_", "/").replace(" ", "").replace("\r", "")
                    
                    # RECONSTRUCCIÓN MANUAL PURA
                    # Esto garantiza que la cabecera sea EXACTAMENTE la que Firebase quiere
                    final_key = f"-----BEGIN PRIVATE KEY-----\n{cuerpo_base64}\n-----END PRIVATE KEY-----"
                else:
                    final_key = clean_text
            else:
                final_key = clean_text

            # 4. Creación del diccionario limpio
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
            # Si falla, mostramos exactamente qué está recibiendo el sistema para depurar
            st.error(f"Error de Certificado: {e}")
            st.stop()

# Inicialización
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # Lista de variables a asegurar
    for v in ['integrantes', 'datos_problema', 'datos_zona', 'arbol_tarjetas', 'arbol_objetivos']:
        if v not in st.session_state:
            st.session_state[v] = [] if 'arbol' in v or 'integrantes' in v else {}

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
            # Aquí agregas todas tus variables de sesión para guardar
            datos = {
                "integrantes": st.session_state.get('integrantes', []),
                "diagnostico": st.session_state.get('datos_problema', {}),
                "arbol_p": st.session_state.get('arbol_tarjetas', []),
                "arbol_o": st.session_state.get('arbol_objetivos', [])
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(datos)
            st.success("Guardado exitoso en Firebase")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
