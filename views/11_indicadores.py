import streamlit as st
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-seccion">📊 11. Indicadores</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Fase IV: Análisis de Objetivos - Construcción de Indicadores</div>', unsafe_allow_html=True)
st.divider()

# -----------------------------
# Helpers robustos
# -----------------------------
def _norm_text(x):
    if x is None:
        return ""
    return str(x).strip()

def _clean_spaces(texto):
    # Limpieza robusta: colapsa cualquier cantidad de espacios/line breaks en un solo espacio
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
        # Preferimos id_unico si existe (mucho más estable que el texto)
        return _norm_text(item.get("id_unico", ""))
    return ""

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
# Inicialización + compatibilidad hacia atrás
# -----------------------------
# Nuevo estándar: datos_indicadores se guarda por clave estable (id_unico o uuid)
if 'datos_indicadores' not in st.session_state or not isinstance(st.session_state.get('datos_indicadores'), dict):
    st.session_state['datos_indicadores'] = {}

# Mapa auxiliar: Objetivo (texto) -> key estable
# Sirve para:
# - Migrar datos antiguos guardados por texto
# - Mantener consistencia si no hay id_unico en los objetivos
if 'indicadores_mapa_objetivo' not in st.session_state or not isinstance(st.session_state.get('indicadores_mapa_objetivo'), dict):
    st.session_state['indicadores_mapa_objetivo'] = {}

# Migración suave:
# Si existen entradas en datos_indicadores que parecen estar guardadas por "texto de objetivo",
# las convertimos a una key estable y guardamos el mapa para no perderlas.
# (No borra las viejas; solo asegura que a futuro se use key estable.)
datos_actuales = st.session_state['datos_indicadores']
mapa = st.session_state['indicadores_mapa_objetivo']

# Detectar entradas antiguas: claves que NO parecen UUID y que son textos largos con espacios
# (heurística simple; evita romper si ya tienes keys estables)
for k in list(datos_actuales.keys()):
    if not isinstance(k, str):
        continue
    k_str = k.strip()
    # Si el objetivo exacto ya está mapeado, no tocar
    if k_str in mapa:
        continue
    # Heurística de "clave antigua": tiene espacios y no parece uuid
    parece_uuid = False
    try:
        uuid.UUID(k_str)
        parece_uuid = True
    except Exception:
        parece_uuid = False

    if (not parece_uuid) and (" " in k_str) and (len(k_str) >= 12):
        new_key = str(uuid.uuid4())
        mapa[k_str] = new_key
        # Copiar valores al nuevo key (si no existe ya)
        if new_key not in datos_actuales:
            datos_actuales[new_key] = datos_actuales.get(k_str, {})

st.session_state['datos_indicadores'] = datos_actuales
st.session_state['indicadores_mapa_objetivo'] = mapa

# -----------------------------
# Construcción de filas para editor
# -----------------------------
def _resolve_key(obj_texto, id_unico):
    # 1) Si existe id_unico, esa es la clave (estable y preferida)
    if id_unico:
        return id_unico

    # 2) Si hay mapa por texto, usarlo
    if obj_texto in st.session_state['indicadores_mapa_objetivo']:
        return st.session_state['indicadores_mapa_objetivo'][obj_texto]

    # 3) Si no existe, crear uuid y mapearlo
    new_key = str(uuid.uuid4())
    st.session_state['indicadores_mapa_objetivo'][obj_texto] = new_key
    return new_key

filas = []
for row in lista_base:
    obj_texto = row["Objetivo"]
    key_estable = _resolve_key(obj_texto, row.get("id_unico", ""))

    guardado = st.session_state['datos_indicadores'].get(key_estable, {})
    # Compatibilidad adicional: si no está por key estable, intentar por texto antiguo
    if not guardado and obj_texto in st.session_state['datos_indicadores']:
        guardado = st.session_state['datos_indicadores'].get(obj_texto, {})

    obj = _norm_text(guardado.get("Objeto", ""))
    cond = _norm_text(guardado.get("Condicion", guardado.get("Condición", "")))
    lugar = _norm_text(guardado.get("Lugar", ""))
    indicador_guardado = _norm_text(guardado.get("Indicador", ""))

    filas.append({
        "_key": key_estable,  # columna técnica (bloqueada)
        "Nivel": row["Nivel"],
        "Objetivo": obj_texto,
        "Objeto": obj,
        "Condición Deseada (Verbo)": cond,
        "Lugar": lugar,
        "Indicador (Automático)": indicador_guardado
    })

# -----------------------------
# UI: Tabla
# -----------------------------
st.info("💡 Diligencia Objeto, Condición y Lugar. Luego presiona 'Guardar'. "
        "La clave de guardado es estable (usa id_unico si existe), evitando pérdida de datos por cambios de texto.")

edited_rows = st.data_editor(
    filas,
    column_config={
        "_key": st.column_config.TextColumn("Key", disabled=True, width="small"),
        "Nivel": st.column_config.TextColumn("Nivel", disabled=True),
        "Objetivo": st.column_config.TextColumn("Objetivo", disabled=True, width="large"),
        "Objeto": st.column_config.TextColumn("1. Objeto"),
        "Condición Deseada (Verbo)": st.column_config.TextColumn("2. Condición Deseada"),
        "Lugar": st.column_config.TextColumn("3. Lugar"),
        "Indicador (Automático)": st.column_config.TextColumn("Indicador Generado", disabled=True, width="large"),
    },
    hide_index=True,
    use_container_width=True,
    key="editor_indicadores"
)

# -----------------------------
# Guardado + generación
# -----------------------------
def _generar_indicador(obj, cond, lugar):
    indicador = f"{_norm_text(obj)} {_norm_text(cond)} {_norm_text(lugar)}"
    return _clean_spaces(indicador)

if st.button("💾 Generar Indicadores y Guardar", type="primary"):
    errores = []
    guardados_ok = 0

    for row in edited_rows:
        key_estable = _norm_text(row.get("_key", ""))
        objetivo_txt = _norm_text(row.get("Objetivo", ""))

        obj = _norm_text(row.get("Objeto", ""))
        cond = _norm_text(row.get("Condición Deseada (Verbo)", ""))
        lugar = _norm_text(row.get("Lugar", ""))

        # Validación mínima (para evitar basura)
        # Ajusta la regla si quieres: aquí exijo Objeto y Condición
        if not obj or not cond:
            # no bloqueamos toda la ejecución; reportamos fila
            if objetivo_txt:
                errores.append(f"- Falta Objeto/Condición en: {objetivo_txt[:80]}")
            continue

        indicador_calculado = _generar_indicador(obj, cond, lugar)

        st.session_state['datos_indicadores'][key_estable] = {
            "Objetivo": objetivo_txt,  # se guarda como referencia humana
            "Objeto": obj,
            "Condicion": cond,
            "Lugar": lugar,
            "Indicador": indicador_calculado
        }

        # Para que el editor refleje inmediatamente en siguiente rerun
        guardados_ok += 1

    guardar_datos_nube()

    if errores:
        st.warning("Se guardó lo válido, pero hay filas incompletas:\n" + "\n".join(errores))
    if guardados_ok > 0:
        st.success("✅ Indicadores generados y sincronizados en la nube.")
        st.rerun()
    else:
        st.info("No se guardó nada porque faltan Objeto y/o Condición en las filas editadas.")
