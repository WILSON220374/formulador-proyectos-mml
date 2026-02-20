import streamlit as st
import os
import graphviz
import textwrap
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
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CONFIGURACIÓN DE NIVELES (manteniendo estilo/colores del diseño) ---
CONFIG_NIVELES = {
    "OBJETIVO GENERAL":     {"color": "#2563EB", "bg": "#EFF6FF"},
    "OBJETIVO ESPECIFICO":  {"color": "#2563EB", "bg": "#EFF6FF"},
    "COMPONENTE / PRODUCTO": {"color": "#059669", "bg": "#ECFDF5"},
    "ACTIVIDAD":            {"color": "#D97706", "bg": "#FFFBEB"},
}

# --- Helpers ---
def _norm_text(v) -> str:
    if v is None:
        return ""
    return str(v).replace("\u00a0", " ").strip()


def _norm_key(v) -> str:
    return " ".join(_norm_text(v).lower().split())


def _tipo_from_nivel(nivel_txt: str) -> str:
    n = _norm_text(nivel_txt)
    if n == "Objetivo General":
        return "OBJETIVO GENERAL"
    if n.startswith("Objetivo Específico"):
        return "OBJETIVO ESPECIFICO"
    if n in ("Actividad Clave", "ACTIVIDAD"):
        return "ACTIVIDAD"
    return ""  # desconocido


def _wrap_br(t: str, w: int) -> str:
    return "<BR/>".join(textwrap.wrap(_norm_text(t), width=w))


def _gv_escape(s: str) -> str:
    # Escape mínimo para labels HTML en graphviz
    s = _norm_text(s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s


# --- Construcción de datos reales desde H11 + H12 ---
# Selección = Sí por P1..P5
P_COLS = ["P1", "P2", "P3", "P4", "P5"]
keys_si = []
for k, sel in (st.session_state.get("seleccion_indicadores") or {}).items():
    if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in P_COLS):
        keys_si.append(_norm_text(k))

# Fuente: datos_indicadores (objetivo/indicador/nivel)
datos_ind = st.session_state.get("datos_indicadores") or {}
# Fuente: meta_resultados_parciales (meta)
metas = st.session_state.get("meta_resultados_parciales") or {}
# Fuente: hoja 12 (supuestos)
df_riesgos = st.session_state.get("datos_riesgos")
if not isinstance(df_riesgos, pd.DataFrame):
    df_riesgos = pd.DataFrame()

supuestos_por_obj = {}
if not df_riesgos.empty and "Objetivo" in df_riesgos.columns and "Supuesto" in df_riesgos.columns:
    for _, rr in df_riesgos.iterrows():
        obj = _norm_key(rr.get("Objetivo", ""))
        sup = _norm_text(rr.get("Supuesto", ""))
        if not obj or not sup:
            continue
        supuestos_por_obj.setdefault(obj, set()).add(sup)

# Filas para tarjetas
rows = []
for k in keys_si:
    base = datos_ind.get(k, {}) if isinstance(datos_ind, dict) else {}
    nivel = _norm_text(base.get("Nivel", ""))
    tipo = _tipo_from_nivel(nivel)

    objetivo = _norm_text(base.get("Objetivo", ""))
    indicador = _norm_text(base.get("Indicador", ""))
    meta = _norm_text(metas.get(k, {}).get("Meta", "")) if isinstance(metas, dict) else ""

    sups = sorted(list(supuestos_por_obj.get(_norm_key(objetivo), set())))
    supuesto = "\n".join([f"• {s}" for s in sups]) if sups else ""

    # Solo incluir si hay contenido mínimo
    if not (tipo or objetivo or indicador or meta or supuesto):
        continue

    if not tipo:
        # Si por alguna razón no mapeó, lo colocamos como ACTIVIDAD para no perderlo visualmente
        tipo = "ACTIVIDAD"

    rows.append(
        {
            "tipo": tipo,
            "objetivo": objetivo,
            "indicador": indicador,
            "meta": meta,
            "supuesto": supuesto,
        }
    )

# Orden jerárquico fijo
ORDER_RANK = {
    "OBJETIVO GENERAL": 0,
    "OBJETIVO ESPECIFICO": 1,
    "COMPONENTE / PRODUCTO": 2,
    "ACTIVIDAD": 3,
}
rows.sort(key=lambda r: (ORDER_RANK.get(r.get("tipo", ""), 99)))


