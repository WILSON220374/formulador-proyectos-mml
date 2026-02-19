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
    .titulo-seccion { font-size: 30px !important; font-weight: 900 !important; color: #1E3A8A; margin-bottom: 4px; }
    .subtitulo-gris { font-size: 15px !important; color: #666; margin-bottom: 10px; }
    .subtitulo-seccion { font-size: 20px !important; font-weight: 900 !important; color: #0f172a; margin: 18px 0 8px 0; }
    .subtitulo-seccion-2 { font-size: 20px !important; font-weight: 900 !important; color: #0f172a; margin: 22px 0 8px 0; }

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
st.markdown('<div class="titulo-seccion">📊 11. Indicadores</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Fuente única: Tabla superior de Hoja 7 (Alternativa Seleccionada). Guardado automático en nube.</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="info-box">Diligencia: <b>1. Objeto</b>, <b>2. Condición Deseada</b> y <b>3. Lugar</b>. '
    'El indicador se genera dentro de la tabla y se guarda automáticamente.</div>',
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

if "df_indicadores" not in st.session_state or not isinstance(st.session_state.get("df_indicadores"), pd.DataFrame):
    st.session_state["df_indicadores"] = pd.DataFrame()

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

def _build_df_from_ref():
    rows = []
    for nivel, objetivo_txt in _build_rows_from_ref():
        k = _resolve_key(nivel, objetivo_txt)
        guardado = st.session_state["datos_indicadores"].get(k, {})

        obj = _norm_text(guardado.get("Objeto", ""))
        cond = _norm_text(guardado.get("Condicion", guardado.get("Condición", "")))
        lugar = _norm_text(guardado.get("Lugar", ""))

        rows.append({
            "_key": k,
            "Nivel": nivel,
            "Objetivo": objetivo_txt,
            "1. Objeto": obj,
            "2. Condición Deseada": cond,
            "3. Lugar": lugar,
            "Indicador Generado": "",
        })

    df = pd.DataFrame(rows)
    df = _ensure_columns(df, cols_defaults)
    return df[target_cols].copy()

def _sync_df_keep_user_edits(df_old):
    df_new = _build_df_from_ref()
    if df_old is None or df_old.empty:
        return df_new

    df_old = _ensure_columns(df_old, cols_defaults)

    keycols = ["_key", "Nivel", "Objetivo"]
    df_merge = pd.merge(df_new[keycols], df_old, on=keycols, how="left")
    df_merge = _ensure_columns(df_merge, cols_defaults)

    for col_edit in ["1. Objeto", "2. Condición Deseada", "3. Lugar"]:
        mask = df_merge[col_edit].isna() | (df_merge[col_edit].astype(str) == "nan")
        df_merge.loc[mask, col_edit] = df_new[col_edit].values

    df_merge["Indicador Generado"] = ""
    return df_merge[target_cols].copy()

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

gb.configure_grid_options(domLayout="autoHeight", enableCellTextSelection=True, ensureDomOrder=True)
gridOptions = gb.build()

grid_response = AgGrid(
    df_work,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    key="grid_indicadores"
)

df_live = pd.DataFrame(grid_response.get("data", []))
df_live = _ensure_columns(df_live, cols_defaults)
df_live = df_live[target_cols].copy()

cols_hash_1 = ["_key", "Nivel", "Objetivo", "1. Objeto", "2. Condición Deseada", "3. Lugar"]
hash_actual_1 = _stable_hash_df(df_live, cols_hash_1)
hash_prev_1 = st.session_state.get("hash_indicadores", "")

if hash_actual_1 and (hash_actual_1 != hash_prev_1):
    st.session_state["hash_indicadores"] = hash_actual_1
    st.session_state["df_indicadores"] = df_live

    for _, r in df_live.iterrows():
        k = _norm_text(r.get("_key", ""))
        nivel = _norm_text(r.get("Nivel", ""))
        objetivo_txt = _norm_text(r.get("Objetivo", ""))

        obj = _norm_text(r.get("1. Objeto", ""))
        cond = _norm_text(r.get("2. Condición Deseada", ""))
        lugar = _norm_text(r.get("3. Lugar", ""))

        indicador = _generar_indicador(obj, cond, lugar)

        st.session_state["datos_indicadores"][k] = {
            "Objetivo": objetivo_txt,
            "Nivel": nivel,
            "Objeto": obj,
            "Condicion": cond,
            "Lugar": lugar,
            "Indicador": indicador
        }

    guardar_datos_nube()

# -----------------------------
# Tabla 2: Selección de indicadores (HÍBRIDO)
# -----------------------------
st.markdown('<div class="subtitulo-seccion">Selección de indicadores</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-2">Marca las validaciones. La columna <b>Selección</b> será <b>Sí</b> solo si todas están chuleadas. '
    'Fila verde tenue si es <b>Sí</b>, rojo tenue si es <b>No</b>. Para guardar y habilitar la tabla de metas, presiona <b>Aplicar selección</b>.</div>',
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

def _get_sel_bool(sel_dict, short_key, long_key):
    if not isinstance(sel_dict, dict):
        return False
    if short_key in sel_dict:
        return bool(sel_dict.get(short_key, False))
    if long_key in sel_dict:
        return bool(sel_dict.get(long_key, False))
    return False

def _build_df_seleccion_from_state():
    rows = []
    for nivel, objetivo_txt in _build_rows_from_ref():
        k = _resolve_key(nivel, objetivo_txt)
        guardado = st.session_state["datos_indicadores"].get(k, {})
        ind = _norm_text(guardado.get("Indicador", ""))

        sel = st.session_state.get("seleccion_indicadores", {}).get(k, {})
        a = _get_sel_bool(sel, P1, Q1)
        b = _get_sel_bool(sel, P2, Q2)
        c = _get_sel_bool(sel, P3, Q3)
        d = _get_sel_bool(sel, P4, Q4)
        e = _get_sel_bool(sel, P5, Q5)

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
    return df[sel_cols].copy()

df_base_sel = _build_df_seleccion_from_state()

js_value_getter_sel = JsCode(
    """
    function(params) {
        const a = !!params.data['P1'];
        const b = !!params.data['P2'];
        const c = !!params.data['P3'];
        const d = !!params.data['P4'];
        const e = !!params.data['P5'];
        return (a && b && c && d && e) ? 'Sí' : 'No';
    }
    """
)

js_row_style = JsCode(
    """
    function(params) {
        const a = !!params.data['P1'];
        const b = !!params.data['P2'];
        const c = !!params.data['P3'];
        const d = !!params.data['P4'];
        const e = !!params.data['P5'];
        const ok = (a && b && c && d && e);
        return ok ? {'backgroundColor': '#ecfdf5'} : {'backgroundColor': '#fef2f2'};
    }
    """
)

gb2 = GridOptionsBuilder.from_dataframe(df_base_sel)
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
    df_base_sel,
    gridOptions=gridOptions2,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme="streamlit",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    key="grid_seleccion_indicadores"
)

c_apply_1, c_apply_2 = st.columns([1, 5], vertical_alignment="center")
with c_apply_1:
    aplicar = st.button("Aplicar selección", use_container_width=True)
with c_apply_2:
    st.caption("Use este botón para guardar las selecciones y actualizar la tabla de METAS.")

if aplicar:
    df_sel_live = pd.DataFrame(grid_response_2.get("data", []))
    df_sel_live = _ensure_columns(df_sel_live, sel_cols_defaults)

    if "_key" not in df_sel_live.columns or df_sel_live["_key"].astype(str).eq("").all():
        df_sel_live["_key"] = df_base_sel["_key"].values[: len(df_sel_live)]

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

    try:
        keys_si = []
        for k, sel in st.session_state.get("seleccion_indicadores", {}).items():
            if all(bool(sel.get(p, False)) for p in P_COLS):
                keys_si.append(k)
        actuales = set(keys_si)
        existentes_meta = set(st.session_state.get("meta_resultados_parciales", {}).keys())
        for k in list(existentes_meta - actuales):
            st.session_state["meta_resultados_parciales"].pop(k, None)

        existentes_mv = set(st.session_state.get("medios_verificacion", {}).keys())
        for k in list(existentes_mv - actuales):
            st.session_state["medios_verificacion"].pop(k, None)

    except Exception:
        pass

    guardar_datos_nube()
    st.rerun()

# -----------------------------
# META Y RESULTADOS PARCIALES
# -----------------------------
st.markdown('<div class="subtitulo-seccion-2">META Y RESULTADOS PARCIALES</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-3">Indica la cantidad de periodos (número entero). Se crearán columnas dinámicas '
    'Periodo 1..N. La suma de periodos por fila debe coincidir con la Meta (si no coincide, la fila se marca en color tenue).</div>',
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

df_sel_for_meta = _build_df_seleccion_from_state()
keys_si = df_sel_for_meta.loc[df_sel_for_meta["Selección"] == "Sí", "_key"].astype(str).tolist()

indicador_txt_por_key = {}
for _, r in df_sel_for_meta.iterrows():
    k = _norm_text(r.get("_key", ""))
    if not k:
        continue
    indicador_txt_por_key[k] = _norm_text(r.get("Indicador", ""))

if not keys_si:
    st.info("Aún no hay indicadores con Selección = Sí. Marca las 5 validaciones (P1..P5) y presiona “Aplicar selección”.")
else:
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
            "Unidad de medida": um
        }
        for pc in period_cols:
            row[pc] = _norm_text(per_guard.get(pc, ""))

        rows_meta.append(row)

    df_meta = pd.DataFrame(rows_meta)
    df_meta = _ensure_columns(df_meta, cols_meta_defaults)
    df_meta = df_meta[meta_cols].copy()

    row_style_meta_js = JsCode(
        f"""
        function(params) {{
            const metaRaw = (params.data && params.data['Meta'] !== undefined) ? String(params.data['Meta']).trim() : '';
            if (!metaRaw) return {{}};

            function toNum(v) {{
                if (v === null || v === undefined) return null;
                let s = String(v).trim();
                if (!s) return 0;
                s = s.replace(',', '.');
                const n = Number(s);
                return isNaN(n) ? null : n;
            }}

            const metaNum = toNum(metaRaw);
            if (metaNum === null) return {{'backgroundColor': '#fef2f2'}};

            let sum = 0;
            const cols = {json.dumps(period_cols)};
            for (let i=0; i<cols.length; i++) {{
                const c = cols[i];
                const v = (params.data && params.data[c] !== undefined) ? params.data[c] : '';
                const n = toNum(v);
                if (n === null) return {{'backgroundColor': '#fef2f2'}};
                sum += n;
            }}

            if (Math.abs(sum - metaNum) > 1e-9) {{
                return {{'backgroundColor': '#fff7ed'}};
            }}
            return {{}};
        }}
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

    gb3.configure_grid_options(getRowStyle=row_style_meta_js, domLayout="autoHeight")
    gridOptions3 = gb3.build()

    grid_response_3 = AgGrid(
        df_meta,
        gridOptions=gridOptions3,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        key="grid_meta_resultados_parciales"
    )

    df_meta_live = pd.DataFrame(grid_response_3.get("data", []))
    df_meta_live = _ensure_columns(df_meta_live, cols_meta_defaults)

    if "_key" not in df_meta_live.columns or df_meta_live["_key"].astype(str).eq("").all():
        df_meta_live["_key"] = df_meta["_key"].values[: len(df_meta_live)]

    df_meta_live = df_meta_live[meta_cols].copy()

    cols_hash_3 = ["_key", "Línea base", "Meta", "Unidad de medida"] + period_cols
    hash_actual_3 = _stable_hash_df(df_meta_live, cols_hash_3)
    hash_prev_3 = st.session_state.get("hash_meta_resultados_parciales", "")

    if hash_actual_3 and (hash_actual_3 != hash_prev_3):
        st.session_state["hash_meta_resultados_parciales"] = hash_actual_3

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
# MEDIOS DE VERIFICACIÓN (tabla final)
# -----------------------------
st.markdown('<div class="subtitulo-seccion-2">MEDIOS DE VERIFICACIÓN</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="info-box-2">Las columnas <b>Tipo</b>, <b>Objetivo</b>, <b>Indicador</b> y <b>Meta</b> se cargan automáticamente. '
    'Las demás casillas son de <b>libre diligenciamiento</b> y se guardan en nube.</div>',
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

df_sel_for_mv = _build_df_seleccion_from_state()
keys_si_mv = df_sel_for_mv.loc[df_sel_for_mv["Selección"] == "Sí", "_key"].astype(str).tolist()

if not keys_si_mv:
    st.info("Aún no hay indicadores con Selección = Sí. Marca P1..P5 y presiona “Aplicar selección”.")
else:
    mv_map = {}
    for _, rr in df_sel_for_mv.iterrows():
        k = _norm_text(rr.get("_key", ""))
        if not k:
            continue
        mv_map[k] = {
            "Nivel": _norm_text(rr.get("Nivel", "")),
            "Objetivo": _norm_text(rr.get("Objetivo", "")),
            "Indicador": _norm_text(rr.get("Indicador", "")),
        }

    rows_mv = []
    for k in keys_si_mv:
        base = mv_map.get(k, {"Nivel": "", "Objetivo": "", "Indicador": ""})
        nivel = base.get("Nivel", "")
        objetivo_txt = base.get("Objetivo", "")
        indicador_txt = base.get("Indicador", "")

        meta_txt = _norm_text(st.session_state.get("meta_resultados_parciales", {}).get(k, {}).get("Meta", ""))

        guard = st.session_state.get("medios_verificacion", {}).get(k, {})
        row = {
            "_key": k,
            "Tipo": _tipo_from_nivel(nivel),
            "Objetivo": objetivo_txt,
            "Indicador": indicador_txt,
            "Meta": meta_txt
        }
        for c in MV_LIBRES:
            row[c] = _norm_text(guard.get(c, ""))
        rows_mv.append(row)

    df_mv = pd.DataFrame(rows_mv)

    mv_defaults = {"_key": "", "Tipo": "", "Objetivo": "", "Indicador": "", "Meta": ""}
    for c in MV_LIBRES:
        mv_defaults[c] = ""

    df_mv = _ensure_columns(df_mv, mv_defaults)

    mv_cols = ["_key", "Tipo", "Objetivo", "Indicador", "Meta"] + MV_LIBRES
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

    cols_hash_4 = ["_key"] + MV_LIBRES
    hash_actual_4 = _stable_hash_df(df_mv_live, cols_hash_4)
    hash_prev_4 = st.session_state.get("hash_medios_verificacion", "")

    if hash_actual_4 and (hash_actual_4 != hash_prev_4):
        st.session_state["hash_medios_verificacion"] = hash_actual_4

        for _, r in df_mv_live.iterrows():
            k = _norm_text(r.get("_key", ""))
            if not k:
                continue
            st.session_state["medios_verificacion"][k] = {c: _norm_text(r.get(c, "")) for c in MV_LIBRES}

        existentes = set(st.session_state.get("medios_verificacion", {}).keys())
        actuales = set(keys_si_mv)
        for k in list(existentes - actuales):
            st.session_state["medios_verificacion"].pop(k, None)

        guardar_datos_nube()
