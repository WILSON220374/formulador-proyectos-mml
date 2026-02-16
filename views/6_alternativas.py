import streamlit as st
import pandas as pd
import itertools
import os
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# 1. Carga de datos y persistencia
inicializar_session()

# --- ESTILOS CSS (DISEÑO UNIFICADO Y COMPACTO) ---
st.markdown("""
    <style>
    /* Colchón inferior para que no se corte el final */
    .block-container { padding-bottom: 150px !important; }

    /* Estilos del Encabezado */
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

    /* Estilo para botones principales */
    div.stButton > button:first-child {
        background-color: #1E3A8A;
        color: white;
        border: none;
        font-size: 16px;
        padding: 8px 16px;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #153075;
        color: white;
    }
    
    /* --- AJUSTE CLAVE: REDUCIR ESPACIO ENTRE TABLA Y BOTÓN --- */
    
    /* 1. Quitamos margen abajo a la tabla AgGrid */
    .ag-root-wrapper { 
        border-radius: 8px; 
        border: 1px solid #eee; 
        margin-bottom: 0px !important; 
    }
    
    /* 2. Subimos los botones con margen negativo para pegarlos al elemento anterior */
    div.stButton { 
        margin-top: -20px !important; 
        margin-bottom: 0px !important; 
    }
    
    .compact-divider { margin: 10px 0px !important; border-top: 1px solid #eee; }
    </style>
""", unsafe_allow_html=True)

# --- CÁLCULO DEL PROGRESO ---
progreso_val = 0.0
if not st.session_state['df_evaluacion_alternativas'].empty:
    progreso_val += 0.33
if st.session_state.get('lista_alternativas'):
    progreso_val += 0.33
if not st.session_state.get('df_calificaciones', pd.DataFrame()).empty:
    if st.session_state['df_calificaciones'].sum().sum() > (len(st.session_state['df_calificaciones']) * 4):
        progreso_val += 0.34
progreso_val = min(progreso_val, 1.0)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown('<div class="titulo-seccion">⚖️ 6. Análisis de Alternativas</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Evaluación, comparación y selección de las mejores estrategias.</div>', unsafe_allow_html=True)
    st.caption(f"Nivel de Completitud: {int(progreso_val * 100)}%")
    st.progress(progreso_val)

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 1. EVALUACIÓN DE RELEVANCIA Y ALCANCE (Ag-Grid Auto-Height)
# ==============================================================================
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

# Leyenda compacta
st.markdown("""
    <div style="display: flex; gap: 10px; margin-bottom: 5px; align-items: center; font-size: 0.85rem; color: #444;">
        <span style="background-color: #F0FDF4; border: 1px solid #BBF7D0; padding: 2px 8px; border-radius: 4px;">✅ Seleccionada</span>
        <span style="background-color: #FEF2F2; border: 1px solid #FECACA; padding: 2px 8px; border-radius: 4px;">⬜ Descartada</span>
    </div>
""", unsafe_allow_html=True)

# Sincronización de datos
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
        
        if len(df_sync) != len(df_old) or not df_sync["OBJETIVO"].equals(df_old["OBJETIVO"]):
             st.session_state['df_evaluacion_alternativas'] = df_sync
             guardar_datos_nube()
             st.rerun()

# --- AG-GRID CONFIG ---
df_work = st.session_state['df_evaluacion_alternativas'].copy()

gb = GridOptionsBuilder.from_dataframe(df_work)
# Columnas de texto con AJUSTE AUTOMÁTICO (Wrap Text)
gb.configure_column("OBJETIVO", headerName="🎯 Objetivo Específico", wrapText=True, autoHeight=True, width=300)
gb.configure_column("ACTIVIDAD", headerName="🛠️ Actividad", wrapText=True, autoHeight=True, width=400)
gb.configure_column("ENFOQUE", headerName="¿Enfoque?", editable=True, width=110)
gb.configure_column("ALCANCE", headerName="¿Alcance?", editable=True, width=110)

# Colores condicionales
jscode_row_style = JsCode("""
function(params) {
    if (params.data.ENFOQUE === true && params.data.ALCANCE === true) {
        return { 'background-color': '#F0FDF4', 'color': '#000000' };
    } else {
        return { 'background-color': '#FEF2F2', 'color': '#000000' };
    }
};
""")
# domLayout='autoHeight' CLAVE PARA ELIMINAR ESPACIO
gb.configure_grid_options(getRowStyle=jscode_row_style, domLayout='autoHeight')
gridOptions = gb.build()

custom_css = {
    ".ag-header-cell-text": {"font-size": "14px !important", "font-weight": "800 !important", "color": "#1E3A8A !important"},
    ".ag-header": {"background-color": "#f8f9fa !important"}
}

grid_response = AgGrid(
    df_work,
    gridOptions=gridOptions,
    custom_css=custom_css,
    update_mode=GridUpdateMode.MANUAL,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    theme='streamlit',
    allow_unsafe_jscode=True
)

