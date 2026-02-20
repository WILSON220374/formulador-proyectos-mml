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
st.markdown(textwrap.dedent("""
    <style>
    .card-mml {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 18px 18px 14px 18px;
        margin-bottom: 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 6px 14px -10px rgba(0, 0, 0, 0.18);
        position: relative;
    }
    .mml-leftbar{
        position:absolute; left:0; top:0; bottom:0; width:10px;
        border-top-left-radius:16px; border-bottom-left-radius:16px;
    }
    .mml-toprow{
        display:flex;
        align-items:center;
        gap: 14px;
        margin-bottom: 10px;
    }
    .tipo-badge {
        color: white;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 800;
        display: inline-block;
        text-transform: uppercase;
        white-space: nowrap;
    }
    .mml-head{
        flex: 1;
        display: grid;
        grid-template-columns: 2fr 1.5fr 0.7fr 1.4fr;
        gap: 14px;
        align-items: center;
    }
    .mml-head-title{
        color:#1E3A8A;
        font-weight: 900;
        font-size: 0.82rem;
        text-transform: uppercase;
        text-align:center;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
    }
    .mml-row{
        display:grid;
        grid-template-columns: 2fr 1.5fr 0.7fr 1.4fr;
        gap: 14px;
        align-items: start;
    }
    .col-content{
        font-size: 0.96rem;
        color: #0f172a;
        text-align: center;
        line-height: 1.45;
        padding: 6px 4px;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    </style>
"""), unsafe_allow_html=True)

# --- CONFIGURACIÓN DE NIVELES (MISMO ESTILO) ---
# Se agrega FIN / OBJETIVO GENERAL manteniendo paleta sobria.
CONFIG_NIVELES = {
    "FIN / OBJETIVO GENERAL": {"color": "#1E3A8A", "bg": "#EFF6FF"},
    "PROPÓSITO / ESPECÍFICO": {"color": "#2563EB", "bg": "#EFF6FF"},
    "COMPONENTE / PRODUCTO":  {"color": "#059669", "bg": "#ECFDF5"},
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}
}

# Orden fijo de fichas (como jerarquía MML)
ORDEN_TIPOS = [
    "FIN / OBJETIVO GENERAL",
    "PROPÓSITO / ESPECÍFICO",
    "COMPONENTE / PRODUCTO",
    "ACTIVIDAD",
]

def _norm_text(v) -> str:
    if v is None:
        return ""
    return str(v).replace("\u00a0", " ").strip()

def _norm_key(v) -> str:
    return _norm_text(v).lower()

def _map_tipo(tipo_hoja11: str) -> str:
    t = _norm_text(tipo_hoja11).upper()
    if t == "OBJETIVO GENERAL":
        return "FIN / OBJETIVO GENERAL"
    if t == "OBJETIVO ESPECIFICO":
        return "PROPÓSITO / ESPECÍFICO"
    if t == "COMPONENTE":
        return "COMPONENTE / PRODUCTO"
    if t == "ACTIVIDAD":
        return "ACTIVIDAD"
    # fallback conservador
    return "PROPÓSITO / ESPECÍFICO" if "ESPECIF" in t else ("ACTIVIDAD" if "ACTIV" in t else "COMPONENTE / PRODUCTO")


def _badge_display(mapped_tipo: str) -> str:
    """Texto del óvalo, como en el Excel."""
    t = _norm_text(mapped_tipo)
    if t == "FIN / OBJETIVO GENERAL":
        return "OBJETIVO GENERAL"
    if t == "PROPÓSITO / ESPECÍFICO":
        return "OBJETIVO ESPECIFICO"
    if t == "COMPONENTE / PRODUCTO":
        return "COMPONENTE"
    if t == "ACTIVIDAD":
        return "ACTIVIDAD"
    return t

