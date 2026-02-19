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
    .block-container { padding-bottom: 150px !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 900 !important; color: #1E3A8A; margin-bottom: 4px; }
    .subtitulo-gris { font-size: 15px !important; color: #666; margin-bottom: 10px; }
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
    """
    Key estable para guardar en session_state['datos_indicadores'].
    (Opción 1 estricta: no depende del árbol por niveles, solo de la tabla superior 'referencia_manual')
    """
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

# Estricto: si no hay nada, se detiene
if not obj_general and len(especificos) == 0 and len(actividades) == 0:
    st.error("La tabla superior de Hoja 7 está vacía. En Hoja 7 pestaña 2 presiona: “Sincronizar con Árbol”.")
    st.stop()

# normalizar textos
especificos = [ _norm_text(x) for x in especificos if _norm_text(x) ]
actividades = [ _norm_text(x) for x in actividades if _norm_text(x) ]

# -----------------------------
# State hoja 11
# -----------------------------
if "datos_indicadores" not in st.session_state or not isinstance(st.session_state.get("datos_indicadores"), dict):
    st.session_state["datos_indicadores"] = {}

if "df_indicadores" not in st.session_state or not isinstance(st.session_state.get("df_indicadores"), pd.DataFrame):
    st.session_state["df_indicadores"] = pd.DataFrame()

if "hash_indicadores" not in st.session_state:
    st.session_state["hash_indicadores"] = ""

# -----------------------------
# DataFrame base (UI)
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

def _build_rows_from_ref():
    rows = []

    if obj_general:
        rows.append(("Objetivo General", obj_general))

    for e in especificos:
        rows.append(("Objetivo Específico (Componente)", e))

    for a in actividades:
        rows.append(("Actividad Clave", a))

    return rows

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
            # el display se calcula en JS
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

    # Conservar edición del usuario
    for col_edit in ["1. Objeto", "2. Condición Deseada", "3. Lugar"]:
        mask = df_merge[col_edit].isna() | (df_merge[col_edit].astype(str) == "nan")
        df_merge.loc[mask, col_edit] = df_new[col_edit].values

    df_merge["Indicador Generado"] = ""
    df_merge = df_merge[target_cols].copy()
    return df_merge

df_old_ui = st.session_state.get("df_indicadores", pd.DataFrame())
df_ui = _sync_df_keep_user_edits(df_old_ui)

# Reemplazar si cambió estructura (por cambios en Hoja 7)
if df_old_ui is None or df_old_ui.empty:
    st.session_state["df_indicadores"] = df_ui.copy()
else:
    if list(df_old_ui.columns) != list(df_ui.columns) or len(df_old_ui) != len(df_ui):
        st.session_state["df_indicadores"] = df_ui.copy()

df_work = st.session_state["df_indicadores"].copy()
df_work = _ensure_columns(df_work, cols_defaults)
df_work = df_work[target_cols].copy()

# -----------------------------
# AgGrid config
# - Indicador calculado en FRONT (JS) -> se actualiza al instante
# - Filas completas en azul tenue (JS)
# - Objetivo no editable pero copiable (selección de texto habilitada)
# -----------------------------
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

jscode_row_style = JsCode("""
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

gb.configure_grid_options(getRowStyle=jscode_row_style)

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

# -----------------------------
# Captura data devuelta por AgGrid
# (valueGetter no siempre viene en data => persistimos calculando en Python)
# -----------------------------
df_live = pd.DataFrame(grid_response.get("data", []))
df_live = _ensure_columns(df_live, cols_defaults)
df_live = df_live[target_cols].copy()

# Hash SOLO por campos editables y llaves
cols_hash = ["Nivel", "Objetivo", "1. Objeto", "2. Condición Deseada", "3. Lugar"]
hash_actual = _stable_hash_df(df_live, cols_hash)
hash_prev = st.session_state.get("hash_indicadores", "")

if hash_actual and (hash_actual != hash_prev):
    st.session_state["hash_indicadores"] = hash_actual
    st.session_state["df_indicadores"] = df_live

    # Persistencia: actualizar datos_indicadores por key estable
    for _, r in df_live.iterrows():
        nivel = _norm_text(r.get("Nivel", ""))
        objetivo_txt = _norm_text(r.get("Objetivo", ""))

        obj = _norm_text(r.get("1. Objeto", ""))
        cond = _norm_text(r.get("2. Condición Deseada", ""))
        lugar = _norm_text(r.get("3. Lugar", ""))

        # evita escribir basura si no hay nada diligenciado
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

    # Guardado automático en nube
    guardar_datos_nube()
