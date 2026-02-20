import streamlit as st
import os
import textwrap
from session_state import inicializar_session

# 1) Asegurar persistencia
inicializar_session()

# -----------------------------
# CSS (tarjetas)
# -----------------------------
st.markdown(
    """
    <style>
    .card-mml{
        background-color:#ffffff;
        border-radius:16px;
        padding:18px 18px 14px 18px;
        margin: 18px 0;
        border:1px solid #e2e8f0;
        box-shadow: 0 4px 10px -6px rgba(0,0,0,.18);
        position: relative;
    }
    .mml-leftbar{
        position:absolute; left:0; top:0; bottom:0; width:10px;
        border-top-left-radius:16px; border-bottom-left-radius:16px;
    }
    .mml-badge{
        display:inline-block;
        padding:6px 12px;
        border-radius:999px;
        font-weight:800;
        font-size:0.72rem;
        letter-spacing:.3px;
        color:#fff;
        margin-bottom:8px;
    }
    .mml-grid{
        display:grid;
        grid-template-columns: 2.2fr 1.2fr 0.8fr 1.4fr;
        gap: 14px;
        align-items: start;
    }
    .mml-coltitle{
        color:#1E3A8A;
        font-weight:900;
        font-size:0.78rem;
        text-transform:uppercase;
        text-align:center;
        margin-bottom:6px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom:4px;
    }
    .mml-text{
        font-size:0.95rem;
        color:#0f172a;
        text-align:center;
        line-height:1.25rem;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .mml-subtitle{
        color:#64748b;
        font-size:0.95rem;
        margin-top:-6px;
        margin-bottom:10px;
    }
    .mml-info{
        background:#eff6ff;
        border:1px solid #dbeafe;
        color:#1e40af;
        padding:10px 12px;
        border-radius:12px;
        margin: 14px 0 8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def _norm_text(v) -> str:
    if v is None:
        return ""
    return str(v).replace("\u00a0", " ").strip()

def _norm_key(v) -> str:
    return _norm_text(v).lower()

def _tipo_from_nivel(nivel_txt: str) -> str:
    n = _norm_text(nivel_txt)
    if n == "Objetivo General":
        return "OBJETIVO GENERAL"
    if n.startswith("Objetivo Específico"):
        return "OBJETIVO ESPECIFICO"
    if n == "Actividad Clave":
        return "ACTIVIDAD"
    return n.upper() if n else ""

# -----------------------------
# Header (igual estilo otras hojas)
# -----------------------------
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="mml-subtitle">Validación.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

# -----------------------------
# Construcción de filas desde HOJA 11 + SUPUESTO desde HOJA 12
# Fuente:
#   - Objetivo/Indicador/Meta: "Medios de verificación" (Hoja 11)
#     (en la práctica, vienen de datos_indicadores + meta_resultados_parciales)
#   - Supuesto: Hoja 12 (datos_riesgos) por match SOLO con Objetivo
# -----------------------------
P_COLS = ["P1", "P2", "P3", "P4", "P5"]

keys_si = []
for k, sel in st.session_state.get("seleccion_indicadores", {}).items():
    if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in P_COLS):
        keys_si.append(_norm_text(k))

datos_ind = st.session_state.get("datos_indicadores", {}) or {}
metas = st.session_state.get("meta_resultados_parciales", {}) or {}

df_riesgos = st.session_state.get("datos_riesgos", None)
if df_riesgos is None:
    df_riesgos = pd.DataFrame()

# index rápido de supuestos por objetivo (match SOLO por Objetivo)
supuestos_por_obj = {}
if isinstance(df_riesgos, pd.DataFrame) and not df_riesgos.empty and "Objetivo" in df_riesgos.columns:
    col_obj = df_riesgos["Objetivo"].astype(str).map(_norm_key)
    col_sup = df_riesgos["Supuesto"].astype(str) if "Supuesto" in df_riesgos.columns else ""
    for obj_norm, sup in zip(col_obj, col_sup):
        s = _norm_text(sup)
        if not obj_norm or not s:
            continue
        supuestos_por_obj.setdefault(obj_norm, set()).add(s)

rows = []
for k in keys_si:
    base = datos_ind.get(k, {}) if isinstance(datos_ind, dict) else {}
    nivel = _norm_text(base.get("Nivel", ""))
    tipo = _tipo_from_nivel(nivel)
    objetivo = _norm_text(base.get("Objetivo", ""))
    indicador = _norm_text(base.get("Indicador", ""))

    meta = _norm_text(metas.get(k, {}).get("Meta", "")) if isinstance(metas, dict) else ""

    obj_norm = _norm_key(objetivo)
    sups = sorted(list(supuestos_por_obj.get(obj_norm, set())))
    supuesto = "\n".join([f"• {t}" for t in sups]) if sups else ""

    # Solo se renderizan tarjetas si hay al menos objetivo o indicador
    if any([tipo, objetivo, indicador, meta, supuesto]):
        rows.append(
            {
                "tipo": tipo,
                "objetivo": objetivo,
                "indicador": indicador,
                "meta": meta,
                "supuesto": supuesto,
            }
        )

# -----------------------------
# Progreso de la matriz (vista final)
# Regla: % de filas con (objetivo+indicador+meta) no vacíos.
# -----------------------------
def _is_filled(x: str) -> bool:
    return bool(_norm_text(x))

total = len(rows)
if total == 0:
    progreso = 0.0
else:
    completas = 0
    for r in rows:
        if _is_filled(r.get("objetivo", "")) and _is_filled(r.get("indicador", "")) and _is_filled(r.get("meta", "")):
            completas += 1
    progreso = completas / max(total, 1)

st.progress(progreso)
st.write(f"Progreso de la Matriz: {int(round(progreso * 100, 0))}%")

st.divider()

st.markdown(
    '<div class="mml-info">✅ Esta hoja es de <b>validación final</b>. '
    'Trae <b>Objetivo, Indicador y Meta</b> desde <b>Medios de verificación (Hoja 11)</b> y '
    '<b>Supuestos</b> desde <b>Riesgos (Hoja 12)</b> (match por <b>Objetivo</b>).</div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Render de tarjetas
# -----------------------------
STYLE = {
    "OBJETIVO GENERAL": {"label": "FIN / OBJETIVO GENERAL", "bar": "#1d4ed8", "bg": "#eff6ff", "badge": "#2563eb"},
    "OBJETIVO ESPECIFICO": {"label": "PROPÓSITO / ESPECÍFICO", "bar": "#1d4ed8", "bg": "#eff6ff", "badge": "#2563eb"},
    "COMPONENTE": {"label": "COMPONENTE / PRODUCTO", "bar": "#15803d", "bg": "#ecfdf5", "badge": "#16a34a"},
    "ACTIVIDAD": {"label": "ACTIVIDAD", "bar": "#c2410c", "bg": "#fff7ed", "badge": "#ea580c"},
}

def _tipo_label_and_style(tipo: str):
    t = _norm_text(tipo)
    if t in ("OBJETIVO ESPECIFICO",):
        return STYLE["OBJETIVO ESPECIFICO"]
    if t in ("OBJETIVO GENERAL",):
        return STYLE["OBJETIVO GENERAL"]
    if t in ("ACTIVIDAD", "ACTIVIDAD CLAVE"):
        return STYLE["ACTIVIDAD"]
    # fallback
    return {"label": t if t else "MML", "bar": "#334155", "bg": "#f8fafc", "badge": "#475569"}

if not rows:
    st.info("Aún no hay datos para mostrar. Primero complete selección/medios (Hoja 11) y supuestos (Hoja 12).")
else:
    # orden visual por tipo
    order_rank = {"OBJETIVO GENERAL": 0, "OBJETIVO ESPECIFICO": 1, "COMPONENTE": 2, "ACTIVIDAD": 3}
    rows_sorted = sorted(rows, key=lambda r: order_rank.get(_norm_text(r.get("tipo","")), 99))

    for r in rows_sorted:
        conf = _tipo_label_and_style(r.get("tipo", ""))
        st.markdown(
            f"""
            <div class="card-mml" style="background-color:{conf['bg']};">
                <div class="mml-leftbar" style="background-color:{conf['bar']};"></div>
                <div style="padding-left:10px;">
                    <span class="mml-badge" style="background:{conf['badge']};">{conf['label']}</span>
                    <div class="mml-grid">
                        <div>
                            <div class="mml-coltitle">🎯 OBJETIVO</div>
                            <div class="mml-text">{_norm_text(r.get("objetivo",""))}</div>
                        </div>
                        <div>
                            <div class="mml-coltitle">📊 INDICADOR</div>
                            <div class="mml-text">{_norm_text(r.get("indicador",""))}</div>
                        </div>
                        <div>
                            <div class="mml-coltitle">🏁 META</div>
                            <div class="mml-text">{_norm_text(r.get("meta",""))}</div>
                        </div>
                        <div>
                            <div class="mml-coltitle">🛡️ SUPUESTOS</div>
                            <div class="mml-text">{_norm_text(r.get("supuesto",""))}</div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