def _build_datos_mml() -> list[dict]:
    """Construye las fichas desde:
    - Hoja 11: Objetivo + Indicador + Meta (medios de verificación)
    - Hoja 12: Supuestos (columna interna 'Supuesto'), match SOLO por Objetivo
    """
    # 1) Filtrar claves seleccionadas (P1..P5 = True)
    sel = st.session_state.get("seleccion_indicadores", {}) or {}
    P_COLS = ["P1", "P2", "P3", "P4", "P5"]
    keys_si = [k for k, v in sel.items() if isinstance(v, dict) and all(bool(v.get(p, False)) for p in P_COLS)]

    # 2) Datos base
    mv_dict = st.session_state.get("medios_verificacion", {}) or {}
    datos_ind = st.session_state.get("datos_indicadores", {}) or {}
    metas = st.session_state.get("meta_resultados_parciales", {}) or {}

    # 3) Index de supuestos por objetivo (solo por Objetivo)
    supuestos_por_obj = {}
    df_r = st.session_state.get("datos_riesgos", None)
    if isinstance(df_r, pd.DataFrame) and not df_r.empty and "Objetivo" in df_r.columns and "Supuesto" in df_r.columns:
        for _, rr in df_r.iterrows():
            obj = _norm_key(rr.get("Objetivo", ""))
            sup = _norm_text(rr.get("Supuesto", ""))
            if not obj or not sup:
                continue
            supuestos_por_obj.setdefault(obj, set()).add(sup)

    datos = []
    for k in keys_si:
        base = datos_ind.get(k, {}) if isinstance(datos_ind, dict) else {}
        nivel = _norm_text(base.get("Nivel", ""))
        objetivo = _norm_text(base.get("Objetivo", ""))
        indicador = _norm_text(base.get("Indicador", ""))

        # Meta desde Meta y resultados parciales
        meta = _norm_text(metas.get(k, {}).get("Meta", "")) if isinstance(metas, dict) else ""

        # Tipo desde nivel
        tipo_hoja11 = ""
        if nivel == "Objetivo General":
            tipo_hoja11 = "OBJETIVO GENERAL"
        elif str(nivel).startswith("Objetivo Espec"):
            tipo_hoja11 = "OBJETIVO ESPECIFICO"
        elif nivel == "Actividad Clave":
            tipo_hoja11 = "ACTIVIDAD"
        else:
            # fallback: si ya existiera en base
            tipo_hoja11 = _norm_text(base.get("Tipo", ""))

        tipo = _map_tipo(tipo_hoja11)

        # Supuestos (lista)
        sups = sorted(list(supuestos_por_obj.get(_norm_key(objetivo), set())))
        supuesto = "\n".join([f"• {s}" for s in sups]) if sups else ""

        # Permitir múltiples fichas por tipo; una por cada clave seleccionada
        if any([objetivo, indicador, meta, supuesto]):
            datos.append({
                "tipo": tipo,
                "objetivo": objetivo,
                "indicador": indicador,
                "meta": meta,
                "supuesto": supuesto,
            })

    # Ordenar por jerarquía sin cambiar orden interno de cada grupo
    orden_idx = {t:i for i,t in enumerate(ORDEN_TIPOS)}
    datos.sort(key=lambda r: orden_idx.get(r.get("tipo",""), 99))
    return datos

datos_mml = _build_datos_mml()

