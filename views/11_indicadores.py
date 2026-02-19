import streamlit as st
import uuid
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

# -----------------------------
# Estilo (limpio, consistente)
# -----------------------------
st.markdown("""
<style>
.block-container { padding-bottom: 4rem !important; }
.h-title { font-size: 30px; font-weight: 900; color: #1E3A8A; margin: 0 0 4px 0; }
.h-sub { font-size: 14px; color: #64748b; margin: 0 0 12px 0; }
.note {
  padding: 10px 12px; border-radius: 10px;
  background: rgba(79, 139, 255, 0.10);
  border: 1px solid rgba(79, 139, 255, 0.18);
  color: #1e3a8a; font-weight: 600; font-size: 13px;
  margin: 8px 0 12px 0;
}
.small { color:#64748b; font-size: 12px; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 14px 0 16px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="h-title">11. Indicadores</div>', unsafe_allow_html=True)
st.markdown('<div class="h-sub">Fase IV · Construcción de indicadores por objetivo</div>', unsafe_allow_html=True)
st.markdown('<div class="note">El indicador se autogenera al editar. Presiona <b>Guardar en Nube</b> para persistir.</div>', unsafe_allow_html=True)

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

def _estado_fila(obj, cond, lugar):
    return "Completo" if (_norm_text(obj) and _norm_text(cond) and _norm_text(lugar)) else "Pendiente"

# -----------------------------
# Datos base (Hoja 7)
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
    st.warning("No se encontraron objetivos. Completa primero la Hoja 7 (Árbol de Objetivos Final).")
    st.stop()

# -----------------------------
# Session init (Hoja 11)
# -----------------------------
if 'datos_indicadores' not in st.session_state or not isinstance(st.session_state.get('datos_indicadores'), dict):
    st.session_state['datos_indicadores'] = {}

if 'indicadores_mapa_objetivo' not in st.session_state or not isinstance(st.session_state.get('indicadores_mapa_objetivo'), dict):
    st.session_state['indicadores_mapa_objetivo'] = {}

def _resolve_key(nivel, objetivo_txt, id_unico):
    if id_unico:
        return id_unico

    kmap = _mk_map_key(nivel, objetivo_txt)
    if kmap in st.session_state['indicadores_mapa_objetivo']:
        return st.session_state['indicadores_mapa_objetivo'][kmap]

    new_key = str(uuid.uuid4())
    st.session_state['indicadores_mapa_objetivo'][kmap] = new_key
    return new_key

base_lookup = {(r["Nivel"], r["Objetivo"]): r.get("id_unico", "") for r in lista_base}

# -----------------------------
# Construcción DF base (desde nube)
# -----------------------------
rows = []
for r in lista_base:
    nivel = r["Nivel"]
    objetivo_txt = r["Objetivo"]
    id_unico = r.get("id_unico", "")

    key_estable = _resolve_key(nivel, objetivo_txt, id_unico)
    guardado = st.session_state['datos_indicadores'].get(key_estable, {})

    # Compatibilidad muy vieja (si alguien guardó por texto)
    if (not guardado) and (objetivo_txt in st.session_state['datos_indicadores']):
        guardado = st.session_state['datos_indicadores'].get(objetivo_txt, {})

    obj = _norm_text(guardado.get("Objeto", ""))
    cond = _norm_text(guardado.get("Condicion", guardado.get("Condición", "")))
    lugar = _norm_text(guardado.get("Lugar", ""))

    indicador = _norm_text(guardado.get("Indicador", "")) or _generar_indicador(obj, cond, lugar)
    estado = _estado_fila(obj, cond, lugar)

    rows.append({
        "Estado": estado,
        "Nivel": nivel,
        "Objetivo": objetivo_txt,
        "1. Objeto": obj,
        "2. Condición Deseada": cond,
        "3. Lugar": lugar,
        "Indicador Generado": indicador,
    })

df_base = pd.DataFrame(rows)

# -----------------------------
# Autogeneración en vivo (1 sola tabla)
# -----------------------------
key_editor = "editor_indicadores"

df_work = df_base.copy()

if key_editor in st.session_state:
    val = st.session_state.get(key_editor)

    try:
        if isinstance(val, pd.DataFrame):
            df_tmp = val.copy()
        elif isinstance(val, list):
            df_tmp = pd.DataFrame(val)
        elif isinstance(val, dict):
            df_tmp = pd.DataFrame(val)
        else:
            df_tmp = None

        if df_tmp is not None and not df_tmp.empty:
            # asegurar columnas
            for col in df_work.columns:
                if col not in df_tmp.columns:
                    df_tmp[col] = df_work[col]

            # proteger columnas fijas
            df_tmp["Nivel"] = df_work["Nivel"].values
            df_tmp["Objetivo"] = df_work["Objetivo"].values

            # autocalcular estado + indicador
            df_tmp["Indicador Generado"] = df_tmp.apply(
                lambda r: _generar_indicador(r.get("1. Objeto", ""), r.get("2. Condición Deseada", ""), r.get("3. Lugar", "")),
                axis=1
            )
            df_tmp["Estado"] = df_tmp.apply(
                lambda r: _estado_fila(r.get("1. Objeto", ""), r.get("2. Condición Deseada", ""), r.get("3. Lugar", "")),
                axis=1
            )

            df_work = df_tmp[df_work.columns].copy()
    except Exception:
        df_work = df_base.copy()

# -----------------------------
# Editor
# -----------------------------
st.markdown('<div class="small">Sugerencia: completa primero Objeto y Condición, luego Lugar.</div>', unsafe_allow_html=True)

df_edited = st.data_editor(
    df_work,
    column_config={
        "Estado": st.column_config.TextColumn("Estado", disabled=True, width="small"),
        "Nivel": st.column_config.TextColumn("Nivel", disabled=True, width="small"),
        "Objetivo": st.column_config.TextColumn("Objetivo", disabled=True, width="large"),
        "1. Objeto": st.column_config.TextColumn("1. Objeto", width="medium"),
        "2. Condición Deseada": st.column_config.TextColumn("2. Condición Deseada", width="medium"),
        "3. Lugar": st.column_config.TextColumn("3. Lugar", width="small"),
        "Indicador Generado": st.column_config.TextColumn("Indicador Generado", disabled=True, width="large"),
    },
    hide_index=True,
    use_container_width=True,
    height=520,
    key=key_editor
)

# -----------------------------
# Guardar
# -----------------------------
col_btn, col_stats = st.columns([1, 2], vertical_alignment="center")
with col_btn:
    guardar = st.button("💾 Guardar en Nube", type="primary")

with col_stats:
    try:
        total = len(df_edited)
        completos = int((df_edited["Estado"] == "Completo").sum())
        st.markdown(f'<div class="small"><b>Completos:</b> {completos} / {total}</div>', unsafe_allow_html=True)
    except Exception:
        pass

if guardar:
    errores = []
    guardados_ok = 0

    registros = df_edited.to_dict(orient="records") if isinstance(df_edited, pd.DataFrame) else []

    for row in registros:
        nivel = _norm_text(row.get("Nivel", ""))
        objetivo_txt = _norm_text(row.get("Objetivo", ""))

        obj = _norm_text(row.get("1. Objeto", ""))
        cond = _norm_text(row.get("2. Condición Deseada", ""))
        lugar = _norm_text(row.get("3. Lugar", ""))

        # Validación mínima
        if not obj or not cond:
            if objetivo_txt:
                errores.append(f"- Falta Objeto/Condición en: {objetivo_txt[:90]}")
            continue

        id_unico = _norm_text(base_lookup.get((nivel, objetivo_txt), ""))
        key_estable = _resolve_key(nivel, objetivo_txt, id_unico)

        indicador_calculado = _generar_indicador(obj, cond, lugar)

        st.session_state['datos_indicadores'][key_estable] = {
            "Objetivo": objetivo_txt,
            "Nivel": nivel,
            "Objeto": obj,
            "Condicion": cond,
            "Lugar": lugar,
            "Indicador": indicador_calculado
        }
        guardados_ok += 1

    guardar_datos_nube()

    if errores:
        st.warning("Se guardó lo válido, pero hay filas incompletas:\n" + "\n".join(errores))
    if guardados_ok > 0:
        st.success("Guardado y sincronizado en la nube.")
        st.rerun()
    else:
        st.info("No se guardó nada porque faltan Objeto y/o Condición en las filas editadas.")
