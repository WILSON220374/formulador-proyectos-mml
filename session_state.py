import streamlit as st
import pandas as pd
from supabase import create_client

def conectar_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def inicializar_session():
    # --- AJUSTE VISUAL ---
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
    
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {"problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""}
    
    # --- HOJA 9 ---
    if 'datos_zona' not in st.session_state: 
        st.session_state['datos_zona'] = {
            "problema_central": "", "departamento": "", "provincia": "", "municipio": "", 
            "barrio_vereda": "", "latitud": "", "longitud": "",
            "limites_geograficos": "", "limites_administrativos": "", "otros_limites": "",
            "accesibilidad": "", "ruta_mapa": None, "ruta_foto1": None, "ruta_foto2": None,
            "pie_mapa": "", "pie_foto1": "", "pie_foto2": "",
            "poblacion_referencia": 0, "poblacion_afectada": 0, "poblacion_objetivo": 0
        }

    # --- INSERCIÓN 1: MEMORIA HOJA 10 ---
    if 'descripcion_problema' not in st.session_state:
        st.session_state['descripcion_problema'] = {
            "tabla_datos": {},
            "redaccion_narrativa": "",
            "antecedentes": ""
        }

    if 'df_interesados' not in st.session_state: st.session_state['df_interesados'] = pd.DataFrame()
    if 'analisis_participantes' not in st.session_state: st.session_state['analisis_participantes'] = ""
    
    if 'arbol_tarjetas' not in st.session_state: 
        st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []}
    if 'arbol_objetivos' not in st.session_state: 
        st.session_state['arbol_objetivos'] = {"Fin Último": [], "Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [], "Medios Directos": [], "Medios Indirectos": []}
    
    if 'df_evaluacion_alternativas' not in st.session_state: st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
    if 'df_relaciones_objetivos' not in st.session_state: st.session_state['df_relaciones_objetivos'] = pd.DataFrame()
    if 'lista_alternativas' not in st.session_state: st.session_state['lista_alternativas'] = []
    if 'ponderacion_criterios' not in st.session_state: st.session_state['ponderacion_criterios'] = {"COSTO": 25.0, "FACILIDAD": 25.0, "BENEFICIOS": 25.0, "TIEMPO": 25.0}
    if 'df_calificaciones' not in st.session_state: st.session_state['df_calificaciones'] = pd.DataFrame()
    if 'arbol_objetivos_final' not in st.session_state: st.session_state['arbol_objetivos_final'] = {}
    if 'arbol_problemas_final' not in st.session_state: st.session_state['arbol_problemas_final'] = {}

def limpiar_datos_arbol(arbol_dict):
    if not isinstance(arbol_dict, dict): return arbol_dict
    arbol_limpio = {}
    for nivel, tarjetas in arbol_dict.items():
        if isinstance(tarjetas, list):
            arbol_limpio[nivel] = [
                t for t in tarjetas 
                if isinstance(t, dict) and t.get('texto') and 
                str(t.get('texto')).strip().upper() != "NONE" and 
                len(str(t.get('texto')).strip()) > 1
            ]
        else:
            arbol_limpio[nivel] = tarjetas
    return arbol_limpio

def cargar_datos_nube(user_id):
    try:
        db = conectar_db()
        res = db.table("proyectos").select("*").eq("user_id", user_id).execute()
        
        if res.data:
            row = res.data[0]
            d = row.get('datos', {}) 
            if not d: d = {}

            st.session_state['integrantes'] = d.get('integrantes', [])
            st.session_state['datos_problema'] = d.get('diagnostico', st.session_state['datos_problema'])
            st.session_state['datos_zona'] = d.get('zona', st.session_state['datos_zona'])
            
            # --- INSERCIÓN 2: CARGAR HOJA 10 ---
            st.session_state['descripcion_problema'] = d.get('desc_p', st.session_state['descripcion_problema'])

            st.session_state['analisis_participantes'] = d.get('analisis_txt', "")
            st.session_state['arbol_tarjetas'] = limpiar_datos_arbol(d.get('arbol_p', st.session_state['arbol_tarjetas']))
            st.session_state['arbol_objetivos'] = limpiar_datos_arbol(d.get('arbol_o', st.session_state['arbol_objetivos']))
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
        st.session_state['arbol_tarjetas'] = limpiar_datos_arbol(st.session_state['arbol_tarjetas'])
        st.session_state['arbol_objetivos'] = limpiar_datos_arbol(st.session_state['arbol_objetivos'])

        paquete = {
            "integrantes": st.session_state['integrantes'],
            "diagnostico": st.session_state['datos_problema'],
            "zona": st.session_state['datos_zona'],
            
            # --- INSERCIÓN 3: GUARDAR HOJA 10 ---
            "desc_p": st.session_state['descripcion
