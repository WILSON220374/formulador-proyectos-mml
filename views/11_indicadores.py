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
    .block-container { padding-bottom: 220px !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 900 !important; margin-bottom: 0px !important; }
    .subtitulo-seccion { font-size: 20px !important; font-weight: 800 !important; margin-top: 12px !important; margin-bottom: 6px !important; }
    .subtitulo-seccion-2 { font-size: 20px !important; font-weight: 800 !important; margin-top: 24px !important; margin-bottom: 6px !important; }
    .info-box {
        background: #eff6ff;
        border: 1px solid #dbeafe;
        color: #1e3a8a;
        padding: 12px 14px;
        border-radius: 10px;
        font-size: 14px;
        margin: 10px 0 14px 0;
        font-weight: 600;
    }
    .info-box-2 {
        background: #ecfeff;
        border: 1px solid #cffafe;
        color: #155e75;
        padding: 12px 14px;
        border-radius: 10px;
        font-size: 14px;
        margin: 10px 0 14px 0;
        font-weight: 600;
    }
    .info-box-3 {
        background: #fef9c3;
        border: 1px solid #fde68a;
        color: #92400e;
        padding: 12px 14px;
        border-radius: 10px;
        font-size: 14px;
        margin: 10px 0 14px 0;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Helpers
# -----------------------------
def _clean_spaces(s: str) -> str:
    return " ".join(str(s).replace("\n", " ").replace("\r", " ").split()).strip()

def _norm_text(x) -> str:
    if x is None:
        return ""
    s = str(x)
    if s.lower() == "nan":
        return ""
    return _clean_spaces(s)

def _mk_map_key(nivel, objetivo_txt):
    base = f"{_norm_text(nivel)}||{_norm_text(objetivo_txt)}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()

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
# Datos en sesión
# -----------------------------
if "referencia_manual" not in st.session_state or not isinstance(st.session_state.get("referencia_manual"), dict):
    st.session_state["referencia_manual"] = {}

if "datos_indicadores" not in st.session_state or not isinstance(st.session_state.get("datos_indicadores"), dict):
    st.session_state["datos_indicadores"] = {}

if "seleccion_indicadores" not in st.session_state or not isinstance(st.session_state.get("seleccion_indicadores"), dict):
    st.session_state["seleccion_indicadores"] = {}

if "hash_indicadores" not in st.session_state:
    st.session_state["hash_indicadores"] = ""

if "hash_seleccion_indicadores" not in st.session_state:
    st.session_state["hash_seleccion_indicadores"] = ""

if "duracion_proyecto_periodos" not in st.session_state:
    st.session_state["duracion_proyecto_periodos"] = 4

if "meta_resultados_parciales" not in st.session_state or not isinstance(st.session_state.get("meta_resultados_parciales"), dict):
    st.session_state["meta_resultados_parciales"] = {}

if "hash_meta_resultados_parciales" not in st.session_state:
    st.session_state["hash_meta_resultados_parciales"] = ""

# -----------------------------
# Construcción filas base desde referencia_manual
# -----------------------------
def _build_rows_from_ref():
    ref = st.session_state.get("referencia_manual", {}) or {}

    rows = []
    for k, v in ref.items():
        if not isinstance(v, dict):
            continue

        nivel = _norm_text(v.get("Nivel", ""))
        objetivo = _norm_text(v.get("Objetivo", v.get("Objetivo / Actividad", "")))

        if not nivel or not objetivo:
            continue

        rows.append((nivel, objetivo))

    return rows

# -----------------------------
# UI - Título
# -----------------------------
st.markdown('<div class="titulo-seccion">11. Indicadores</div>', unsafe_allow_html=True)
st.caption("Fuente única: Tabla superior de Hoja 7 (Alternativa Seleccionada). Guardado automático en nube.")
st.markdown(
    '<div class="info-box">Diligencia: 1. Objeto, 2. Condición Deseada y 3. Lugar. El indicador se genera al instante dentro de la tabla y se guarda automáticamente en la nube.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Tabla 1: Construcción del Indicador
# -----------------------------
def _build_df_from_ref():
    rows = []
    for nivel, objetivo_txt in _build_rows_from_ref():
        key_estable = _resolve_key(nivel, objetivo_txt)
        guardado = st.session_state["datos_indicadores"].get(key_estable, {})

        obj = _norm_text(guardado.get("Objeto", ""))
        cond = _norm_text(guardado.get("Condicion", guardado.get("Condición", "")))
        lugar = _norm_text(guardado.get("Lugar", ""))

        rows.append({
            "_key": key_estable,
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

    # Backward-compat: si venimos de una versión anterior sin _key, lo reconstruimos
    if "_key" not in df_old.columns:
        df_old["_key"] = df_old.apply(
            lambda r: _resolve_key(_norm_text(r.get("Nivel", "")), _norm_text(r.get("Objetivo", ""))),
            axis=1
        )

    # Evitar duplicados por llave estable (primer valor gana)
    df_old = df_old.drop_duplicates(subset=["_key"], keep="first").copy()

    df_merge = df_new.copy()

    # Preservar ediciones del usuario (incluye strings vacíos si el usuario borró)
    edit_cols = ["1. Objeto", "2. Condición Deseada", "3. Lugar"]
    old_ix = df_old.set_index("_key", drop=False)

    present_mask = df_merge["_key"].isin(old_ix.index)
    if present_mask.any():
        for col_edit in edit_cols:
            if col_edit in old_ix.columns:
                mapped = df_merge.loc[present_mask, "_key"].map(old_ix[col_edit])
                df_merge.loc[present_mask, col_edit] = mapped.values

    df_merge["Indicador Generado"] = ""
    df_merge = _ensure_columns(df_merge, cols_defaults)
    df_merge = df_merge[target_cols].copy()
    return df_merge

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

gb.configure_column("_key", headerName="_key", editable=False, hide=True)

gb.configure_column("Nivel", headerName="Nivel", editable=False, wrapText=True, autoHeight=True, width=220)
gb.configure_column("Objetivo", headerName="Objetivo", editable=False, wrapText=True, autoHeight=True, width=560)

gb.configure_column("1. Objeto", headerName="1. Objeto", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("2. Condición Deseada", headerName="2. Condición Deseada", editable=True, wrapText=True, autoHeight=True, width=300)
gb.configure_column("3. Lugar", headerName="3. Lugar", editable=True, wrapText=True, autoHeight=True, width=190)

value_getter_indicador = JsCode(
    """
    function(params) {
        let obj = (params.data['1. Objeto'] || '').toString().trim();
        let cond = (params.data['2. Condición Deseada'] || '').toString().trim();
        let lugar = (params.data['3. Lugar'] || '').toString().trim();

        let txt = (obj + ' ' + cond + ' ' + lugar).replace(/\\s+/g,' ').trim();
        return txt;
    }
    """
)

gb.configure_column("Indicador Generado", headerName="Indicador Generado", editable=False, valueGetter=value_getter_indicador, wrapText=True, autoHeight=True, width=400)

gridOptions = gb.build()

grid_response = AgGrid(
    df_work,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    key="grid_indicadores"
)

df_live = pd.DataFrame(grid_response.get("data", []))
df_live = _ensure_columns(df_live, cols_defaults)

# Backward-compat / resiliencia: si AgGrid no devuelve _key (columna oculta), la restauramos por posición
if "_key" not in df_live.columns or df_live["_key"].astype(str).eq("").all():
    try:
        base_keys = df_work.get("_key", pd.Series(dtype=str)).astype(str).values
        df_live["_key"] = base_keys[: len(df_live)]
    except Exception:
        # Fallback: reconstruir por Nivel/Objetivo
        df_live["_key"] = df_live.apply(
            lambda r: _resolve_key(_norm_text(r.get("Nivel", "")), _norm_text(r.get("Objetivo", ""))),
            axis=1
        )

df_live = df_live[target_cols].copy()

cols_hash_1 = ["_key", "Nivel", "Objetivo", "1. Objeto", "2. Condición Deseada", "3. Lugar"]
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

        key_estable = _norm_text(r.get("_key", "")) or _resolve_key(nivel, objetivo_txt)

        # Si el usuario borró todo, persistimos el borrado eliminando el registro en nube
        if not obj and not cond and not lugar:
            st.session_state["datos_indicadores"].pop(key_estable, None)
            st.session_state.get("seleccion_indicadores", {}).pop(key_estable, None)
            st.session_state.get("meta_resultados_parciales", {}).pop(key_estable, None)
            continue

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
P5 = "El indicador es lo bastante representativo para el conjunto de resultados e impactos"

sel_cols_defaults = {
    "_key": "",
    "Nivel": "",
    "Objetivo": "",
    "Indicador": "",
    P1: False,
    P2: False,
    P3: False,
    P4: False,
    P5: False,
    "Selección": "No"
}
sel_cols = list(sel_cols_defaults.keys())

def _build_df_seleccion():
    rows = []
    for nivel, objetivo_txt in _build_rows_from_ref():
        k = _resolve_key(nivel, objetivo_txt)
        guardado = st.session_state["datos_indicadores"].get(k, {})
        ind = _norm_text(guardado.get("Indicador", ""))

        sel = st.session_state.get("seleccion_indicadores", {}).get(k, {})
        a = bool(sel.get(P1, False))
        b = bool(sel.get(P2, False))
        c = bool(sel.get(P3, False))
        d = bool(sel.get(P4, False))
        e = bool(sel.get(P5, False))

        seleccion_txt = "Sí" if (a and b and c and d and e) else "No"

        rows.append({
            "_key": k,
            "Nivel": nivel,
            "Objetivo": objetivo_txt,
            "Indicador": ind,
            P1: a,
            P2: b,
            P3: c,
            P4: d,
            P5: e,
            "Selección": seleccion_txt
        })

    df = pd.DataFrame(rows)
    df = _ensure_columns(df, sel_cols_defaults)
    df = df[sel_cols].copy()
    return df

df_base_sel = _build_df_seleccion()

gb2 = GridOptionsBuilder.from_dataframe(df_base_sel)

gb2.configure_column("_key", headerName="_key", editable=False, hide=True)
gb2.configure_column("Nivel", headerName="Nivel", editable=False, wrapText=True, autoHeight=True, width=200)
gb2.configure_column("Objetivo", headerName="Objetivo", editable=False, wrapText=True, autoHeight=True, width=520)
gb2.configure_column("Indicador", headerName="Indicador", editable=False, wrapText=True, autoHeight=True, width=420)

gb2.configure_column(P1, headerName=P1, editable=True, width=220)
gb2.configure_column(P2, headerName=P2, editable=True, width=260)
gb2.configure_column(P3, headerName=P3, editable=True, width=220)
gb2.configure_column(P4, headerName=P4, editable=True, width=360)
gb2.configure_column(P5, headerName=P5, editable=True, width=320)

row_style_js = JsCode(
    """
    function(params) {
        if (params.data['Selección'] === 'Sí') {
            return {'backgroundColor': '#ecfdf5'};
        }
        return {'backgroundColor': '#fef2f2'};
    }
    """
)

gb2.configure_column("Selección", headerName="Selección", editable=False, width=120)
gb2.configure_grid_options(getRowStyle=row_style_js)

gridOptions2 = gb2.build()

grid_response_2 = AgGrid(
    df_base_sel,
    gridOptions=gridOptions2,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    key="grid_seleccion_indicadores"
)

df_sel_live = pd.DataFrame(grid_response_2.get("data", []))
df_sel_live = _ensure_columns(df_sel_live, sel_cols_defaults)

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

# -----------------------------
# Sección: META Y RESULTADOS PARCIALES
# -----------------------------
st.markdown('<div class="subtitulo-seccion-2">META Y RESULTADOS PARCIALES</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-3">Indica la cantidad de periodos (número entero). Se crearán columnas dinámicas '
    'Periodo 1..N. La suma de periodos por fila debe coincidir con la Meta (si no coincide, la fila se marca en rojo tenue).</div>',
    unsafe_allow_html=True
)

# Pregunta duración (entero)
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

# Determinar qué indicadores están en "Sí"
def _is_seleccion_si(row_dict):
    a = bool(row_dict.get(P1, False))
    b = bool(row_dict.get(P2, False))
    c = bool(row_dict.get(P3, False))
    d = bool(row_dict.get(P4, False))
    e = bool(row_dict.get(P5, False))
    return a and b and c and d and e

keys_si = []
indicador_txt_por_key = {}

# Usamos df_sel_live como fuente
for _, r in df_sel_live.iterrows():
    k = _norm_text(r.get("_key", ""))
    if not k:
        continue
    if _is_seleccion_si(r.to_dict()):
        keys_si.append(k)
        indicador_txt_por_key[k] = _norm_text(r.get("Indicador", ""))

if not keys_si:
    st.info("Aún no hay indicadores con Selección = Sí. Marca todas las validaciones para activar la tabla de metas.")
else:
    # Construir df_meta con columnas dinámicas de periodos
    period_cols = [f"Periodo {i}" for i in range(1, dur + 1)]

    cols_meta_defaults = {
        "_key": "",
        "Indicador": "",
        "Línea base": "",
        "Meta": "",
        "Unidad de medida": "",
    }
    for pc in period_cols:
        cols_meta_defaults[pc] = ""

    meta_cols = list(cols_meta_defaults.keys())

    rows_meta = []
    for k in keys_si:
        guard = st.session_state.get("meta_resultados_parciales", {}).get(k, {})
        linea_base = _norm_text(guard.get("Línea base", ""))
        meta = _norm_text(guard.get("Meta", ""))
        um = _norm_text(guard.get("Unidad de medida", ""))

        per_guard = guard.get("Periodos", {}) if isinstance(guard.get("Periodos", {}), dict) else {}

        row = {
            "_key": k,
            "Indicador": indicador_txt_por_key.get(k, ""),
            "Línea base": linea_base,
            "Meta": meta,
            "Unidad de medida": um,
        }
        for pc in period_cols:
            row[pc] = _norm_text(per_guard.get(pc, ""))

        rows_meta.append(row)

    df_meta = pd.DataFrame(rows_meta)
    df_meta = _ensure_columns(df_meta, cols_meta_defaults)
    df_meta = df_meta[meta_cols].copy()

    # AgGrid con validación visual: suma(periodos) == Meta (cuando Meta es numérica)
    custom_css_3 = {
        ".ag-header-cell-label": {"font-weight": "800"},
        ".ag-cell": {"font-size": "13px"},
    }

    # JS para pintar fila tenue rojo si suma != meta (ambos numéricos)
    row_style_meta_js = JsCode(
        """
        function(params) {
            let meta = (params.data['Meta'] || '').toString().trim().replace(',', '.');
            let metaNum = parseFloat(meta);
            if (isNaN(metaNum)) { return {}; }

            let sum = 0.0;
            Object.keys(params.data).forEach(function(k){
                if (k.startsWith('Periodo ')) {
                    let v = (params.data[k] || '').toString().trim().replace(',', '.');
                    let n = parseFloat(v);
                    if (!isNaN(n)) { sum += n; }
                }
            });

            // tolerancia básica
            if (Math.abs(sum - metaNum) > 1e-9) {
                return {'backgroundColor': '#fff7ed'};
            }
            return {};
        }
        """
    )

    gb3 = GridOptionsBuilder.from_dataframe(df_meta)
    gb3.configure_column("_key", headerName="_key", editable=False, hide=True)
    gb3.configure_column("Indicador", headerName="Indicador", editable=False, wrapText=True, autoHeight=True, width=520)
    gb3.configure_column("Línea base", headerName="Línea base", editable=True, width=140)
    gb3.configure_column("Meta", headerName="Meta", editable=True, width=110)
    gb3.configure_column("Unidad de medida", headerName="Unidad de medida", editable=True, width=180)

    for pc in period_cols:
        gb3.configure_column(pc, headerName=pc, editable=True, width=120)

    gb3.configure_grid_options(getRowStyle=row_style_meta_js)
    gridOptions3 = gb3.build()

    grid_response_3 = AgGrid(
        df_meta,
        gridOptions=gridOptions3,
        custom_css=custom_css_3,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        allow_unsafe_jscode=True,
        key="grid_meta_resultados_parciales"
    )

    df_meta_live = pd.DataFrame(grid_response_3.get("data", []))
    df_meta_live = _ensure_columns(df_meta_live, cols_meta_defaults)

    if "_key" not in df_meta_live.columns or df_meta_live["_key"].astype(str).eq("").all():
        df_meta_live["_key"] = df_meta["_key"].values[: len(df_meta_live)]

    df_meta_live = df_meta_live[meta_cols].copy()

    # Auto-guardar (solo si cambia)
    cols_hash_3 = ["_key", "Línea base", "Meta", "Unidad de medida"] + period_cols
    hash_actual_3 = _stable_hash_df(df_meta_live, cols_hash_3)
    hash_prev_3 = st.session_state.get("hash_meta_resultados_parciales", "")

    if hash_actual_3 and (hash_actual_3 != hash_prev_3):
        st.session_state["hash_meta_resultados_parciales"] = hash_actual_3

        # Persistir por clave estable
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

        # Limpiar keys que ya no están en "Sí" (desaparecer)
        existentes = set(st.session_state["meta_resultados_parciales"].keys())
        actuales = set(keys_si)
        for k in list(existentes - actuales):
            st.session_state["meta_resultados_parciales"].pop(k, None)

        guardar_datos_nube()
