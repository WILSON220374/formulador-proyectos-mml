import streamlit as st
import pandas as pd
from supabase import create_client


def conectar_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def _df_from_saved(obj):
    """
    Compatibilidad:
    - Nuevo formato recomendado: list[dict] (records)
    - Formato antiguo: dict (to_dict() por columnas)
    """
    if obj is None:
        return pd.DataFrame()
    if isinstance(obj, list):
        return pd.DataFrame(obj)
    if isinstance(obj, dict):
        return pd.DataFrame(obj)
    return pd.DataFrame()


def inicializar_session():
    # --- AJUSTE VISUAL PARA QUE NO TENGAS QUE HACER SCROLL ---
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        h1 { margin-top: 0 !important; padding-top: 0 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario_id' not in st.session_state:
        st.session_state['usuario_id'] = ""
    if 'integrantes' not in st.session_state:
        st.session_state['integrantes'] = []

    # Inicialización de variables vacías
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {
            "problema_central": "",
            "sintomas": "",
            "causas_inmediatas": "",
            "factores_agravantes": ""
        }
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {}
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame()
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = ""
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {
            "Efectos Indirectos": [],
            "Efectos Directos": [],
            "Problema Principal": [],
            "Causas Directas": [],
            "Causas Indirectas": []
        }
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = {
            "Fin Último": [],
            "Fines Indirectos": [],
            "Fines Directos": [],
            "Objetivo General": [],
            "Medios Directos": [],
            "Medios Indirectos": []
        }
    if 'df_evaluacion_alternativas' not in st.session_state:
        st.session_state['df_evaluacion_alternativas'] = pd.DataFrame()
    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame()
    if 'lista_alternativas' not in st.session_state:
        st.session_state['lista_alternativas'] = []
    if 'ponderacion_criterios' not in st.session_state:
        st.session_state['ponderacion_criterios'] = {
            "COSTO": 25.0,
            "FACILIDAD": 25.0,
            "BENEFICIOS": 25.0,
            "TIEMPO": 25.0
        }
    if 'df_calificaciones' not in st.session_state:
        st.session_state['df_calificaciones'] = pd.DataFrame()
    if 'arbol_objetivos_final' not in st.session_state:
        st.session_state['arbol_objetivos_final'] = {}
    if 'arbol_problemas_final' not in st.session_state:
        st.session_state['arbol_problemas_final'] = {}
    if 'descripcion_zona' not in st.session_state:
        st.session_state['descripcion_zona'] = {
            "departamento": "",
            "municipio": "",
            "barrio_vereda": "",
            "latitud": "",
            "longitud": "",
            "poblacion_referencia": 0
        }

    # --- HOJA 11 (Indicadores) ---
    if 'datos_indicadores' not in st.session_state:
        st.session_state['datos_indicadores'] = {}
    if 'indicadores_mapa_objetivo' not in st.session_state:
        st.session_state['indicadores_mapa_objetivo'] = {}


def cargar_datos_nube(user_id):
    try:
        db = conectar_db()
        # 1. Buscamos por 'user_id'
        res = db.table("proyectos").select("*").eq("user_id", user_id).execute()

        if res.data:
            row = res.data[0]
            # 2. Extraemos el JSON de la columna 'datos'
            d = row.get('datos', {})

            if not d:
                d = {}

            # 3. Cargamos la información desempaquetada
            st.session_state['usuario_id'] = user_id
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
            st.session_state['descripcion_zona'] = d.get('zona_detallada', {})

            # --- HOJA 11 (Indicadores) ---
            st.session_state['datos_indicadores'] = d.get('datos_indicadores', {})
            st.session_state['indicadores_mapa_objetivo'] = d.get('indicadores_mapa_objetivo', {})

            # DataFrames (compatibilidad: records o dict)
            if 'interesados' in d:
                st.session_state['df_interesados'] = _df_from_saved(d.get('interesados'))
            if 'eval_alt' in d:
                st.session_state['df_evaluacion_alternativas'] = _df_from_saved(d.get('eval_alt'))
            if 'rel_obj' in d:
                st.session_state['df_relaciones_objetivos'] = _df_from_saved(d.get('rel_obj'))
            if 'calificaciones' in d:
                st.session_state['df_calificaciones'] = _df_from_saved(d.get('calificaciones'))

    except Exception as e:
        st.error(f"Error al cargar: {e}")


def guardar_datos_nube():
    try:
        db = conectar_db()

        # Empaquetamos todo en un diccionario
        paquete = {
            "integrantes": st.session_state.get('integrantes', []),
            "diagnostico": st.session_state.get('datos_problema', {}),
            "zona": st.session_state.get('datos_zona', {}),
            # Guardado recomendado: records (más estable)
            "interesados": st.session_state.get('df_interesados', pd.DataFrame()).to_dict(orient="records"),
            "analisis_txt": st.session_state.get('analisis_participantes', ""),
            "arbol_p": st.session_state.get('arbol_tarjetas', {}),
            "arbol_o": st.session_state.get('arbol_objetivos', {}),
            "alternativas": st.session_state.get('lista_alternativas', []),
            "eval_alt": st.session_state.get('df_evaluacion_alternativas', pd.DataFrame()).to_dict(orient="records"),
            "rel_obj": st.session_state.get('df_relaciones_objetivos', pd.DataFrame()).to_dict(orient="records"),
            "pesos_eval": st.session_state.get('ponderacion_criterios', {}),
            "calificaciones": st.session_state.get('df_calificaciones', pd.DataFrame()).to_dict(orient="records"),
            "arbol_f": st.session_state.get('arbol_objetivos_final', {}),
            "arbol_p_f": st.session_state.get('arbol_problemas_final', {}),
            "zona_detallada": st.session_state.get('descripcion_zona', {}),

            # --- HOJA 11 (Indicadores) ---
            "datos_indicadores": st.session_state.get('datos_indicadores', {}),
            "indicadores_mapa_objetivo": st.session_state.get('indicadores_mapa_objetivo', {}),
        }

        # Guardamos en la columna 'datos' buscando por 'user_id'
        db.table("proyectos").update({"datos": paquete}).eq("user_id", st.session_state.get('usuario_id', "")).execute()

    except Exception as e:
        st.error(f"Error al guardar: {e}")
