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

# --- SECCIÓN 1: SECTOR Y PROGRAMA ---
st.markdown('<div class="header-tabla">🏢 1. Sector y Programa de Inversión</div>', unsafe_allow_html=True)
col_s1, col_s2 = st.columns(2)
with col_s1:
    sector_seleccionado = st.selectbox("Sector de Inversión", ["Seleccione..."])
with col_s2:
    programa_seleccionado = st.selectbox("Programa", ["Seleccione..."])

st.divider()

# --- SECCIÓN 2: MATRIZ DE PRODUCTO ---
st.markdown('<div class="header-tabla">📦 2. Producto Principal</div>', unsafe_allow_html=True)

columnas_producto = ["PRODUCTO", "Descripción", "Medido a través de", "Indicador de Producto", "Unidad de medida"]
df_producto_vacio = pd.DataFrame(columns=columnas_producto)
st.dataframe(df_producto_vacio, use_container_width=True, hide_index=True)

st.divider()

# =========================================================
# 🏷️ SECCIÓN 3: NOMBRE DEL PROYECTO (CON VISTA PREVIA VERDE ESMERALDA)
# =========================================================
st.markdown('<div class="header-tabla">🏷️ 3. Nombre del Proyecto</div>', unsafe_allow_html=True)

nombre_proyecto = st.text_area("Escriba el nombre definitivo del proyecto", 
                               value=st.session_state.get('nombre_proyecto_libre', ""),
                               placeholder="Ej: Construcción de la planta de tratamiento de aguas residuales en el municipio...", 
                               height=100)

# Cartel de Vista Previa Destacado (Verde Esmeralda sin el subtítulo)
if nombre_proyecto.strip():
    st.markdown(f"""
        <div style="margin-top: 15px; padding: 25px; border-radius: 10px; background-color: #059669; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 1.5rem; font-weight: 800; text-transform: uppercase; line-height: 1.3;">
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
    
    guardar_datos_nube()
    st.success("✅ Información guardada correctamente.")
