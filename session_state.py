import streamlit as st
import pandas as pd
from supabase import create_client

def conectar_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def inicializar_session():
    # --- AJUSTE VISUAL PARA QUE NO TENGAS QUE HACER SCROLL ---
    st.markdown("""
        <style>
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        h1 { margin-top: 0 !important; padding-top: 0 !important; }
        </style>
    """, unsafe_allow_html=True)

    if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state: st.session_state['usuario_id'] = ""
    if 'integrantes' not in st.session_state: st.session_state['integrantes'] = []
    
    # Inicialización de variables vacías
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    if 'datos_zona' not in st.session_state: st.session_state['datos_zona'] = {}
    if 'df_interesados' not in st.session_state: st.session_state['df_interesados'] = pd.DataFrame()
    if 'analisis_participantes' not in st.session_state: st.session_state['analisis_participantes'] = ""
    if 'arbol_tarjetas' not in st.session_state: st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []}
    if 'arbol_objetivos' not in st.session_state: st.session_state['arbol_objetivos'] = {"Fin Último": [], "Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [], "Medios Directos": [], "Medios Indirectos": []}
    if 'df_evaluacion_alternativas' not in st.session_state: st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
    if 'df_relaciones_objetivos' not in st.session_state: st.session_state['df_relaciones_objetivos'] = pd.DataFrame()
    if 'lista_alternativas' not in st.session_state: st.session_state['lista_alternativas'] = []
    if 'ponderacion_criterios' not in st.session_state: st.session_state['ponderacion_criterios'] = {"COSTO": 25.0, "FACILIDAD": 25.0, "BENEFICIOS": 25.0, "TIEMPO": 25.0}
    if 'df_calificaciones' not in st.session_state: st.session_state['df_calificaciones'] = pd.DataFrame()
    if 'arbol_objetivos_final' not in st.session_state: st.session_state['arbol_objetivos_final'] = {}
    if 'arbol_problemas_final' not in st.session_state: st.session_state['arbol_problemas_final'] = {}

def cargar_datos_nube(user_id):
    try:
        db = conectar_db()
        # 1. Buscamos por 'user_id' (Confirmado en tu foto)
        res = db.table("proyectos").select("*").eq("user_id", user_id).execute()
        
        if res.data:
            row = res.data[0]
            # 2. Extraemos el JSON de la columna 'datos' (Confirmado en tu foto)
            d = row.get('datos', {}) 
            
            # Si 'datos' está vacío o es None, evitamos errores
            if not d: d = {}

            # 3. Cargamos la información desempaquetada
            st.session_state['integrantes'] = d.get('integrantes', [])
            st.session_state['datos_problema'] = d.get('diagnostico', st.session_state['datos_problema'])
            st.session_state['datos_zona'] = d.get('zona', {})
            st.session_state['analisis_participantes'] = d.get('analisis_txt', "")
            st.session_state['arbol_tarjetas'] = d.get('arbol_p', st.session_state['arbol_tarjetas'])
            st.session_state['arbol_objetivos'] = d.get('arbol_o', st.session_state['arbol_objetivos'])
            st.session_state['lista_alternativas'] = d.get('alternativas', [])
            st.session_state['ponderacion_criterios'] = d.get('pesos_eval', st.session_state['ponderacion_criterios'])
            st.session_state['arbol_objetivos_final'] = d.get('arbol_f', {})
            st.session_state['arbol_problemas_final'] = d.get('arbol_p_f', {})
            
            if 'interesados' in d: st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
            if 'eval_alt' in d: st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(d['eval_alt'])
            if 'rel_obj' in d: st.session_state['df_relaciones_objetivos'] = pd.DataFrame(d['rel_obj'])
            if 'calificaciones' in d: st.session_state['df_calificaciones'] = pd.DataFrame(d['calificaciones'])
    except Exception as e:
        st.error(f"Error al cargar: {e}")

def guardar_datos_nube():
    try:
        db = conectar_db()
        # Empaquetamos todo en un diccionario
        paquete = {
            "integrantes": st.session_state['integrantes'],
            "diagnostico": st.session_state['datos_problema'],
            "zona": st.session_state['datos_zona'],
            "interesados": st.session_state['df_interesados'].to_dict(),
            "analisis_txt": st.session_state['analisis_participantes'],
            "arbol_p": st.session_state['arbol_tarjetas'],
            "arbol_o": st.session_state['arbol_objetivos'],
            "alternativas": st.session_state['lista_alternativas'],
            "eval_alt": st.session_state['df_evaluacion_alternativas'].to_dict(),
            "rel_obj": st.session_state['df_relaciones_objetivos'].to_dict(),
            "pesos_eval": st.session_state['ponderacion_criterios'],
            "calificaciones": st.session_state['df_calificaciones'].to_dict(),
            "arbol_f": st.session_state['arbol_objetivos_final'],
            "arbol_p_f": st.session_state['arbol_problemas_final']
        }
        # Guardamos en la columna 'datos' buscando por 'user_id'
        db.table("proyectos").update({"datos": paquete}).eq("user_id", st.session_state['usuario_id']).execute()
    except Exception as e:
        st.error(f"Error al guardar: {e}")
