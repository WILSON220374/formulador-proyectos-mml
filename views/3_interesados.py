import streamlit as st
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
    /* Headers */
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Botones */
    div.stButton > button:first-child {
        background-color: #1E3A8A; color: white; border: none; font-size: 20px; padding: 5px 15px; border-radius: 8px;
    }
    div.stButton > button:hover { background-color: #153075; color: white; }
    
    /* Botones de Acción */
    .stButton button { width: 100%; }
    
    /* MATRIZ Y CUADRANTES */
    .matrix-container {
        display: grid;
        grid-template-columns: 40px 1fr 1fr;
        grid-template-rows: 1fr 1fr 40px;
        gap: 15px;
        font-family: sans-serif;
    }
    .axis-y {
        grid-row: 1 / 3; grid-column: 1; writing-mode: vertical-rl; transform: rotate(180deg);
        text-align: center; font-weight: 900; color: #94a3b8; letter-spacing: 2px; font-size: 14px;
        border-right: 2px solid #e2e8f0; padding-left: 10px;
    }
    .axis-x {
        grid-row: 3; grid-column: 2 / 4; text-align: center; font-weight: 900; color: #94a3b8;
        letter-spacing: 2px; font-size: 14px; border-top: 2px solid #e2e8f0; padding-top: 10px;
    }
    .quadrant-box {
        border-radius: 12px; padding: 15px;
        display: flex; flex-direction: column; gap: 4px; 
        height: 100%; min-height: 220px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.02); 
    }
    .q-title {
        font-size: 12px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; opacity: 0.9;
    }
    .actor-item {
        font-size: 13px; color: #334155; display: flex; align-items: center; gap: 8px;
        padding: 2px 0; border-bottom: 1px solid rgba(0,0,0,0.05); 
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

# --- PREPARACIÓN DE DATOS (FILA AUTOMÁTICA) ---
columnas_validas = [
    "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", 
    "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA", "BORRAR"
]

if df_actual.empty: 
    df_clean = pd.DataFrame(columns=columnas_validas)
else:
    for col in columnas_validas:
        if col not in df_actual.columns:
            df_actual[col] = False if col == "BORRAR" else ""
    df_clean = df_actual[columnas_validas].copy().reset_index(drop=True)

# Lógica de Fila Fantasma: Agrega una vacía si la última tiene datos
if df_clean.empty or (df_clean.iloc[-1]["NOMBRE"] and str(df_clean.iloc[-1]["NOMBRE"]).strip() != ""):
    nueva_fila = pd.DataFrame([{col: (False if col == "BORRAR" else "") for col in columnas_validas}])
    df_clean = pd.concat([df_clean, nueva_fila], ignore_index=True)

opciones_pos = ["🔴 Opositor", "🟢 Cooperante", "🔵 Beneficiario", "🟣 Perjudicado"]
opciones_niv = ["⚡ ALTO", "🔅 BAJO"]

# --- TABLA REACTIVA (EDICIÓN ESTILO EXCEL) ---
gb = GridOptionsBuilder.from_dataframe(df_clean)

# Columna para borrar marcando un check
gb.configure_column("BORRAR", headerName="🗑️", editable=True, 
                    cellRenderer=JsCode('function(params) { return params.value ? "✅" : "⬜"; }'), 
                    width=70)

gb.configure_column("NOMBRE", headerName="👤 Nombre", width=180, editable=True, wrapText=True, autoHeight=True)
gb.configure_column("GRUPO", headerName="🏢 Grupo", width=120, editable=True, wrapText=True, autoHeight=True)
gb.configure_column("POSICIÓN", headerName="🚩 Posición", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_pos}, width=140)
gb.configure_column("EXPECTATIVA", headerName="🎯 Expectativa", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("CONTRIBUCION AL PROYECTO", headerName="💡 Contribución", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("PODER", headerName="⚡ Poder", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)
gb.configure_column("INTERÉS", headerName="👁️ Interés", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)

# Lógica de Estrategia y Colores (Mantenemos tu lógica original)
js_calc_strategy = JsCode("""
function(params) {
    if (!params.data.PODER || !params.data.INTERÉS) return "";
    var p = params.data.PODER.replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();
    var i = params.data.INTERÉS.replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();
    if (p === 'ALTO' && i === 'BAJO') return 'INVOLUCRAR - MANTENER SATISFECHOS';
    if (p === 'ALTO' && i === 'ALTO') return 'INVOLUCRAR Y ATRAER EFECTIVAMENTE';
    if (p === 'BAJO' && i === 'ALTO') return 'MANTENER INFORMADOS';
    if (p === 'BAJO' && i === 'BAJO') return 'MONITOREAR';
    return "";
}
""")
gb.configure_column("ESTRATEGIA", headerName="🚀 Estrategia", valueGetter=js_calc_strategy, width=200)

jscode_row_style = JsCode("""
function(params) {
    var p = (params.data.PODER || "").replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();
    var i = (params.data.INTERÉS || "").replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();
    if (p === 'ALTO' && i === 'BAJO') return { 'background-color': '#FEF2F2' };
    if (p === 'ALTO' && i === 'ALTO') return { 'background-color': '#F0FDF4' };
    if (p === 'BAJO' && i === 'ALTO') return { 'background-color': '#EFF6FF' };
    if (p === 'BAJO' && i === 'BAJO') return { 'background-color': '#FEFCE8' };
    return null;
};
""")

gb.configure_grid_options(getRowStyle=jscode_row_style, domLayout='autoHeight', stopEditingWhenCellsLoseFocus=True)
gridOptions = gb.build()

st.subheader("📝 Matriz de Interesados")
grid_response = AgGrid(
    df_clean, gridOptions=gridOptions,
    update_mode=GridUpdateMode.VALUE_CHANGED, # Actualización en vivo
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True, theme='streamlit', allow_unsafe_jscode=True
)

# --- PROCESAMIENTO Y GUARDADO AUTOMÁTICO ---
df_editado = pd.DataFrame(grid_response['data'])
if "BORRAR" in df_editado.columns:
    # Quitamos las filas que marcaste para borrar
    df_final = df_editado[df_editado["BORRAR"] != True].drop(columns=["BORRAR"])
    
    # Solo guardamos si realmente cambió algo para no saturar la red
    if not df_final.equals(df_actual[columnas_validas[:-1]] if not df_actual.empty else None):
        st.session_state['df_interesados'] = df_final
        guardar_datos_nube()
        # Nota: quitamos el rerun aquí para permitir escritura fluida
# --- MAPA DE INFLUENCIA (ACTUALIZACIÓN EN VIVO) ---
st.subheader("📊 Mapa de Influencia Estratégico")


# Usamos los datos directos de la tabla para que el mapa se mueva mientras escribes
df_mapa = pd.DataFrame(grid_response['data'])

if not df_mapa.empty and df_mapa['NOMBRE'].dropna().any():
    def get_list_items_html(p_key, i_key):
        filtered = df_mapa[
            (df_mapa['PODER'].astype(str).str.upper().str.contains(p_key)) & 
            (df_mapa['INTERÉS'].astype(str).str.upper().str.contains(i_key)) & 
            (df_mapa['NOMBRE'].notna()) & (df_mapa['NOMBRE'] != "")
        ]
        if filtered.empty: return '<div style="font-size:11px; color:#aaa; font-style:italic;">Sin actores</div>'
        html_items = ""
        for _, r in filtered.iterrows():
            pos = str(r['POSICIÓN'])
            icon = "⚪"
            if "Opositor" in pos: icon = "🔴"
            elif "Cooperante" in pos: icon = "🟢"
            elif "Beneficiario" in pos: icon = "🔵"
            elif "Perjudicado" in pos: icon = "🟣"
            html_items += f'<div class="actor-item"><span>{icon}</span> <span>{r["NOMBRE"]}</span></div>'
        return html_items

    html_matrix = f"""
<div class="matrix-container">
    <div class="axis-y">PODER</div>
    <div class="quadrant-box" style="background-color: #FEF2F2; grid-row: 1; grid-column: 2; border-top: 4px solid #fecaca;">
        <div class="q-title" style="color: #991b1b;">🤝 Mantener Satisfechos</div>
        {get_list_items_html("ALTO", "BAJO")}
    </div>
    <div class="quadrant-box" style="background-color: #F0FDF4; grid-row: 1; grid-column: 3; border-top: 4px solid #86efac;">
        <div class="q-title" style="color: #166534;">🚀 Involucrar y Atraer Efectivamente</div>
        {get_list_items_html("ALTO", "ALTO")}
    </div>
    <div class="quadrant-box" style="background-color: #FEFCE8; grid-row: 2; grid-column: 2; border-top: 4px solid #fde047;">
        <div class="q-title" style="color: #854d0e;">🔍 Monitorear</div>
        {get_list_items_html("BAJO", "BAJO")}
    </div>
    <div class="quadrant-box" style="background-color: #EFF6FF; grid-row: 2; grid-column: 3; border-top: 4px solid #bfdbfe;">
        <div class="q-title" style="color: #1e40af;">ℹ️ Mantener Informados</div>
        {get_list_items_html("BAJO", "ALTO")}
    </div>
    <div class="axis-x">INTERÉS</div>
</div>
"""
    st.markdown(html_matrix, unsafe_allow_html=True)
else:
    st.info("Empieza a escribir en la tabla para ver el mapa de influencia en tiempo real.")
    
# --- ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")
num_lineas = analisis_txt.count('\n') + 1
altura_dinamica = max(150, num_lineas * 25 + 50)

analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, height=altura_dinamica,
    key="txt_analisis_final_panel", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True) 

if analisis_actual != analisis_txt:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
