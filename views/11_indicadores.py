import streamlit as st
import pandas as pd
import uuid
import os
import json
import hashlib

from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# 1) Sesión
inicializar_session()

# -----------------------------
# CSS (alineado a Hoja 10)
# -----------------------------
st.markdown(
    """
    <style>
    .block-container { padding-bottom: 220px !important; }

    /* Títulos */
    .titulo-seccion { font-size: 30px !important; font-weight: 900 !important; color: #1E3A8A; margin-bottom: 4px; }
    .subtitulo-gris { font-size: 15px !important; color: #666; margin-bottom: 10px; }
    .subtitulo-seccion { font-size: 20px !important; font-weight: 900 !important; color: #0f172a; margin: 18px 0 8px 0; }
    .subtitulo-seccion-2 { font-size: 20px !important; font-weight: 900 !important; color: #0f172a; margin: 22px 0 8px 0; }

    .ag-root-wrapper { border-radius: 10px; border: 1px solid #eee; margin-bottom: 6px !important; }

    .info-box {
        padding: 10px 12px;
        border-radius: 12px;
        background: rgba(79, 139, 255, 0.10);
        border: 1px solid rgba(79, 139, 255, 0.18);
        color: #1E3A8A;
        font-weight: 700;
        font-size: 13px;
        margin: 6px 0 14px 0;
    }
    .info-box-2 {
        padding: 10px 12px;
        border-radius: 12px;
        background: rgba(16, 185, 129, 0.10);
        border: 1px solid rgba(16, 185, 129, 0.18);
        color: #065f46;
        font-weight: 700;
        font-size: 13px;
        margin: 6px 0 12px 0;
    }
    .legend-box {
        padding: 10px 12px;
        border-radius: 12px;
        background: rgba(2, 132, 199, 0.08);
        border: 1px solid rgba(2, 132, 199, 0.15);
        color: #0c4a6e;
        font-weight: 700;
        font-size: 13px;
        margin: 6px 0 10px 0;
    }
    .legend-box ul { margin: 8px 0 0 18px; }
    .legend-box li { margin: 4px 0; font-weight: 600; }

    .info-box-3 {
        padding: 10px 12px;
        border-radius: 12px;
        background: rgba(245, 158, 11, 0.10);
        border: 1px solid rgba(245, 158, 11, 0.20);
        color: #92400e;
        font-weight: 700;
        font-size: 13px;
        margin: 6px 0 12px 0;
    }

    /* Botón Aplicar selección (solo submit button del formulario) */
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] button {
        background-color: #0F2D6B !important;
        color: #ffffff !important;
        border: 1px solid #0F2D6B !important;
        border-radius: 10px !important;
        font-weight: 900 !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #0B2458 !important;
        border-color: #0B2458 !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Estilos AgGrid (headers + alineación vertical)
# -----------------------------
custom_css_grid = {
    ".ag-header": {
        "background-color": "#F1F5F9 !important",
        "border-bottom": "1px solid #E5E7EB !important",
    },
    ".ag-header-cell-label": {
        "justify-content": "center !important",
        "text-align": "center !important",
    },
    ".ag-header-cell-text": {
        "color": "#0F2D6B !important",
        "font-weight": "900 !important",
        "font-size": "13px !important",
        "width": "100% !important",
        "text-align": "center !important",
    },

    # Importante:
    # No usamos flex para centrar verticalmente porque rompe el autoHeight/wrapText y genera solapamiento.
    # En su lugar dejamos que la fila crezca y damos padding/line-height para legibilidad.
    ".ag-cell": {
        "white-space": "normal !important",
        "line-height": "1.35 !important",
        "padding-top": "6px !important",
        "padding-bottom": "6px !important",
    },
    ".ag-cell-value": {
        "white-space": "normal !important",
        "line-height": "1.35 !important",
    },
}

# -----------------------------
# Helpers
# -----------------------------
def _norm_text(x):
    if x is None:
        return ""
    return str(x).strip()

def _clean_spaces(texto):
    return " ".join(str(texto).split()).strip()

def _as_list(valor):
    if valor is None:
        return []
    if isinstance(valor, list):
        return valor
    return [valor]

def _mk_map_key(nivel, objetivo):
    return f"{_norm_text(nivel)}||{_norm_text(objetivo)}"

def _generar_indicador(obj, cond, lugar):
    obj = _norm_text(obj)
    cond = _norm_text(cond)
    lugar = _norm_text(lugar)
    if not obj and not cond and not lugar:
        return ""
    return _clean_spaces(f"{obj} {cond} {lugar}")

def _ensure_columns(df, cols_defaults):
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()
    for c, v in cols_defaults.items():
        if c not in df.columns:
            df[c] = v
    return df

def _stable_hash_df(df, cols_for_hash):
    try:
        df2 = df.copy()
        df2 = df2.fillna("")
        for c in cols_for_hash:
            if c not in df2.columns:
                df2[c] = ""
        df2 = df2[cols_for_hash].astype(str)
        payload = df2.to_dict(orient="records")
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()
    except Exception:
        return ""

# -----------------------------
# Header + barra de progreso (patrón Hoja 10)
# -----------------------------
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">11. Indicadores</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Definición, selección, metas y medios de verificación.</div>', unsafe_allow_html=True)

    # Progreso (estimado)
    datos_ind = st.session_state.get("datos_indicadores", {})
    sel_ind = st.session_state.get("seleccion_indicadores", {})
    meta_par = st.session_state.get("meta_resultados_parciales", {})
    mv = st.session_state.get("medios_verificacion", {})

    total_campos = 0
    try:
        if isinstance(datos_ind, dict):
            for v in datos_ind.values():
                if isinstance(v, dict):
                    total_campos += sum(1 for k in ["Objeto", "Condicion", "Lugar"] if _norm_text(v.get(k, "")))
        if isinstance(sel_ind, dict):
            for v in sel_ind.values():
                if isinstance(v, dict):
                    total_campos += sum(1 for k in ["P1", "P2", "P3", "P4", "P5"] if bool(v.get(k, False)))
        if isinstance(meta_par, dict):
            for v in meta_par.values():
                if isinstance(v, dict):
                    total_campos += sum(1 for k in ["Línea base", "Meta", "Unidad de medida"] if _norm_text(v.get(k, "")))
        if isinstance(mv, dict):
            for v in mv.values():
                if isinstance(v, dict):
                    total_campos += sum(1 for k in ["FUENTE DE INFORMACION", "METODO DE ANALISIS", "FRECUENCIA DE RECOLECCION", "RESPONSABLE"] if _norm_text(v.get(k, "")))
    except Exception:
        total_campos = 0

    progreso = min(1.0, total_campos / 30) if total_campos > 0 else 0.0
    st.progress(progreso, text=f"Avance estimado: {int(progreso*100)}%")

with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.markdown(
    '<div class="info-box">Diligencia: <b>1. Objeto</b>, <b>2. Condición Deseada</b> y <b>3. Lugar</b>. '
    'Luego valida P1..P5 y define metas. El guardado es automático.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Fuente estricta: Hoja 7 -> arbol_objetivos_final["referencia_manual"]
# -----------------------------
arbol = st.session_state.get("arbol_objetivos_final", {})
if not isinstance(arbol, dict):
    arbol = {}

ref = arbol.get("referencia_manual", None)
if not isinstance(ref, dict):
    st.error("Falta la tabla superior de Hoja 7 (referencia_manual). En Hoja 7 pestaña 2 presiona: “Sincronizar con Árbol”.")
    st.stop()

obj_general = _norm_text(ref.get("objetivo", ""))
especificos = _as_list(ref.get("especificos", []))
actividades = _as_list(ref.get("actividades", []))

if not obj_general and len(especificos) == 0 and len(actividades) == 0:
    st.error("La tabla superior de Hoja 7 está vacía. En Hoja 7 pestaña 2 presiona: “Sincronizar con Árbol”.")
    st.stop()

especificos = [_norm_text(x) for x in especificos if _norm_text(x)]
actividades = [_norm_text(x) for x in actividades if _norm_text(x)]

# -----------------------------
# Estado hoja 11
# -----------------------------
if "indicadores_mapa_objetivo" not in st.session_state or not isinstance(st.session_state.get("indicadores_mapa_objetivo"), dict):
    st.session_state["indicadores_mapa_objetivo"] = {}

def _resolve_key(nivel, objetivo_txt):
    kmap = _mk_map_key(nivel, objetivo_txt)
    if kmap in st.session_state["indicadores_mapa_objetivo"]:
        return st.session_state["indicadores_mapa_objetivo"][kmap]
    new_key = str(uuid.uuid4())
    st.session_state["indicadores_mapa_objetivo"][kmap] = new_key
    return new_key

if "datos_indicadores" not in st.session_state or not isinstance(st.session_state.get("datos_indicadores"), dict):
    st.session_state["datos_indicadores"] = {}

if "hash_indicadores" not in st.session_state:
    st.session_state["hash_indicadores"] = ""

if "seleccion_indicadores" not in st.session_state or not isinstance(st.session_state.get("seleccion_indicadores"), dict):
    st.session_state["seleccion_indicadores"] = {}

if "duracion_proyecto_periodos" not in st.session_state:
    st.session_state["duracion_proyecto_periodos"] = 4

if "meta_resultados_parciales" not in st.session_state or not isinstance(st.session_state.get("meta_resultados_parciales"), dict):
    st.session_state["meta_resultados_parciales"] = {}

if "hash_meta_resultados_parciales" not in st.session_state:
    st.session_state["hash_meta_resultados_parciales"] = ""

if "medios_verificacion" not in st.session_state or not isinstance(st.session_state.get("medios_verificacion"), dict):
    st.session_state["medios_verificacion"] = {}

if "hash_medios_verificacion" not in st.session_state:
    st.session_state["hash_medios_verificacion"] = ""

# -----------------------------
# Construcción filas base desde referencia_manual Hoja 7
# -----------------------------
def _build_rows_from_ref():
    rows = []
    if obj_general:
        rows.append(("Objetivo General", obj_general))
    for e in especificos:
        rows.append(("Objetivo Específico (Componente)", e))
    for a in actividades:
        rows.append(("Actividad Clave", a))
    return rows

# -----------------------------
# Tabla 1: Indicadores
# -----------------------------
cols_defaults = {
    "_key": "",
    "Nivel": "",
    "Objetivo": "",
    "1. Objeto": "",
    "2. Condición Deseada": "",
    "3. Lugar": "",
    "Indicador Generado": "",
}
target_cols = list(cols_defaults.keys())

rows = []
for nivel, objetivo_txt in _build_rows_from_ref():
    k = _resolve_key(nivel, objetivo_txt)
    guard = st.session_state["datos_indicadores"].get(k, {})

    rows.append({
        "_key": k,
        "Nivel": nivel,
        "Objetivo": objetivo_txt,
        "1. Objeto": _norm_text(guard.get("Objeto", "")),
        "2. Condición Deseada": _norm_text(guard.get("Condicion", "")),
        "3. Lugar": _norm_text(guard.get("Lugar", "")),
        "Indicador Generado": "",
    })

df_ind = pd.DataFrame(rows)
df_ind = _ensure_columns(df_ind, cols_defaults)
df_ind = df_ind[target_cols].copy()

gb = GridOptionsBuilder.from_dataframe(df_ind)
gb.configure_column("_key", headerName="_key", editable=False, hide=True)
gb.configure_column("Nivel", headerName="Nivel", editable=False, wrapText=True, autoHeight=True, width=220)
gb.configure_column("Objetivo", headerName="Objetivo", editable=False, wrapText=True, autoHeight=True, width=560)
gb.configure_column("1. Objeto", headerName="1. Objeto", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("2. Condición Deseada", headerName="2. Condición Deseada", editable=True, wrapText=True, autoHeight=True, width=300)
gb.configure_column("3. Lugar", headerName="3. Lugar", editable=True, wrapText=True, autoHeight=True, width=190)

value_getter_indicador = JsCode("""
function(params) {
  const a = (params.data && params.data["1. Objeto"]) ? String(params.data["1. Objeto"]).trim() : "";
  const b = (params.data && params.data["2. Condición Deseada"]) ? String(params.data["2. Condición Deseada"]).trim() : "";
  const c = (params.data && params.data["3. Lugar"]) ? String(params.data["3. Lugar"]).trim() : "";
  let s = (a + " " + b + " " + c).replace(/\s+/g, " ").trim();
  return s;
}
""")
gb.configure_column("Indicador Generado", headerName="Indicador Generado", editable=False, wrapText=True, autoHeight=True, width=520, valueGetter=value_getter_indicador)
gb.configure_grid_options(domLayout="autoHeight", enableCellTextSelection=True, ensureDomOrder=True)
gridOptions = gb.build()

grid_response = AgGrid(
    df_ind,
    gridOptions=gridOptions,
    custom_css=custom_css_grid,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    key="grid_indicadores"
)

df_ind_live = pd.DataFrame(grid_response.get("data", []))
df_ind_live = _ensure_columns(df_ind_live, cols_defaults)
df_ind_live = df_ind_live[target_cols].copy()

hash_actual_1 = _stable_hash_df(df_ind_live, ["_key", "1. Objeto", "2. Condición Deseada", "3. Lugar"])
if hash_actual_1 and hash_actual_1 != st.session_state.get("hash_indicadores", ""):
    st.session_state["hash_indicadores"] = hash_actual_1
    for _, r in df_ind_live.iterrows():
        k = _norm_text(r.get("_key", ""))
        if not k:
            continue
        obj = _norm_text(r.get("1. Objeto", ""))
        cond = _norm_text(r.get("2. Condición Deseada", ""))
        lugar = _norm_text(r.get("3. Lugar", ""))
        st.session_state["datos_indicadores"][k] = {
            "Nivel": _norm_text(r.get("Nivel", "")),
            "Objetivo": _norm_text(r.get("Objetivo", "")),
            "Objeto": obj,
            "Condicion": cond,
            "Lugar": lugar,
            "Indicador": _generar_indicador(obj, cond, lugar),
        }
    guardar_datos_nube()

# -----------------------------
# Tabla 2: Selección de indicadores
# -----------------------------
st.markdown('<div class="subtitulo-seccion">Selección de indicadores</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-2">Marca las validaciones. La columna <b>Selección</b> será <b>Sí</b> solo si todas están chuleadas. '
    'Fila verde tenue si es <b>Sí</b>, rojo tenue si es <b>No</b>. Para fijar la selección presiona <b>Aplicar selección</b>.</div>',
    unsafe_allow_html=True
)

P1, P2, P3, P4, P5 = "P1", "P2", "P3", "P4", "P5"
P_COLS = [P1, P2, P3, P4, P5]

Q1 = "El Sentido del indicador es claro"
Q2 = "Existe información disponible o se puede recolectar fácilmente"
Q3 = "El indicador es tangible y se puede observar"
Q4 = "La tarea de recolectar datos está al alcance del proyecto y no requiere expertos para su análisis"
Q5 = "El indicador es lo bastante representativo para el conjunto de resultados e impactos"

st.markdown(
    f"""
    <div class="legend-box">
      <div><b>Convenciones</b></div>
      <ul>
        <li><b>{P1}:</b> {Q1}</li>
        <li><b>{P2}:</b> {Q2}</li>
        <li><b>{P3}:</b> {Q3}</li>
        <li><b>{P4}:</b> {Q4}</li>
        <li><b>{P5}:</b> {Q5}</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True
)

