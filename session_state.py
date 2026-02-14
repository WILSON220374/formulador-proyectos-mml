import streamlit as st
import pandas as pd
from supabase import create_client

def conectar_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def inicializar_session():
    # --- INYECCIÓN DE DISEÑO ULTRA COMPACTO (Ajuste Final) ---
    st.markdown("""
        <style>
        /* 1. Ocultar el header vacío de Streamlit que ocupa espacio arriba */
        header[data-testid="stHeader"] {
            display: none !important;
        }

        /* 2. Reducir el padding superior al mínimo absoluto */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: -3rem !important; /* Sube todo el bloque principal */
        }
        
        /* 3. Compactar títulos y reducir su margen superior */
        h1 {
            margin-top: 0 !important;
            padding-top: 0 !important;
            margin-bottom: 0.5rem !important;
        }

        /* 4. Ajustar el contenedor de imágenes para que no empuje el contenido */
        [data-testid="stImage"] {
            margin-top: -1rem !important;
            margin-bottom: 0.5rem !important;
        }

        /* 5. Ocultar el botón de pantalla completa en todas las imágenes */
        button[title="View fullscreen"] {
            display: none !important;
        }

        /* 6. Estilo unificado para tarjetas (TextArea) */
        div[data-testid="stTextArea"] textarea {
            background-color: #ffffff !important;
            border: none !important;           
            border-radius: 0 0 10px 10px !important;
            text-align: center !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            color: #000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    
    # --- DATOS DEL EQUIPO ---
    if 'integrantes' not in st.session_state:
        st.session_state['integrantes'] = []
    
    # --- FASE I: IDENTIFICACIÓN (Páginas 1 y 2) ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {}
        
    # --- FASE II: PARTICIPANTES (Página 3) ---
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame()
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = ""

    # --- FASE III: ANÁLISIS (Páginas 4 y 5) ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []}
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = {"Fin Último": [], "Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [], "Medios Directos": [], "Medios Indirectos": []}

    # --- FASE IV: PLANIFICACIÓN Y EVALUACIÓN (Página 6) ---
    if 'df_evaluacion_alternativas' not in st.session_state:
        st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame()
    if 'lista_alternativas' not in st.session_state:
        st.session_state['lista_alternativas'] = []
    if 'ponderacion_criterios' not in st.session_state:
        st.session_state['ponderacion_criterios'] = {"COSTO": 25.0, "FACILIDAD": 25.0, "BENEFICIOS": 25.0, "TIEMPO": 25.0}
    if 'df_calificaciones' not in st.session_state:
        st.session_state['df_calificaciones'] = pd.DataFrame()

    # --- FASE V: ÁRBOLES FINALES PODADOS (Páginas 7 y 8) ---
    if 'arbol_objetivos_final' not in st.session_state:
        st.session_state['arbol_objetivos_final'] = {}
    if 'arbol_problemas_final' not in st.session_state:
        st.session_state['arbol_problemas_final'] = {}

def cargar_datos_nube(user_id):
    try:
        db = conectar_db()
        res = db.table("proyectos").select("datos").eq("user_id", user_id).execute()
        if res.data and res.data[0]['datos']:
            d = res.data[0]['datos']
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
        db.table("proyectos").update({"datos": paquete}).eq("user_id", st.session_state['usuario_id']).execute()
    except Exception as e:
        st.error(f"Error crítico al guardar: {e}")
