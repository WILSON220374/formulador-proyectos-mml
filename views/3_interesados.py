import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube
# IMPORTAMOS LA LIBRERÍA QUE AGREGAMOS AL REQUIREMENTS
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# 1. Inicialización
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 20px; }
    
    /* KPI Cards */
    .kpi-card {
        background-color: #f8f9fa; border-radius: 8px; padding: 15px;
        text-align: center; border: 1px solid #eee;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-val { font-size: 22px; font-weight: 800; color: #4F8BFF; }
    .kpi-lbl { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }

    [data-testid="stImage"] img { border-radius: 10px; pointer-events: none; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Gestión de actores con semaforización de riesgos (AgGrid).</div>', unsafe_allow_html=True)
    
    tiene_datos = not df_actual.empty and df_actual['NOMBRE'].dropna().any() if 'NOMBRE' in df_actual.columns else False
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Avance: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- KPIs ---
if tiene_datos:
    total = len(df_actual.dropna(subset=["NOMBRE"]))
    opos = len(df_actual[df_actual['POSICIÓN'] == "Opositor"])
    coop = len(df_actual[df_actual['POSICIÓN'] == "Cooperante"])
    poder = len(df_actual[df_actual['PODER'] == "Alto"])

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{total}</div><div class="kpi-lbl">Total</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#ef4444;">{opos}</div><div class="kpi-lbl">Opositores</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#22c55e;">{coop}</div><div class="kpi-lbl">Cooperantes</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{poder}</div><div class="kpi-lbl">Poder Alto</div></div>', unsafe_allow_html=True)
    st.write("")

# --- MATRIZ PROFESIONAL (AG-GRID) ---
st.subheader("📝 Matriz de Datos")

# 1. Preparar columnas
cols = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "PODER", "INTERÉS", "ESTRATEGIA"]
if df_actual.empty: df_actual = pd.DataFrame(columns=cols)
for c in cols:
    if c not in df_actual.columns: df_actual[c] = ""
df_render = df_actual[cols].copy()

# 2. Configurar AgGrid
gb = GridOptionsBuilder.from_dataframe(df_render)
gb.configure_default_column(editable=True, resizable=True, filterable=True, wrapText=True, autoHeight=True)

# ---> ESTO ES LO QUE ARREGLA EL SCROLL: Auto altura <---
gb.configure_grid_options(domLayout='autoHeight')

# 3. Inyectar JAVASCRIPT para los colores (Rojo/Verde)
cell_style_js = JsCode("""
function(params) {
    if (params.value == 'Opositor') {
        return {'backgroundColor': '#ffcccc', 'color': '#990000', 'fontWeight': 'bold'};
    }
    if (params.value == 'Cooperante') {
        return {'backgroundColor': '#ccffcc', 'color': '#006600', 'fontWeight': 'bold'};
    }
    if (params.value == 'Beneficiario') {
        return {'backgroundColor': '#cceeff', 'color': '#003366'};
    }
    return {};
}
""")

gb.configure_column("NOMBRE", header_name="Actor / Entidad", minWidth=220, pinned="left")
gb.configure_column("GRUPO", width=120)
gb.configure_column("POSICIÓN", 
    cellStyle=cell_style_js, 
    cellEditor='agSelectCellEditor', 
    cellEditorParams={'values': ['Opositor', 'Cooperante', 'Beneficiario', 'Perjudicado', 'Indiferente']},
    width=130
)
gb.configure_column("EXPECTATIVA", width=350)
gb.configure_column("PODER", cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Alto', 'Bajo']}, width=100)
gb.configure_column("INTERÉS", cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Alto', 'Bajo']}, width=100)
gb.configure_column("ESTRATEGIA", editable=False, cellStyle={'color': 'gray', 'fontStyle': 'italic'}, width=200)

gb.configure_selection('single', use_checkbox=False)
gridOptions = gb.build()

st.caption("💡 Doble clic en una celda para editar. La tabla crece automáticamente.")

# 4. Mostrar la tabla
grid_response = AgGrid(
    df_render,
    gridOptions=gridOptions,
    allow_unsafe_jscode=True, # Permitir JS para colores
    update_mode=GridUpdateMode.VALUE_CHANGED,
    height=None, # Dejar que autoHeight controle la altura
    fit_columns_on_grid_load=True,
    theme='streamlit',
    key='aggrid_final_fix'
)

st.divider()

# --- ANÁLISIS CUALITATIVO (Siempre visible al final) ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, height=200, 
    key="txt_analisis_final", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)

# --- GUARDADO ---
# 1. Recuperar datos de la tabla AgGrid
df_modificado = grid_response['data']
if isinstance(df_modificado, pd.DataFrame): 
    df_new = df_modificado
else: 
    df_new = pd.DataFrame(df_modificado)

# 2. Recalcular estrategias (Lógica Python)
def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

df_new["ESTRATEGIA"] = df_new.apply(calcular_estrategia, axis=1)

# 3. Detectar cambios y guardar
cambio_tabla = not df_new.equals(df_actual)
cambio_texto = analisis_actual != analisis_txt

if cambio_tabla or cambio_texto:
    if cambio_tabla:
        st.session_state['df_interesados'] = df_new
    if cambio_texto:
        st.session_state['analisis_participantes'] = analisis_actual
    
    guardar_datos_nube()
    st.rerun()