sel_rows = []
for nivel, objetivo_txt in _build_rows_from_ref():
    k = _resolve_key(nivel, objetivo_txt)
    ind = _norm_text(st.session_state.get("datos_indicadores", {}).get(k, {}).get("Indicador", ""))
    sel = st.session_state.get("seleccion_indicadores", {}).get(k, {})
    a = bool(sel.get(P1, False))
    b = bool(sel.get(P2, False))
    c = bool(sel.get(P3, False))
    d = bool(sel.get(P4, False))
    e = bool(sel.get(P5, False))
    sel_rows.append({
        "_key": k,
        "Nivel": nivel,
        "Objetivo": objetivo_txt,
        "Indicador": ind,
        P1: a, P2: b, P3: c, P4: d, P5: e,
        "Selección": "Sí" if (a and b and c and d and e) else "No"
    })

df_sel = pd.DataFrame(sel_rows)
df_sel = _ensure_columns(df_sel, {"_key":"", "Nivel":"", "Objetivo":"", "Indicador":"", P1:False, P2:False, P3:False, P4:False, P5:False, "Selección":"No"})
df_sel = df_sel[["_key","Nivel","Objetivo","Indicador",P1,P2,P3,P4,P5,"Selección"]].copy()

js_value_getter_sel = JsCode("""
function(params) {
    const a = !!params.data['P1'];
    const b = !!params.data['P2'];
    const c = !!params.data['P3'];
    const d = !!params.data['P4'];
    const e = !!params.data['P5'];
    return (a && b && c && d && e) ? 'Sí' : 'No';
}
""")
js_row_style = JsCode("""
function(params) {
    const a = !!params.data['P1'];
    const b = !!params.data['P2'];
    const c = !!params.data['P3'];
    const d = !!params.data['P4'];
    const e = !!params.data['P5'];
    const ok = (a && b && c && d && e);
    return ok ? {'backgroundColor': '#ecfdf5'} : {'backgroundColor': '#fef2f2'};
}
""")
gb2 = GridOptionsBuilder.from_dataframe(df_sel)
gb2.configure_column("_key", headerName="_key", editable=False, hide=True)
gb2.configure_column("Nivel", headerName="Nivel", editable=False, wrapText=True, autoHeight=True, width=220)
gb2.configure_column("Objetivo", headerName="Objetivo", editable=False, wrapText=True, autoHeight=True, width=520)
gb2.configure_column("Indicador", headerName="Indicador", editable=False, wrapText=True, autoHeight=True, width=520)
for p in P_COLS:
    gb2.configure_column(p, headerName=p, editable=True, width=80, cellRenderer="agCheckboxCellRenderer", cellEditor="agCheckboxCellEditor")