if st.button("💾 Guardar Selección"):
    df_editado = pd.DataFrame(grid_response['data'])
    if not df_editado.empty:
        df_editado["ENFOQUE"] = df_editado["ENFOQUE"].astype(bool)
        df_editado["ALCANCE"] = df_editado["ALCANCE"].astype(bool)
        st.session_state['df_evaluacion_alternativas'] = df_editado
        guardar_datos_nube()
        st.rerun()

# Espacio manual mínimo en lugar de Divider grande
st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 2. ANÁLISIS DE RELACIONES
# ==============================================================================
st.subheader("🔄 2. Análisis de Relaciones")

df_master = st.session_state['df_evaluacion_alternativas']
try:
    aprobadas = df_master[(df_master["ENFOQUE"] == True) & (df_master["ALCANCE"] == True)]
except:
    aprobadas = pd.DataFrame()

if not aprobadas.empty:
    objetivos_seleccionados = aprobadas["OBJETIVO"].unique().tolist()
    if len(objetivos_seleccionados) >= 2:
        pares_actuales = list(itertools.combinations(objetivos_seleccionados, 2))
        df_existente = st.session_state['df_relaciones_objetivos']
        
        nuevas_filas = []
        for o_a, o_b in pares_actuales:
            existe = False
            if not df_existente.empty:
                existe = not df_existente[((df_existente["OBJETIVO A"] == o_a) & (df_existente["OBJETIVO B"] == o_b)) |
                                          ((df_existente["OBJETIVO A"] == o_b) & (df_existente["OBJETIVO B"] == o_a))].empty
            if not existe:
                nuevas_filas.append({"OBJETIVO A": o_a, "OBJETIVO B": o_b, "RELACIÓN": "Por definir"})

        if nuevas_filas:
            st.session_state['df_relaciones_objetivos'] = pd.concat([df_existente, pd.DataFrame(nuevas_filas)], ignore_index=True)
            guardar_datos_nube()

        st.info("Defina la relación entre objetivos seleccionados.")
        df_rel_editado = st.data_editor(
            st.session_state['df_relaciones_objetivos'],
            column_config={
                "OBJETIVO A": st.column_config.TextColumn("Objetivo A", disabled=True),
                "OBJETIVO B": st.column_config.TextColumn("Objetivo B", disabled=True),
                "RELACIÓN": st.column_config.SelectboxColumn("Relación", options=["Por definir", "Complementario", "Excluyente"], required=True)
            },
            hide_index=True, use_container_width=True, key="tabla_rel_v9"
        )
        if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
            st.session_state['df_relaciones_objetivos'] = df_rel_editado
            guardar_datos_nube(); st.rerun()
    else:
        st.warning("Seleccione al menos 2 objetivos válidos arriba.")
else:
    st.info("No hay actividades seleccionadas arriba.")

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 3. CONSTRUCTOR DE ALTERNATIVAS
# ==============================================================================
st.subheader("📦 3. Constructor de Alternativas")

if not aprobadas.empty and objetivos_seleccionados:
    with st.container(border=True):
        c_nombre, c_desc = st.columns([1, 2])
        with c_nombre: nombre_alt = st.text_input("Nombre Alternativa:")
        with c_desc: desc_alt = st.text_area("Descripción:", height=68)

        st.write("###### Seleccionar Objetivos:")
        objs_en_paquete = []
        cols_obj = st.columns(2)
        for i, obj_opcion in enumerate(objetivos_seleccionados):
            with cols_obj[i % 2]:
                if st.checkbox(f"🎯 {obj_opcion}", key=f"paq_obj_{i}"):
                    objs_en_paquete.append(obj_opcion)

        # Validación
        conflicto = False
        msg_conflicto = ""
        if len(objs_en_paquete) > 1:
            for o_a, o_b in itertools.combinations(objs_en_paquete, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_a))
                ]
                if not rel.empty and rel.iloc[0]["RELACIÓN"] == "Excluyente":
                    conflicto = True
                    msg_conflicto = f"❌ Conflicto: '{o_a}' y '{o_b}' son EXCLUYENTES."

        if conflicto: st.error(msg_conflicto)
        
        config_final = []
        if objs_en_paquete and not conflicto:
            st.write("###### Seleccionar Actividades:")
            for obj_p in objs_en_paquete:
                with st.expander(f"📌 {obj_p}", expanded=False):
                    acts_aprob = aprobadas[aprobadas["OBJETIVO"] == obj_p]["ACTIVIDAD"].tolist()
                    sel_del_obj = []
                    for act in acts_aprob:
                        if st.checkbox(act, value=True, key=f"paq_act_{obj_p}_{act}"):
                            sel_del_obj.append(act)
                    if sel_del_obj:
                        config_final.append({"objetivo": obj_p, "actividades": sel_del_obj})

        if st.button("🚀 Crear Alternativa", type="primary", disabled=(conflicto or not config_final or not nombre_alt)):
            st.session_state['lista_alternativas'].append({
                "nombre": nombre_alt, "descripcion": desc_alt, "configuracion": config_final
            })
            guardar_datos_nube(); st.rerun()

