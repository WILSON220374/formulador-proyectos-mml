import streamlit as st
import pandas as pd
from supabase import create_client

def conectar_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def inicializar_session():
    # 0. Autenticación
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    
    # --- FASE I: IDENTIFICACIÓN (Páginas 1 y 2) ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    
    if 'datos_zona' not in st.session_state: #
        st.session_state['datos_zona'] = {}
        
    # --- FASE II: PARTICIPANTES (Página 3) ---
    if 'df_interesados' not in st.session_state: #
        st.session_state['df_interesados'] = pd.DataFrame()
        
    if 'analisis_participantes' not in st.session_state: #
        st.session_state['analisis_participantes'] = ""

    # --- FASE III: ANÁLISIS (Páginas 4 y 5) ---
    if 'arbol_tarjetas' not in st.session_state: #
        st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []}
        
    if 'arbol_objetivos' not in st.session_state: #
        st.session_state['arbol_objetivos'] = {"Fin Último": [], "Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [], "Medios Directos": [], "Medios Indirectos": []}

    # --- FASE IV: PLANIFICACIÓN (Página 6) ---
    if 'df_evaluacion_alternativas' not in st.session_state: #
        st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
        
    if 'df_relaciones_objetivos' not in st.session_state: #
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame()
        
    if 'lista_alternativas' not in st.session_state: #
        st.session_state['lista_alternativas'] = []

def cargar_datos_nube(user_id):
    try:
        db = conectar_db()
        res = db.table("proyectos").select("datos").eq("user_id", user_id).execute()
        if res.data and res.data[0]['datos']:
            d = res.data[0]['datos']
            
            # Carga Masiva y Sincronizada
            st.session_state['datos_problema'] = d.get('diagnostico', st.session_state['datos_problema'])
            st.session_state['datos_zona'] = d.get('zona', {}) # Recuperamos Zona
            st.session_state['analisis_participantes'] = d.get('analisis_txt', "") # Recuperamos Análisis
            st.session_state['arbol_tarjetas'] = d.get('arbol_p', st.session_state['arbol_tarjetas'])
            st.session_state['arbol_objetivos'] = d.get('arbol_o', st.session_state['arbol_objetivos'])
            st.session_state['lista_alternativas'] = d.get('alternativas', [])
            
            # Recuperación de Tablas (DataFrame)
            if 'interesados' in d: # Recuperamos Interesados
                st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
            if 'eval_alt' in d:
                st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(d['eval_alt'])
            if 'rel_obj' in d:
                st.session_state['df_relaciones_objetivos'] = pd.DataFrame(d['rel_obj'])
                
    except Exception as e:
        st.error(f"Error al cargar el proyecto: {e}")

def guardar_datos_nube():
    try:
        db = conectar_db()
        # Construimos el "Libro Completo" del proyecto para la nube
        paquete = {
            "diagnostico": st.session_state['datos_problema'],
            "zona": st.session_state['datos_zona'], # Guardamos Zona
            "interesados": st.session_state['df_interesados'].to_dict(), # Guardamos Interesados
            "analisis_txt": st.session_state['analisis_participantes'], # Guardamos Análisis
            "arbol_p": st.session_state['arbol_tarjetas'],
            "arbol_o": st.session_state['arbol_objetivos'],
            "alternativas": st.session_state['lista_alternativas'],
            "eval_alt": st.session_state['df_evaluacion_alternativas'].to_dict(),
            "rel_obj": st.session_state['df_relaciones_objetivos'].to_dict()
        }
        db.table("proyectos").update({"datos": paquete}).eq("user_id", st.session_state['usuario_id']).execute()
    except Exception as e:
        st.error(f"Error crítico al guardar: {e}")