gb2.configure_column("Selección", headerName="Selección", editable=False, width=110, valueGetter=js_value_getter_sel)
gb2.configure_grid_options(getRowStyle=js_row_style, domLayout="autoHeight")
gridOptions2 = gb2.build()

grid_response_2 = AgGrid(
    df_sel,
    gridOptions=gridOptions2,
    custom_css=custom_css_grid,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    key="grid_seleccion_indicadores"
)

c_apply_1, c_apply_2 = st.columns([1, 5], vertical_alignment="center")
with c_apply_1:
    with st.form("form_aplicar_seleccion", clear_on_submit=False):
        aplicar = st.form_submit_button("Aplicar selección", use_container_width=True)
with c_apply_2:
    st.caption("Use este botón para guardar las selecciones y actualizar las tablas siguientes.")

if aplicar:
    df_sel_live = pd.DataFrame(grid_response_2.get("data", []))
    df_sel_live = _ensure_columns(df_sel_live, {"_key":"", P1:False, P2:False, P3:False, P4:False, P5:False})
    if "_key" not in df_sel_live.columns or df_sel_live["_key"].astype(str).eq("").all():
        df_sel_live["_key"] = df_sel["_key"].values[: len(df_sel_live)]

    for _, r in df_sel_live.iterrows():
        k = _norm_text(r.get("_key", ""))
        if not k:
            continue
        st.session_state["seleccion_indicadores"][k] = {
            P1: bool(r.get(P1, False)),
            P2: bool(r.get(P2, False)),
            P3: bool(r.get(P3, False)),
            P4: bool(r.get(P4, False)),
            P5: bool(r.get(P5, False)),
        }

    # limpieza: solo conservar meta/mv de seleccionados
    keys_si_now = []
    for k, sel in st.session_state.get("seleccion_indicadores", {}).items():
        if all(bool(sel.get(p, False)) for p in P_COLS):
            keys_si_now.append(k)

    actuales = set(keys_si_now)
    for k in list(set(st.session_state.get("meta_resultados_parciales", {}).keys()) - actuales):
        st.session_state["meta_resultados_parciales"].pop(k, None)
    for k in list(set(st.session_state.get("medios_verificacion", {}).keys()) - actuales):
        st.session_state["medios_verificacion"].pop(k, None)

    guardar_datos_nube()
    st.rerun()

