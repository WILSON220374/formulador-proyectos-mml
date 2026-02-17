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
    
    if 'descripcion_zona' not in st.session_state: 
        st.session_state['descripcion_zona'] = {
            "problema_central": "", "departamento": "", "provincia": "", "municipio": "", 
            "barrio_vereda": "", "latitud": "", "longitud": "",
            "limites_geograficos": "", "limites_administrativos": "", "otros_limites": "",
            "accesibilidad": "", "ruta_mapa": None, "ruta_foto1": None, "ruta_foto2": None,
            "pie_mapa": "", "pie_foto1": "", "pie_foto2": "",
            "poblacion_referencia": 0, "poblacion_afectada": 0, "poblacion_objetivo": 0
        }
    
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(columns=['Actor/Interesado', 'Relación', 'Poder', 'Interés', 'Estrategia'])
    
    if 'analisis_participantes' not in st.session_state: st.session_state['analisis_participantes'] = ""
    
    if 'ponderacion_criterios' not in st.session_state: st.session_state['ponderacion_criterios'] = {"COSTO": 25.0, "FACILIDAD": 25.0, "BENEFICIOS": 25.0, "TIEMPO": 25.0}
    
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Principal": [{"id": "pc-0", "texto": ""}], "Causas Directas": [], "Causas Indirectas": []}
    
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = {"Fines Indirectos": [], "Fines Directos": [], "Objetivo General": [{"id": "og-0", "texto": ""}], "Efectos Directos": [], "Efectos Indirectos": []}
    
    if 'lista_alternativas' not in st.session_state: st.session_state['lista_alternativas'] = []
    
    if 'df_evaluacion_alternativas' not in st.session_state:
        st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(columns=['Alternativa'])
        
    if 'df_calificaciones' not in st.session_state:
        st.session_state['df_calificaciones'] = pd.DataFrame()

    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame(columns=['Objetivo', 'Relación', 'Impacto'])

    if 'arbol_objetivos_final' not in st.session_state:
        st.session_state['arbol_objetivos_final'] = {}

    if 'arbol_problemas_final' not in st.session_state:
        st.session_state['arbol_problemas_final'] = {}

    if 'descripcion_problema' not in st.session_state:
        st.session_state['descripcion_problema'] = {'tabla_datos': {}, 'redaccion_narrativa': "", 'antecedentes': ""}

    # --- [NUEVO] INICIALIZACIÓN FASE IV: ANÁLISIS DE OBJETIVOS ---
    if 'analisis_objetivos' not in st.session_state:
        st.session_state['analisis_objetivos'] = {'tabla_indicadores': {}}

def limpiar_datos_arbol(datos):
    datos_limpios = {}
    for seccion, tarjetas in datos.items():
        if isinstance(tarjetas, list):
            datos_limpios[seccion] = [t for t in tarjetas if isinstance(t, dict) and t.get('texto')]
        else:
            datos_limpios[seccion] = tarjetas
    return datos_limpios

def cargar_datos_nube():
    if not st.session_state.get('usuario_id'): return
    try:
        supabase = conectar_db()
        res = supabase.table("proyectos").select("data").eq("id", st.session_state['usuario_id']).execute()
        if res.data:
            data = res.data[0]['data']
            st.session_state['integrantes'] = data.get('integrantes', [])
            st.session_state['datos_problema'] = data.get('diagnostico', {})
            st.session_state['descripcion_zona'] = data.get('zona', {})
            st.session_state['descripcion_problema'] = data.get('desc_problema', {'tabla_datos': {}, 'redaccion_narrativa': "", 'antecedentes': ""})
            st.session_state['analisis_objetivos'] = data.get('analisis_obj', {'tabla_indicadores': {}})
            st.session_state['df_interesados'] = pd.DataFrame(data.get('interesados', {}))
            st.session_state['analisis_participantes'] = data.get('analisis_txt', "")
            st.session_state['arbol_tarjetas'] = data.get('arbol_p', {})
            st.session_state['arbol_objetivos'] = data.get('arbol_o', {})
            st.session_state['lista_alternativas'] = data.get('alternativas', [])
            st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(data.get('eval_alt', {}))
            st.session_state['df_relaciones_objetivos'] = pd.DataFrame(data.get('rel_obj', {}))
            st.session_state['ponderacion_criterios'] = data.get('pesos_eval', {})
            st.session_state['df_calificaciones'] = pd.DataFrame(data.get('calificaciones', {}))
            st.session_state['arbol_objetivos_final'] = data.get('arbol_f', {})
            st.session_state['arbol_problemas_final'] = data.get('arbol_p_final', {})
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

def guardar_datos_nube():
    if not st.session_state.get('usuario_id'): return
    try:
        supabase = conectar_db()
        st.session_state['arbol_tarjetas'] = limpiar_datos_arbol(st.session_state['arbol_tarjetas'])
        st.session_state['arbol_objetivos'] = limpiar_datos_arbol(st.session_state['arbol_objetivos'])

        paquete = {
            "integrantes": st.session_state['integrantes'],
            "diagnostico": st.session_state['datos_problema'],
            "zona": st.session_state['descripcion_zona'],
            "desc_problema": st.session_state['descripcion_problema'],
            "analisis_obj": st.session_state['analisis_objetivos'],
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
            "arbol_p_final": st.session_state['arbol_problemas_final']
        }
        supabase.table("proyectos").upsert({"id": st.session_state['usuario_id'], "data": paquete}).execute()
    except Exception as e:
        print(f"Error crítico: {e}")
        st.error(f"Error al guardar en la nube: {e}")
