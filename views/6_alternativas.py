import streamlit as st
import pandas as pd
import itertools
import os
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# 1. Carga de datos y persistencia
inicializar_session()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 150px !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    [data-testid="stImage"] img { border-radius: 12px; }
    
    /* Botones y diseño general */
    div.stButton > button:first-child {
        background-color: #1E3A8A; color: white; border: none; font-size: 15px; padding: 6px 14px; border-radius: 8px;
    }
    .ag-root-wrapper { border-radius: 8px; border: 1px solid #eee; margin-bottom: 5px !important; }
    .compact-divider { margin: 15px 0px !important; border-top: 1px solid #eee; }
    
    /* Centrado de encabezados en AgGrid */
    .ag-header-cell-label { justify-content: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- PROGRESO ---
progreso_val = 0.0
if not st.session_state['df_evaluacion_alternativas'].empty: progreso_val += 0.33
if st.session_state.get('lista_alternativas'): progreso_val += 0.33
if not st.session_state.get('df_calificaciones', pd.DataFrame()).empty:
    if st.session_state['df_calificaciones'].sum().sum() > (len(st.session_state['df_calificaciones']) * 4):
        progreso_val += 0.34
progreso_val = min(progreso_val, 1.0)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">⚖️ 6. Análisis de Alternativas</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Evaluación y selección de estrategias basadas en relevancia técnica.</div>', unsafe_allow_html=True)
    st.progress(progreso_val, text=f"Completitud: {int(progreso_val * 100)}%")
with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# ==============================================================================
# 1. EVALUACIÓN DE RELEVANCIA Y ALCANCE (AUTOMÁTICA)
# ==============================================================================
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

st.markdown("""
    <div style="display: flex; gap: 10px; margin-bottom: 12px; align-items: center; font-size: 0.85rem; color: #444;">
        <span style="background-color: #F0FDF4; border: 1px solid #BBF7D0; padding: 2px 8px; border-radius: 4px;">✅ Seleccionada</span>
        <span style="background-color: #FEF2F2; border: 1px solid #FECACA; padding: 2px 8px; border-radius: 4px;">⬜ Descartada</span>
    </div>
""", unsafe_allow_html=True)

# Sincronización de Árboles
obj_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])
datos_arbol_actual = []
for obj in obj_especificos:
    o_txt = obj["texto"] if isinstance(obj, dict) else obj
    hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == o_txt]
    for a_txt in hijas:
        datos_arbol_actual.append({"OBJETIVO": o_txt, "ACTIVIDAD": a_txt})

df_arbol_actual = pd.DataFrame(datos_arbol_actual)

if st.session_state['df_evaluacion_alternativas'].empty:
    if not df_arbol_actual.empty:
        df_sync = df_arbol_actual.copy()
        df_sync["ENFOQUE"] = False
        df_sync["ALCANCE"] = False
        st.session_state['df_evaluacion_alternativas'] = df_sync
        guardar_datos_nube()
else:
    df_old = st.session_state['df_evaluacion_alternativas']
    if not df_arbol_actual.empty:
        df_sync = pd.merge(df_arbol_actual, df_old, on=["OBJETIVO", "ACTIVIDAD"], how="left")
        df_sync["ENFOQUE"] = df_sync["ENFOQUE"].fillna(False).infer_objects(copy=False).astype(bool)
        df_sync["ALCANCE"] = df_sync["ALCANCE"].fillna(False).infer_objects(copy=False).astype(bool)
        if not df_sync.equals(df_old):
             st.session_state['df_evaluacion_alternativas'] = df_sync
             guardar_datos_nube()

# Ag-Grid Paso 1
df_work = st.session_state['df_evaluacion_alternativas'].copy()
gb = GridOptionsBuilder.from_dataframe(df_work)
gb.configure_column("OBJETIVO", headerName="🎯 Objetivo Específico", wrapText=True, autoHeight=True, width=300)
gb.configure_column("ACTIVIDAD", headerName="🛠️ Actividad", wrapText=True, autoHeight=True, width=400)
gb.configure_column("ENFOQUE", headerName="¿Enfoque?", editable=True, width=110)
gb.configure_column("ALCANCE", headerName="¿Alcance?", editable=True, width=110)

jscode_row_style = JsCode("""
function(params) {
    if (params.data.ENFOQUE === true && params.data.ALCANCE === true) {
        return { 'background-color': '#F0FDF4', 'color': '#000000' };
    } else {
        return { 'background-color': '#FEF2F2', 'color': '#000000' };
    }
};
""")
gb.configure_grid_options(getRowStyle=jscode_row_style, domLayout='autoHeight')
gridOptions = gb.build()
custom_css = {".ag-header-cell-text": {"font-size": "14px !important", "font-weight": "800 !important", "color": "#1E3A8A !important"}}

