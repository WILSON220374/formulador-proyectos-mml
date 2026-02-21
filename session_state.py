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




def _safe_int(value, default: int = 2026) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        if isinstance(value, (int, float)):
            return int(value)
        s = str(value).strip()
        if s == "":
            return default
        return int(float(s))
    except Exception:
        return default


def _normalize_tabla_deficit(obj):
    """Normaliza tabla_deficit al formato esperado por Hoja 14:
    dict[str, {"dem": float, "ofe": float}]
    Acepta:
      - dict ya normalizado
      - dict con otras llaves
      - list[dict] tipo records (AÑO, CANTIDAD DEMANDADA, CANTIDAD OFERTADA)
      - DataFrame (convertido a records)
    """
    if obj is None:
        return {}

    # DataFrame -> records
    if isinstance(obj, pd.DataFrame):
        obj = obj.to_dict(orient="records")

    # records
    if isinstance(obj, list):
        out = {}
        for row in obj:
            if not isinstance(row, dict):
                continue
            # claves posibles
            a = row.get("AÑO", row.get("Año", row.get("anio", row.get("year"))))
            if a is None:
                continue
            k = str(int(float(a))) if str(a).strip() != "" else None
            if not k:
                continue

            dem = row.get("dem", row.get("Demanda", row.get("CANTIDAD DEMANDADA", row.get("cantidad_demandada", 0))))
            ofe = row.get("ofe", row.get("Oferta", row.get("CANTIDAD OFERTADA", row.get("cantidad_ofertada", 0))))

            try:
                dem_f = float(dem) if dem is not None and str(dem).strip() != "" else 0.0
            except Exception:
                dem_f = 0.0
            try:
                ofe_f = float(ofe) if ofe is not None and str(ofe).strip() != "" else 0.0
            except Exception:
                ofe_f = 0.0

            out[k] = {"dem": dem_f, "ofe": ofe_f}
        return out

    # dict
    if isinstance(obj, dict):
        # caso ya normalizado por año -> {dem, ofe}
        # o por año -> {"Demanda":..., "Oferta":...}
        out = {}
        for year_key, val in obj.items():
            try:
                y = str(int(float(str(year_key).strip())))
            except Exception:
                # si la llave no es año, ignorar
                continue

            if isinstance(val, pd.DataFrame):
                # inesperado: intentar leer primera fila
                val = val.to_dict(orient="records")

            if isinstance(val, list):
                # si viene como lista de filas para un año
                # tomar primera fila si tiene dem/ofe
                if val:
                    vv = val[0] if isinstance(val[0], dict) else {}
                    val = vv
                else:
                    val = {}

            if isinstance(val, dict):
                dem = val.get("dem", val.get("Demanda", val.get("CANTIDAD DEMANDADA", val.get("cantidad_demandada", 0))))
                ofe = val.get("ofe", val.get("Oferta", val.get("CANTIDAD OFERTADA", val.get("cantidad_ofertada", 0))))
            else:
                dem, ofe = 0, 0

            try:
                dem_f = float(dem) if dem is not None and str(dem).strip() != "" else 0.0
            except Exception:
                dem_f = 0.0
            try:
                ofe_f = float(ofe) if ofe is not None and str(ofe).strip() != "" else 0.0
            except Exception:
                ofe_f = 0.0

            out[y] = {"dem": dem_f, "ofe": ofe_f}
        return out

    return {}
