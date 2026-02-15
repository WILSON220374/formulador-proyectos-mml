import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# 1. Inicialización
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Headers */
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Botones */
    div.stButton > button:first-child {
        background-color: #1E3A8A; color: white; border: none; font-size: 20px; padding: 5px 15px; border-radius: 8px;
    }
    div.stButton > button:hover { background-color: #153075; color: white; }
    
    /* MATRIZ DE INTERESADOS (CSS GRID AVANZADO) */
    .matrix-container {
        display: grid;
        grid-template-columns: 40px 1fr 1fr;
        grid-template-rows: 1fr 1fr 40px;
        gap: 15px;
        font-family: sans-serif;
    }
    
    /* Etiquetas de Ejes */
    .axis-y {
        grid-row: 1 / 3;
        grid-column: 1;
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        text-align: center;
        font-weight: 900;
        color: #94a3b8;
        letter-spacing: 2px;
        font-size: 14px;
        border-right: 2px solid #e2e8f0;
        padding-left: 10px;
    }
    .axis-x {
        grid-row: 3;
        grid-column: 2 / 4;
        text-align: center;
        font-weight: 900;
        color: #94a3b8;
        letter-spacing: 2px;
        font-size: 14px;
        border-top: 2px solid #e2e8f0;
        padding-top: 10px;
    }
    
    /* Cuadrantes (Tarjetas Grandes) */
    .quadrant-box {
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        gap: 8px;
        height: 100%;
        min-height: 220px;
    }
    
    /* Títulos de Cuadrantes */
    .q-title {
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 8px;
        opacity: 0.8;
    }
    
    /* Chips de Actores */
    .actor-chip {
        background: white;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        color: #334155;
        border-left: 4px solid #cbd5e1; /* Default border */
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores clave y mapeo de influencias estratégicas.</div>', unsafe_allow_html=True)
    
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

opciones_pos = ["🔴 Opositor", "🟢 Cooperante", "🔵 Beneficiario", "🟣 Perjudicado"]
opciones_niv = ["⚡ ALTO", "🔅 BAJO"]

# --- TABLA AG-GRID ---
gb = GridOptionsBuilder.from_dataframe(df_clean)
gb.configure_column("NOMBRE", headerName="👤 Nombre", width=180, editable=True, wrapText=True, autoHeight=True)
gb.configure_column("GRUPO", headerName="🏢 Grupo", width=120, editable=True, wrapText=True, autoHeight=True)
gb.configure_column("POSICIÓN", headerName="🚩 Posición", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_pos}, width=140)
gb.configure_column("EXPECTATIVA", headerName="🎯 Expectativa", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("CONTRIBUCION AL PROYECTO", headerName="💡 Contribución", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("PODER", headerName="⚡ Poder", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)
gb.configure_column("INTERÉS", headerName="👁️ Interés", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)
gb.configure_column("ESTRATEGIA", headerName="🚀 Estrategia", editable=False, wrapText=True, autoHeight=True, width=200)

jscode_row_style = JsCode("""
function(params) {
    if (params.data.POSICIÓN === '🔴 Opositor') return { 'background-color': '#FEF2F2', 'color': 'black' };
    if (params.data.POSICIÓN === '🟢 Cooperante') return { 'background-color': '#F0FDF4', 'color': 'black' };
    if (params.data.POSICIÓN === '🔵 Beneficiario') return { 'background-color': '#EFF6FF', 'color': 'black' };
    if (params.data.POSICIÓN === '🟣 Perjudicado') return { 'background-color': '#FAF5FF', 'color': 'black' };
    return null;
};
""")
gb.configure_grid_options(getRowStyle=jscode_row_style, domLayout='autoHeight')
gridOptions = gb.build()

custom_css = {
    ".ag-header-cell-text": {"font-size": "14px !important", "font-weight": "700 !important", "color": "#1E3A8A !important"},
    ".ag-header": {"background-color": "#f8f9fa !important"}
}

st.subheader("📝 Matriz de Interesados")
grid_response = AgGrid(
    df_clean, gridOptions=gridOptions, custom_css=custom_css,
    update_mode=GridUpdateMode.MANUAL, data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True, theme='streamlit', allow_unsafe_jscode=True
)

col_btn, col_rest = st.columns([1, 10])
with col_btn:
    btn_guardar = st.button("💾", help="Guardar Cambios")

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
st.divider()

# --- MAPA DE INFLUENCIA (DISEÑO PROFESIONAL HTML/CSS) ---
st.subheader("📊 Mapa de Influencia Estratégico")

if tiene_datos:
    df_mapa = st.session_state.get('df_interesados', df_clean)

    # Función auxiliar para generar HTML de chips
    def get_chips_html(p_key, i_key):
        filtered = df_mapa[
            (df_mapa['PODER'].astype(str).str.upper().str.contains(p_key)) & 
            (df_mapa['INTERÉS'].astype(str).str.upper().str.contains(i_key)) & 
            (df_mapa['NOMBRE'].notna()) & (df_mapa['NOMBRE'] != "")
        ]
        
        if filtered.empty:
            return '<div style="font-size:11px; color:#aaa; font-style:italic;">Sin actores</div>'
            
        html_chips = ""
        for _, r in filtered.iterrows():
            pos = str(r['POSICIÓN'])
            nombre = r['NOMBRE']
            
            # Color del borde según posición
            border_color = "#cbd5e1" # Gris default
            icon = "⚪"
            if "Opositor" in pos: border_color = "#ef4444"; icon = "🔴" # Rojo
            elif "Cooperante" in pos: border_color = "#22c55e"; icon = "🟢" # Verde
            elif "Beneficiario" in pos: border_color = "#3b82f6"; icon = "🔵" # Azul
            elif "Perjudicado" in pos: border_color = "#a855f7"; icon = "🟣" # Morado
            
            html_chips += f"""
            <div class="actor-chip" style="border-left-color: {border_color};">
                <span>{icon}</span>
                <span>{nombre}</span>
            </div>
            """
        return html_chips

    # Construcción de la Matriz HTML (SIN SANGRÍA)
    html_matrix = f"""
<div class="matrix-container">
<div class="axis-y">PODER</div>

<div class="quadrant-box" style="background-color: #FEF2F2; grid-row: 1; grid-column: 2;">
    <div class="q-title" style="color: #991b1b;">🤝 Mantener Satisfechos</div>
    {get_chips_html("ALTO", "BAJO")}
</div>

<div class="quadrant-box" style="background-color: #F0FDF4; grid-row: 1; grid-column: 3; border: 2px solid #bbf7d0;">
    <div class="q-title" style="color: #166534;">🚀 Gestionar Atentamente</div>
    {get_chips_html("ALTO", "ALTO")}
</div>

<div class="quadrant-box" style="background-color: #FEFCE8; grid-row: 2; grid-column: 2;">
    <div class="q-title" style="color: #854d0e;">🔍 Monitorear</div>
    {get_chips_html("BAJO", "BAJO")}
</div>

<div class="quadrant-box" style="background-color: #EFF6FF; grid-row: 2; grid-column: 3;">
    <div class="q-title" style="color: #1e40af;">ℹ️ Mantener Informados</div>
    {get_chips_html("BAJO", "ALTO")}
</div>

<div class="axis-x">INTERÉS</div>
</div>
"""
    
    st.markdown(html_matrix, unsafe_allow_html=True)
    
    # Leyenda pequeña
    st.markdown("""
    <div style="margin-top: 10px; display: flex; gap: 15px; font-size: 11px; color: #666; justify-content: center;">
        <span>🔴 Opositor</span>
        <span>🟢 Cooperante</span>
        <span>🔵 Beneficiario</span>
        <span>🟣 Perjudicado</span>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Complete la matriz y guarde para visualizar el Mapa de Influencia.")

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
