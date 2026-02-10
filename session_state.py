import streamlit as st
import pandas as pd
from supabase import create_client

def conectar_db():
    """Conexión segura usando los Secrets de Streamlit."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def inicializar_session():
    """Inicializa la memoria y evita errores de variables faltantes."""
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    
    # Prevenir KeyError: inicializar todas las llaves necesarias
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {}
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(columns=["#", "NOMBRE", "POSICIÓN", "GRUPO", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"])
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = "" # <--- Solución al error de tu captura
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {"Problema Superior": [], "Efectos Indirectos": [], "Efectos Directos": [], "Problema Central": [], "Causas Directas": [], "Causas Indirectas": []}
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = {"Fin Último": [], "Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [], "Medios Directos": [], "Medios Indirectos": []}

def cargar_datos_nube(user_id):
    """Trae el avance guardado desde Supabase al iniciar sesión."""
    db = conectar_db()
    res = db.table("proyectos").select("datos").eq("user_id", user_id).execute()
    if res.data and res.data[0]['datos']:
        d = res.data[0]['datos']
        st.session_state['datos_problema'] = d.get('diagnostico', st.session_state['datos_problema'])
        st.session_state['datos_zona'] = d.get('zona', st.session_state['datos_zona'])
        st.session_state['analisis_participantes'] = d.get('analisis_txt', "")
        if 'interesados' in d:
            st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
        st.session_state['arbol_tarjetas'] = d.get('arbol_p', st.session_state['arbol_tarjetas'])
        st.session_state['arbol_objetivos'] = d.get('arbol_o', st.session_state['arbol_objetivos'])

def guardar_datos_nube():
    """Sincroniza todo el trabajo actual con la base de datos."""
    db = conectar_db()
    paquete = {
        "diagnostico": st.session_state['datos_problema'],
        "zona": st.session_state['datos_zona'],
        "interesados": st.session_state['df_interesados'].to_dict(),
        "analisis_txt": st.session_state['analisis_participantes'],
        "arbol_p": st.session_state['arbol_tarjetas'],
        "arbol_o": st.session_state['arbol_objetivos']
    }
    db.table("proyectos").update({"datos": paquete}).eq("user_id", st.session_state['usuario_id']).execute()
