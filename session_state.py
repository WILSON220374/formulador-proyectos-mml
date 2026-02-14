import streamlit as st
import pandas as pd
from supabase import create_client

def conectar_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def inicializar_session():
    # --- INYECCIÓN DE DISEÑO ULTRA-COMPACTO ---
    st.markdown("""
        <style>
        /* 1. Eliminar cabecera y reducir espacios del contenedor principal */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .block-container {
            padding-top: 0.5rem !important; 
            padding-bottom: 0rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        /* 2. Compactar Títulos y Subtítulos */
        h1 {
            margin-top: -10px !important;
            padding-top: 0 !important;
            margin-bottom: 0.5rem !important;
            font-size: 28px !important;
        }
        h2, h3 {
            margin-top: 5px !important;
            margin-bottom: 5px !important;
            font-size: 22px !important;
        }

        /* 3. Ajuste de imagen (Logo) */
        [data-testid="stImage"] {
            margin-top: 0 !important;
            display: flex;
            justify-content: center;
        }

        /* 4. Ocultar elementos innecesarios */
        button[title="View fullscreen"] {
            display: none !important;
        }

        /* 5. Estilo de tarjetas de texto compacto */
        div[data-testid="stTextArea"] textarea {
            font-size: 13px !important;
            padding: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
    if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False
    if 'grupo_id' not in st.session_state: st.session_state['grupo_id'] = ""
    if 'integrantes' not in st.session_state: st.session_state['integrantes'] = []
    
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {
            'problema_central': "", 'sintomas': "", 
            'causas_inmediatas': "", 'factores_agravantes': ""
        }
    
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {
            'pob_total': 0, 'pob_urbana': 0, 'pob_rural': 0,
            'ubicacion': "", 'limites': "", 'economia': "", 'vias': ""
        }

    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(columns=["#", "NOMBRE", "POSICIÓN", "GRUPO", "EXPECTATIVA", "CONTRIBUCION", "PODER", "INTERÉS", "ESTRATEGIA"])
    
    if 'analisis_participantes' not in st.session_state: st.session_state['analisis_participantes'] = ""
    if 'arbol_tarjetas' not in st.session_state: st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Central": [], "Causas Directas": [], "Causas Indirectas": []}
    if 'arbol_objetivos' not in st.session_state: st.session_state['arbol_objetivos'] = {"Fin Último": [], "Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [], "Medios Directos": [], "Medios Indirectos": []}
    if 'lista_alternativas' not in st.session_state: st.session_state['lista_alternativas'] = []
    if 'df_evaluacion_alternativas' not in st.session_state: st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
    if 'ponderacion_criterios' not in st.session_state: st.session_state['ponderacion_criterios'] = {"COSTO": 25, "FACILIDAD": 25, "BENEFICIOS": 25, "TIEMPO": 25}
    if 'df_calificaciones' not in st.session_state: st.session_state['df_calificaciones'] = pd.DataFrame()
    if 'arbol_objetivos_final' not in st.session_state: st.session_state['arbol_objetivos_final'] = {}
    if 'arbol_problemas_final' not in st.session_state: st.session_state['arbol_problemas_final'] = {}
    if 'df_relaciones_objetivos' not in st.session_state: st.session_state['df_relaciones_objetivos'] = pd.DataFrame()

def cargar_datos_nube(id_grupo):
    try:
        db = conectar_db()
        res = db.table("proyectos").select("*").eq("id_grupo", id_grupo).execute()
        if res.data:
            d = res.data[0]
            st.session_state['integrantes'] = d.get('integrantes', [])
            st.session_state['datos_problema'] = d.get('diagnostico', {})
            st.session_state['datos_zona'] = d.get('zona', {})
            if 'interesados' in d: st.session_state['df_interesados'] = pd.DataFrame(d['interesados'])
            st.session_state['analisis_participantes'] = d.get('analisis_txt', "")
            st.session_state['arbol_tarjetas'] = d.get('arbol_p', {})
            st.session_state['arbol_objetivos'] = d.get('arbol_o', {})
            st.session_state['lista_alternativas'] = d.get('alternativas', [])
            if 'eval_alt' in d: st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(d['eval_alt'])
            st.session_state['ponderacion_criterios'] = d.get('pesos_eval', {"COSTO": 25, "FACILIDAD": 25, "BENEFICIOS": 25, "TIEMPO": 25})
            st.session_state['arbol_objetivos_final'] = d.get('arbol_f', {})
            st.session_state['arbol_problemas_final'] = d.get('arbol_p_f', {})
            if 'rel_obj' in d: st.session_state['df_relaciones_objetivos'] = pd.DataFrame(d['rel_obj'])
            if 'calificaciones' in d: st.session_state['df_calificaciones'] = pd.DataFrame(d['calificaciones'])
    except Exception as e:
        st.error(f"Error al cargar: {e}")

def guardar_datos_nube():
    try:
        db = conectar_db()
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
        db.table("proyectos").upsert({"id_grupo": st.session_state['grupo_id'], **paquete}).execute()
    except Exception as e:
        st.error(f"Error al guardar: {e}")