# -----------------------------
# META Y RESULTADOS PARCIALES
# -----------------------------
st.markdown('<div class="subtitulo-seccion-2">META Y RESULTADOS PARCIALES</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-3">Indica la cantidad de periodos (número entero). Se crearán columnas dinámicas Periodo 1..N.</div>',
    unsafe_allow_html=True
)

dur = st.number_input(
    "¿Cuántos periodos dura su proyecto?",
    min_value=1,
    step=1,
    value=int(st.session_state.get("duracion_proyecto_periodos", 4))
)
dur = int(dur)
if dur != int(st.session_state.get("duracion_proyecto_periodos", 4)):
    st.session_state["duracion_proyecto_periodos"] = dur
    guardar_datos_nube()

# claves seleccionadas Sí
keys_si = []
for k, sel in st.session_state.get("seleccion_indicadores", {}).items():
    if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in P_COLS):
        keys_si.append(k)

if not keys_si:
    st.info("Aún no hay indicadores con Selección = Sí. Marca P1..P5 y presiona “Aplicar selección”.")
else:
    period_cols = [f"Periodo {i}" for i in range(1, dur + 1)]
    meta_defaults = {"_key":"", "Indicador":"", "Línea base":"", "Meta":"", "Unidad de medida":""}
    for pc in period_cols:
        meta_defaults[pc] = ""

    rows_meta = []
    for k in keys_si:
        ind_txt = _norm_text(st.session_state.get("datos_indicadores", {}).get(k, {}).get("Indicador", ""))
        guard = st.session_state.get("meta_resultados_parciales", {}).get(k, {})
        per_guard = guard.get("Periodos", {}) if isinstance(guard.get("Periodos", {}), dict) else {}
        row = {
            "_key": k,
            "Indicador": ind_txt,
            "Línea base": _norm_text(guard.get("Línea base", "")),
            "Meta": _norm_text(guard.get("Meta", "")),
            "Unidad de medida": _norm_text(guard.get("Unidad de medida", "")),
        }
        for pc in period_cols:
            row[pc] = _norm_text(per_guard.get(pc, ""))
        rows_meta.append(row)

    df_meta = pd.DataFrame(rows_meta)
    df_meta = _ensure_columns(df_meta, meta_defaults)
    meta_cols = ["_key","Indicador","Línea base","Meta","Unidad de medida"] + period_cols
    df_meta = df_meta[meta_cols].copy()

    gb3 = GridOptionsBuilder.from_dataframe(df_meta)
    gb3.configure_column("_key", headerName="_key", editable=False, hide=True)
    gb3.configure_column("Indicador", headerName="Indicador", editable=False, wrapText=True, autoHeight=True, width=520)
    gb3.configure_column("Línea base", headerName="Línea base", editable=True, width=140)
    gb3.configure_column("Meta", headerName="Meta", editable=True, width=110)
    gb3.configure_column("Unidad de medida", headerName="Unidad de medida", editable=True, width=180)
    for pc in period_cols:
        gb3.configure_column(pc, headerName=pc, editable=True, width=120)
    gb3.configure_grid_options(domLayout="autoHeight")
    gridOptions3 = gb3.build()

    grid_response_3 = AgGrid(
        df_meta,
        gridOptions=gridOptions3,
        custom_css=custom_css_grid,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        key="grid_meta_resultados_parciales"
    )

    df_meta_live = pd.DataFrame(grid_response_3.get("data", []))
    df_meta_live = _ensure_columns(df_meta_live, meta_defaults)
    if "_key" not in df_meta_live.columns or df_meta_live["_key"].astype(str).eq("").all():
        df_meta_live["_key"] = df_meta["_key"].values[: len(df_meta_live)]
    df_meta_live = df_meta_live[meta_cols].copy()

    hash_meta = _stable_hash_df(df_meta_live, ["_key","Línea base","Meta","Unidad de medida"] + period_cols)
    if hash_meta and hash_meta != st.session_state.get("hash_meta_resultados_parciales", ""):
        st.session_state["hash_meta_resultados_parciales"] = hash_meta
        for _, r in df_meta_live.iterrows():
            k = _norm_text(r.get("_key", ""))
            if not k:
                continue
            st.session_state["meta_resultados_parciales"][k] = {
                "Línea base": _norm_text(r.get("Línea base", "")),
                "Meta": _norm_text(r.get("Meta", "")),
                "Unidad de medida": _norm_text(r.get("Unidad de medida", "")),
                "Periodos": {pc: _norm_text(r.get(pc, "")) for pc in period_cols}
            }
        guardar_datos_nube()

