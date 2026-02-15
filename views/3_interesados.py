iimport streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# 1. Inicialización
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* Estilos generales del Header */
    .titulo-seccion { 
        font-size: 30px !important; 
        font-weight: 800 !important; 
        color: #1E3A8A; 
        margin-bottom: 5px; 
    }
    .subtitulo-gris { 
        font-size: 16px !important; 
        color: #666; 
        margin-bottom: 15px; 
    }
    
    /* Imagen del logo con bordes redondeados */
    [data-testid="stImage"] img { border-radius: 12px; }

    /* Estilo para el botón de guardar (Solo icono, azul oscuro) */
    div.stButton > button:first-child {
        background-color: #1E3A8A;
        color: white;
        border: none;
        font-size: 20px;
        padding: 5px 15px;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #153075;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores clave y mapeo de influencias estratégicas.</div>', unsafe_allow_html=True)
    
    # Cálculo de progreso
    tiene_datos = False
    if isinstance(df_actual, pd.DataFrame) and not df_actual.empty and 'NOMBRE' in df_actual.columns:
        tiene_datos = df_actual['NOMBRE'].dropna().any()
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Completitud: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- PREPARACIÓN DE DATOS ---
columnas_validas = [
    "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", 
    "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA"
]

if df_actual.empty: 
    df_clean = pd.DataFrame(columns=columnas_validas)
else:
    for col in columnas_validas:
        if col not in df_actual.columns:
            df_actual[col] = ""
    df_clean = df_actual[columnas_validas].copy()
    df_clean = df_clean.reset_index(drop=True)

# Opciones listas desplegables
opciones_pos = ["🔴 Opositor", "🟢 Cooperante", "🔵 Beneficiario", "🟣 Perjudicado"]
opciones_niv = ["⚡ ALTO", "🔅 BAJO"]

# --- CONFIGURACIÓN AG-GRID ---
gb = GridOptionsBuilder.from_dataframe(df_clean)

# 1. Configuración de Columnas (Texto Ajustado + Auto Altura)
gb.configure_column("NOMBRE", headerName="👤 Nombre", width=180, editable=True, wrapText=True, autoHeight=True)
gb.configure_column("GRUPO", headerName="🏢 Grupo", width=120, editable=True, wrapText=True, autoHeight=True)

# Selectores
gb.configure_column("POSICIÓN", headerName="🚩 Posición", editable=True, 
                    cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_pos}, width=140)

# Textos largos
gb.configure_column("EXPECTATIVA", headerName="🎯 Expectativa", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("CONTRIBUCION AL PROYECTO", headerName="💡 Contribución", editable=True, wrapText=True, autoHeight=True, width=250)

# Niveles
gb.configure_column("PODER", headerName="⚡ Poder", editable=True, 
                    cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)
gb.configure_column("INTERÉS", headerName="👁️ Interés", editable=True, 
                    cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)

# Estrategia calculada
gb.configure_column("ESTRATEGIA", headerName="🚀 Estrategia", editable=False, wrapText=True, autoHeight=True, width=200)

# 2. COLORES INTELIGENTES (Javascript)
jscode_row_style = JsCode("""
function(params) {
    if (params.data.POSICIÓN === '🔴 Opositor') {
        return { 'background-color': '#FEF2F2', 'color': 'black' }; // Rojo muy suave
    } else if (params.data.POSICIÓN === '🟢 Cooperante') {
        return { 'background-color': '#F0FDF4', 'color': 'black' }; // Verde muy suave
    } else if (params.data.POSICIÓN === '🔵 Beneficiario') {
        return { 'background-color': '#EFF6FF', 'color': 'black' }; // Azul muy suave
    } else if (params.data.POSICIÓN === '🟣 Perjudicado') {
        return { 'background-color': '#FAF5FF', 'color': 'black' }; // Morado muy suave
    }
    return null;
};
""")

gb.configure_grid_options(getRowStyle=jscode_row_style, domLayout='autoHeight')
gridOptions = gb.build()

# 3. Estilos de Cabecera (Negrita y Azul)
custom_css = {
    ".ag-header-cell-text": {"font-size": "14px !important", "font-weight": "700 !important", "color": "#1E3A8A !important"},
    ".ag-header": {"background-color": "#f8f9fa !important"}
}

# 4. Renderizar Tabla
st.subheader("📝 Matriz de Interesados")
grid_response = AgGrid(
    df_clean,
    gridOptions=gridOptions,
    custom_css=custom_css,
    update_mode=GridUpdateMode.MANUAL, # Evita parpadeo
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    theme='streamlit',
    allow_unsafe_jscode=True
)

# --- BOTÓN DE GUARDADO ---
col_btn, col_rest = st.columns([1, 10])
with col_btn:
    btn_guardar = st.button("💾", help="Guardar Cambios de la Tabla")

# Función de cálculo
def calcular_estrategia(row):
    p = str(row.get('PODER', '')).replace("⚡ ", "").replace("🔅 ", "").strip().upper()
    i = str(row.get('INTERÉS', '')).replace("⚡ ", "").replace("🔅 ", "").strip().upper()
    
    if p == "ALTO" and i == "BAJO": return "INVOLUCRAR - MANTENER SATISFECHOS"
    if p == "ALTO" and i == "ALTO": return "INVOLUCRAR Y ATRAER EFECTIVAMENTE"
    if p == "BAJO" and i == "ALTO": return "MANTENER INFORMADOS"
    if p == "BAJO" and i == "BAJO": return "MONITOREAR"
    return ""

if btn_guardar:
    df_editado = pd.DataFrame(grid_response['data'])
    
    if not df_editado.empty:
        df_editado["ESTRATEGIA"] = df_editado.apply(calcular_estrategia, axis=1)
        st.session_state['df_interesados'] = df_editado
        guardar_datos_nube()
        st.rerun()

st.write("")

# --- MAPA ESTRATÉGICO ---
st.subheader("📊 Mapa de Influencia")
if tiene_datos:
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    
    df_mapa = st.session_state.get('df_interesados', df_clean)

    def obtener_lista(p_key, i_key):
        if df_mapa.empty: return ["*Sin datos*"]
        
        f = df_mapa[
            (df_mapa['PODER'].astype(str).str.upper().str.contains(p_key)) & 
            (df_mapa['INTERÉS'].astype(str).str.upper().str.contains(i_key)) & 
            (df_mapa['NOMBRE'].notna()) & (df_mapa['NOMBRE'] != "")
        ]
        res = []
        for _, r in f.iterrows():
            pos_txt = str(r['POSICIÓN'])
            icono = "⚪"
            for k, v in color_map.items():
                if k in pos_txt: icono = v; break
            res.append(f"{icono} **{r['NOMBRE']}**")
        return res or ["*Sin actores*"]

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **INVOLUCRAR - MANTENER SATISFECHOS** (P:Alto / I:Bajo)")
            for item in obtener_lista("ALTO", "BAJO"): st.markdown(item)
        with st.container(border=True):
            st.warning("🔍 **MONITOREAR** (P:Bajo / I:Bajo)")
            for item in obtener_lista("BAJO", "BAJO"): st.markdown(item)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y ATRAER EFECTIVAMENTE** (P:Alto / I:Alto)")
            for item in obtener_lista("ALTO", "ALTO"): st.markdown(item)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS** (P:Bajo / I:Alto)")
            for item in obtener_lista("BAJO", "ALTO"): st.markdown(item)
else:
    st.info("Complete la matriz y guarde para activar el mapa estratégico.")

st.divider()

# --- ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, height=200, 
    key="txt_analisis_final_panel", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)

if analisis_actual != analisis_txt:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