def inicializar_session():
    # --- AJUSTE VISUAL PARA QUE NO TENGAS QUE HACER SCROLL ---
    st.markdown(
        """
        <style>
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

    # --- HOJA 10 (Descripción del problema) ---
    if 'descripcion_problema' not in st.session_state:
        st.session_state['descripcion_problema'] = {
            "tabla_datos": {},
            "redaccion_narrativa": "",
            "antecedentes": ""
        }

    # --- HOJA 11 (Indicadores) ---
    if 'datos_indicadores' not in st.session_state:
        st.session_state['datos_indicadores'] = {}
    if 'indicadores_mapa_objetivo' not in st.session_state:
        st.session_state['indicadores_mapa_objetivo'] = {}

    # NUEVO: selección de indicadores (tabla 2)
    if 'seleccion_indicadores' not in st.session_state:
        st.session_state['seleccion_indicadores'] = {}

    # NUEVO: meta y resultados parciales (duración + tabla)
    if 'duracion_proyecto_periodos' not in st.session_state:
        st.session_state['duracion_proyecto_periodos'] = 4
    if 'meta_resultados_parciales' not in st.session_state:
        st.session_state['meta_resultados_parciales'] = {}

    # --- HOJA 14 (Necesidad) ---
    # Nota: la Hoja 14 espera tipos específicos:
    # - anio_formulacion: int
    # - tabla_deficit: dict[str, {"dem": float, "ofe": float}]
    if 'desc_objetivo_general' not in st.session_state:
        st.session_state['desc_objetivo_general'] = ""
    if 'necesidad_atender' not in st.session_state:
        st.session_state['necesidad_atender'] = ""
    if 'anio_formulacion' not in st.session_state:
        st.session_state['anio_formulacion'] = 2026
    if 'tabla_deficit' not in st.session_state:
        st.session_state['tabla_deficit'] = {}

    # --- HOJA 15 (Producto) ---
    if 'sector_seleccionado' not in st.session_state:
        st.session_state['sector_seleccionado'] = "Seleccione..."
    if 'programa_seleccionado' not in st.session_state:
        st.session_state['programa_seleccionado'] = "Seleccione..."
    if 'producto_seleccionado' not in st.session_state:
        st.session_state['producto_seleccionado'] = "Seleccione..."
    if 'producto_seleccionado_label' not in st.session_state:
        st.session_state['producto_seleccionado_label'] = "Seleccione..."
    if 'producto_principal' not in st.session_state:
        st.session_state['producto_principal'] = {}
    if 'nombre_proyecto_libre' not in st.session_state:
        st.session_state['nombre_proyecto_libre'] = ""
    if 'plan_nombre' not in st.session_state:
        st.session_state['plan_nombre'] = ""
    if 'plan_eje' not in st.session_state:
        st.session_state['plan_eje'] = ""
    if 'plan_programa' not in st.session_state:
        st.session_state['plan_programa'] = ""


    # NUEVO: medios de verificación (Hoja 11 - tabla final)
    if 'medios_verificacion' not in st.session_state:
        st.session_state['medios_verificacion'] = {}

    # NUEVO: hoja 12 (Riesgos)
    # Nota: NO inicializamos 'datos_riesgos' aquí.
    # La Hoja 12 construye la matriz a partir de los objetivos (Hoja 7) cuando la clave NO existe.


def cargar_datos_nube(user_id):
    try:
        db = conectar_db()
        res = db.table("proyectos").select("*").eq("user_id", user_id).execute()

        if res.data:
            row = res.data[0]
            d = row.get('datos', {}) or {}

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

            # --- HOJA 10 (Descripción del problema) ---
            st.session_state['descripcion_problema'] = d.get('descripcion_problema', st.session_state.get('descripcion_problema', {
                "tabla_datos": {},
                "redaccion_narrativa": "",
                "antecedentes": ""
            }))

            # --- HOJA 11 (Indicadores) ---
            st.session_state['datos_indicadores'] = d.get('datos_indicadores', {})
            st.session_state['indicadores_mapa_objetivo'] = d.get('indicadores_mapa_objetivo', {})

            # NUEVO: selección de indicadores (tabla 2)
            st.session_state['seleccion_indicadores'] = d.get('seleccion_indicadores', {})

            # NUEVO: meta y resultados parciales
            st.session_state['duracion_proyecto_periodos'] = d.get('duracion_proyecto_periodos', 4)
            st.session_state['meta_resultados_parciales'] = d.get('meta_resultados_parciales', {})

            # NUEVO: medios de verificación (Hoja 11 - tabla final)
            st.session_state['medios_verificacion'] = d.get('medios_verificacion', {})

            # --- HOJA 14 (Necesidad) ---
            st.session_state['desc_objetivo_general'] = d.get('desc_objetivo_general', st.session_state.get('desc_objetivo_general', ""))
            st.session_state['necesidad_atender'] = d.get('necesidad_atender', st.session_state.get('necesidad_atender', ""))
            st.session_state['anio_formulacion'] = _safe_int(d.get('anio_formulacion', st.session_state.get('anio_formulacion', 2026)), 2026)
            st.session_state['tabla_deficit'] = _normalize_tabla_deficit(d.get('tabla_deficit', st.session_state.get('tabla_deficit', {})))


            # --- HOJA 15 (Producto) ---
            st.session_state['sector_seleccionado'] = d.get('sector_seleccionado', st.session_state.get('sector_seleccionado', "Seleccione..."))
            st.session_state['programa_seleccionado'] = d.get('programa_seleccionado', st.session_state.get('programa_seleccionado', "Seleccione..."))
            st.session_state['producto_seleccionado'] = d.get('producto_seleccionado', st.session_state.get('producto_seleccionado', "Seleccione..."))
            st.session_state['producto_seleccionado_label'] = d.get('producto_seleccionado_label', st.session_state.get('producto_seleccionado_label', "Seleccione..."))
            st.session_state['producto_principal'] = d.get('producto_principal', st.session_state.get('producto_principal', {}))
            st.session_state['nombre_proyecto_libre'] = d.get('nombre_proyecto_libre', st.session_state.get('nombre_proyecto_libre', ""))
            st.session_state['plan_nombre'] = d.get('plan_nombre', st.session_state.get('plan_nombre', ""))
            st.session_state['plan_eje'] = d.get('plan_eje', st.session_state.get('plan_eje', ""))
            st.session_state['plan_programa'] = d.get('plan_programa', st.session_state.get('plan_programa', ""))
            # NUEVO: hoja 12 (Riesgos)
            if 'datos_riesgos' in d:
                st.session_state['datos_riesgos'] = _df_from_saved(d.get('datos_riesgos'))
            elif 'riesgos' in d:
                # Compatibilidad si el key se guardó como 'riesgos'
                st.session_state['datos_riesgos'] = _df_from_saved(d.get('riesgos'))
            else:
                # Si no hay datos persistidos, eliminamos la clave para que la Hoja 12 la genere desde los objetivos.
                st.session_state.pop('datos_riesgos', None)
            # Validación: si se cargó un DataFrame vacío o sin la columna clave,
            # eliminamos la clave para que la Hoja 12 regenere la matriz desde los objetivos (Hoja 7).
            if 'datos_riesgos' in st.session_state:
                dr = st.session_state.get('datos_riesgos')
                if (not isinstance(dr, pd.DataFrame)) or dr.empty or ('Objetivo' not in dr.columns):
                    st.session_state.pop('datos_riesgos', None)


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

            # --- HOJA 10 (Descripción del problema) ---
            "descripcion_problema": st.session_state.get('descripcion_problema', {
                "tabla_datos": {},
                "redaccion_narrativa": "",
                "antecedentes": ""
            }),

            # --- HOJA 11 (Indicadores) ---
            "datos_indicadores": st.session_state.get('datos_indicadores', {}),
            "indicadores_mapa_objetivo": st.session_state.get('indicadores_mapa_objetivo', {}),

            # NUEVO: selección de indicadores (tabla 2)
            "seleccion_indicadores": st.session_state.get('seleccion_indicadores', {}),

            # NUEVO: meta y resultados parciales
            "duracion_proyecto_periodos": st.session_state.get('duracion_proyecto_periodos', 4),
            "meta_resultados_parciales": st.session_state.get('meta_resultados_parciales', {}),

            # NUEVO: medios de verificación (Hoja 11 - tabla final)
            "medios_verificacion": st.session_state.get('medios_verificacion', {}),

            # NUEVO: hoja 12 (Riesgos) - guardado como records
            "datos_riesgos": (
                st.session_state.get('datos_riesgos', pd.DataFrame()).to_dict(orient="records")
                if isinstance(st.session_state.get('datos_riesgos', None), pd.DataFrame)
                else pd.DataFrame(st.session_state.get('datos_riesgos', []) or []).to_dict(orient="records")
            ),
       

            # --- HOJA 15 (Producto) ---
            "sector_seleccionado": st.session_state.get('sector_seleccionado', "Seleccione..."),
            "programa_seleccionado": st.session_state.get('programa_seleccionado', "Seleccione..."),
            "producto_seleccionado": st.session_state.get('producto_seleccionado', "Seleccione..."),
            "producto_seleccionado_label": st.session_state.get('producto_seleccionado_label', "Seleccione..."),
            "producto_principal": st.session_state.get('producto_principal', {}),
            "nombre_proyecto_libre": st.session_state.get('nombre_proyecto_libre', ""),
            "plan_nombre": st.session_state.get('plan_nombre', ""),
            "plan_eje": st.session_state.get('plan_eje', ""),
            "plan_programa": st.session_state.get('plan_programa', ""),
            # --- HOJA 14 (Necesidad) ---
            "desc_objetivo_general": st.session_state.get('desc_objetivo_general', ""),
            "necesidad_atender": st.session_state.get('necesidad_atender', ""),
            "anio_formulacion": _safe_int(st.session_state.get('anio_formulacion', 2026), 2026),
            "tabla_deficit": _normalize_tabla_deficit(st.session_state.get('tabla_deficit', {})),
        }

        db.table("proyectos").update({"datos": paquete}).eq("user_id", st.session_state.get('usuario_id', "")).execute()

    except Exception as e:
        st.error(f"Error al guardar: {e}")
