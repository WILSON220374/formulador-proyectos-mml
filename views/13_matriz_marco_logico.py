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
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE NIVELES ---
CONFIG_NIVELES = {
    "OBJETIVO GENERAL":       {"color": "#1D4ED8", "bg": "#EFF6FF"},
    "PROPÓSITO / ESPECÍFICO": {"color": "#2563EB", "bg": "#EFF6FF"},
    "COMPONENTE / PRODUCTO":  {"color": "#059669", "bg": "#ECFDF5"},
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}
}

# -----------------------------
# Helpers
# -----------------------------
def _norm_text(v) -> str:
    if v is None:
        return ""
    return str(v).replace("\u00a0", " ").strip()

def _norm_key(v) -> str:
    return _norm_text(v).lower()

def _tipo_from_nivel(nivel: str) -> str:
    n = _norm_text(nivel)
    if n == "Objetivo General":
        return "OBJETIVO GENERAL"
    if n.startswith("Objetivo Específico"):
        return "PROPÓSITO / ESPECÍFICO"
    if n == "Actividad Clave":
        return "ACTIVIDAD"
    return n.upper() if n else ""

def _build_supuestos_map(df_riesgos: pd.DataFrame) -> dict:
    out = {}
    if not isinstance(df_riesgos, pd.DataFrame) or df_riesgos.empty:
        return out
    if "Objetivo" not in df_riesgos.columns or "Supuesto" not in df_riesgos.columns:
        return out
    for _, r in df_riesgos.iterrows():
        obj = _norm_key(r.get("Objetivo", ""))
        sup = _norm_text(r.get("Supuesto", ""))
        if not obj or not sup:
            continue
        out.setdefault(obj, [])
        if sup not in out[obj]:
            out[obj].append(sup)
    return out

def _safe_html(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))

# -----------------------------
# Construir datos reales (Hoja 11 + Hoja 12)
# -----------------------------
P_COLS = ["P1", "P2", "P3", "P4", "P5"]

seleccion = st.session_state.get("seleccion_indicadores", {}) or {}
datos_ind = st.session_state.get("datos_indicadores", {}) or {}
metas = st.session_state.get("meta_resultados_parciales", {}) or {}
df_riesgos = st.session_state.get("datos_riesgos", pd.DataFrame())
supuestos_map = _build_supuestos_map(df_riesgos)

df_indicadores = st.session_state.get("df_indicadores", None)
mapa = st.session_state.get("indicadores_mapa_objetivo", {}) or {}

ordered_keys = []
if isinstance(df_indicadores, pd.DataFrame) and ("Nivel" in df_indicadores.columns) and ("Objetivo" in df_indicadores.columns):
    for _, r in df_indicadores.iterrows():
        nivel = _norm_text(r.get("Nivel", ""))
        obj = _norm_text(r.get("Objetivo", ""))
        mk = f"{nivel}||{obj}"
        k = mapa.get(mk, "")
        if k:
            ordered_keys.append(k)

if not ordered_keys:
    ordered_keys = list(seleccion.keys())

keys_si = []
for k in ordered_keys:
    sel = seleccion.get(k, {})
    if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in P_COLS):
        keys_si.append(k)

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

    sups = supuestos_map.get(_norm_key(objetivo), [])
    supuesto = "\n".join([f"• {s}" for s in sups]) if sups else ""

    datos_mml.append({
        "tipo": tipo,
        "objetivo": objetivo,
        "indicador": indicador,
        "meta": meta,
        "supuesto": supuesto
    })

# --- FUNCIÓN DE EXPORTACIÓN ESTÉTICA ---
def generar_png_estetico(datos):
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB', nodesep='0.3', ranksep='0.2', bgcolor='white', fontname='Arial')

    for i, fila in enumerate(datos):
        conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#1E3A8A", "bg": "#f8fafc"})

        def wrap(t, w=25):
            s = '' if t is None else str(t)
            s = html.escape(s)
            return "<BR/>".join(textwrap.wrap(s, width=w))

        sup_plain = '' if fila.get('supuesto', '') is None else str(fila.get('supuesto', ''))
        sup_plain = sup_plain.replace("
", " ").replace("•", "-").strip()
        sup_plain = html.escape(sup_plain)

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
                            <TD WIDTH="180" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['objetivo'])}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['indicador'], 20)}</FONT></TD>
                            <TD WIDTH="80" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['meta'], 12)}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(sup_plain, 20)}</FONT></TD>
                        </TR>
                    </TABLE>
                </TD>
            </TR>
        </TABLE>>'''
        dot.node(f'card_{i}', label=label, shape='rect', style='filled', fillcolor='white', color='#e2e8f0', penwidth='2')
        if i > 0:
            dot.edge(f'card_{i-1}', f'card_{i}', style='invis')

    try:
        return dot.pipe(format='png')
    except Exception:
        return None

# --- PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Exportación Visual")
    st.write("Descarga una versión estética de alta resolución de tu matriz.")

    if datos_mml:
        imagen_estetica = generar_png_estetico(datos_mml)
        st.download_button(
            label="🖼️ Descargar Matriz Estética (PNG)",
            data=imagen_estetica,
            file_name="MML_Visual.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("Aún no hay elementos para exportar (verifica selección en Hoja 11).")

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

# --- RENDERIZADO EN PANTALLA ---
if not datos_mml:
    st.info("No hay datos para mostrar. Verifica en Hoja 11 que existan indicadores con Selección = Sí y metas diligenciadas.")
    st.divider()
else:
    for fila in datos_mml:
        conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#64748b", "bg": "#f8fafc"})

        objetivo_html = _safe_html(fila.get("objetivo", ""))
        indicador_html = _safe_html(fila.get("indicador", ""))
        meta_html = _safe_html(fila.get("meta", ""))
        supuesto_html = _safe_html(fila.get("supuesto", "")).replace("\n", "<br>")

        st.markdown(f"""
            <div class="card-mml" style="border-left: 10px solid {conf['color']}; background-color: {conf['bg']};">
                <div class="tipo-badge" style="background-color: {conf['color']};">
                    {fila['tipo']}
                </div>
                <div style="display: flex; flex-direction: row; gap: 15px;">
                    <div style="flex: 2;"><div class="col-title" style="color: {conf['color']};">🎯 Objetivo</div><div class="col-content">{objetivo_html}</div></div>
                    <div style="flex: 1.5;"><div class="col-title" style="color: {conf['color']};">📊 Indicador</div><div class="col-content">{indicador_html}</div></div>
                    <div style="flex: 1;"><div class="col-title" style="color: {conf['color']};">🏁 Meta</div><div class="col-content">{meta_html}</div></div>
                    <div style="flex: 1.5;"><div class="col-title" style="color: {conf['color']};">🛡️ Supuestos</div><div class="col-content">{supuesto_html}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.divider()
