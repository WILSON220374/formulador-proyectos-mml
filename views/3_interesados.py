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
    /* 1. SOLUCIÓN AL SCROLL: Espacio extra al final */
    .block-container { padding-bottom: 250px !important; }

    /* 2. Títulos Generales */
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* 3. FORZAR CABECERA AZUL OSCURO Y TEXTO BLANCO */
    .ag-theme-streamlit .ag-header {
        background-color: #1E3A8A !important;
    }
    .ag-theme-streamlit .ag-header-cell-text {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    .ag-theme-streamlit .ag-header-icon {
        color: #FFFFFF !important;
    }

    /* 4. KPIs en Negro */
    .kpi-card {
        background: white; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-val { font-size: 24px; font-weight: 800; color: #000000 !important; } 
    .kpi-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Ajustes generales */
    [data-testid="stImage"] img { border-radius: 12px; pointer-events: none; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1])
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores clave y mapeo de influencias estratégicas.</div>', unsafe_allow_html=True)
    
    # Cálculo seguro del progreso
    tiene_datos = not df_actual.empty and 'NOMBRE' in df_actual.columns and df_actual['NOMBRE'].dropna().any()
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Completitud: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- KPIs ---
if tiene_datos:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{len(df_actual.dropna(subset=["NOMBRE"]))}</div><div class="kpi-label">Total Actores</div></div>', unsafe_allow_html=True)
    with c2: 
        opos = len(df_actual[df_actual["POSICIÓN"] == "Opositor"])
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{opos}</div><div class="kpi-label">Opositores</div></div>', unsafe_allow_html=True)
    with c3:
        coop = len(df_actual[df_actual["POSICIÓN"] == "Cooperante"])
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{coop}</div><div class="kpi-label">Cooperantes</div></div>', unsafe_allow_html=True)
    with c4:
        p_alto = len(df_actual[df_actual["PODER"] == "Alto"])
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{p_alto}</div><div class="kpi-label">Poder Alto</div></div>', unsafe_allow_html=True)

# --- MATRIZ DE DATOS ---
st.subheader("📝 Matriz de Datos")

# 1. BOTÓN PARA AGREGAR FILAS VACÍAS
# Usamos columnas para que el botón no ocupe todo el ancho
col_btn, _ = st.columns([1, 4])
with col_btn:
    if st.button("➕ Agregar Nuevo Actor", type="primary", use_container_width=True):
        # Crear fila vacía con valores por defecto seguros
        new_row = pd.DataFrame([{
            "NOMBRE": "", 
            "GRUPO": "", 
            "POSICIÓN": "Indiferente", 
            "EXPECTATIVA": "", 
            "CONTRIBUCION AL PROYECTO": "", 
            "PODER": "Bajo", 
            "INTERÉS": "Bajo", 
            "ESTRATEGIA": ""
        }])
        # Concatenar y guardar en sesión
        st.session_state['df_interesados'] = pd.concat([df_actual, new_row], ignore_index=True)
        guardar_datos_nube() 
        st.rerun()

# 2. Preparar DataFrame
cols_orden = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA"]
if df_actual.empty: df_actual = pd.DataFrame(columns=cols_orden)
# Asegurar columnas
for c in cols_orden:
    if c not in df_actual.columns: df_actual[c] = ""
df_render = df_actual[cols_orden].copy()

# 3. Configurar AgGrid
gb = GridOptionsBuilder.from_dataframe(df_render)
gb.configure_default_column(editable=True, resizable=True, filterable=True, wrapText=True, autoHeight=True)
gb.configure_grid_options(domLayout='autoHeight') 

# 4. COLORES PASTEL Y FUENTES
cell_style_js = JsCode("""
function(params) {
    // Colores Pastel Suaves - Letra normal (#333)
    if (params.value == 'Opositor') { return {'backgroundColor': '#FFEBEE', 'color': '#333333'}; }
    if (params.value == 'Cooperante') { return {'backgroundColor': '#E8F5E9', 'color': '#333333'}; }
    if (params.value == 'Beneficiario') { return {'backgroundColor': '#E3F2FD', 'color': '#333333'}; }
    if (params.value == 'Perjudicado') { return {'backgroundColor': '#FFFDE7', 'color': '#333333'}; }
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
gb.configure_column("EXPECTATIVA", width=300)
gb.configure_column("CONTRIBUCION AL PROYECTO", header_name="Contribución", width=200)
gb.configure_column("PODER", cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Alto', 'Bajo']}, width=100)
gb.configure_column("INTERÉS", cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Alto', 'Bajo']}, width=100)

# ESTRATEGIA: Negrita
gb.configure_column("ESTRATEGIA", editable=False, cellStyle={'fontWeight': 'bold', 'color': '#444'}, width=220)

gb.configure_selection('single', use_checkbox=False)
gridOptions = gb.build()

st.caption("💡 Use el botón superior para agregar filas vacías. Doble clic para editar.")

# 5. Renderizar Tabla
grid_response = AgGrid(
    df_render,
    gridOptions=gridOptions,
    allow_unsafe_jscode=True,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    height=None, 
    fit_columns_on_grid_load=True,
    theme='streamlit',
    key='aggrid_interesados_v_final_clean'
)

df_modificado = pd.DataFrame(grid_response['data'])

st.divider()

# --- MAPA ESTRATÉGICO ---
st.subheader("📊 Mapa de Influencia")

if not df_modificado.empty and 'NOMBRE' in df_modificado.columns:
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    def obtener_lista(p, i):
        # Filtro seguro
        f = df_modificado[(df_modificado['PODER'] == p) & (df_modificado['INTERÉS'] == i) & (df_modificado['NOMBRE'].notna()) & (df_modificado['NOMBRE'] != "")]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}**" for _, r in f.iterrows()] or ["*Sin actores*"]

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **SATISFACER / CONSULTAR** (P:Alto / I:Bajo)")
            for item in obtener_lista("Alto", "Bajo"): st.markdown(item)
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR** (P:Bajo / I:Bajo)")
            for item in obtener_lista("Bajo", "Bajo"): st.markdown(item)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR ATENTAMENTE** (P:Alto / I:Alto)")
            for item in obtener_lista("Alto", "Alto"): st.markdown(item)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS** (P:Bajo / I:Alto)")
            for item in obtener_lista("Bajo", "Alto"): st.markdown(item)
else:
    st.info("Complete la matriz para activar el mapa estratégico.")

st.divider()

# --- ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, height=200, 
    key="txt_analisis_final_panel", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)

# --- LÓGICA DE GUARDADO ---
def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

if not df_modificado.empty:
    df_modificado["ESTRATEGIA"] = df_modificado.apply(calcular_estrategia, axis=1)

hubo_cambio_tabla = not df_modificado.equals(df_actual)
hubo_cambio_texto = analisis_actual != analisis_txt

if hubo_cambio_tabla or hubo_cambio_texto:
    if hubo_cambio_tabla:
        st.session_state['df_interesados'] = df_modificado
    if hubo_cambio_texto:
        st.session_state['analisis_participantes'] = analisis_actual
    
    guardar_datos_nube()
    st.rerun()
