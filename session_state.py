import streamlit as st
import pandas as pd
from supabase import create_client

def conectar_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def inicializar_session():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    
    # --- Fase I: Identificación ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {}
    if 'df_interesados' not in st.session_state:
        columnas = ["NOMBRE", "POSICIÓN", "GRUPO", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
        st.session_state['df_interesados'] = pd.DataFrame(columns=columnas)
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = ""

    # --- Fase II: Análisis ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []}
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = {"Fin Último": [], "Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [], "Medios Directos": [], "Medios Indirectos": []}

    # --- Fase III: Planificación (Sincronización de Alternativas) ---
    if 'df_evaluacion_alternativas' not in st.session_state:
        st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame()
    if 'lista_alternativas' not in st.session_state:
        st.session_state['lista_alternativas'] = []

def cargar_datos_nube(user_id):
    try:
        db = conectar_db()
        res = db.table("proyectos").select("datos").eq("user_id", user_id).execute()
        if res.data and res.data[0]['datos']:
            d = res.data[0]['datos']
            st.session_state['datos_problema'] = d.get('diagnostico', st.session_state['datos_problema'])
            st.session_state['datos_zona'] = d.get('zona', st.session_state['datos_zona'])
            st.session_state['analisis_participantes'] = d.get('analisis_txt', "")
            st.session_state['arbol_tarjetas'] = d.get('arbol_p', st.session_state['arbol_tarjetas'])
            st.session_state['arbol_objetivos'] = d.get('arbol_o', st.session_state['arbol_objetivos'])
            st.session_state['lista_alternativas'] = d.get('alternativas', [])
            
            # Recuperación de tablas de evaluación
            if 'eval_alt' in d:
                st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(d['eval_alt'])
            if 'rel_obj' in d:
                st.session_state['df_relaciones_objetivos'] = pd.DataFrame(d['rel_obj'])
                
            if 'interesados' in d:
                st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
    except Exception as e:
        st.error(f"Error al cargar: {e}")

def guardar_datos_nube():
    try:
        db = conectar_db()
        paquete = {
            "diagnostico": st.session_state['datos_problema'],
            "zona": st.session_state['datos_zona'],
            "interesados": st.session_state['df_interesados'].to_dict(),
            "analisis_txt": st.session_state['analisis_participantes'],
            "arbol_p": st.session_state['arbol_tarjetas'],
            "arbol_o": st.session_state['arbol_objetivos'],
            "alternativas": st.session_state['lista_alternativas'],
            # Empaque de tablas para la nube
            "eval_alt": st.session_state['df_evaluacion_alternativas'].to_dict(),
            "rel_obj": st.session_state['df_relaciones_objetivos'].to_dict()
        }
        db.table("proyectos").update({"datos": paquete}).eq("user_id", st.session_state['usuario_id']).execute()
    except Exception as e:
        st.error(f"Error al guardar: {e}")
