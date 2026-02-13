import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import json  # Importamos la librería nativa para leer el JSON

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # ESTRATEGIA SEGURA: Leer el JSON completo desde Secrets
            # Esto evita que toquemos la llave privada manualmente y rompe el ciclo de errores.
            json_text = st.secrets["firebase_credentials"]["text_json"]
            
            # Convertimos el texto a un diccionario Python real
            cred_info = json.loads(json_text)
            
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error de conexión con Firebase: {e}")
            st.stop()

# Inicialización inmediata
inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    # --- VARIABLES DEL PROYECTO ---
    vars_list = [
        'integrantes', 'datos_problema', 'datos_zona', 'df_interesados',
        'arbol_tarjetas', 'arbol_objetivos', 'analisis_participantes',
        'lista_alternativas', 'df_evaluacion_alternativas', 
        'df_relaciones_objetivos', 'ponderacion_criterios', 'df_calificaciones'
    ]
    
    for v in vars_list:
        if v not in st.session_state:
            if 'df_' in v:
                st.session_state[v] = pd.DataFrame()
            elif 'datos_' in v or 'ponderacion' in v:
                st.session_state[v] = {}
            else:
                st.session_state[v] = []

# --- LÓGICA DE LOGIN ---
def login(usuario, clave):
    try:
        doc = db.collection("usuarios").document(usuario).get()
        if doc.exists:
            d = doc.to_dict()
            if str(d.get("password")) == str(clave):
                st.session_state.autenticado = True
                st.session_state.usuario_id = usuario
                cargar_datos_nube(usuario)
                return True
    except Exception as e:
        st.error(f"Error en login: {e}")
    return False

# --- CARGA Y GUARDADO ---
def cargar_datos_nube(user_id):
    try:
        doc = db.collection("proyectos").document(user_id).get()
        if doc.exists:
            d = doc.to_dict()
            # Mapeo directo de variables
            if 'integrantes' in d: st.session_state['integrantes'] = d['integrantes']
            if 'diagnostico' in d: st.session_state['datos_problema'] = d['diagnostico']
            if 'zona' in d: st.session_state['datos_zona'] = d['zona']
            if 'interesados' in d: st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
            if 'arbol_p' in d: st.session_state['arbol_tarjetas'] = d['arbol_p']
            if 'arbol_o' in d: st.session_state['arbol_objetivos'] = d['arbol_o']
    except Exception as e:
        st.error(f"Error cargando datos: {e}")

def guardar_datos_nube():
    if st.session_state.usuario_id:
        try:
            # Preparar paquete convirtiendo DataFrames a dicts
            paquete = {
                "integrantes": st.session_state.get('integrantes', []),
                "diagnostico": st.session_state.get('datos_problema', {}),
                "zona": st.session_state.get('datos_zona', {}),
                "interesados": st.session_state.get('df_interesados', pd.DataFrame()).to_dict(),
                "arbol_p": st.session_state.get('arbol_tarjetas', []),
                "arbol_o": st.session_state.get('arbol_objetivos', [])
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(paquete)
            st.success("Progreso guardado en la nube")
        except Exception as e:
            st.error(f"Error guardando: {e}")