grid_response = AgGrid(
    df_work, 
    gridOptions=gridOptions, 
    custom_css=custom_css, 
    update_mode=GridUpdateMode.VALUE_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
    fit_columns_on_grid_load=True, 
    theme='streamlit', 
    allow_unsafe_jscode=True,
    key="grid_paso_1_auto"
)

df_editado_live = pd.DataFrame(grid_response['data'])
if not df_editado_live.empty and not df_editado_live.equals(st.session_state['df_evaluacion_alternativas']):
    st.session_state['df_evaluacion_alternativas'] = df_editado_live
    guardar_datos_nube(); st.rerun()

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 2. ANÁLISIS DE RELACIONES (CON AUTOLIMPIEZA)
# ==============================================================================
st.subheader("🔄 2. Análisis de Relaciones")

df_master = st.session_state['df_evaluacion_alternativas']
try:
    aprobadas = df_master[(df_master["ENFOQUE"] == True) & (df_master["ALCANCE"] == True)]
except:
    aprobadas = pd.DataFrame()

if not aprobadas.empty and "ACTIVIDAD" in aprobadas.columns:
    actividades_seleccionadas = aprobadas["ACTIVIDAD"].unique().tolist()
    
    if len(actividades_seleccionadas) >= 2:
        if 'df_relaciones_actividades' not in st.session_state:
            st.session_state['df_relaciones_actividades'] = pd.DataFrame(columns=["ACTIVIDAD A", "ACTIVIDAD B", "RELACIÓN"])
        
        df_rel_acts = st.session_state['df_relaciones_actividades'].copy()
        df_rel_acts = df_rel_acts[
            (df_rel_acts["ACTIVIDAD A"].isin(actividades_seleccionadas)) & 
            (df_rel_acts["ACTIVIDAD B"].isin(actividades_seleccionadas))
        ]
        
        pares_actuales = list(itertools.combinations(actividades_seleccionadas, 2))
        nuevas_filas = []
        for a_a, a_b in pares_actuales:
            existe = not df_rel_acts[
                ((df_rel_acts["ACTIVIDAD A"] == a_a) & (df_rel_acts["ACTIVIDAD B"] == a_b)) |
                ((df_rel_acts["ACTIVIDAD A"] == a_b) & (df_rel_acts["ACTIVIDAD B"] == a_a))
            ].empty
            if not existe:
                nuevas_filas.append({"ACTIVIDAD A": a_a, "ACTIVIDAD B": a_b, "RELACIÓN": "Complementaria"})
        
        if nuevas_filas:
            df_rel_acts = pd.concat([df_rel_acts, pd.DataFrame(nuevas_filas)], ignore_index=True)

        if not df_rel_acts.equals(st.session_state['df_relaciones_actividades']):
            st.session_state['df_relaciones_actividades'] = df_rel_acts
            guardar_datos_nube(); st.rerun()

        st.info("Defina las relaciones técnicas entre actividades.")
        cols_finales = ["ACTIVIDAD A", "ACTIVIDAD B", "RELACIÓN"]
        df_visual_rel = df_rel_acts[cols_finales].copy()

        gb_rel = GridOptionsBuilder.from_dataframe(df_visual_rel)
        gb_rel.configure_column("ACTIVIDAD A", headerName="🛠️ Actividad A", wrapText=True, autoHeight=True, width=350)
        gb_rel.configure_column("ACTIVIDAD B", headerName="🛠️ Actividad B", wrapText=True, autoHeight=True, width=350)
        gb_rel.configure_column("RELACIÓN", headerName="🔗 Relación", editable=True, 
                                cellEditor='agSelectCellEditor', 
                                cellEditorParams={'values': ["Complementaria", "Excluyente"]}, width=180)

        jscode_rel_style = JsCode("""
        function(params) {
            if (params.data.RELACIÓN === 'Excluyente') {
                return { 'background-color': '#FEF2F2', 'color': '#991b1b', 'font-weight': 'bold' };
            }
            return null;
        };
        """)
        gb_rel.configure_grid_options(getRowStyle=jscode_rel_style, domLayout='autoHeight')
        gridOptionsRel = gb_rel.build()

        grid_response_rel = AgGrid(
            df_visual_rel, 
            gridOptions=gridOptionsRel, 
            custom_css=custom_css, 
            update_mode=GridUpdateMode.VALUE_CHANGED,
            theme='streamlit', allow_unsafe_jscode=True, key="grid_relaciones_final"
        )
        
        df_rel_live = pd.DataFrame(grid_response_rel['data'])
        if not df_rel_live.empty and not df_rel_live[cols_finales].equals(st.session_state['df_relaciones_actividades'][cols_finales]):
            st.session_state['df_relaciones_actividades'] = df_rel_live[cols_finales]
            guardar_datos_nube()
                
    else:
        st.warning("⚠️ Seleccione al menos 2 actividades válidas arriba.")
