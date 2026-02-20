# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- DISEÑO ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)


# --- ENCABEZADO CON BARRA DE PROGRESO E IMAGEN ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown(
        '<div style="font-size: 30px; font-weight: 800; color: #1E3A8A; line-height: 1.2;">🛡️ 12. SUPUESTOS Y RIESGOS</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">Fase IV: Análisis de riesgos y factores externos.</div>',
        unsafe_allow_html=True
    )
    # Progreso (se actualiza después de inicializar la matriz)
    _progress_placeholder = st.empty()
    _progress_placeholder.progress(0.0, text="Avance estimado: 0%")

with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()


# -----------------------------
# Fuente: Hoja 11 (Medios de verificación)
# - Traer columnas: Tipo y Objetivo (en ese orden)
# -----------------------------
P_COLS = ["P1", "P2", "P3", "P4", "P5"]

def _norm_text(x) -> str:
    if x is None:
        return ""
    try:
        s = str(x)
    except Exception:
        return ""
    return " ".join(s.replace("\n", " ").replace("\r", " ").split()).strip()

def _tipo_from_nivel(nivel_txt: str) -> str:
    n = _norm_text(nivel_txt)
    if n == "Objetivo General":
        return "OBJETIVO GENERAL"
    if n.startswith("Objetivo Específico"):
        return "OBJETIVO ESPECIFICO"
    if n == "Actividad Clave":
        return "ACTIVIDAD"
    return n.upper() if n else ""

def _get_keys_si() -> list[str]:
    sel = st.session_state.get("seleccion_indicadores", {})
    keys = []
    if isinstance(sel, dict):
        for k, v in sel.items():
            if not isinstance(v, dict):
                continue
            val_sel = _norm_text(v.get("Selección", ""))
            if val_sel == "Sí":
                keys.append(k)
                continue
            # Fallback: si no existe "Selección", calculamos por P1..P5
            if val_sel == "":
                if all(bool(v.get(pc, False)) for pc in P_COLS):
                    keys.append(k)
    return keys

keys_si = _get_keys_si()

if not keys_si:
    st.warning("⚠️ No hay indicadores seleccionados (Hoja 11). Marca P1..P5 y presiona “Aplicar selección”, luego vuelve a esta hoja.")
    st.stop()

datos_ind = st.session_state.get("datos_indicadores", {})
if not isinstance(datos_ind, dict):
    datos_ind = {}

# Base (una fila por indicador seleccionado)
rows_base = []
for k in keys_si:
    base = datos_ind.get(k, {})
    if not isinstance(base, dict):
        base = {}
    nivel = _norm_text(base.get("Nivel", ""))
    objetivo_txt = _norm_text(base.get("Objetivo", ""))

    rows_base.append({
        "_key": _norm_text(k),
        "Tipo": _tipo_from_nivel(nivel),
        "Objetivo": objetivo_txt,
    })

df_base = pd.DataFrame(rows_base)

# -----------------------------
# Estructura de la matriz (mantener nombres y funcionalidades)
# -----------------------------
opciones_probabilidad = ["Muy Baja", "Baja", "Media", "Alta", "Muy Alta"]
opciones_impacto = ["Insignificante", "Menor", "Moderado", "Mayor", "Catastrófico"]
opciones_categoria = ["Financiero", "Operativo", "Social", "Ambiental", "Político", "Técnico"]

DEFAULTS_EDITABLE = {
    "Supuesto": "",
    "Riesgo": "",
    "Categoría": "Técnico",
    "Probabilidad": "Media",
    "Impacto": "Moderado",
    "Efecto": "",
    "Medida de Mitigación": ""
}

COLUMN_ORDER = [
    "_key",
    "Tipo",
    "Objetivo",
    "Supuesto",
    "Riesgo",
    "Categoría",
    "Probabilidad",
    "Impacto",
    "Efecto",
    "Medida de Mitigación",
]

def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    for c in COLUMN_ORDER:
        if c not in df2.columns:
            df2[c] = "" if c not in DEFAULTS_EDITABLE else DEFAULTS_EDITABLE[c]
    # Limpiar columnas extra que puedan venir de versiones anteriores
    df2 = df2[[c for c in COLUMN_ORDER if c in df2.columns]].copy()
    return df2

def _rebuild_from_base_keep_edits(df_old: pd.DataFrame, df_new_base: pd.DataFrame) -> pd.DataFrame:
    # Si no hay _key válido en old, devolvemos base con defaults
    if not isinstance(df_old, pd.DataFrame) or df_old.empty or "_key" not in df_old.columns:
        out = df_new_base.copy()
        for c, v in DEFAULTS_EDITABLE.items():
            out[c] = v
        return _ensure_columns(out)[COLUMN_ORDER].copy()

    old = df_old.copy()
    old["_key"] = old["_key"].astype(str)

    base = df_new_base.copy()
    base["_key"] = base["_key"].astype(str)

    # Tomar columnas editables desde old (último valor por _key)
    editable_cols = list(DEFAULTS_EDITABLE.keys())
    old_small = old[["_key"] + [c for c in editable_cols if c in old.columns]].copy()
    old_small = old_small.dropna(subset=["_key"])
    old_small = old_small.drop_duplicates(subset=["_key"], keep="last")

    merged = base.merge(old_small, on="_key", how="left")

    for c, default_val in DEFAULTS_EDITABLE.items():
        if c not in merged.columns:
            merged[c] = default_val
        else:
            merged[c] = merged[c].fillna(default_val)

    merged = _ensure_columns(merged)
    return merged[COLUMN_ORDER].copy()