# --- FUNCIÓN DE EXPORTACIÓN ESTÉTICA (robusta) ---
def generar_png_estetico(datos):
    """Genera una imagen que imita visualmente las tarjetas de la interfaz."""
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.2", bgcolor="white", fontname="Arial")

    for i, fila in enumerate(datos):
        conf = CONFIG_NIVELES.get(fila["tipo"], {"color": "#1E3A8A", "bg": "#f8fafc"})

        objetivo = _gv_escape(fila.get("objetivo", ""))
        indicador = _gv_escape(fila.get("indicador", ""))
        meta = _gv_escape(fila.get("meta", ""))
        supuesto = _gv_escape(fila.get("supuesto", ""))

        # Ajuste de texto
        def wrap_html(t, w=25):
            return "<BR/>".join(textwrap.wrap(str(t), width=w))

        label = f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
            <TR>
                <TD WIDTH="10" BGCOLOR="{conf['color']}"></TD>
                <TD BGCOLOR="{conf['bg']}">
                    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="10" CELLPADDING="5">
                        <TR>
                            <TD COLSPAN="4" ALIGN="LEFT">
                                <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5">
                                    <TR><TD BGCOLOR="{conf['color']}" PORT="header"><FONT COLOR="white" POINT-SIZE="10"><B>  {fila['tipo']}  </B></FONT></TD></TR>
                                </TABLE>
                            </TD>
                        </TR>
                        <TR>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>🎯 OBJETIVO</B></FONT></TD>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>📊 INDICADOR</B></FONT></TD>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>🏁 META</B></FONT></TD>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>🛡️ SUPUESTOS</B></FONT></TD>
                        </TR>
                        <TR>
                            <TD WIDTH="180" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(objetivo)}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(indicador, 20)}</FONT></TD>
                            <TD WIDTH="80" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(meta, 12)}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html(supuesto, 20)}</FONT></TD>
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

    # devolver bytes o None
    try:
        return dot.pipe(format="png")
    except Exception:
        return None


# --- PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Exportación Visual")
    st.write("Descarga una versión estética de alta resolución de tu matriz.")

    imagen_estetica = generar_png_estetico(rows)
    if isinstance(imagen_estetica, (bytes, bytearray)) and len(imagen_estetica) > 0:
        st.download_button(
            label="🖼️ Descargar Matriz Estética (PNG)",
            data=imagen_estetica,
            file_name="MML_Visual.png",
            mime="image/png",
            use_container_width=True,
        )
    else:
        st.info("No fue posible generar el PNG en este momento.")


# --- CUERPO DE LA PÁGINA ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Vista de validación estética y operativa.</div>', unsafe_allow_html=True)
    st.progress(0.60)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

if not rows:
    st.info("No hay datos suficientes para construir la matriz. Verifica Hoja 11 (selección Sí + metas) y Hoja 12 (supuestos).")
    st.stop()

# --- RENDERIZADO EN PANTALLA ---
for fila in rows:
    conf = CONFIG_NIVELES.get(fila["tipo"], {"color": "#64748b", "bg": "#f8fafc"})
    st.markdown(
        f"""
        <div class="card-mml" style="border-left: 10px solid {conf['color']}; background-color: {conf['bg']};">
            <div class="tipo-badge" style="background-color: {conf['color']};">
                {fila['tipo']}
            </div>
            <div style="display: flex; flex-direction: row; gap: 15px;">
                <div style="flex: 2;">
                    <div class="col-title" style="color: {conf['color']};">🎯 Objetivo</div>
                    <div class="col-content">{_norm_text(fila.get('objetivo',''))}</div>
                </div>
                <div style="flex: 1.5;">
                    <div class="col-title" style="color: {conf['color']};">📊 Indicador</div>
                    <div class="col-content">{_norm_text(fila.get('indicador',''))}</div>
                </div>
                <div style="flex: 1;">
                    <div class="col-title" style="color: {conf['color']};">🏁 Meta</div>
                    <div class="col-content">{_norm_text(fila.get('meta',''))}</div>
                </div>
                <div style="flex: 1.5;">
                    <div class="col-title" style="color: {conf['color']};">🛡️ Supuestos</div>
                    <div class="col-content">{_norm_text(fila.get('supuesto',''))}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