# ==============================================================================
# 4. VISUALIZACIÓN
# ==============================================================================
if st.session_state.get('lista_alternativas'):
    st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)
    st.subheader("📋 4. Alternativas Consolidadas")
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        with st.expander(f"**{idx+1}. {alt['nombre'].upper()}**"):
            st.caption(alt.get('descripcion', ''))
            for item in alt['configuracion']:
                st.markdown(f"**🎯 {item['objetivo']}**")
                for a in item['actividades']: st.markdown(f"&nbsp;&nbsp;🔹 {a}")
            if st.button(f"🗑️ Borrar", key=f"del_{idx}"):
                st.session_state['lista_alternativas'].pop(idx)
                guardar_datos_nube(); st.rerun()

st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)

# ==============================================================================
# 5. EVALUACIÓN MULTICRITERIO (REAL-TIME AG-GRID)
# ==============================================================================
st.subheader("📊 5. Evaluación de Alternativas")

alts = st.session_state.get('lista_alternativas', [])

if not alts:
    st.info("👆 Cree alternativas arriba para evaluar.")
else:
    # 1. Pesos
    with st.expander("⚙️ Configurar Pesos (%)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        p = st.session_state.get('ponderacion_criterios', {"COSTO": 25.0, "FACILIDAD": 25.0, "BENEFICIOS": 25.0, "TIEMPO": 25.0})
        pc = c1.number_input("Costo", 0, 100, int(p['COSTO']))
        pf = c2.number_input("Facilidad", 0, 100, int(p['FACILIDAD']))
        pb = c3.number_input("Beneficios", 0, 100, int(p['BENEFICIOS']))
        pt = c4.number_input("Tiempo", 0, 100, int(p['TIEMPO']))
        
        if pc+pf+pb+pt == 100:
            st.session_state['ponderacion_criterios'] = {"COSTO": pc, "FACILIDAD": pf, "BENEFICIOS": pb, "TIEMPO": pt}
        else:
            st.warning(f"Suma: {pc+pf+pb+pt}%. Debe ser 100%.")

    # 2. Preparar Datos para AgGrid
    nombres_alts = [a['nombre'] for a in alts]
    criterios = ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]
    
    if st.session_state['df_calificaciones'].empty or len(st.session_state['df_calificaciones']) != len(nombres_alts):
        st.session_state['df_calificaciones'] = pd.DataFrame(1, index=nombres_alts, columns=criterios)
    else:
        st.session_state['df_calificaciones'].index = nombres_alts
    
    # Reset index para tener 'Alternativa' como columna en AgGrid
    df_scores_reset = st.session_state['df_calificaciones'].reset_index().rename(columns={"index": "Alternativa"})

    # 3. Configurar AgGrid con Fórmula JS para Total
    gb_score = GridOptionsBuilder.from_dataframe(df_scores_reset)
    
    gb_score.configure_column("Alternativa", editable=False, width=200, pinned="left")
    for crit in criterios:
        gb_score.configure_column(crit, editable=True, width=120, type=["numericColumn", "numberColumnFilter"], min=0, max=5)

    # Inyección de Pesos en JS
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
    
    gb_score.configure_column("TOTAL", valueGetter=js_calc_total, width=140, cellStyle={'fontWeight': 'bold', 'backgroundColor': '#f0f9ff'})
    
    gb_score.configure_grid_options(domLayout='autoHeight')
    gridOptionsScore = gb_score.build()
    
    st.markdown("##### 🏆 Matriz de Decisión (1-5)")
    st.caption("Edite los valores. El total se actualiza automáticamente.")
    
    grid_response_score = AgGrid(
        df_scores_reset,
        gridOptions=gridOptionsScore,
        custom_css=custom_css,
        update_mode=GridUpdateMode.VALUE_CHANGED, # <--- ESTO ACTUALIZA LA APP AL CAMBIAR UN DATO
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
        theme='streamlit',
        allow_unsafe_jscode=True,
        key="grid_scores_realtime"
    )

    # 4. Procesar Resultados (Actualización Inmediata)
    df_res = pd.DataFrame(grid_response_score['data'])
    
    # Recuperamos el índice para guardar
    if not df_res.empty and "Alternativa" in df_res.columns:
        df_save = df_res.set_index("Alternativa")[criterios].astype(float)
        st.session_state['df_calificaciones'] = df_save
        
        # Calculamos ranking para mostrar la ganadora
        res_finales = []
        for alt_n in df_save.index:
            p_final = 0
            for crit in criterios:
                p_final += df_save.loc[alt_n, crit] * (pesos[crit]/100)
            res_finales.append({"Alternativa": alt_n, "PUNTAJE": p_final})
            
        df_ranking = pd.DataFrame(res_finales).sort_values("PUNTAJE", ascending=False)
        
        # Mostrar Ganadora
        if not df_ranking.empty:
            ganadora = df_ranking.iloc[0]
            st.success(f"🎉 **Ganadora Actual:** {ganadora['Alternativa']} con **{ganadora['PUNTAJE']:.2f}** puntos")
            
            # Tabla visual del ranking
            st.dataframe(
                df_ranking,
                column_config={
                    "PUNTAJE": st.column_config.ProgressColumn(
                        "Puntaje", format="%.2f", min_value=0, max_value=5
                    )
                },
                use_container_width=True, hide_index=True
            )

# Espacio final
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
