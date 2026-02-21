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
    
    /* Autoajuste para text areas */
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

# --- LÓGICA DE EXTRACCIÓN DEL OBJETIVO GENERAL (REAL) ---
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

# --- SECCIÓN 1: SECTOR Y PROGRAMA ---
st.markdown('<div class="header-tabla">🏢 1. Sector y Programa de Inversión</div>', unsafe_allow_html=True)
col_s1, col_s2 = st.columns(2)
with col_s1:
    # Selector vacío a la espera del DataFrame
    sector_seleccionado = st.selectbox("Sector de Inversión", ["Seleccione..."])
with col_s2:
    # Selector vacío a la espera del DataFrame
    programa_seleccionado = st.selectbox("Programa", ["Seleccione..."])

st.divider()

# --- SECCIÓN 2: MATRIZ DE PRODUCTO ---
st.markdown('<div class="header-tabla">📦 2. Producto Principal</div>', unsafe_allow_html=True)

# Objetivo General Traído de memoria
st.markdown(f'<div class="readonly-label">Objetivo General</div><div class="readonly-box">{obj_general}</div><br>', unsafe_allow_html=True)

# Tabla vacía con la estructura exacta del Excel
columnas_producto = ["PRODUCTO", "Descripción", "Medido a través de", "Indicador de Producto", "Unidad de medida"]
df_producto_vacio = pd.DataFrame(columns=columnas_producto)

st.dataframe(df_producto_vacio, use_container_width=True, hide_index=True)

st.divider()

# --- SECCIÓN 3: NOMBRE DEL PROYECTO ---
st.markdown('<div class="header-tabla">🏷️ 3. Nombre del Proyecto</div>', unsafe_allow_html=True)
nombre_proyecto = st.text_area("Escritura Libre", 
                               value=st.session_state.get('nombre_proyecto_libre', ""),
                               placeholder="Ej: Construcción de la planta de tratamiento de aguas residuales en el municipio...", 
                               height=120)

st.divider()

# --- SECCIÓN 4: PLAN DE DESARROLLO ---
st.markdown('<div class="header-tabla">🗺️ 4. Plan de Desarrollo</div>', unsafe_allow_html=True)
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    nombre_plan = st.text_input("Nombre del Plan", value=st.session_state.get('plan_nombre', ""))
with col_p2:
    eje_plan = st.text_input("Eje", value=st.session_state.get('plan_eje', ""))
with col_p3:
    programa_plan = st.text_input("Programa", value=st.session_state.get('plan_programa', ""))

st.divider()

# --- BOTÓN DE GUARDADO ---
if st.button("💾 Guardar Información de Producto", type="primary"):
    # Guardamos los campos de texto libre
    st.session_state['nombre_proyecto_libre'] = nombre_proyecto
    st.session_state['plan_nombre'] = nombre_plan
    st.session_state['plan_eje'] = eje_plan
    st.session_state['plan_programa'] = programa_plan
    
    # Aquí luego agregaremos el guardado de los selectores cuando estén conectados
    
    guardar_datos_nube()
    st.success("✅ Información guardada correctamente.")
