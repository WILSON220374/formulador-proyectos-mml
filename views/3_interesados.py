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
    .titulo-seccion { font-size: 32px !important; font-weight: 800 !important; color: #4F8BFF; margin-bottom: 5px; line-height: 1.2; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 10px; }
    
    /* Estilo para los cuadros de texto de análisis */
    .stTextArea textarea {
        background-color: #fcfdfe;
        border: 1px solid #e0e7ff;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #4F8BFF;
        box-shadow: 0 0 0 2px rgba(79, 139, 255, 0.1);
    }

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
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- PREPARACIÓN DE DATOS ---
columnas_validas = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA"]

if df_actual.empty: 
    df_clean = pd.DataFrame(columns=columnas_validas)
else:
    for col in columnas_validas:
        if col not in df_actual.columns: df_actual[col] = ""
    df_clean = df_actual[columnas_validas].copy().reset_index(drop=True)

opciones_pos = ["🔴 Opositor", "🟢 Cooperante", "🔵 Beneficiario", "🟣 Perjudicado"]
opciones_niv = ["⚡ ALTO", "🔅 BAJO"]

# --- FUNCIÓN DE ALTURA AJUSTADA ---
def calcular_altura(texto, min_h=100):
    if not texto: return min_h
    texto_str = str(texto)
    lineas = texto_str.count('\n') + (len(texto_str) // 120)
    return max(min_h, (lineas + 1) * 24)

# --- CONTROLES (UNIFICADOS DEBAJO) ---
# Usamos una sola fila para botones de acción rápida
c_add, c_del, c_save, c_space = st.columns([1.2, 1, 1.2, 3])

# --- CONFIGURACIÓN DE TABLA AG-GRID ---
gb = GridOptionsBuilder.from_dataframe(df_clean)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_column("NOMBRE", headerName="👤 Nombre", width=180, editable=True)
gb.configure_column("GRUPO", headerName="🏢 Grupo", width=120, editable=True)
gb.configure_column("POSICIÓN", headerName="🚩 Posición", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_pos}, width=140)
gb.configure_column("EXPECTATIVA", headerName="🎯 Expectativa", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("CONTRIBUCION AL PROYECTO", headerName="💡 Contribución", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("PODER", headerName="⚡ Poder", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)
gb.configure_column("INTERÉS", headerName="👁️ Interés", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)

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
gb.configure_grid_options(domLayout='autoHeight')
gridOptions = gb.build()

st.subheader("📝 Matriz de Interesados")
grid_response = AgGrid(
    df_clean, gridOptions=gridOptions, 
    update_mode=GridUpdateMode.VALUE_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True, theme='streamlit', allow_unsafe_jscode=True
)

# --- LÓGICA DE BOTONES ---
with c_add:
    if st.button("➕ Agregar Actor"):
        # Intentamos capturar lo que hay en el grid antes de resetear
        df_temp = pd.DataFrame(grid_response['data'])
        new_row = pd.DataFrame([{col: "" for col in columnas_validas}])
        st.session_state['df_interesados'] = pd.concat([df_temp, new_row], ignore_index=True)
        guardar_datos_nube()
        st.rerun()

with c_del:
    if st.button("🗑️ Eliminar"):
        sel_rows = grid_response['selected_rows']
        if sel_rows is not None and len(sel_rows) > 0:
            df_sel = pd.DataFrame(sel_rows)
            df_nuevo = df_clean.merge(df_sel, how='left', indicator=True)
            df_nuevo = df_nuevo[df_nuevo['_merge'] == 'left_only'].drop(columns=['_merge'])
            st.session_state['df_interesados'] = df_nuevo
            guardar_datos_nube()
            st.rerun()

with c_save:
    if st.button("💾 Guardar"):
        st.session_state['df_interesados'] = pd.DataFrame(grid_response['data'])
        guardar_datos_nube()
        st.success("¡Datos guardados!")
        st.rerun()

st.write("")
st.divider()

# --- MAPA DE INFLUENCIA ---
st.subheader("📊 Mapa de Influencia Estratégico")

if tiene_datos:
    df_mapa = st.session_state.get('df_interesados', df_clean)
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

    st.markdown(f"""
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
""", unsafe_allow_html=True)
else:
    st.info("Complete la matriz para visualizar el Mapa de Influencia.")

st.write("")
st.divider()

# --- ANÁLISIS FINAL (SECCIÓN ÚNICA ABAJO) ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, 
    height=calcular_altura(analisis_txt, min_h=150),
    key="txt_analisis_final", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)

# --- AJUSTE VISUAL: MARGEN INFERIOR ---
st.markdown("<div style='margin-bottom: 80px;'></div>", unsafe_allow_html=True)

if analisis_actual != analisis_txt:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