# --- FUNCIÓN DE EXPORTACIÓN ESTÉTICA (ROBUSTA) ---
def generar_png_estetico(datos):
    """Genera una imagen que imita visualmente las tarjetas. Devuelve bytes o None."""
    try:
        dot = graphviz.Digraph(format='png')
        dot.attr(rankdir='TB', nodesep='0.3', ranksep='0.2', bgcolor='white', fontname='Arial')

        def wrap_html_safe(t, w=25):
            s = _norm_text(t)
            if not s:
                return ""
            # Escapar para HTML-like labels de graphviz
            s = html.escape(s, quote=True)
            # Mantener viñetas y saltos
            lines = []
            for line in s.splitlines():
                lines.extend(textwrap.wrap(line, width=w) or [""])
            return "<BR/>".join(lines)

        for i, fila in enumerate(datos):
            conf = CONFIG_NIVELES.get(fila.get('tipo',''), {"color": "#1E3A8A", "bg": "#f8fafc"})

            label = f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
                <TR>
                    <TD WIDTH="10" BGCOLOR="{conf['color']}"></TD>
                    <TD BGCOLOR="{conf['bg']}">
                        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="10" CELLPADDING="5">
                            <TR>
                                <TD COLSPAN="4" ALIGN="LEFT">
                                    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5">
                                        <TR><TD BGCOLOR="{conf['color']}" PORT="header"><FONT COLOR="white" POINT-SIZE="10"><B>  {html.escape(_badge_display(fila.get('tipo','')), quote=True)}  </B></FONT></TD></TR>
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
                                <TD WIDTH="180" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html_safe(fila.get('objetivo',''), 34)}</FONT></TD>
                                <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html_safe(fila.get('indicador',''), 22)}</FONT></TD>
                                <TD WIDTH="80"  ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html_safe(fila.get('meta',''), 12)}</FONT></TD>
                                <TD WIDTH="160" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap_html_safe(fila.get('supuesto',''), 22)}</FONT></TD>
                            </TR>
                        </TABLE>
                    </TD>
                </TR>
            </TABLE>>'''

            dot.node(
                f'card_{i}',
                label=label,
                shape='rect',
                style='filled',
                fillcolor='white',
                color='#e2e8f0',
                penwidth='2'
            )

            if i > 0:
                dot.edge(f'card_{i-1}', f'card_{i}', style='invis')

        return dot.pipe(format='png')
    except Exception:
        return None

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
            use_container_width=True
        )
    else:
        st.info("La exportación PNG no está disponible en este momento (Graphviz). La vista en pantalla sí está operativa.")

# --- CUERPO DE LA PÁGINA ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Vista de validación estética y operativa.</div>', unsafe_allow_html=True)

    # Progreso: % de filas con indicador + meta (vista final)
    if len(datos_mml) == 0:
        p = 0.0
    else:
        completas = 0
        for r in datos_mml:
            if _norm_text(r.get("indicador","")) and _norm_text(r.get("meta","")):
                completas += 1
        p = completas / max(len(datos_mml), 1)

    st.write(f"Avance estimado: {int(round(p*100, 0))}%")
    st.progress(p)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- RENDERIZADO EN PANTALLA (MISMO ESTILO) ---
if not datos_mml:
    st.info("No hay elementos para mostrar. Verifica: Hoja 11 (Selección = Sí y Metas) y Hoja 12 (Supuestos).")
else:
    for fila in datos_mml:
        conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#64748b", "bg": "#f8fafc"})
        st.markdown(textwrap.dedent(f"""
            <div class="card-mml" style="background-color:{conf['bg']};">
                <div class="mml-leftbar" style="background:{conf['color']};"></div>

                <div class="mml-toprow">
                    <div class="tipo-badge" style="background-color:{conf['color']};">{_badge_display(fila['tipo'])}</div>
                    <div class="mml-head">
                        <div class="mml-head-title" style="color:{conf['color']};">RESUMEN NARRATIVO</div>
                        <div class="mml-head-title" style="color:{conf['color']};">INDICADOR</div>
                        <div class="mml-head-title" style="color:{conf['color']};">META</div>
                        <div class="mml-head-title" style="color:{conf['color']};">SUPUESTOS</div>
                    </div>
                </div>

                <div class="mml-row">
                    <div class="col-content">{html.escape(_norm_text(fila['objetivo']))}</div>
                    <div class="col-content">{html.escape(_norm_text(fila['indicador']))}</div>
                    <div class="col-content">{html.escape(_norm_text(fila['meta']))}</div>
                    <div class="col-content">{html.escape(_norm_text(fila['supuesto']))}</div>
                </div>
            </div>
        """), unsafe_allow_html=True)

st.divider()