# -----------------------------
# MEDIOS DE VERIFICACIÓN
# -----------------------------
st.markdown('<div class="subtitulo-seccion-2">MEDIOS DE VERIFICACIÓN</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-2">Tipo, Objetivo, Indicador y Meta se cargan automáticamente. Las demás casillas son de libre diligenciamiento.</div>',
    unsafe_allow_html=True
)

MV_LIBRES = ["FUENTE DE INFORMACION", "METODO DE ANALISIS", "FRECUENCIA DE RECOLECCION", "RESPONSABLE"]

def _tipo_from_nivel(nivel_txt: str) -> str:
    n = _norm_text(nivel_txt)
    if n == "Objetivo General":
        return "OBJETIVO GENERAL"
    if n.startswith("Objetivo Específico"):
        return "OBJETIVO ESPECIFICO"
    if n == "Actividad Clave":
        return "ACTIVIDAD"
    return n.upper() if n else ""

if not keys_si:
    st.info("Aún no hay indicadores con Selección = Sí. Marca P1..P5 y presiona “Aplicar selección”.")
else:
    rows_mv = []
    for k in keys_si:
        base = st.session_state.get("datos_indicadores", {}).get(k, {})
        nivel = _norm_text(base.get("Nivel", ""))
        objetivo_txt = _norm_text(base.get("Objetivo", ""))
        indicador_txt = _norm_text(base.get("Indicador", ""))

        meta_txt = _norm_text(st.session_state.get("meta_resultados_parciales", {}).get(k, {}).get("Meta", ""))

        guard = st.session_state.get("medios_verificacion", {}).get(k, {})
        row = {
            "_key": k,
            "Tipo": _tipo_from_nivel(nivel),
            "Objetivo": objetivo_txt,
            "Indicador": indicador_txt,
            "Meta": meta_txt,
        }
        for c in MV_LIBRES:
            row[c] = _norm_text(guard.get(c, ""))
        rows_mv.append(row)

    df_mv = pd.DataFrame(rows_mv)
    mv_defaults = {"_key":"", "Tipo":"", "Objetivo":"", "Indicador":"", "Meta":""}
    for c in MV_LIBRES:
        mv_defaults[c] = ""
    df_mv = _ensure_columns(df_mv, mv_defaults)
    mv_cols = ["_key","Tipo","Objetivo","Indicador","Meta"] + MV_LIBRES
    df_mv = df_mv[mv_cols].copy()

    gb4 = GridOptionsBuilder.from_dataframe(df_mv)
    gb4.configure_column("_key", headerName="_key", editable=False, hide=True)
    gb4.configure_column("Tipo", headerName="Tipo", editable=False, width=190, wrapText=True, autoHeight=True)
    gb4.configure_column("Objetivo", headerName="Objetivo", editable=False, width=520, wrapText=True, autoHeight=True)
    gb4.configure_column("Indicador", headerName="Indicador", editable=False, width=520, wrapText=True, autoHeight=True)
    gb4.configure_column("Meta", headerName="Meta", editable=False, width=110)
    for c in MV_LIBRES:
        gb4.configure_column(c, headerName=c, editable=True, width=220, wrapText=True, autoHeight=True)
    gb4.configure_grid_options(domLayout="autoHeight")
    gridOptions4 = gb4.build()

    grid_response_4 = AgGrid(
        df_mv,
        gridOptions=gridOptions4,
        custom_css=custom_css_grid,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        key="grid_medios_verificacion"
    )

    df_mv_live = pd.DataFrame(grid_response_4.get("data", []))
    df_mv_live = _ensure_columns(df_mv_live, mv_defaults)
    if "_key" not in df_mv_live.columns or df_mv_live["_key"].astype(str).eq("").all():
        df_mv_live["_key"] = df_mv["_key"].values[: len(df_mv_live)]
    df_mv_live = df_mv_live[mv_cols].copy()

    hash_mv = _stable_hash_df(df_mv_live, ["_key"] + MV_LIBRES)
    if hash_mv and hash_mv != st.session_state.get("hash_medios_verificacion", ""):
        st.session_state["hash_medios_verificacion"] = hash_mv
        for _, r in df_mv_live.iterrows():
            k = _norm_text(r.get("_key", ""))
            if not k:
                continue
            st.session_state["medios_verificacion"][k] = {c: _norm_text(r.get(c, "")) for c in MV_LIBRES}
        guardar_datos_nube()
