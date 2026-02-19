import streamlit as st
import pandas as pd
import uuid
import os

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

    .compact-divider { margin: 14px 0px !important; border-top: 1px solid #eee; }
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

def _safe_obj_text(item):
    if isinstance(item, dict):
        return _norm_text(item.get("texto", ""))
    return _norm_text(item)

def _safe_obj_id(item):
    if isinstance(item, dict):
        return _norm_text(item.get("id_unico", ""))
    return ""

def _mk_map_key(nivel, objetivo):
    return f"{_norm_text(nivel)}||{_norm_text(objetivo)}"

def _generar_indicador(obj, cond, lugar):
    obj = _norm_text(obj)
    cond = _norm_text(cond)
    lugar = _norm_text(lugar)
    if not obj or not cond:
        return ""
    return _clean_spaces(f"{obj} {cond} {lugar}")

def _estado(obj, cond, lugar):
    return "Completo" if (_norm_text(obj) and _norm_text(cond) and _norm_text(lugar)) else "Pendiente"

def _resolve_key(nivel, objetivo_txt, id_unico):
    if id_unico:
        return id_unico

    if 'indicadores_mapa_objetivo' not in st.session_state or not isinstance(st.session_state.get('indicadores_mapa_objetivo'), dict):
        st.session_state['indicadores_mapa_objetivo'] = {}

    kmap = _mk_map_key(nivel, objetivo_txt)
    if kmap in st.session_state['indicadores_mapa_objetivo']:
        return st.session_state['indicadores_mapa_objetivo'][kmap]

    new_key = str(uuid.uuid4())
    st.session_state['indicadores_mapa_objetivo'][kmap] = new_key
    return new_key

def _ensure_columns(df, cols_defaults):
    """
    cols_defaults: dict col -> default_value
    """
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()
    for c, v in cols_defaults.items():
        if c not in df.columns:
            df[c] = v
    return df

# -----------------------------
# Header
# -----------------------------
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📊 11. Indicadores</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">El indicador se autogenera al editar. Presiona “Guardar en Nube” para persistir.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.markdown(
    '<div class="info-box">Diligencia: <b>1. Objeto</b>, <b>2. Condición Deseada</b> y <b>3. Lugar</b>. '
    'El sistema autogenera el indicador. Las filas completas se resaltan en azul tenue.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Base de objetivos: Hoja 7
# -----------------------------
arbol = st.session_state.get('arbol_objetivos_final', {})
if not isinstance(arbol, dict):
    arbol = {}

niveles = ["Objetivo General", "Fines Directos", "Fines Indirectos", "Medios Directos", "Medios Indirectos"]

lista_base = []
for nivel in niveles:
    items = _as_list(arbol.get(nivel, []))
    for item in items:
        texto = _safe_obj_text(item)
        if not texto:
            continue
        lista_base.append({
            "Nivel": nivel,
            "Objetivo": texto,
            "id_unico": _safe_obj_id(item)
        })

if not lista_base:
    st.warning("⚠️ No se encontraron objetivos. Completa primero la Hoja 7 (Árbol de Objetivos Final).")
    st.stop()

# -----------------------------
# State hoja 11
# -----------------------------
if 'datos_indicadores' not in st.session_state or not isinstance(st.session_state.get('datos_indicadores'), dict):
    st.session_state['datos_indicadores'] = {}

if 'df_indicadores' not in st.session_state or not isinstance(st.session_state.get('df_indicadores'), pd.DataFrame):
    st.session_state['df_indicadores'] = pd.DataFrame()

base_lookup = {(r["Nivel"], r["Objetivo"]): r.get("id_unico", "") for r in lista_base}

# -----------------------------
# DF base
# -----------------------------
def _build_df_from_base():
    rows = []
    for r in lista_base:
        nivel = r["Nivel"]
        objetivo_txt = r["Objetivo"]
        id_unico = r.get("id_unico", "")

        key_estable = _resolve_key(nivel, objetivo_txt, id_unico)

        guardado = st.session_state['datos_indicadores'].get(key_estable, {})
        if (not guardado) and (objetivo_txt in st.session_state['datos_indicadores']):
            guardado = st.session_state['datos_indicadores'].get(objetivo_txt, {})

        obj = _norm_text(guardado.get("Objeto", ""))
        cond = _norm_text(guardado.get("Condicion", guardado.get("Condición", "")))
        lugar = _norm_text(guardado.get("Lugar", ""))

        indicador = _norm_text(guardado.get("Indicador", "")) or _generar_indicador(obj, cond, lugar)
        est = _estado(obj, cond, lugar)

        rows.append({
            "_estado": est,  # interno (no visible)
            "Nivel": nivel,
            "Objetivo": objetivo_txt,
            "1. Objeto": obj,
            "2. Condición Deseada": cond,
            "3. Lugar": lugar,
            "Indicador Generado": indicador,
        })

    return pd.DataFrame(rows)

def _sync_df_keep_user_edits(df_old):
    df_new = _build_df_from_base()

    if df_old is None or df_old.empty:
        return df_new

    keycols = ["Nivel", "Objetivo"]
    df_old_k = df_old.copy()
    df_new_k = df_new.copy()

    df_merge = pd.merge(
        df_new_k[keycols],
        df_old_k,
        on=keycols,
        how="left",
        suffixes=("", "_old")
    )

    # asegurar columnas
    for col in df_new.columns:
        if col not in df_merge.columns:
            df_merge[col] = df_new[col].values if col in df_new.columns else ""

    # forzar columnas "sistema" desde df_new primero
    df_merge["_estado"] = df_new["_estado"].values
    df_merge["Indicador Generado"] = df_new["Indicador Generado"].values

    # si el usuario ya tenía valores editables, conservarlos
    for col_edit in ["1. Objeto", "2. Condición Deseada", "3. Lugar"]:
        if col_edit in df_old_k.columns:
            mask = df_merge[col_edit].isna() | (df_merge[col_edit].astype(str) == "nan")
            df_merge.loc[mask, col_edit] = df_new[col_edit].values

    # recalcular (por si conserva inputs)
    df_merge["Indicador Generado"] = df_merge.apply(
        lambda r: _generar_indicador(r.get("1. Objeto", ""), r.get("2. Condición Deseada", ""), r.get("3. Lugar", "")),
        axis=1
    )
    df_merge["_estado"] = df_merge.apply(
        lambda r: _estado(r.get("1. Objeto", ""), r.get("2. Condición Deseada", ""), r.get("3. Lugar", "")),
        axis=1
    )

    df_merge = df_merge[df_new.columns].copy()
    return df_merge

df_old_ui = st.session_state.get('df_indicadores', pd.DataFrame())
df_ui = _sync_df_keep_user_edits(df_old_ui)

# asegurar columnas obligatorias
cols_defaults = {
    "_estado": "Pendiente",
    "Nivel": "",
    "Objetivo": "",
    "1. Objeto": "",
    "2. Condición Deseada": "",
    "3. Lugar": "",
    "Indicador Generado": "",
}
df_ui = _ensure_columns(df_ui, cols_defaults)

# guardar si cambió estructura
if df_old_ui is None or df_old_ui.empty:
    st.session_state['df_indicadores'] = df_ui.copy()
else:
    if list(df_old_ui.columns) != list(df_ui.columns) or len(df_old_ui) != len(df_ui):
        st.session_state['df_indicadores'] = df_ui.copy()

df_work = st.session_state['df_indicadores'].copy()
df_work = _ensure_columns(df_work, cols_defaults)

# -----------------------------
# AgGrid config (sin columna Estado visible)
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df_work)

