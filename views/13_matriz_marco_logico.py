import streamlit as st
import os
import graphviz
import textwrap
import html
import pandas as pd
from session_state import inicializar_session

# 1. Asegurar persistencia
inicializar_session()

# --- DISEÑO DE PANTALLA (CSS) ---
st.markdown("""
    <style>
    .card-mml {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .col-title {
        color: #1E3A8A;
        font-weight: 900;
        font-size: 14px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 10px;
    }
    .col-content {
        font-size: 15px;
        text-align: center;
        color: #0f172a;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-weight: 900;
        font-size: 12px;
        color: white;
        margin-bottom: 15px;
    }
    .layout-grid {
        display: grid;
        grid-template-columns: 2fr 1.2fr 0.8fr 1.5fr;
        gap: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER (igual a tus otras hojas) ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Vista final (solo lectura). La información se consolida desde Hojas 11 y 12.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- BARRA DE PROGRESO (fija, como pediste) ---
st.progress(0.60, text="Avance estimado: 60%")

# ============================
#  FUENTES DE DATOS (HOJA 11 + HOJA 12)
# ============================
P_COLS = ["P1", "P2", "P3", "P4", "P5"]

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

def _safe_label(s: str, max_len: int = 180) -> str:
    """
    Sanitiza textos para Graphviz labels.
    - evita comillas dobles
    - recorta longitudes extremas
    """
    s = _norm_text(s)
    s = s.replace('"', "'")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if len(s) > max_len:
        s = s[: max_len - 1] + "…"
    return s

def _collect_keys_si() -> list[str]:
    keys = []
    sel = st.session_state.get("seleccion_indicadores", {}) or {}
    if isinstance(sel, dict):
        for k, v in sel.items():
            if isinstance(v, dict) and all(bool(v.get(p, False)) for p in P_COLS):
                keys.append(_norm_text(k))
    return keys

def _supuestos_por_objetivo() -> dict[str, list[str]]:
    """
    Hoja 12 (Riesgos): usa columna interna 'Objetivo' para match y 'Supuesto' para texto.
    """
    out: dict[str, set[str]] = {}
    df = st.session_state.get("datos_riesgos", None)
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {}
    if "Objetivo" not in df.columns:
        return {}
    sup_col = "Supuesto" if "Supuesto" in df.columns else None
    if sup_col is None:
        return {}
    for _, r in df.iterrows():
        obj = _norm_key(r.get("Objetivo", ""))
        sup = _norm_text(r.get(sup_col, ""))
        if not obj or not sup:
            continue
        out.setdefault(obj, set()).add(sup)
    return {k: sorted(list(v)) for k, v in out.items()}

# Construir "medios de verificación" desde Hoja 11 (sin depender de Excel)
keys_si = _collect_keys_si()
datos_ind = st.session_state.get("datos_indicadores", {}) or {}
metas = st.session_state.get("meta_resultados_parciales", {}) or {}
sup_map = _supuestos_por_objetivo()

datos_mml = []
for k in keys_si:
    base = datos_ind.get(k, {}) if isinstance(datos_ind, dict) else {}
    nivel = _norm_text(base.get("Nivel", ""))
    tipo = _tipo_from_nivel(nivel)

    objetivo = _norm_text(base.get("Objetivo", ""))
    indicador = _norm_text(base.get("Indicador", ""))

    meta = ""
    if isinstance(metas, dict):
        meta = _norm_text(metas.get(k, {}).get("Meta", ""))

    sups = sup_map.get(_norm_key(objetivo), [])
    supuesto = "\n".join([f"• {s}" for s in sups]) if sups else ""

    # Solo tarjetas con contenido mínimo
    if objetivo or indicador or meta or supuesto:
        datos_mml.append({
            "tipo": tipo,
            "objetivo": objetivo,
            "indicador": indicador,
            "meta": meta,
            "supuestos": supuesto,
        })

# ============================
#  CONFIG / ESTILOS POR TIPO
# ============================
CONFIG_NIVELES = {
    "OBJETIVO GENERAL": {
        "label": "FIN / OBJETIVO GENERAL",
        "color": "#1d4ed8",
        "badge": "#2563eb"
    },
    "OBJETIVO ESPECIFICO": {
        "label": "PROPÓSITO / ESPECÍFICO",
        "color": "#1d4ed8",
        "badge": "#2563eb"
    },
    "COMPONENTE": {
        "label": "COMPONENTE / PRODUCTO",
        "color": "#16a34a",
        "badge": "#16a34a"
    },
    "ACTIVIDAD": {
        "label": "ACTIVIDAD",
        "color": "#ea580c",
        "badge": "#ea580c"
    }
}

def _config_tipo(tipo: str) -> dict:
    t = _norm_text(tipo)
    if t in CONFIG_NIVELES:
        return CONFIG_NIVELES[t]
    # fallback
    return {"label": t if t else "MML", "color": "#475569", "badge": "#475569"}

# ============================
#  EXPORTACIÓN PNG (Graphviz)
# ============================
def generar_png_estetico(items: list[dict]) -> bytes | None:
    try:
        dot = graphviz.Digraph(format="png")
        dot.attr(rankdir="TB", bgcolor="white", pad="0.2")
        dot.attr("node", shape="box", style="rounded,filled", fontname="Helvetica", fontsize="10", color="#e2e8f0")

        # Agrupar por tipo en el orden deseado
        orden = ["OBJETIVO GENERAL", "OBJETIVO ESPECIFICO", "COMPONENTE", "ACTIVIDAD"]
        grouped = {k: [] for k in orden}
        other = []
        for it in items:
            t = _norm_text(it.get("tipo", ""))
            if t in grouped:
                grouped[t].append(it)
            else:
                other.append(it)

        idx = 0
        prev_cluster_last = None

        def add_item_node(it, idx_local: int):
            cfg = _config_tipo(it.get("tipo", ""))
            objetivo = _safe_label(it.get("objetivo", ""))
            indicador = _safe_label(it.get("indicador", ""))
            meta = _safe_label(it.get("meta", ""))
            sup = _safe_label(it.get("supuestos", ""), max_len=220)

            label = f"{cfg['label']}\n\nOBJETIVO:\n{objetivo}\n\nINDICADOR:\n{indicador}\n\nMETA:\n{meta}\n\nSUPUESTOS:\n{sup}"
            node_id = f"n{idx_local}"
            dot.node(node_id, label=label, fillcolor="#ffffff")
            return node_id

        # Crear nodos por grupos; conectar con flechas suaves entre grupos
        for t in orden:
            items_t = grouped.get(t, [])
            if not items_t:
                continue

            with dot.subgraph(name=f"cluster_{t}") as c:
                c.attr(color="white")
                for it in items_t:
                    node_id = add_item_node(it, idx)
                    idx += 1
                    # cadenas dentro del cluster (opcional)
                    if prev_cluster_last is not None:
                        dot.edge(prev_cluster_last, node_id, color="#94a3b8")
                        prev_cluster_last = node_id
                    else:
                        prev_cluster_last = node_id

        # otros
        for it in other:
            node_id = add_item_node(it, idx)
            idx += 1
            if prev_cluster_last is not None:
                dot.edge(prev_cluster_last, node_id, color="#94a3b8")
            prev_cluster_last = node_id

        return dot.pipe(format="png")
    except Exception:
        return None

# Sidebar: exportación estética
with st.sidebar:
    st.markdown("### 🖼️ Exportación")
    imagen_estetica = generar_png_estetico(datos_mml)
    if isinstance(imagen_estetica, (bytes, bytearray)) and len(imagen_estetica) > 0:
        st.download_button(
            label="🖼️ Descargar Matriz Estética (PNG)",
            data=bytes(imagen_estetica),
            file_name="matriz_marco_logico.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("Exportación PNG no disponible (Graphviz no pudo generar la imagen con los datos actuales).")

# ============================
#  RENDER DE TARJETAS
# ============================
if not datos_mml:
    st.info("No hay datos para mostrar. Verifica que en Hoja 11 existan indicadores con Selección = Sí y Meta diligenciada.")
    st.stop()

for item in datos_mml:
    cfg = _config_tipo(item.get("tipo", ""))

    badge = cfg["badge"]
    label = cfg["label"]

    objetivo = _norm_text(item.get("objetivo", ""))
    indicador = _norm_text(item.get("indicador", ""))
    meta = _norm_text(item.get("meta", ""))
    supuestos = _norm_text(item.get("supuestos", ""))

    # Ajuste de texto para tarjetas (sin romper HTML)
    objetivo = html.escape(objetivo)
    indicador = html.escape(indicador)
    meta = html.escape(meta)
    supuestos = html.escape(supuestos)

    st.markdown(
        f"""
        <div class="card-mml">
            <div class="badge" style="background:{badge};">{label}</div>
            <div class="layout-grid">
                <div>
                    <div class="col-title">OBJETIVOS</div>
                    <div class="col-content">{objetivo}</div>
                </div>
                <div>
                    <div class="col-title">INDICADOR</div>
                    <div class="col-content">{indicador}</div>
                </div>
                <div>
                    <div class="col-title">META</div>
                    <div class="col-content">{meta}</div>
                </div>
                <div>
                    <div class="col-title">SUPUESTOS</div>
                    <div class="col-content">{supuestos}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
