import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# 1. Inicialización
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    [data-testid="stImage"] img { pointer-events: none; border-radius: 10px; }
    
    /* Ajuste para que AgGrid se vea limpio */
    .ag-theme-streamlit {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores con semaforización de riesgos.</div>', unsafe_allow_html=True)
    # Progreso
    tiene_datos = not df_actual.empty and df_actual['NOMBRE'].dropna().any() if 'NOMBRE' in df_actual.columns else False
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Fase de Identificación: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- CONTEXTO ---
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
with st.expander("📌 Contexto: Problema Central", expanded=False):
    st.info(f"**Problema:** {problema}")

# --- MATRIZ PROFESIONAL (AG-GRID AUTO-EXPANDIBLE) ---
st.subheader("📝 Matriz de Gestión")

# 1. Preparar datos
columnas = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "PODER", "INTERÉS", "ESTRATEGIA"]
if df_actual.empty: df_actual = pd.DataFrame(columns=columnas)
for c in columnas:
    if c not in df_actual.columns: df_actual[c] = ""
df_actual = df_actual[columnas]

# 2. Configurar AgGrid
gb = GridOptionsBuilder.from_dataframe(df_actual)
gb.configure_default_column(editable=True, resizable=True, filterable=True, wrapText=True, autoHeight=True)

# ---> CORRECCIÓN CLAVE: Activar Auto-Altura para eliminar el scroll interno <---
gb.configure_grid_options(domLayout='autoHeight') 

# Colores Condicionales (Tus semáforos)
cell_style_posicion = JsCode("""
function(params) {
    if (params.value == 'Opositor') { return {'backgroundColor': '#ffcccc', 'color': '#990000', 'fontWeight': 'bold'}; }
    if (params.value == 'Cooperante') { return {'backgroundColor': '#ccffcc', 'color': '#006600', 'fontWeight': 'bold'}; }
    if (params.value == 'Beneficiario') { return {'backgroundColor': '#cceeff', 'color': '#003366'}; }
    return {};
}
""")

gb.configure_column("NOMBRE", header_name="Actor / Entidad", minWidth=200, pinned="left")
gb.configure_column("GRUPO", width=120)
gb.configure_column("POSICIÓN", cellStyle=cell_style_posicion, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Opositor', 'Cooperante', 'Beneficiario', 'Perjudicado', 'Indiferente']}, width=130)
gb.configure_column("EXPECTATIVA", width=300)
gb.configure_column("PODER", cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Alto', 'Bajo']}, width=100)
gb.configure_column("INTERÉS", cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Alto', 'Bajo']}, width=100)
gb.configure_column("ESTRATEGIA", editable=False, cellStyle={'color': 'gray', 'fontStyle': 'italic'}, width=200)

gb.configure_selection('single', use_checkbox=False)
gridOptions = gb.build()

# 3. Mostrar Tabla
st.caption("💡 La tabla se expandirá automáticamente para mostrar todos los actores.")
grid_response = AgGrid(
    df_actual,
    gridOptions=gridOptions,
    allow_unsafe_jscode=True,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    # height=400,  <-- ELIMINAMOS LA ALTURA FIJA
    fit_columns_on_grid_load=True, # Ajusta las columnas al ancho disponible
    theme='streamlit',
    key='aggrid_interesados_auto'
)

# 4. Recuperar y Guardar
df_modificado = grid_response['data']

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

if isinstance(df_modificado, pd.DataFrame): df_new = df_modificado
else: df_new = pd.DataFrame(df_modificado)

df_new["ESTRATEGIA"] = df_new.apply(calcular_estrategia, axis=1)

if not df_new.equals(df_actual):
    st.session_state['df_interesados'] = df_new
    guardar_datos_nube()
    st.rerun()

st.divider()

# --- ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, height=150, 
    key="txt_analisis_final", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)

if analisis_actual != analisis_txt:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