# Oculta columna interna de estado
gb.configure_column("_estado", headerName="", editable=False, hide=True)

gb.configure_column("Nivel", headerName="Nivel", editable=False, wrapText=True, autoHeight=True, width=180)
gb.configure_column("Objetivo", headerName="Objetivo", editable=False, wrapText=True, autoHeight=True, width=520)

gb.configure_column("1. Objeto", headerName="1. Objeto", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("2. Condición Deseada", headerName="2. Condición Deseada", editable=True, wrapText=True, autoHeight=True, width=280)
gb.configure_column("3. Lugar", headerName="3. Lugar", editable=True, wrapText=True, autoHeight=True, width=170)

gb.configure_column("Indicador Generado", headerName="Indicador Generado", editable=False, wrapText=True, autoHeight=True, width=440)

# Fondo azul tenue cuando está completo
jscode_row_style = JsCode("""
function(params) {
    if (params.data && params.data._estado === "Completo") {
        return { 'background-color': '#EFF6FF', 'color': '#000000' };
    }
    return { 'background-color': '#FFFFFF', 'color': '#000000' };
};
""")

gb.configure_grid_options(getRowStyle=jscode_row_style, domLayout='autoHeight')

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
    theme='streamlit',
    allow_unsafe_jscode=True,
    key="grid_indicadores"
)

