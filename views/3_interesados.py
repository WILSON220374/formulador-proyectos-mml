import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# --- FUNCIÓN DE ALTURA DINÁMICA ---
def calc_altura_textarea(texto, min_h=150, max_h=600, chars_por_linea=110):
    if not texto: return min_h
    lineas = 0
    for ln in str(texto).splitlines() or [""]:
        lineas += max(1, (len(ln) // chars_por_linea) + 1)
    
    altura = (lineas * 24) + 60
    return min(max_h, max(min_h, altura))
    
# 1. Inicialización
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS ---
st.markdown("""
  <style>
    /* 1. FUERZA EL SCROLL AL FINAL (Ajustado para eliminar espacios gigantes) */
    .main .block-container {
        padding-bottom: 10rem !important; /* Espacio base reducido */
    }
    
    /* Ataca el último bloque vertical para que no empuje tanto el fondo */
    [data-testid="stVerticalBlock"] > div:last-child {
        margin-bottom: 2rem !important; /* Reducido para acercar el contenido */
    }

    /* Asegura que el contenedor principal permita el desbordamiento */
    .stApp {
        overflow-y: auto;
    }

    /* 2. TÍTULOS Y SUBTÍTULOS */
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    /* 3. CAMPOS DE TEXTO (TEXTAREAS) */
    textarea { resize: none !important; }
    .stTextArea textarea {
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
    }
    /* 4. BOTONES INSTITUCIONALES */
    div.stButton > button:first-child {
        background-color: #1E3A8A; 
        color: white; 
        border: none; 
        font-size: 20px; 
        padding: 5px 15px; 
        border-radius: 8px;
        width: 100%;
    }
    div.stButton > button:hover { 
        background-color: #153075; 
        color: white; 
    }

    /* 5. MATRIZ Y CUADRANTES */
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

# --- CONTROLES (AGREGAR / BORRAR) ---
c_add, c_del, c_space = st.columns([1, 1, 4])

with c_add:
    if st.button("➕ Agregar Actor"):
        new_row = pd.DataFrame([{col: "" for col in columnas_validas}])
        st.session_state['df_interesados'] = pd.concat([df_clean, new_row], ignore_index=True)
        guardar_datos_nube()
        st.rerun()

# --- TABLA AG-GRID CON CÁLCULO EN VIVO ---
gb = GridOptionsBuilder.from_dataframe(df_clean)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)

# Columnas Básicas
gb.configure_column("NOMBRE", headerName="👤 Nombre", width=180, editable=True, wrapText=True, autoHeight=True)
gb.configure_column("GRUPO", headerName="🏢 Grupo", width=120, editable=True, wrapText=True, autoHeight=True)
gb.configure_column("POSICIÓN", headerName="🚩 Posición", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_pos}, width=140)
gb.configure_column("EXPECTATIVA", headerName="🎯 Expectativa", editable=True, wrapText=True, autoHeight=True, width=250)
gb.configure_column("CONTRIBUCION AL PROYECTO", headerName="💡 Contribución", editable=True, wrapText=True, autoHeight=True, width=250)

# Niveles (Poder e Interés)
gb.configure_column("PODER", headerName="⚡ Poder", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)
gb.configure_column("INTERÉS", headerName="👁️ Interés", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': opciones_niv}, width=110)

# --- FÓRMULA JS PARA ESTRATEGIA EN VIVO ---
js_calc_strategy = JsCode("""
function(params) {
    if (!params.data.PODER || !params.data.INTERÉS) return "";
    
    // Limpiamos los emojis para comparar texto puro
    var p = params.data.PODER.replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();
    var i = params.data.INTERÉS.replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();

    if (p === 'ALTO' && i === 'BAJO') return 'INVOLUCRAR - MANTENER SATISFECHOS';
    if (p === 'ALTO' && i === 'ALTO') return 'INVOLUCRAR Y ATRAER EFECTIVAMENTE';
    if (p === 'BAJO' && i === 'ALTO') return 'MANTENER INFORMADOS';
    if (p === 'BAJO' && i === 'BAJO') return 'MONITOREAR';
    return "";
}
""")

# Aplicamos la fórmula con valueGetter
gb.configure_column("ESTRATEGIA", headerName="🚀 Estrategia", 
                    valueGetter=js_calc_strategy, 
                    editable=False, wrapText=True, autoHeight=True, width=200)

# --- COLORES EN VIVO (Usan el valor calculado por JS) ---
jscode_row_style = JsCode("""
function(params) {
    // Como usamos valueGetter, params.data.ESTRATEGIA puede no estar actualizado en el objeto data crudo,
    // pero podemos recalcularlo o confiar en que AgGrid pasa el valor visualizado.
    // Para asegurar, repetimos la logica o leemos el valor.
    
    var p = (params.data.PODER || "").replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();
    var i = (params.data.INTERÉS || "").replace("⚡ ", "").replace("🔅 ", "").trim().toUpperCase();
    
    if (p === 'ALTO' && i === 'BAJO') return { 'background-color': '#FEF2F2', 'color': 'black' }; // Rojo
    if (p === 'ALTO' && i === 'ALTO') return { 'background-color': '#F0FDF4', 'color': 'black' }; // Verde
    if (p === 'BAJO' && i === 'ALTO') return { 'background-color': '#EFF6FF', 'color': 'black' }; // Azul
    if (p === 'BAJO' && i === 'BAJO') return { 'background-color': '#FEFCE8', 'color': 'black' }; // Amarillo
    
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
    update_mode=GridUpdateMode.VALUE_CHANGED, # Actualiza más rápido
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True, theme='streamlit', allow_unsafe_jscode=True
)

# --- ELIMINAR (Blindado) ---
with c_del:
    if st.button("🗑️ Eliminar"):
        sel_rows = grid_response['selected_rows']
        if sel_rows is not None and len(sel_rows) > 0:
            if isinstance(sel_rows, pd.DataFrame): df_sel = sel_rows
            else: df_sel = pd.DataFrame(sel_rows)
            
            cols_comunes = [c for c in df_clean.columns if c in df_sel.columns]
            if cols_comunes:
                df_merged = df_clean.merge(df_sel[cols_comunes], on=cols_comunes, how='left', indicator=True)
                df_nuevo = df_merged[df_merged['_merge'] == 'left_only'].drop(columns=['_merge'])
                st.session_state['df_interesados'] = df_nuevo
                guardar_datos_nube()
                st.rerun()

col_btn, col_rest = st.columns([1, 10])
with col_btn:
    btn_guardar = st.button("💾 Guardar Cambios", help="Guardar permanentemente")

# Función Python (Respaldo para el guardado)
def calcular_estrategia_py(row):
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
        # Recalculamos en Python para asegurar que se guarde bien en la base de datos
        # (aunque JS lo muestre, necesitamos el dato real en Python)
        df_editado["ESTRATEGIA"] = df_editado.apply(calcular_estrategia_py, axis=1)
        st.session_state['df_interesados'] = df_editado
        guardar_datos_nube()
        st.rerun()

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
            nombre = r['NOMBRE']
            icon = "⚪"
            if "Opositor" in pos: icon = "🔴"
            elif "Cooperante" in pos: icon = "🟢"
            elif "Beneficiario" in pos: icon = "🔵"
            elif "Perjudicado" in pos: icon = "🟣"
            html_items += f'<div class="actor-item"><span>{icon}</span> <span>{nombre}</span></div>'
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
    st.markdown("""
    <div style="margin-top: 10px; display: flex; gap: 15px; font-size: 11px; color: #666; justify-content: center;">
        <span>🔴 Opositor</span><span>🟢 Cooperante</span><span>🔵 Beneficiario</span><span>🟣 Perjudicado</span>
    </div>""", unsafe_allow_html=True)
else:
    st.info("Complete la matriz y guarde para visualizar el Mapa de Influencia.")

st.divider()

# --- ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")

# Calculamos la altura según el contenido real
altura_dinamica = calc_altura_textarea(analisis_txt)

analisis_actual = st.text_area(
    "Analisis", 
    value=analisis_txt, 
    height=altura_dinamica, # <--- Altura automática aplicada aquí
    key="txt_analisis_final_panel", 
    label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True) 

if analisis_actual != analisis_txt:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