else:
    st.info("Complete la selección de actividades en el Paso 1.")

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 3. CONSTRUCTOR DE ALTERNATIVAS
# ==============================================================================
st.subheader("📦 3. Constructor de Alternativas")

if not aprobadas.empty and "ACTIVIDAD" in aprobadas.columns:
    objetivos_disponibles = aprobadas["OBJETIVO"].unique().tolist()
    
    with st.container(border=True):
        c_nombre, c_desc = st.columns([1, 2])
        with c_nombre: nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Estrategia A")
        with c_desc: desc_alt = st.text_area("Descripción corta:", height=68)

        st.write("###### Seleccione las actividades:")
        actividades_elegidas = []
        for obj in objetivos_disponibles:
            acts_del_obj = aprobadas[aprobadas["OBJETIVO"] == obj]["ACTIVIDAD"].tolist()
            with st.expander(f"🎯 {obj}", expanded=True):
                for act in acts_del_obj:
                    if st.checkbox(f"{act}", key=f"sel_alt_{obj}_{act}"):
                        actividades_elegidas.append({"OBJETIVO": obj, "ACTIVIDAD": act})

        conflicto = False
        msg_conf = ""
        if len(actividades_elegidas) > 1:
            lista_actos = [item["ACTIVIDAD"] for item in actividades_elegidas]
            df_rel = st.session_state.get('df_relaciones_actividades', pd.DataFrame())
            for a1, a2 in itertools.combinations(lista_actos, 2):
                match = df_rel[((df_rel["ACTIVIDAD A"] == a1) & (df_rel["ACTIVIDAD B"] == a2)) |
                               ((df_rel["ACTIVIDAD A"] == a2) & (df_rel["ACTIVIDAD B"] == a1))]
                if not match.empty and match.iloc[0]["RELACIÓN"] == "Excluyente":
                    conflicto = True
                    msg_conf = f"❌ Error: '{a1}' y '{a2}' son EXCLUYENTES."
                    break

        if conflicto: st.error(msg_conf)
        
        if st.button("🚀 Crear Alternativa", type="primary", disabled=(conflicto or not actividades_elegidas or not nombre_alt)):
            config_final = []
            df_temp = pd.DataFrame(actividades_elegidas)
            for obj in df_temp["OBJETIVO"].unique():
                acts = df_temp[df_temp["OBJETIVO"] == obj]["ACTIVIDAD"].tolist()
                config_final.append({"objetivo": obj, "actividades": acts})
            
            st.session_state['lista_alternativas'].append({
                "nombre": nombre_alt, "descripcion": desc_alt, "configuracion": config_final
            })
            guardar_datos_nube(); st.rerun()

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 4. VISUALIZACIÓN (TARJETAS SIEMPRE VISIBLES)
# ==============================================================================
if st.session_state.get('lista_alternativas'):
    st.subheader("📋 4. Alternativas Consolidadas")
    
    colores = ["#1E3A8A", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
    
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        color_actual = colores[idx % len(colores)]
        with st.container(border=True):
            st.markdown(f"""
                <div style="background-color: {color_actual}; padding: 12px; border-radius: 6px; color: white; margin-bottom: 15px;">
                    <strong style="font-size: 1.2rem; letter-spacing: 1px;">{idx+1}. {alt['nombre'].upper()}</strong><br>
                    <span style="font-size: 0.95rem; opacity: 0.9;">📝 {alt.get('descripcion', 'Sin descripción')}</span>
                </div>
            """, unsafe_allow_html=True)
            for item in alt['configuracion']:
                st.markdown(f"**🎯 {item['objetivo'].strip()}**")
                for a in item['actividades']: st.markdown(f"&nbsp;&nbsp;🔹 {a.strip()}")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"🗑️ Eliminar Alternativa", key=f"del_alt_btn_{idx}"):
                st.session_state['lista_alternativas'].pop(idx)
                guardar_datos_nube(); st.rerun()

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 5. EVALUACIÓN MULTICRITERIO (AJUSTADO: CENTRADO Y GUÍA DINÁMICA)
# ==============================================================================
st.subheader("📊 5. Evaluación de Alternativas")

alts = st.session_state.get('lista_alternativas', [])

if not alts:
    st.info("Cree alternativas arriba para evaluar.")