# -----------------------------
# INICIALIZACIÓN / SINCRONIZACIÓN
# -----------------------------
if "datos_riesgos" not in st.session_state or not isinstance(st.session_state.get("datos_riesgos"), pd.DataFrame):
    st.session_state["datos_riesgos"] = _rebuild_from_base_keep_edits(pd.DataFrame(), df_base)
else:
    st.session_state["datos_riesgos"] = _rebuild_from_base_keep_edits(st.session_state["datos_riesgos"], df_base)

# Forzar orden de columnas (evita “desorden” al recargar)
st.session_state["datos_riesgos"] = _ensure_columns(st.session_state["datos_riesgos"])[COLUMN_ORDER].copy()

# --- ACTUALIZAR PROGRESO (después de inicializar/ordenar la matriz) ---
st.info("💡 Completa la matriz de riesgos. Las columnas de Categoría, Probabilidad e Impacto tienen menús desplegables. El texto se ajusta automáticamente y las filas crecen según el contenido.")

df_grid = st.session_state["datos_riesgos"].copy()

# -----------------------------
# AGGRID: Wrap + AutoHeight (sin perder funcionalidades)
# -----------------------------
gob = GridOptionsBuilder.from_dataframe(df_grid)

# Ocultar llave técnica
gob.configure_column("_key", hide=True)

# Columnas fijas (no editables)
gob.configure_column("Tipo", editable=False, width=170)
gob.configure_column("Objetivo", editable=False, width=420)

# Columnas editables con wrap/autoHeight
wrap_cellstyle = JsCode("""function(params){return {'whiteSpace': 'normal', 'lineHeight': '1.2'};}""")

gob.configure_column(
    "Supuesto",
    header_name="Supuesto (Condición para éxito)",
    editable=True,
    wrapText=True,
    autoHeight=True,
    cellStyle=wrap_cellstyle,
    width=260,
)

gob.configure_column(
    "Riesgo",
    header_name="Riesgo Identificado",
    editable=True,
    wrapText=True,
    autoHeight=True,
    cellStyle=wrap_cellstyle,
    width=240,
)

gob.configure_column(
    "Efecto",
    header_name="Efecto del Riesgo",
    editable=True,
    wrapText=True,
    autoHeight=True,
    cellStyle=wrap_cellstyle,
    width=220,
)

gob.configure_column(
    "Medida de Mitigación",
    header_name="Medida de Mitigación/Control",
    editable=True,
    wrapText=True,
    autoHeight=True,
    cellStyle=wrap_cellstyle,
    width=300,
)

# Selects
gob.configure_column(
    "Categoría",
    editable=True,
    cellEditor="agSelectCellEditor",
    cellEditorParams={"values": opciones_categoria},
    width=140,
)

gob.configure_column(
    "Probabilidad",
    editable=True,
    cellEditor="agSelectCellEditor",
    cellEditorParams={"values": opciones_probabilidad},
    width=140,
)

gob.configure_column(
    "Impacto",
    editable=True,
    cellEditor="agSelectCellEditor",
    cellEditorParams={"values": opciones_impacto},
    width=140,
)

# Default col def (wrap + autoHeight para no cortar al achicar columnas)
gob.configure_default_column(
    resizable=True,
    sortable=True,
    filter=True,
    wrapText=True,
    autoHeight=True,
)

grid_options = gob.build()
grid_options["domLayout"] = "autoHeight"  # el componente crece hacia abajo según contenido/filas

grid_response = AgGrid(
    df_grid,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.AS_INPUT,
    fit_columns_on_grid_load=False,
    allow_unsafe_jscode=True,
    custom_css={
        ".ag-header-cell-label": {"justify-content": "center"},
        ".ag-header-cell-text": {"color": "#1E3A8A", "font-weight": "800"},
        ".ag-header": {"background-color": "#f8fafc"},
    },
    theme="streamlit",
    key="grid_riesgos",
)

edited_df = pd.DataFrame(grid_response.get("data", []))
edited_df = _ensure_columns(edited_df)[COLUMN_ORDER].copy()

# --- PROGRESO (calculado sobre lo que el usuario edita en pantalla) ---
try:
    _required_cols = [
        "Riesgo Identificado",
        "Supuesto",
        "Efecto del Riesgo",
        "Medida de Mitigación/Control",
    ]
    if len(edited_df) > 0 and all(c in edited_df.columns for c in _required_cols):
        _tmp = edited_df[_required_cols].copy()
        # Normalizar vacíos
        _tmp = _tmp.fillna("").astype(str).applymap(lambda x: x.strip())
        _filled = (_tmp != "").sum().sum()
        _total = _tmp.shape[0] * _tmp.shape[1]
        _progreso = (_filled / _total) if _total > 0 else 0.0
    else:
        _progreso = 0.0
    _progreso = float(max(0.0, min(1.0, _progreso)))
    _progress_placeholder.progress(_progreso, text=f"Avance estimado: {int(_progreso*100)}%")
except Exception:
    pass


# --- BOTÓN DE GUARDADO ---
if st.button("💾 Guardar Matriz de Riesgos", type="primary"):
    st.session_state["datos_riesgos"] = edited_df.copy()
    guardar_datos_nube()
    st.success("✅ Matriz de riesgos actualizada y guardada en la nube.")
    st.rerun()
