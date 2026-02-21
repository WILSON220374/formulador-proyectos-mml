import streamlit as st
import os
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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
        min-height: 80px; line-height: 1.5;
    }

    /* CSS CUSTOM PARA AGGRID (Encabezados Azul Oscuro y Centrados) */
    .header-azul {
        background-color: #1E3A8A !important;
        color: white !important;
        font-weight: bold !important;
        text-align: center !important;
        display: flex;
        justify-content: center;
    }
    
    /* ¡NUEVO!: CSS PARA AUTOAJUSTAR LOS TEXT AREA */
    .stTextArea textarea {
        field-sizing: content !important;
        min-height: 120px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO Y AVANCE ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 14. Necesidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Identificación de la necesidad y balance automático de oferta-demanda.</div>', unsafe_allow_html=True)
    progress_placeholder = st.empty()
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- EXTRACCIÓN DEL OBJETIVO GENERAL ---
mapa = st.session_state.get("indicadores_mapa_objetivo", {})
datos_ind = st.session_state.get("datos_indicadores", {})
seleccion = st.session_state.get("seleccion_indicadores", {})
metas = st.session_state.get("meta_resultados_parciales", {})

obj_general, ind_general, meta_general = "No definido (Complete Hoja 11)", "No definido", "No definido"

for kmap, k in mapa.items():
    partes = kmap.split("||")
    if len(partes) != 2: continue
    
    nivel_original = partes[0]
    if "General" in nivel_original or "Fin" in nivel_original:
        sel = seleccion.get(k, {})
        is_selected = True if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in ["P1", "P2", "P3", "P4", "P5"]) else False
        
        if is_selected:
            obj_general = partes[1]
            ind_general = str(datos_ind.get(k, {}).get("Indicador", "")).strip()
            meta_general = str(metas.get(k, {}).get("Meta", "")).strip()
            break

# --- SECCIÓN 1: OBJETIVO GENERAL ---
st.markdown('<div class="header-tabla">🎯 Objetivo General del Proyecto</div>', unsafe_allow_html=True)
with st.container(border=True):
    col1, col2, col3 = st.columns([2, 1.5, 1])
    with col1: st.markdown(f'<div class="readonly-label">Descripción del Objetivo</div><div class="readonly-box">{obj_general}</div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="readonly-label">Indicador</div><div class="readonly-box">{ind_general}</div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="readonly-label">Meta</div><div class="readonly-box" style="text-align: center; min-height: 45px;">{meta_general}</div>', unsafe_allow_html=True)

st.divider()

# --- SECCIÓN 2: NECESIDADES ---
st.markdown('<div class="header-tabla">🔍 Análisis de la Necesidad</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a: desc_objetivo = st.text_area("Descripción del objetivo general", value=st.session_state.get('desc_objetivo_general', ""), placeholder="Describa el objetivo general...")
with col_b: nec_atender = st.text_area("Necesidad a atender", value=st.session_state.get('necesidad_atender', ""), placeholder="¿Qué necesidad principal se está atendiendo?")

st.divider()

# --- SECCIÓN 3: CÁLCULO DEL DÉFICIT (CON AGGRID) ---
st.markdown('<div class="header-tabla">📉 Cálculo del Déficit (Proyección a 10 años)</div>', unsafe_allow_html=True)

anio_form = st.number_input("Año de Formulación", min_value=1950, max_value=2070, value=st.session_state.get('anio_formulacion', 2026), step=1)

def obtener_df_base(anio_central):
    anios = list(range(anio_central - 5, anio_central + 6))
    datos_guardados = st.session_state.get('tabla_deficit', {})
    rows = []
    for a in anios:
        val = datos_guardados.get(str(a), {"dem": 0.0, "ofe": 0.0})
        dem = float(val["dem"])
        ofe = float(val["ofe"])
        rows.append({
            "AÑO": a,
            "CANTIDAD DEMANDADA": dem,
            "CANTIDAD OFERTADA": ofe,
            "DÉFICIT (OFERTA - DEMANDA)": ofe - dem
        })
    return pd.DataFrame(rows)

df_base = obtener_df_base(anio_form)

st.info("💡 Haz doble clic en las celdas de 'Cantidad Demandada' y 'Cantidad Ofertada' para editar. Presiona Enter para guardar.")

# Configuración de la tabla AgGrid
gb = GridOptionsBuilder.from_dataframe(df_base)

# Aplicar centrado general y el color azul a la cabecera
gb.configure_default_column(
    headerClass="header-azul",
    cellStyle={'textAlign': 'center'}
)

# Configurar columnas específicas
gb.configure_column("AÑO", editable=False, width=100)
gb.configure_column("CANTIDAD DEMANDADA", editable=True, type=["numericColumn", "numberColumnFilter"], width=200)
gb.configure_column("CANTIDAD OFERTADA", editable=True, type=["numericColumn", "numberColumnFilter"], width=200)
gb.configure_column("DÉFICIT (OFERTA - DEMANDA)", editable=False, width=220)

gridOptions = gb.build()

# Mostrar la tabla
grid_response = AgGrid(
    df_base,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    theme="streamlit",
    fit_columns_on_grid_load=True,
    height=450,
    allow_unsafe_jscode=True
)

# Recuperar datos editados y recalcular déficit
edited_df = pd.DataFrame(grid_response['data'])
if not edited_df.empty:
    edited_df["CANTIDAD DEMANDADA"] = pd.to_numeric(edited_df["CANTIDAD DEMANDADA"], errors='coerce').fillna(0.0)
    edited_df["CANTIDAD OFERTADA"] = pd.to_numeric(edited_df["CANTIDAD OFERTADA"], errors='coerce').fillna(0.0)
    edited_df["DÉFICIT (OFERTA - DEMANDA)"] = edited_df["CANTIDAD OFERTADA"] - edited_df["CANTIDAD DEMANDADA"]

# --- BARRA DE PROGRESO ---
progreso_actual = 0.90 
if desc_objetivo and len(desc_objetivo.strip()) > 2: progreso_actual += 0.03
if nec_atender and len(nec_atender.strip()) > 2: progreso_actual += 0.03
if not edited_df.empty and (edited_df["CANTIDAD DEMANDADA"].sum() > 0 or edited_df["CANTIDAD OFERTADA"].sum() > 0): progreso_actual += 0.04
progress_placeholder.progress(min(1.0, progreso_actual))

# --- GUARDADO ---
if st.button("💾 Guardar Información de Necesidad", type="primary"):
    st.session_state['desc_objetivo_general'] = desc_objetivo
    st.session_state['necesidad_atender'] = nec_atender
    st.session_state['anio_formulacion'] = anio_form
    
    dict_final = {}
    if not edited_df.empty:
        for _, row in edited_df.iterrows():
            dict_final[str(int(row["AÑO"]))] = {
                "dem": row["CANTIDAD DEMANDADA"],
                "ofe": row["CANTIDAD OFERTADA"]
            }
        st.session_state['tabla_deficit'] = dict_final
    
    guardar_datos_nube()
    st.success("✅ Datos guardados y déficit calculado correctamente.")
    st.rerun()
