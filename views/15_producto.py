import streamlit as st
import os
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia 
inicializar_session()

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 12rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    .header-tabla { font-weight: 800; color: #1E3A8A; margin-bottom: 10px; font-size: 1.1rem; text-transform: uppercase; }
    
    .readonly-label { font-size: 0.85rem; color: #374151; font-weight: 600; margin-bottom: 4px; }
    .readonly-box {
        border: 1px solid #d1d5db; border-radius: 8px; padding: 12px;
        background-color: #f3f4f6; color: #000000; font-size: 0.95rem;
        min-height: 50px; line-height: 1.5;
    }
    
    .stTextArea textarea {
        min-height: 100px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO Y AVANCE ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 15. Producto y Proyecto</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Definición del producto principal, alineación estratégica y nombre del proyecto.</div>', unsafe_allow_html=True)
    st.progress(0.95) 
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- LÓGICA DE EXTRACCIÓN DEL OBJETIVO GENERAL ---
mapa = st.session_state.get("indicadores_mapa_objetivo", {})
seleccion = st.session_state.get("seleccion_indicadores", {})
obj_general = "No definido (Complete la Hoja 11)"

for kmap, k in mapa.items():
    partes = kmap.split("||")
    if len(partes) != 2: continue
    
    nivel_original = partes[0]
    if "General" in nivel_original or "Fin" in nivel_original:
        sel = seleccion.get(k, {})
        is_selected = True if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in ["P1", "P2", "P3", "P4", "P5"]) else False
        
        if is_selected:
            obj_general = partes[1]
            break

# =========================================================
# 🎯 OBJETIVO GENERAL (TÍTULO AZUL DESTACADO)
# =========================================================
st.markdown('<div class="header-tabla" style="font-size: 1.3rem; text-align: center;">🎯 OBJETIVO GENERAL DEL PROYECTO</div>', unsafe_allow_html=True)
st.markdown(f"""
    <div style="background-color: #1E3A8A; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 1.2rem; font-weight: bold; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        {obj_general}
    </div>
""", unsafe_allow_html=True)

st.divider()


# =========================================================
# CARGA EXCEL: data/productos.xlsx (en repo)
# =========================================================
def _excel_path() -> str:
    base_dir = os.path.dirname(__file__)  # views/
    candidates = [
        os.path.abspath(os.path.join(base_dir, "..", "data", "productos.xlsx")),
        os.path.abspath(os.path.join(base_dir, "productos.xlsx")),
        os.path.abspath(os.path.join(os.getcwd(), "data", "productos.xlsx")),
        os.path.abspath(os.path.join(os.getcwd(), "productos.xlsx")),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

@st.cache_data(show_spinner=False)
def _load_productos(path: str) -> pd.DataFrame:
    return pd.read_excel(path)

xlsx_path = _excel_path()
if not os.path.exists(xlsx_path):
    st.error(f"No encuentro el archivo productos.xlsx en el repositorio. Ruta esperada: {xlsx_path}")
    st.stop()

df_productos = _load_productos(xlsx_path)

# Normalización mínima
for _c in ["Nombre del Sector", "Nombre del Programa", "Producto", "Descripción", "Medido a través de", "Indicador de Producto", "Unidad de medida"]:
    if _c in df_productos.columns:
        df_productos[_c] = df_productos[_c].astype(str).replace("nan", "").str.strip()


# --- SECCIÓN 1: SECTOR Y PROGRAMA ---
st.markdown('<div class="header-tabla">🏢 1. Sector y Programa de Inversión</div>', unsafe_allow_html=True)
col_s1, col_s2 = st.columns(2)

# Opciones dinámicas desde Excel
_sectores = []
if "Nombre del Sector" in df_productos.columns:
    _sectores = sorted([x for x in df_productos["Nombre del Sector"].dropna().unique().tolist() if str(x).strip() != ""])
_sector_default = st.session_state.get("sector_seleccionado", "Seleccione...")
_sector_options = ["Seleccione..."] + _sectores
if _sector_default not in _sector_options:
    _sector_default = "Seleccione..."
_sector_index = _sector_options.index(_sector_default)

with col_s1:
    sector_seleccionado = st.selectbox("Sector de Inversión", _sector_options, index=_sector_index)

_df_sector = df_productos.copy()
if sector_seleccionado != "Seleccione..." and "Nombre del Sector" in _df_sector.columns:
    _df_sector = _df_sector[_df_sector["Nombre del Sector"] == sector_seleccionado]
else:
    _df_sector = _df_sector.iloc[0:0].copy()

_programas = []
if "Nombre del Programa" in _df_sector.columns:
    _programas = sorted([x for x in _df_sector["Nombre del Programa"].dropna().unique().tolist() if str(x).strip() != ""])
_programa_default = st.session_state.get("programa_seleccionado", "Seleccione...")
_programa_options = ["Seleccione..."] + _programas
if _programa_default not in _programa_options:
    _programa_default = "Seleccione..."
_programa_index = _programa_options.index(_programa_default)

with col_s2:
    programa_seleccionado = st.selectbox("Programa", _programa_options, index=_programa_index)

# Persistir selección actual en sesión (para que quede precargada en el UI)
st.session_state["sector_seleccionado"] = sector_seleccionado
st.session_state["programa_seleccionado"] = programa_seleccionado

st.divider()

# --- SECCIÓN 2: MATRIZ DE PRODUCTO ---
st.markdown('<div class="header-tabla">📦 2. Producto Principal</div>', unsafe_allow_html=True)

# Filtrar productos por sector y programa (si están seleccionados)
_df_prog = _df_sector.copy()
if programa_seleccionado != "Seleccione..." and "Nombre del Programa" in _df_prog.columns:
    _df_prog = _df_prog[_df_prog["Nombre del Programa"] == programa_seleccionado]
else:
    _df_prog = _df_prog.iloc[0:0].copy()

# Selector (con búsqueda por escritura) - SOLO nombre del producto
if _df_prog.empty:
    producto_nombre = st.selectbox("Producto", ["Seleccione..."], index=0)
    _seleccion = None
else:
    _df_prog2 = _df_prog.reset_index(drop=True).copy()

    _map_nombre_idx = {}
    for i, r in _df_prog2.iterrows():
        nombre = str(r.get("Producto", "")).strip()
        if nombre and nombre not in _map_nombre_idx:
            _map_nombre_idx[nombre] = i

    _nombres = sorted(_map_nombre_idx.keys())
    _opts = ["Seleccione..."] + _nombres

    _default = st.session_state.get("producto_seleccionado_label", "Seleccione...")
    if _default not in _opts:
        _default = "Seleccione..."
    _idx = _opts.index(_default)

    producto_nombre = st.selectbox("Producto", _opts, index=_idx)

    _seleccion = None
    if producto_nombre != "Seleccione..." and producto_nombre in _map_nombre_idx:
        _seleccion = _df_prog2.iloc[_map_nombre_idx[producto_nombre]]

# Mostrar campos (uno debajo de otro)
def _box(label: str, value: str):
    st.markdown(
        f'<div class="readonly-label">{label}</div>'
        f'<div class="readonly-box">{value if str(value).strip() else ""}</div>',
        unsafe_allow_html=True
    )

if _seleccion is None:
    _box("Producto", "")
    _box("Descripción", "")
    _box("Medido a través de", "")
    _box("Indicador de Producto", "")
    _box("Unidad de medida", "")
else:
    _box("Producto", _seleccion.get("Producto", ""))
    _box("Descripción", _seleccion.get("Descripción", ""))
    _box("Medido a través de", _seleccion.get("Medido a través de", ""))
    _box("Indicador de Producto", _seleccion.get("Indicador de Producto", ""))
    _box("Unidad de medida", _seleccion.get("Unidad de medida", ""))

    # Guardar selección en sesión (sin cambiar UI del resto)
    st.session_state["producto_seleccionado_label"] = producto_nombre
    st.session_state["producto_seleccionado"] = producto_nombre
    st.session_state["producto_principal"] = {
        "PRODUCTO": _seleccion.get("Producto", ""),
        "Descripción": _seleccion.get("Descripción", ""),
        "Medido a través de": _seleccion.get("Medido a través de", ""),
        "Indicador de Producto": _seleccion.get("Indicador de Producto", ""),
        "Unidad de medida": _seleccion.get("Unidad de medida", ""),
    }

st.divider()

# =========================================================
# 🏷️ SECCIÓN 3: NOMBRE DEL PROYECTO (CON VISTA PREVIA VERDE)
# =========================================================
st.markdown('<div class="header-tabla">🏷️ 3. Nombre del Proyecto</div>', unsafe_allow_html=True)

nombre_proyecto = st.text_area("Escriba el nombre definitivo del proyecto", 
                               value=st.session_state.get('nombre_proyecto_libre', ""),
                               placeholder="Ej: Construcción de la planta de tratamiento de aguas residuales en el municipio...", 
                               height=100)

# Cartel de Vista Previa Destacado (Verde)
# Cartel de Vista Previa Destacado (Verde)
if nombre_proyecto.strip():
    st.markdown(f"""
        <div style="margin-top: 15px; padding: 25px; border-radius: 10px; background-color: #166534; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 2.2rem; font-weight: 800; text-transform: uppercase; line-height: 1.3;">
                {nombre_proyecto}
            </span>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- SECCIÓN 4: PLAN DE DESARROLLO (APILADO) ---
st.markdown('<div class="header-tabla">🗺️ 4. Plan de Desarrollo</div>', unsafe_allow_html=True)

nombre_plan = st.text_input("Nombre del Plan", value=st.session_state.get('plan_nombre', ""), placeholder="Ej: Plan Nacional de Desarrollo...")
eje_plan = st.text_input("Eje", value=st.session_state.get('plan_eje', ""), placeholder="Ej: Equidad y crecimiento...")
programa_plan = st.text_input("Programa", value=st.session_state.get('plan_programa', ""), placeholder="Ej: Saneamiento básico...")

st.divider()

# --- BOTÓN DE GUARDADO ---
if st.button("💾 Guardar Información de Producto", type="primary"):
    st.session_state['nombre_proyecto_libre'] = nombre_proyecto
    st.session_state['plan_nombre'] = nombre_plan
    st.session_state['plan_eje'] = eje_plan
    st.session_state['plan_programa'] = programa_plan
    st.session_state["sector_seleccionado"] = sector_seleccionado
    st.session_state["programa_seleccionado"] = programa_seleccionado
    st.session_state["producto_seleccionado"] = st.session_state.get("producto_seleccionado", "")
    st.session_state["producto_seleccionado_label"] = st.session_state.get("producto_seleccionado_label", "")
    st.session_state["producto_principal"] = st.session_state.get("producto_principal", {})
    
    guardar_datos_nube()
    st.success("✅ Información guardada correctamente.")
