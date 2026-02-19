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
# CSS
# -----------------------------
st.markdown(
    """
    <style>
    .block-container { padding-bottom: 170px !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 900 !important; color: #1E3A8A; margin-bottom: 4px; }
    .subtitulo-gris { font-size: 15px !important; color: #666; margin-bottom: 10px; }
    .subtitulo-seccion { font-size: 20px !important; font-weight: 900 !important; color: #0f172a; margin: 18px 0 8px 0; }
    [data-testid="stImage"] img { border-radius: 12px; }

    .ag-root-wrapper { border-radius: 10px; border: 1px solid #eee; margin-bottom: 6px !important; }
    .ag-header-cell-label { justify-content: center !important; text-align: center !important; }
    .ag-header-cell-text { width: 100%; text-align: center; }

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
    </style>
    """,
    unsafe_allow_html=True
)

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

def _resolve_key(nivel, objetivo_txt):
    if 'indicadores_mapa_objetivo' not in st.session_state or not isinstance(st.session_state.get('indicadores_mapa_objetivo'), dict):
        st.session_state['indicadores_mapa_objetivo'] = {}

    kmap = _mk_map_key(nivel, objetivo_txt)
    if kmap in st.session_state['indicadores_mapa_objetivo']:
        return st.session_state['indicadores_mapa_objetivo'][kmap]

    new_key = str(uuid.uuid4())
    st.session_state['indicadores_mapa_objetivo'][kmap] = new_key
    return new_key

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
# Header
# -----------------------------
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📊 11. Indicadores</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Fuente única: Tabla superior de Hoja 7 (Alternativa Seleccionada). Guardado automático en nube.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.markdown(
    '<div class="info-box">Diligencia: <b>1. Objeto</b>, <b>2. Condición Deseada</b> y <b>3. Lugar</b>. '
    'El indicador se genera al instante dentro de la tabla y se guarda automáticamente en la nube.</div>',
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
# State hoja 11
# -----------------------------
if "datos_indicadores" not in st.session_state or not isinstance(st.session_state.get("datos_indicadores"), dict):
    st.session_state["datos_indicadores"] = {}

if "df_indicadores" not in st.session_state or not isinstance(st.session_state.get("df_indicadores"), pd.DataFrame):
    st.session_state["df_indicadores"] = pd.DataFrame()

if "hash_indicadores" not in st.session_state:
    st.session_state["hash_indicadores"] = ""

if "seleccion_indicadores" not in st.session_state or not isinstance(st.session_state.get("seleccion_indicadores"), dict):
    st.session_state["seleccion_indicadores"] = {}

if "hash_seleccion_indicadores" not in st.session_state:
    st.session_state["hash_seleccion_indicadores"] = ""

# -----------------------------
# Construcción filas base desde referencia_manual
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
# Tabla 1: Indicadores (AgGrid)
# -----------------------------
cols_defaults = {
    "Nivel": "",
    "Objetivo": "",
    "1. Objeto": "",
    "2. Condición Deseada": "",
    "3. Lugar": "",
    "Indicador Generado": "",
}
target_cols = list(cols_defaults.keys())

def _build_df_from_ref():
    rows = []
    for nivel, objetivo_txt in _build_rows_from_ref():
        key_estable = _resolve_key(nivel, objetivo_txt)
        guardado = st.session_state["datos_indicadores"].get(key_estable, {})

        obj = _norm_text(guardado.get("Objeto", ""))
        cond = _norm_text(guardado.get("Condicion", guardado.get("Condición", "")))
        lugar = _norm_text(guardado.get("Lugar", ""))

        rows.append({
            "Nivel": nivel,
            "Objetivo": objetivo_txt,
            "1. Objeto": obj,
            "2. Condición Deseada": cond,
            "3. Lugar": lugar,
            "Indicador Generado": "",
        })

    df = pd.DataFrame(rows)
    df = _ensure_columns(df, cols_defaults)
    df = df[target_cols].copy()
    return df

def _sync_df_keep_user_edits(df_old):
    df_new = _build_df_from_ref()
    if df_old is None or df_old.empty:
        return df_new

    df_old = _ensure_columns(df_old, cols_defaults)

    keycols = ["Nivel", "Objetivo"]
    df_merge = pd.merge(df_new[keycols], df_old, on=keycols, how="left")
    df_merge = _ensure_columns(df_merge, cols_defaults)

    for col_edit in ["1. Objeto", "2. Condición Deseada", "3. Lugar"]:
        mask = df_merge[col_edit].isna() | (df_merge[col_edit].astype(str) == "nan")
        df_merge.loc[mask, col_edit] = df_new[col_edit].values

    df_merge["Indicador Generado"] = ""
    df_merge = df_merge[target_cols].copy()
    return df_merge

df_old_ui = st.session_state.get("df_indicadores", pd.DataFrame())
df_ui = _sync_df_keep_user_edits(df_old_ui)

if df_old_ui is None or df_old_ui.empty:
    st.session_state["df_indicadores"] = df_ui.copy()
else:
    if list(df_old_ui.columns) != list(df_ui.columns) or len(df_old_ui) != len(df_ui):
        st.session_state["df_indicadores"] = df_ui.copy()

df_work = st.session_state["df_indicadores"].copy()
df_work = _ensure_columns(df_work, cols_defaults)
df_work = df_work[target_cols].copy()

gb = GridOptionsBuilder.from_dataframe(df_work)

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
  let s = (a + " " + b + " " + c).replace(/\\s+/g, " ").trim();
  return s;
}
""")

gb.configure_column(
    "Indicador Generado",
    headerName="Indicador Generado",
    editable=False,
    wrapText=True,
    autoHeight=True,
    width=520,
    valueGetter=value_getter_indicador
)

gb.configure_grid_options(
    enableCellTextSelection=True,
    ensureDomOrder=True,
    suppressCopyRowsToClipboard=False,
    rowSelection="single",
    domLayout="autoHeight"
)

jscode_row_style_1 = JsCode("""
function(params) {
  const a = (params.data && params.data["1. Objeto"]) ? String(params.data["1. Objeto"]).trim() : "";
  const b = (params.data && params.data["2. Condición Deseada"]) ? String(params.data["2. Condición Deseada"]).trim() : "";
  const c = (params.data && params.data["3. Lugar"]) ? String(params.data["3. Lugar"]).trim() : "";
  const completo = (a.length > 0 && b.length > 0 && c.length > 0);
  if (completo) {
    return { 'background-color': '#EFF6FF', 'color': '#000000' };
  }
  return { 'background-color': '#FFFFFF', 'color': '#000000' };
}
""")

gb.configure_grid_options(getRowStyle=jscode_row_style_1)

gridOptions = gb.build()

custom_css = {
    ".ag-header-cell-text": {
        "font-size": "14px !important",
        "font-weight": "900 !important",
        "color": "#1E3A8A !important"
    }
}

grid_response = AgGrid(
    df_work,
    gridOptions=gridOptions,
    custom_css=custom_css,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    key="grid_indicadores"
)

df_live = pd.DataFrame(grid_response.get("data", []))
df_live = _ensure_columns(df_live, cols_defaults)
df_live = df_live[target_cols].copy()

cols_hash_1 = ["Nivel", "Objetivo", "1. Objeto", "2. Condición Deseada", "3. Lugar"]
hash_actual_1 = _stable_hash_df(df_live, cols_hash_1)
hash_prev_1 = st.session_state.get("hash_indicadores", "")

if hash_actual_1 and (hash_actual_1 != hash_prev_1):
    st.session_state["hash_indicadores"] = hash_actual_1
    st.session_state["df_indicadores"] = df_live

    for _, r in df_live.iterrows():
        nivel = _norm_text(r.get("Nivel", ""))
        objetivo_txt = _norm_text(r.get("Objetivo", ""))

        obj = _norm_text(r.get("1. Objeto", ""))
        cond = _norm_text(r.get("2. Condición Deseada", ""))
        lugar = _norm_text(r.get("3. Lugar", ""))

        if not obj and not cond and not lugar:
            continue

        key_estable = _resolve_key(nivel, objetivo_txt)
        indicador = _generar_indicador(obj, cond, lugar)

        st.session_state["datos_indicadores"][key_estable] = {
            "Objetivo": objetivo_txt,
            "Nivel": nivel,
            "Objeto": obj,
            "Condicion": cond,
            "Lugar": lugar,
            "Indicador": indicador
        }

    guardar_datos_nube()

# -----------------------------
# Tabla 2: Selección de indicadores
# -----------------------------
st.markdown('<div class="subtitulo-seccion">Selección de indicadores</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-2">Marca las validaciones. La columna <b>Selección</b> será <b>Sí</b> solo si todas están chuleadas. '
    'Fila verde tenue si es <b>Sí</b>, rojo tenue si es <b>No</b>. Guardado automático en nube.</div>',
    unsafe_allow_html=True
)

P1 = "El Sentido del indicador es claro"
P2 = "Existe información disponible o se puede recolectar fácilmente"
P3 = "El indicador es tangible y se puede observar"
P4 = "La tarea de recolectar datos está al alcance del proyecto y no requiere expertos para su análisis"
P5 = "El indicador es lo bastante representativo para el conjunto de resultados esperados."

# Leyenda (sin texto extra)
st.markdown(
    f"""
    <div class="legend-box">
      <div><b>Leyenda:</b></div>
      <ul>
        <li><b>P1</b>: {P1}</li>
        <li><b>P2</b>: {P2}</li>
        <li><b>P3</b>: {P3}</li>
        <li><b>P4</b>: {P4}</li>
        <li><b>P5</b>: {P5}</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True
)

