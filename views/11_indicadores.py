import streamlit as st
import uuid
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO ---
st.markdown("""
<style>
.block-container { padding-bottom: 5rem !important; }
.h-title { font-size: 30px; font-weight: 900; color: #1E3A8A; margin: 0 0 4px 0; }
.h-sub { font-size: 14px; color: #64748b; margin: 0 0 14px 0; }
.badge {
  display:inline-block; padding: 4px 10px; border-radius: 999px;
  font-weight: 700; font-size: 12px; background: #eef2ff; color: #1e3a8a;
  border: 1px solid rgba(30,58,138,0.12);
}
.small-note { color:#64748b; font-size: 12px; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 10px 0 18px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="h-title">📊 11. Indicadores</div>', unsafe_allow_html=True)
st.markdown('<div class="h-sub">Fase IV: Análisis de Objetivos · Construcción de Indicadores</div>', unsafe_allow_html=True)
st.markdown('<span class="badge">Edición</span> <span class="small-note">El indicador se autogenera en vivo. Presiona “Guardar” para persistir en nube.</span>', unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# Helpers robustos
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

# -----------------------------
# EXTRACCIÓN DE OBJETIVOS (HOJA 7)
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
            "id_unico": _safe_obj_id(item)  # puede venir vacío
        })

if not lista_base:
    st.warning("⚠️ No se encontraron objetivos. Completa primero la Hoja 7 (Árbol de Objetivos Final).")
    st.stop()

# -----------------------------
# Inicialización state para hoja 11
# -----------------------------
if 'datos_indicadores' not in st.session_state or not isinstance(st.session_state.get('datos_indicadores'), dict):
    st.session_state['datos_indicadores'] = {}

if 'indicadores_mapa_objetivo' not in st.session_state or not isinstance(st.session_state.get('indicadores_mapa_objetivo'), dict):
    st.session_state['indicadores_mapa_objetivo'] = {}

# -----------------------------
# Key estable interna (NO visible)
# -----------------------------
def _resolve_key(nivel, obj_texto, id_unico):
    if id_unico:
        return id_unico

    kmap = _mk_map_key(nivel, obj_texto)
    if kmap in st.session_state['indicadores_mapa_objetivo']:
        return st.session_state['indicadores_mapa_objetivo'][kmap]

    new_key = str(uuid.uuid4())
    st.session_state['indicadores_mapa_objetivo'][kmap] = new_key
    return new_key

# Lookup para resolver id_unico desde lo que ve el usuario
base_lookup = {(r["Nivel"], r["Objetivo"]): r.get("id_unico", "") for r in lista_base}

# -----------------------------
# Construir DF base (valores guardados)
# -----------------------------
base_rows = []
for row in lista_base:
    nivel = row["Nivel"]
    obj_texto = row["Objetivo"]
    id_unico = row.get("id_unico", "")

    key_estable = _resolve_key(nivel, obj_texto, id_unico)
    guardado = st.session_state['datos_indicadores'].get(key_estable, {})

    # Compatibilidad: si existía guardado por texto
    if (not guardado) and (obj_texto in st.session_state['datos_indicadores']):
        guardado = st.session_state['datos_indicadores'].get(obj_texto, {})

    obj = _norm_text(guardado.get("Objeto", ""))
    cond = _norm_text(guardado.get("Condicion", guardado.get("Condición", "")))
    lugar = _norm_text(guardado.get("Lugar", ""))
    indicador_guardado = _norm_text(guardado.get("Indicador", ""))

    # Si no hay indicador guardado, lo calculamos en base a los campos
    if not indicador_guardado:
        indicador_guardado = _generar_indicador(obj, cond, lugar)

    base_rows.append({
        "Nivel": nivel,
        "Objetivo": obj_texto,
        "1. Objeto": obj,
        "2. Condición Deseada": cond,
        "3. Lugar": lugar,
        "Indicador Generado": indicador_guardado,
    })

df_base = pd.DataFrame(base_rows)

# -----------------------------
# Recuperar edición previa del widget para autogeneración en vivo
# -----------------------------
# Streamlit guarda el valor del data_editor en st.session_state[key] tras cada interacción.
# Tomamos ese valor, lo normalizamos y recalculamos "Indicador Generado" para mostrarlo actualizado.
key_editor = "editor_indicadores"

df_work = df_base.copy()

if key_editor in st.session_state:
    val = st.session_state.get(key_editor)

    # El valor puede llegar como DataFrame o como lista/dict según versión; soportamos ambos.
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
            # Asegurar columnas mínimas
            for col in df_work.columns:
                if col not in df_tmp.columns:
                    df_tmp[col] = df_work[col]

            # Mantener "Nivel" y "Objetivo" desde base para evitar que el usuario los altere por estado raro
            df_tmp["Nivel"] = df_work["Nivel"].values
            df_tmp["Objetivo"] = df_work["Objetivo"].values

            # Autogenerar indicador en vivo
            df_tmp["Indicador Generado"] = df_tmp.apply(
                lambda r: _generar_indicador(r.get("1. Objeto", ""), r.get("2. Condición Deseada", ""), r.get("3. Lugar", "")),
                axis=1
            )

            df_work = df_tmp[df_work.columns].copy()
    except Exception:
        df_work = df_base.copy()

# -----------------------------
# UI: Editor
# -----------------------------
st.info("💡 El indicador se actualiza automáticamente al editar. Presiona **“Guardar”** para persistir en la nube.")

df_edited = st.data_editor(
    df_work,
    column_config={
        "Nivel": st.column_config.TextColumn("Nivel", disabled=True, width="small"),
        "Objetivo": st.column_config.TextColumn("Objetivo", disabled=True, width="large"),
        "1. Objeto": st.column_config.TextColumn("1. Objeto", width="medium"),
        "2. Condición Deseada": st.column_config.TextColumn("2. Condición Deseada", width="medium"),
        "3. Lugar": st.column_config.TextColumn("3. Lugar", width="small"),
        "Indicador Generado": st.column_config.TextColumn("Indicador Generado", disabled=True, width="large"),
    },
    hide_index=True,
    use_container_width=True,
    key=key_editor
)

col_btn, col_hint = st.columns([1, 3], vertical_alignment="center")
with col_btn:
    guardar = st.button("💾 Guardar en Nube", type="primary")
with col_hint:
    st.markdown('<span class="small-note">Las filas “completas” se resaltan en la vista previa (azul tenue).</span>', unsafe_allow_html=True)

# -----------------------------
# Guardado
# -----------------------------
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
        st.success("✅ Guardado y sincronizado en la nube.")
        st.rerun()
    else:
        st.info("No se guardó nada porque faltan Objeto y/o Condición en las filas editadas.")

# -----------------------------
# Vista previa estilizada (filas completas en azul tenue)
# -----------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown('<span class="badge">Vista previa</span> <span class="small-note">Resalta filas completas.</span>', unsafe_allow_html=True)

df_preview = df_edited.copy() if isinstance(df_edited, pd.DataFrame) else df_work.copy()

def _is_complete_row(r):
    return bool(_norm_text(r.get("1. Objeto", ""))) and bool(_norm_text(r.get("2. Condición Deseada", ""))) and bool(_norm_text(r.get("3. Lugar", "")))

df_preview["Estado"] = df_preview.apply(lambda r: "Completo" if _is_complete_row(r) else "Pendiente", axis=1)

cols_order = ["Estado", "Nivel", "Objetivo", "1. Objeto", "2. Condición Deseada", "3. Lugar", "Indicador Generado"]
df_preview = df_preview[cols_order]

def _style_rows(row):
    if row["Estado"] == "Completo":
        return ["background-color: rgba(79, 139, 255, 0.12)"] * len(row)
    return [""] * len(row)

st.dataframe(
    df_preview.style.apply(_style_rows, axis=1),
    use_container_width=True,
    hide_index=True
)
