import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

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

st.markdown('<div class="titulo-seccion">🛡️ 12. Supuestos y Riesgos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Fase IV: Análisis de Riesgos y Factores Externos</div>', unsafe_allow_html=True)
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
    # Si viene de nube como list[dict], session_state ya lo convirtió a DataFrame
    st.session_state["datos_riesgos"] = _rebuild_from_base_keep_edits(pd.DataFrame(), df_base)
else:
    st.session_state["datos_riesgos"] = _rebuild_from_base_keep_edits(st.session_state["datos_riesgos"], df_base)

# Forzar orden de columnas (evita “desorden” al recargar)
st.session_state["datos_riesgos"] = _ensure_columns(st.session_state["datos_riesgos"])[COLUMN_ORDER].copy()

# --- TABLA EDITABLE ---
st.info("💡 Completa la matriz de riesgos. Las columnas de Categoría, Probabilidad e Impacto tienen menús desplegables.")

# Ocultar columna técnica _key: la usamos como índice (oculto) para mantener identidad estable por fila
df_for_editor = st.session_state["datos_riesgos"].set_index("_key", drop=True)

column_config = {
    "Tipo": st.column_config.TextColumn("Tipo", disabled=True, width="small"),
    "Objetivo": st.column_config.TextColumn("Objetivo", disabled=True, width="large"),
    "Supuesto": st.column_config.TextColumn("Supuesto (Condición para éxito)", width="medium"),
    "Riesgo": st.column_config.TextColumn("Riesgo Identificado", width="medium"),
    "Categoría": st.column_config.SelectboxColumn("Categoría", options=opciones_categoria),
    "Probabilidad": st.column_config.SelectboxColumn("Probabilidad", options=opciones_probabilidad),
    "Impacto": st.column_config.SelectboxColumn("Impacto", options=opciones_impacto),
    "Efecto": st.column_config.TextColumn("Efecto del Riesgo"),
    "Medida de Mitigación": st.column_config.TextColumn("Medida de Mitigación/Control", width="large"),
}

edited_view = st.data_editor(
    df_for_editor,
    column_config=column_config,
    hide_index=True,  # oculta _key (índice)
    use_container_width=True,
    key="editor_riesgos",
)

# Volver a DataFrame con _key como columna (para persistir y sincronizar)
edited_df = edited_view.reset_index()

# --- BOTÓN DE GUARDADO ---
if st.button("💾 Guardar Matriz de Riesgos", type="primary"):
    # Reforzar orden antes de persistir
    st.session_state["datos_riesgos"] = _ensure_columns(edited_df)[COLUMN_ORDER].copy()
    guardar_datos_nube()
    st.success("✅ Matriz de riesgos actualizada y guardada en la nube.")
    st.rerun()
