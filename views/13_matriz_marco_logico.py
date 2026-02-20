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
st.markdown(
    """
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
        font-weight: 800;
        font-size: 0.85rem;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 8px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 5px;
    }
    .col-content {
        font-size: 0.95rem;
        color: #334155;
        text-align: center;
        line-height: 1.5;
        padding: 5px;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    .tipo-badge {
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        line-height: 1.2;
        white-space: nowrap;
    }

    /* fila superior como Excel */
    .mml-toprow {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    .mml-head {
        display: grid;
        grid-template-columns: 2fr 1.5fr 1fr 1.5fr;
        width: 100%;
        gap: 15px;
        align-items: center;
    }
    .mml-head-title {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 0.82rem;
        text-transform: uppercase;
        text-align: center;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Configuración de niveles (colores iguales al diseño original)
# -----------------------------
CONFIG_NIVELES = {
    "OBJETIVO GENERAL": {"color": "#2563EB", "bg": "#EFF6FF", "badge": "OBJETIVO GENERAL"},
    "OBJETIVO ESPECIFICO": {"color": "#2563EB", "bg": "#EFF6FF", "badge": "OBJETIVO ESPECIFICO"},
    "COMPONENTE": {"color": "#059669", "bg": "#ECFDF5", "badge": "COMPONENTE / PRODUCTO"},
    "ACTIVIDAD": {"color": "#D97706", "bg": "#FFFBEB", "badge": "ACTIVIDAD"},
}

ORDEN_TIPO = {
    "OBJETIVO GENERAL": 1,
    "OBJETIVO ESPECIFICO": 2,
    "COMPONENTE": 3,
    "ACTIVIDAD": 4,
}


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
    if n == "Componente":
        return "COMPONENTE"
    return ""


def _build_supuestos_index(df_riesgos: pd.DataFrame) -> dict:
    """Indexa supuestos por Objetivo (match solo por Objetivo)."""
    idx = {}
    if not isinstance(df_riesgos, pd.DataFrame) or df_riesgos.empty:
        return idx
    if "Objetivo" not in df_riesgos.columns or "Supuesto" not in df_riesgos.columns:
        return idx

    for _, row in df_riesgos.iterrows():
        obj = _norm_key(row.get("Objetivo", ""))
        sup = _norm_text(row.get("Supuesto", ""))
        if not obj or not sup:
            continue
        idx.setdefault(obj, set()).add(sup)
    return idx


def _wrap_plain(texto: str, width: int = 60) -> str:
    t = _norm_text(texto)
    if not t:
        return ""
    return "\n".join(textwrap.fill(line, width=width) for line in t.splitlines())


def _sanitize_for_graphviz(v: str) -> str:
    """Escapa texto para labels HTML de Graphviz."""
    s = _norm_text(v)
    s = html.escape(s, quote=True)
    s = s.replace("\n", " ")
    s = " ".join(s.split())
    return s


def generar_png_estetico(datos):
    """Genera un PNG con Graphviz. Si falla, retorna None."""
    try:
        dot = graphviz.Digraph(format="png")
        dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.2", bgcolor="white", fontname="Arial")

        def wrap_html(t, w=25):
            return "<BR/>".join(textwrap.wrap(_sanitize_for_graphviz(t), width=w))

        for i, fila in enumerate(datos):
            conf = CONFIG_NIVELES.get(fila["tipo"], {"color": "#1E3A8A", "bg": "#f8fafc", "badge": fila["tipo"]})

            label = f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
                <TR>
                    <TD WIDTH="10" BGCOLOR="{conf['color']}"></TD>
                    <TD BGCOLOR="{conf['bg']}">
                        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="10" CELLPADDING="5">
                            <TR>
                                <TD COLSPAN="4" ALIGN="LEFT">
                                    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5">
                                        <TR><TD BGCOLOR="{conf['color']}"><FONT COLOR="white" POINT-SIZE="10"><B>  {wrap_html(conf['badge'], 28)}  </B></FONT></TD></TR>
                                    </TABLE>
                                </TD>
                            </TR>
                            <TR>
                                <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>RESUMEN NARRATIVO</B></FONT></TD>
                                <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>INDICADOR</B></FONT></TD>
                                <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>META</B></FONT></TD>
                                <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>SUPUESTOS</B></FONT></TD>
                            </TR>
                            <TR>
                                <TD WIDTH="180" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(fila['objetivo'], 28)}</FONT></TD>
                                <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(fila['indicador'], 22)}</FONT></TD>
                                <TD WIDTH="80"  ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(fila['meta'], 14)}</FONT></TD>
                                <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(fila['supuesto'], 22)}</FONT></TD>
                            </TR>
                        </TABLE>
                    </TD>
                </TR>
            </TABLE>>'''

            dot.node(
                f"card_{i}",
                label=label,
                shape="rect",
                style="filled",
                fillcolor="white",
                color="#e2e8f0",
                penwidth="2",
            )
            if i > 0:
                dot.edge(f"card_{i-1}", f"card_{i}", style="invis")

        return dot.pipe(format="png")
    except Exception:
        return None


# -----------------------------
# Construir datos reales desde Hoja 11 y Hoja 12
# -----------------------------
P_COLS = ["P1", "P2", "P3", "P4", "P5"]

keys_si = []
for k, sel in (st.session_state.get("seleccion_indicadores", {}) or {}).items():
    if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in P_COLS):
        keys_si.append(_norm_text(k))

# En Hoja 11 ya se almacenan:
# - datos_indicadores[key] = {Objetivo, Nivel, Indicador, ...}
# - meta_resultados_parciales[key] = {Meta, ...}
datos_ind = st.session_state.get("datos_indicadores", {}) or {}
metas = st.session_state.get("meta_resultados_parciales", {}) or {}

df_riesgos = st.session_state.get("datos_riesgos", None)
if df_riesgos is None:
    df_riesgos = pd.DataFrame()

sup_idx = _build_supuestos_index(df_riesgos)

datos_mml = []
for k in keys_si:
    base = datos_ind.get(k, {}) if isinstance(datos_ind, dict) else {}
    nivel = _norm_text(base.get("Nivel", ""))
    tipo = _tipo_from_nivel(nivel)
    if not tipo:
        continue

    objetivo = _norm_text(base.get("Objetivo", ""))
    indicador = _norm_text(base.get("Indicador", ""))
    meta = _norm_text(metas.get(k, {}).get("Meta", "")) if isinstance(metas, dict) else ""

    sups = sorted(list(sup_idx.get(_norm_key(objetivo), set())))
    supuesto = "\n".join([f"• {s}" for s in sups]) if sups else ""

    datos_mml.append(
        {
            "tipo": tipo,
            "objetivo": objetivo,
            "indicador": indicador,
            "meta": meta,
            "supuesto": supuesto,
        }
    )

# Orden jerárquico (mismo estilo esperado)
datos_mml.sort(key=lambda r: (ORDEN_TIPO.get(r["tipo"], 99), r.get("objetivo", "")))


# --- PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Exportación Visual")
    st.write("Descarga una versión estética de alta resolución de tu matriz.")

    imagen_estetica = generar_png_estetico(datos_mml)
    if isinstance(imagen_estetica, (bytes, bytearray)) and len(imagen_estetica) > 0:
        st.download_button(
            label="🖼️ Descargar Matriz Estética (PNG)",
            data=imagen_estetica,
            file_name="MML_Visual.png",
            mime="image/png",
            use_container_width=True,
        )
    else:
        st.info("No fue posible generar la imagen PNG en este momento. La vista en tarjetas sigue disponible.")


# --- CUERPO DE LA PÁGINA ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Vista de validación estética y operativa.</div>', unsafe_allow_html=True)

    # Progreso: % de filas con objetivo+indicador+meta
    if len(datos_mml) == 0:
        prog = 0.0
    else:
        completas = 0
        for r in datos_mml:
            if _norm_text(r.get("objetivo")) and _norm_text(r.get("indicador")) and _norm_text(r.get("meta")):
                completas += 1
        prog = completas / max(len(datos_mml), 1)
    st.progress(prog)

with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

if not datos_mml:
    st.info("No hay elementos para construir la matriz. Verifica en Hoja 11 que existan indicadores con Selección = Sí y metas diligenciadas.")
    st.stop()


# --- RENDERIZADO EN PANTALLA (tarjetas estilo original + fila de encabezados tipo Excel) ---
for fila in datos_mml:
    conf = CONFIG_NIVELES.get(fila["tipo"], {"color": "#64748b", "bg": "#f8fafc", "badge": fila["tipo"]})
    color = conf["color"]
    bg = conf["bg"]
    badge_text = conf.get("badge", fila["tipo"])  # texto del óvalo

    st.markdown(
        f"""
        <div class="card-mml" style="border-left: 10px solid {color}; background-color: {bg};">
            <div class="mml-toprow">
                <div class="tipo-badge" style="background-color: {color};">{badge_text}</div>
                <div class="mml-head">
                    <div class="mml-head-title" style="color: {color};">RESUMEN NARRATIVO</div>
                    <div class="mml-head-title" style="color: {color};">INDICADOR</div>
                    <div class="mml-head-title" style="color: {color};">META</div>
                    <div class="mml-head-title" style="color: {color};">SUPUESTOS</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 2fr 1.5fr 1fr 1.5fr; gap: 15px;">
                <div><div class="col-content">{_wrap_plain(fila['objetivo'], 80)}</div></div>
                <div><div class="col-content">{_wrap_plain(fila['indicador'], 48)}</div></div>
                <div><div class="col-content">{_wrap_plain(fila['meta'], 18)}</div></div>
                <div><div class="col-content">{_wrap_plain(fila['supuesto'], 54)}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

