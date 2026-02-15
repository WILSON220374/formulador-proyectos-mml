import streamlit as st
import pandas as pd
import itertools
import os
from session_state import inicializar_session, guardar_datos_nube
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# 1. Carga de datos y persistencia
inicializar_session()

# --- ESTILOS PERSONALIZADOS (HEADER, BOTONES Y TABLA) ---
st.markdown("""
    <style>
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
        margin-bottom: 10px; 
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

# --- CÁLCULO DEL PROGRESO ---
# Calculamos qué tan avanzado va el usuario para pintar la barra azul
progreso_val = 0.0
# Paso 1: Si ya hay datos en la tabla de evaluación
if not st.session_state['df_evaluacion_alternativas'].empty:
    progreso_val += 0.33
# Paso 2: Si ya hay alternativas creadas
if st.session_state.get('lista_alternativas'):
    progreso_val += 0.33
# Paso 3: Si ya hay calificaciones hechas
if not st.session_state.get('df_calificaciones', pd.DataFrame()).empty:
    # Verificamos si hay al menos un valor diferente a 1 (significa que ya trabajó)
    if st.session_state['df_calificaciones'].sum().sum() > (len(st.session_state['df_calificaciones']) * 4):
        progreso_val += 0.34

# Aseguramos que no pase de 1.0
progreso_val = min(progreso_val, 1.0)

# --- ENCABEZADO CON BARRA DE PROGRESO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown('<div class="titulo-seccion">⚖️ 6. Análisis de Alternativas</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Evaluación, comparación y selección de las mejores estrategias.</div>', unsafe_allow_html=True)
    
    # BARRA DE PROGRESO (Aquí está lo que faltaba)
    st.caption(f"Nivel de Completitud: {int(progreso_val * 100)}%")
    st.progress(progreso_val)

with col_img:
    # Lógica de imagen inteligente
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- CONTEXTO: DATOS DEL ÁRBOL DE OBJETIVOS ---
obj_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# ==============================================================================
# 1. EVALUACIÓN DE RELEVANCIA Y ALCANCE (DISEÑO ULTRA-SUAVE)
# ==============================================================================
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

# --- LEYENDA COMPACTA Y SUAVE ---
st.markdown("""
    <div style="display: flex; gap: 10px; margin-bottom: 5px; align-items: center; font-size: 0.8rem; color: #444;">
        <span style="background-color: #F0FDF4; border: 1px solid #BBF7D0; padding: 2px 8px; border-radius: 4px;">
            ✅ Seleccionada
        </span>
        <span style="background-color: #FEF2F2; border: 1px solid #FECACA; padding: 2px 8px; border-radius: 4px;">
            ⬜ Descartada
        </span>
        <span style="color: #666; margin-left: 10px;">(Marque las casillas y presione 💾 para guardar)</span>
    </div>
""", unsafe_allow_html=True)

# 1.1 Inicializar DataFrame
if st.session_state['df_evaluacion_alternativas'].empty:
    datos_nuevos = []
    for obj in obj_especificos:
        o_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == o_txt]
        for a_txt in hijas:
            datos_nuevos.append({"OBJETIVO": o_txt, "ACTIVIDAD": a_txt, "ENFOQUE": False, "ALCANCE": False})
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos_nuevos)
    guardar_datos_nube()

# 1.2 Preparar Datos
df_work = st.session_state['df_evaluacion_alternativas'].copy()

# Asegurar booleanos
if df_work["ENFOQUE"].dtype == 'object':
    df_work["ENFOQUE"] = df_work["ENFOQUE"].apply(lambda x: True if x == "SI" else False)
if df_work["ALCANCE"].dtype == 'object':
    df_work["ALCANCE"] = df_work["ALCANCE"].apply(lambda x: True if x == "SI" else False)

# -----------------------------------------------------------------------------
# CONFIGURACIÓN AG-GRID (COLORES ULTRA-SUAVES "OFF-WHITE")
# -----------------------------------------------------------------------------
gb = GridOptionsBuilder.from_dataframe(df_work)

# Configurar columnas de Texto (Ajuste automático)
gb.configure_column("OBJETIVO", headerName="🎯 Objetivo Específico", wrapText=True, autoHeight=True, width=300)
gb.configure_column("ACTIVIDAD", headerName="🛠️ Actividad", wrapText=True, autoHeight=True, width=400)

# Configurar columnas Checkbox
gb.configure_column("ENFOQUE", headerName="¿Tiene el enfoque?", editable=True, width=130)
gb.configure_column("ALCANCE", headerName="¿Está al alcance?", editable=True, width=130)

# --- JAVASCRIPT: COLORES CASI BLANCOS ---
jscode_row_style = JsCode("""
function(params) {
    if (params.data.ENFOQUE === true && params.data.ALCANCE === true) {
        return {
            'background-color': '#F0FDF4',  // Blanco Mentolado
            'color': '#000000'              // Texto Negro
        };
    } else {
        return {
            'background-color': '#FEF2F2',  // Blanco Rosado
            'color': '#000000'              // Texto Negro
        };
    }
};
""")

gb.configure_grid_options(getRowStyle=jscode_row_style, domLayout='autoHeight')
gridOptions = gb.build()

# Renderizar Tabla
grid_response = AgGrid(
    df_work,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.MANUAL, # Evita parpadeo
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    theme='streamlit',
    height=500,
    allow_unsafe_jscode=True
)

# 1.3 BOTÓN DE GUARDADO (ICONO AZUL)
col_btn, col_rest = st.columns([1, 10])
with col_btn:
    btn_guardar = st.button("💾", help="Guardar Cambios de la Tabla")

if btn_guardar:
    df_editado = pd.DataFrame(grid_response['data'])
    if not df_editado.empty:
        df_editado["ENFOQUE"] = df_editado["ENFOQUE"].astype(bool)
        df_editado["ALCANCE"] = df_editado["ALCANCE"].astype(bool)
        st.session_state['df_evaluacion_alternativas'] = df_editado
        guardar_datos_nube()
        st.rerun()

st.divider()

# ==============================================================================
# 2. ANÁLISIS DE RELACIONES
# ==============================================================================
st.subheader("🔄 2. Análisis de Relaciones")

df_master = st.session_state['df_evaluacion_alternativas']
try:
    aprobadas = df_master[(df_master["ENFOQUE"] == True) & (df_master["ALCANCE"] == True)]
except:
    aprobadas = df_master[(df_master["ENFOQUE"] == "SI") & (df_master["ALCANCE"] == "SI")]

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

    st.info("Defina si los objetivos seleccionados pueden ejecutarse juntos (Complementarios) o si son Excluyentes.")
    
    df_rel_editado = st.data_editor(
        st.session_state['df_relaciones_objetivos'],
        column_config={
            "OBJETIVO A": st.column_config.TextColumn("Objetivo A", disabled=True, width="medium"),
            "OBJETIVO B": st.column_config.TextColumn("Objetivo B", disabled=True, width="medium"),
            "RELACIÓN": st.column_config.SelectboxColumn("Tipo de Relación", options=["Por definir", "Complementario", "Excluyente"], required=True)
        },
        hide_index=True, use_container_width=True, key="tabla_rel_v9"
    )

    if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
        st.session_state['df_relaciones_objetivos'] = df_rel_editado
        guardar_datos_nube(); st.rerun()
else:
    st.warning("⚠️ Necesita aprobar actividades de al menos 2 objetivos diferentes en el paso 1 (casillas verdes) para habilitar esta sección.")

st.divider()

# ==============================================================================
# 3. CONSTRUCTOR DE ALTERNATIVAS
# ==============================================================================
st.subheader("📦 3. Constructor de Alternativas")

if objetivos_seleccionados:
    with st.container(border=True):
        st.markdown("#### 🆕 Crear Nueva Alternativa")
        
        c_nombre, c_desc = st.columns([1, 2])
        with c_nombre:
            nombre_alt = st.text_input("Nombre:", placeholder="Ej: Alternativa Tecnológica A")
        with c_desc:
            desc_alt = st.text_area("Descripción Corta:", placeholder="Resumen de la alternativa...", height=68)

        st.markdown("**Seleccione los Objetivos a incluir:**")
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
                    msg_conflicto = f"Conflicto: '{o_a}' y '{o_b}' son EXCLUYENTES."

        if conflicto:
            st.error(f"❌ {msg_conflicto}")
        
        # Configuración Actividades
        config_final = []
        if objs_en_paquete and not conflicto:
            st.markdown("---")
            st.markdown("**Seleccione las actividades:**")
            for obj_p in objs_en_paquete:
                with st.expander(f"📌 {obj_p}", expanded=True):
                    acts_aprob = aprobadas[aprobadas["OBJETIVO"] == obj_p]["ACTIVIDAD"].tolist()
                    sel_del_obj = []
                    for act in acts_aprob:
                        if st.checkbox(act, value=True, key=f"paq_act_{obj_p}_{act}"):
                            sel_del_obj.append(act)
                    if sel_del_obj:
                        config_final.append({"objetivo": obj_p, "actividades": sel_del_obj})

        btn_disable = conflicto or not config_final or not nombre_alt
        
        if st.button("🚀 Guardar Alternativa", type="primary", use_container_width=True, disabled=btn_disable):
            st.session_state['lista_alternativas'].append({
                "nombre": nombre_alt, 
                "descripcion": desc_alt,
                "configuracion": config_final
            })
            guardar_datos_nube(); st.rerun()

st.divider()

# ==============================================================================
# 4. VISUALIZACIÓN
# ==============================================================================
if st.session_state.get('lista_alternativas'):
    st.subheader("📋 4. Alternativas Consolidadas")
    
    colores = ["blue", "green", "orange", "red", "violet"]
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        color = colores[idx % len(colores)]
        nombre = alt.get('nombre', 'Sin nombre').upper()
        desc = alt.get('descripcion', 'Sin descripción')
        
        with st.expander(f"**{idx+1}. {nombre}**", expanded=False):
            st.caption(f"📝 {desc}")
            for item in alt.get('configuracion', []):
                st.markdown(f"**🎯 {item['objetivo']}**")
                for a in item.get('actividades', []):
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🔹 {a}")
            
            if st.button(f"🗑️ Eliminar", key=f"del_alt_{idx}"):
                st.session_state['lista_alternativas'].pop(idx)
                guardar_datos_nube(); st.rerun()

st.divider()

# ==============================================================================
# 5. EVALUACIÓN MULTICRITERIO
# ==============================================================================
st.subheader("📊 5. Evaluación de Alternativas")

alts = st.session_state.get('lista_alternativas', [])

if not alts:
    st.info("👆 Configure y guarde al menos una alternativa arriba para iniciar la evaluación.")
else:
    with st.expander("⚙️ Configurar Criterios y Pesos", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        p = st.session_state.get('ponderacion_criterios', {"COSTO": 25.0, "FACILIDAD": 25.0, "BENEFICIOS": 25.0, "TIEMPO": 25.0})
        
        with c1: pc = st.number_input("Costo (%)", 0, 100, int(p['COSTO']), key="wc")
        with c2: pf = st.number_input("Facilidad (%)", 0, 100, int(p['FACILIDAD']), key="wf")
        with c3: pb = st.number_input("Beneficios (%)", 0, 100, int(p['BENEFICIOS']), key="wb")
        with c4: pt = st.number_input("Tiempo (%)", 0, 100, int(p['TIEMPO']), key="wt")
        
        suma = pc + pf + pb + pt
        if suma == 100:
            st.session_state['ponderacion_criterios'] = {"COSTO": pc, "FACILIDAD": pf, "BENEFICIOS": pb, "TIEMPO": pt}
        else:
            st.warning(f"⚠️ Suma actual: {suma}%. Debe ser 100%.")

    st.markdown("##### 🏆 Matriz de Decisión (Escala 1-5)")
    nombres_alts = [a['nombre'] for a in alts]
    criterios = ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]
    
    if st.session_state['df_calificaciones'].empty or len(st.session_state['df_calificaciones']) != len(nombres_alts):
        st.session_state['df_calificaciones'] = pd.DataFrame(1, index=nombres_alts, columns=criterios)
    else:
        st.session_state['df_calificaciones'].index = nombres_alts

    df_scores = st.data_editor(
        st.session_state['df_calificaciones'],
        column_config={c: st.column_config.NumberColumn(min_value=0, max_value=5, step=1) for c in criterios},
        use_container_width=True, key="ed_scores_final"
    )

    if not df_scores.equals(st.session_state['df_calificaciones']):
        st.session_state['df_calificaciones'] = df_scores
        guardar_datos_nube(); st.rerun()

    st.markdown("### 🥇 Resultados")
    res_finales = []
    pesos = st.session_state['ponderacion_criterios']
    
    if suma == 100:
        for alt_n in nombres_alts:
            fila = {"Alternativa": alt_n}
            p_final = 0
            for crit in criterios:
                sc = df_scores.loc[alt_n, crit]
                w = pesos[crit] / 100
                p_final += sc * w
            fila["PUNTAJE FINAL"] = round(p_final, 2)
            res_finales.append(fila)

        df_final = pd.DataFrame(res_finales).sort_values(by="PUNTAJE FINAL", ascending=False)
        
        st.dataframe(
            df_final, 
            column_config={
                "PUNTAJE FINAL": st.column_config.ProgressColumn(
                    "Puntaje Ponderado", format="%.2f", min_value=0, max_value=5
                )
            },
            use_container_width=True, hide_index=True
        )

        if not df_final.empty:
            ganadora = df_final.iloc[0]
            st.success(f"🎉 Ganadora: **{ganadora['Alternativa']}** ({ganadora['PUNTAJE FINAL']} pts).")
