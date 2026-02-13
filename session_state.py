import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURACIÓN DE FIREBASE ---
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            cred_info = dict(st.secrets["firebase_credentials"])
            if "private_key" in cred_info:
                cred_info["private_key"] = cred_info["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error de conexión con Firebase: {e}")
            st.stop()

inicializar_firebase()
db = firestore.client()

def conectar_db():
    return db

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = None
    
    vars_to_init = [
        'integrantes', 'datos_problema', 'datos_zona', 'df_interesados',
        'arbol_tarjetas', 'arbol_objetivos', 'lista_alternativas', 
        'df_evaluacion_alternativas', 'df_relaciones_objetivos', 
        'ponderacion_criterios', 'df_calificaciones', 'analisis_participantes'
    ]
    for v in vars_to_init:
        if v not in st.session_state:
            if v == 'datos_problema':
                st.session_state[v] = {'problema_central': "", 'sintomas': "", 'causas_inmediatas': "", 'factores_agravantes': ""}
            # AJUSTE: Inicializamos como texto vacío
            elif v == 'analisis_participantes':
                st.session_state[v] = ""
            elif 'df_' in v: st.session_state[v] = pd.DataFrame()
            elif 'datos_' in v or 'ponderacion' in v: st.session_state[v] = {}
            else: st.session_state[v] = []

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
        st.error(f"Error login: {e}")
    return False

def cargar_datos_nube(user_id):
    try:
        doc = db.collection("proyectos").document(user_id).get()
        if doc.exists:
            d = doc.to_dict()
            if 'integrantes' in d: st.session_state['integrantes'] = d['integrantes']
            if 'diagnostico' in d: st.session_state['datos_problema'] = d['diagnostico']
            if 'zona' in d: st.session_state['datos_zona'] = d['zona']
            if 'interesados' in d: st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
            if 'arbol_p' in d: st.session_state['arbol_tarjetas'] = d['arbol_p']
            if 'arbol_o' in d: st.session_state['arbol_objetivos'] = d['arbol_o']
            # AJUSTE: Carga del análisis
            if 'analisis' in d: st.session_state['analisis_participantes'] = d['analisis']
    except Exception as e:
        st.error(f"Error cargando: {e}")

def guardar_datos_nube():
    if st.session_state.get('usuario_id'):
        try:
            paquete = {
                "integrantes": st.session_state.get('integrantes', []),
                "diagnostico": st.session_state.get('datos_problema', {}),
                "zona": st.session_state.get('datos_zona', {}),
                "interesados": st.session_state.get('df_interesados', pd.DataFrame()).to_dict(),
                "arbol_p": st.session_state.get('arbol_tarjetas', []),
                "arbol_o": st.session_state.get('arbol_objetivos', []),
                # AJUSTE: Guardado del análisis
                "analisis": st.session_state.get('analisis_participantes', "")
            }
            db.collection("proyectos").document(st.session_state.usuario_id).set(paquete)
            st.success("Guardado exitoso")
        except Exception as e:
            st.error(f"Error guardando: {e}")