def _build_df_seleccion_from_indicadores(df_ind):
    rows = []
    for _, r in df_ind.iterrows():
        nivel = _norm_text(r.get("Nivel", ""))
        objetivo_txt = _norm_text(r.get("Objetivo", ""))

        obj = _norm_text(r.get("1. Objeto", ""))
        cond = _norm_text(r.get("2. Condición Deseada", ""))
        lugar = _norm_text(r.get("3. Lugar", ""))

        indicador_txt = _generar_indicador(obj, cond, lugar)
        key_estable = _resolve_key(nivel, objetivo_txt)

        guard_sel = st.session_state["seleccion_indicadores"].get(key_estable, {})

        rows.append({
            "_key": key_estable,
            "Indicador": indicador_txt,
            P1: bool(guard_sel.get(P1, False)),
            P2: bool(guard_sel.get(P2, False)),
            P3: bool(guard_sel.get(P3, False)),
            P4: bool(guard_sel.get(P4, False)),
            P5: bool(guard_sel.get(P5, False)),
            "Selección": "",
        })
    return pd.DataFrame(rows)

df_base_sel = _build_df_seleccion_from_indicadores(df_live)

cols_sel_defaults = {
    "_key": "",
    "Indicador": "",
    P1: False,
    P2: False,
    P3: False,
    P4: False,
    P5: False,
    "Selección": "",
}
sel_cols = list(cols_sel_defaults.keys())
df_base_sel = _ensure_columns(df_base_sel, cols_sel_defaults)
df_base_sel = df_base_sel[sel_cols].copy()