else:
    # Ajuste 1: Guía dinámica de puntuación
    num_alts = len(alts)
    
    with st.expander("⚙️ Configurar Pesos (%)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        p = st.session_state.get('ponderacion_criterios', {"COSTO": 25, "FACILIDAD": 25, "BENEFICIOS": 25, "TIEMPO": 25})
        pc = c1.number_input("Costo", 0, 100, int(p['COSTO']))
        pf = c2.number_input("Facilidad", 0, 100, int(p['FACILIDAD']))
        pb = c3.number_input("Beneficios", 0, 100, int(p['BENEFICIOS']))
        pt = c4.number_input("Tiempo", 0, 100, int(p['TIEMPO']))
        if pc+pf+pb+pt == 100:
            st.session_state['ponderacion_criterios'] = {"COSTO": pc, "FACILIDAD": pf, "BENEFICIOS": pb, "TIEMPO": pt}
        else:
            st.warning(f"La suma es {pc+pf+pb+pt}%. Debe ser 100%.")

    nombres_alts = [a['nombre'] for a in alts]
    criterios = ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]
    
    if st.session_state['df_calificaciones'].empty or len(st.session_state['df_calificaciones']) != len(nombres_alts):
        st.session_state['df_calificaciones'] = pd.DataFrame(1, index=nombres_alts, columns=criterios)
    else:
        st.session_state['df_calificaciones'].index = nombres_alts
    
    df_scores_reset = st.session_state['df_calificaciones'].reset_index().rename(columns={"index": "Alternativa"})

    # Ajuste 2: Centrado de Columnas y Encabezados
    gb_score = GridOptionsBuilder.from_dataframe(df_scores_reset)
    gb_score.configure_column("Alternativa", editable=False, width=200, pinned="left")
    
    for crit in criterios:
        gb_score.configure_column(
            crit, 
            editable=True, 
            width=120, 
            type=["numericColumn"], 
            min=0, 
            max=5,
            cellStyle={'textAlign': 'center'}, # Centra el valor
            headerClass='ag-center-header'      # Clase para centrar encabezado
        )

    pesos = st.session_state['ponderacion_criterios']
    js_calc_total = JsCode(f"""
    function(params) {{
        var c = params.data.COSTO || 0;
        var f = params.data.FACILIDAD || 0;
        var b = params.data.BENEFICIOS || 0;
        var t = params.data.TIEMPO || 0;
        var total = (c * {pesos['COSTO']} + f * {pesos['FACILIDAD']} + b * {pesos['BENEFICIOS']} + t * {pesos['TIEMPO']}) / 100;
        return Number(total).toFixed(2);
    }}
    """)
    gb_score.configure_column(
        "TOTAL", 
        valueGetter=js_calc_total, 
        width=140, 
        cellStyle={'fontWeight': 'bold', 'backgroundColor': '#f0f9ff', 'textAlign': 'center'}
    )
    gb_score.configure_grid_options(domLayout='autoHeight')
    gridOptionsScore = gb_score.build()
    
    # Aplicación de la guía dinámica en el título
    st.markdown(f"##### 🏆 Matriz de Decisión (Puntuar de 1 a {num_alts})")
    grid_response_score = AgGrid(df_scores_reset, gridOptions=gridOptionsScore, custom_css=custom_css, update_mode=GridUpdateMode.VALUE_CHANGED, theme='streamlit', allow_unsafe_jscode=True, key="grid_eval_final")

    df_res = pd.DataFrame(grid_response_score['data'])
    if not df_res.empty and "Alternativa" in df_res.columns:
        df_save = df_res.set_index("Alternativa")[criterios].astype(float)
        st.session_state['df_calificaciones'] = df_save
        res_ranking = []
        for alt_n in df_save.index:
            p_final = 0
            for crit in criterios: p_final += df_save.loc[alt_n, crit] * (pesos[crit]/100)
            res_ranking.append({"Alternativa": alt_n, "PUNTAJE": p_final})
        df_ranking = pd.DataFrame(res_ranking).sort_values("PUNTAJE", ascending=False)
        
        if not df_ranking.empty:
            ganadora = df_ranking.iloc[0]
            # Ajuste 3: Cambio de etiqueta "Alternativa Seleccionada"
            st.success(f"🎉 **Alternativa Seleccionada:** {ganadora['Alternativa']} ({ganadora['PUNTAJE']:.2f} pts)")
            st.dataframe(df_ranking, column_config={"PUNTAJE": st.column_config.ProgressColumn("Puntaje", format="%.2f", min_value=0, max_value=5)}, use_container_width=True, hide_index=True)

st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