df_live = pd.DataFrame(grid_response.get("data", []))
df_live = _ensure_columns(df_live, cols_defaults)

# -----------------------------
# Autogeneración en vivo (sin KeyError)
# -----------------------------
df_live["Indicador Generado"] = df_live.apply(
    lambda r: _generar_indicador(r.get("1. Objeto", ""), r.get("2. Condición Deseada", ""), r.get("3. Lugar", "")),
    axis=1
)
df_live["_estado"] = df_live.apply(
    lambda r: _estado(r.get("1. Objeto", ""), r.get("2. Condición Deseada", ""), r.get("3. Lugar", "")),
    axis=1
)

# mantener orden de columnas (todas existen por _ensure_columns)
df_live = df_live[list(df_work.columns)].copy()

def _normalize_df_for_compare(df):
    df2 = df.copy()
    for c in df2.columns:
        df2[c] = df2[c].astype(str)
    return df2

need_rerun = False
df_prev = st.session_state.get("df_indicadores", pd.DataFrame()).copy()
df_prev = _ensure_columns(df_prev, cols_defaults)

a = _normalize_df_for_compare(df_prev)
b = _normalize_df_for_compare(df_live)
if not a.equals(b):
    st.session_state["df_indicadores"] = df_live
    need_rerun = True

if need_rerun:
    st.rerun()

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# -----------------------------
# Guardado a nube
# -----------------------------
col_btn, col_stats = st.columns([1, 2], vertical_alignment="center")
with col_btn:
    btn_guardar = st.button("💾 Guardar en Nube", type="primary")

with col_stats:
    try:
        df_stats = st.session_state.get("df_indicadores", pd.DataFrame())
        df_stats = _ensure_columns(df_stats, cols_defaults)
        total = len(df_stats)
        completos = int((df_stats["_estado"] == "Completo").sum()) if (not df_stats.empty) else 0
        st.markdown(f"**Completos:** {completos} / {total}")
    except Exception:
        pass

if btn_guardar:
    df_save = st.session_state.get("df_indicadores", pd.DataFrame()).copy()
    df_save = _ensure_columns(df_save, cols_defaults)

    if df_save.empty:
        st.warning("No hay datos para guardar.")
        st.stop()

    errores = []
    guardados_ok = 0

    for _, r in df_save.iterrows():
        nivel = _norm_text(r.get("Nivel", ""))
        objetivo_txt = _norm_text(r.get("Objetivo", ""))

        obj = _norm_text(r.get("1. Objeto", ""))
        cond = _norm_text(r.get("2. Condición Deseada", ""))
        lugar = _norm_text(r.get("3. Lugar", ""))

        if not obj or not cond:
            if objetivo_txt:
                errores.append(f"- Falta Objeto/Condición en: {objetivo_txt[:90]}")
            continue

        id_unico = _norm_text(base_lookup.get((nivel, objetivo_txt), ""))
        key_estable = _resolve_key(nivel, objetivo_txt, id_unico)

        indicador = _generar_indicador(obj, cond, lugar)

        st.session_state['datos_indicadores'][key_estable] = {
            "Objetivo": objetivo_txt,
            "Nivel": nivel,
            "Objeto": obj,
            "Condicion": cond,
            "Lugar": lugar,
            "Indicador": indicador
        }
        guardados_ok += 1

    guardar_datos_nube()

    if errores:
        st.warning("Se guardó lo válido, pero hay filas incompletas:\n" + "\n".join(errores))
    if guardados_ok > 0:
        st.success("✅ Indicadores guardados y sincronizados en la nube.")
    else:
        st.info("No se guardó nada (faltan Objeto y/o Condición en las filas editadas).")