gb2 = GridOptionsBuilder.from_dataframe(df_base_sel)

gb2.configure_column("_key", headerName="", editable=False, hide=True)
gb2.configure_column("Indicador", headerName="Indicador", editable=False, wrapText=True, autoHeight=True, width=520)

# Encabezados cortos (sin tooltip)
gb2.configure_column(P1, headerName="P1", editable=True, width=90,
                     cellRenderer="agCheckboxCellRenderer", cellEditor="agCheckboxCellEditor")
gb2.configure_column(P2, headerName="P2", editable=True, width=90,
                     cellRenderer="agCheckboxCellRenderer", cellEditor="agCheckboxCellEditor")
gb2.configure_column(P3, headerName="P3", editable=True, width=90,
                     cellRenderer="agCheckboxCellRenderer", cellEditor="agCheckboxCellEditor")
gb2.configure_column(P4, headerName="P4", editable=True, width=90,
                     cellRenderer="agCheckboxCellRenderer", cellEditor="agCheckboxCellEditor")
gb2.configure_column(P5, headerName="P5", editable=True, width=90,
                     cellRenderer="agCheckboxCellRenderer", cellEditor="agCheckboxCellEditor")

value_getter_sel = JsCode(f"""
function(params) {{
  const a = !!(params.data && params.data[{json.dumps(P1)}]);
  const b = !!(params.data && params.data[{json.dumps(P2)}]);
  const c = !!(params.data && params.data[{json.dumps(P3)}]);
  const d = !!(params.data && params.data[{json.dumps(P4)}]);
  const e = !!(params.data && params.data[{json.dumps(P5)}]);
  return (a && b && c && d && e) ? "Sí" : "No";
}}
""")

gb2.configure_column("Selección", headerName="Selección", editable=False, width=110, valueGetter=value_getter_sel)

gb2.configure_grid_options(
    enableCellTextSelection=True,
    ensureDomOrder=True,
    suppressCopyRowsToClipboard=False,
    rowSelection="single",
    domLayout="autoHeight"
)

row_style_sel = JsCode(f"""
function(params) {{
  const a = !!(params.data && params.data[{json.dumps(P1)}]);
  const b = !!(params.data && params.data[{json.dumps(P2)}]);
  const c = !!(params.data && params.data[{json.dumps(P3)}]);
  const d = !!(params.data && params.data[{json.dumps(P4)}]);
  const e = !!(params.data && params.data[{json.dumps(P5)}]);
  const ok = (a && b && c && d && e);
  if (ok) {{
    return {{ 'background-color': '#ECFDF5', 'color': '#000000' }};
  }}
  return {{ 'background-color': '#FEF2F2', 'color': '#000000' }};
}}
""")

gb2.configure_grid_options(getRowStyle=row_style_sel)

gridOptions2 = gb2.build()

custom_css_2 = {
    ".ag-header-cell-text": {
        "font-size": "13px !important",
        "font-weight": "900 !important",
        "color": "#065f46 !important"
    }
}

grid_response_2 = AgGrid(
    df_base_sel,
    gridOptions=gridOptions2,
    custom_css=custom_css_2,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    key="grid_seleccion_indicadores"
)

df_sel_live = pd.DataFrame(grid_response_2.get("data", []))
df_sel_live = _ensure_columns(df_sel_live, cols_sel_defaults)

if "_key" not in df_sel_live.columns or df_sel_live["_key"].astype(str).eq("").all():
    df_sel_live["_key"] = df_base_sel["_key"].values[: len(df_sel_live)]

df_sel_live = df_sel_live[sel_cols].copy()

cols_hash_2 = ["_key", P1, P2, P3, P4, P5]
hash_actual_2 = _stable_hash_df(df_sel_live, cols_hash_2)
hash_prev_2 = st.session_state.get("hash_seleccion_indicadores", "")

if hash_actual_2 and (hash_actual_2 != hash_prev_2):
    st.session_state["hash_seleccion_indicadores"] = hash_actual_2

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

    guardar_datos_nube()
