import streamlit as st
import pandas as pd
import itertools
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos y persistencia
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: DATOS DEL PASO 5 ---
obj_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN DE RELEVANCIA Y ALCANCE ---
st.subheader("📋 1. Selección de Actividades a Atender")

if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    datos = []
    for obj in obj_especificos:
        o_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == o_txt]
        for a_txt in hijas:
            datos.append({"OBJETIVO": o_txt, "ACTIVIDAD": a_txt, "ENFOQUE": "NO", "ALCANCE": "NO", "RELACIÓN": "Por definir"})
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos)

# Renderizado de selección
df_master = st.session_state['df_evaluacion_alternativas']
for index, row in df_master.iterrows():
    with st.container(border=True):
        st.write(f"**Objetivo:** {row['OBJETIVO']}")
        st.write(f"**Actividad:** {row['ACTIVIDAD']}")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            nuevo_enf = st.selectbox("¿Enfoque?", ["SI", "NO"], index=0 if row["ENFOQUE"]=="SI" else 1, key=f"e_{index}")
        with c2:
            nuevo_alc = st.selectbox("¿Alcance?", ["SI", "NO"], index=0 if row["ALCANCE"]=="SI" else 1, key=f"a_{index}")
        with c3:
            if nuevo_enf == "SI" and nuevo_alc == "SI": st.success("✅ SELECCIONADO")
            else: st.error("❌ DESCARTADO")
        
        if nuevo_enf != row["ENFOQUE"] or nuevo_alc != row["ALCANCE"]:
            st.session_state['df_evaluacion_alternativas'].at[index, "ENFOQUE"] = nuevo_enf
            st.session_state['df_evaluacion_alternativas'].at[index, "ALCANCE"] = nuevo_alc
            guardar_datos_nube(); st.rerun()

st.divider()

# --- 2. ANÁLISIS DE RELACIONES ENTRE OBJETIVOS ---
st.subheader("🔄 2. Análisis de Relaciones entre Objetivos")

aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
]
objetivos_seleccionados = aprobadas["OBJETIVO"].unique().tolist()

if len(objetivos_seleccionados) < 2:
    st.info("Seleccione actividades de al menos dos objetivos diferentes para realizar el análisis de exclusividad.")
else:
    pares_actuales = list(itertools.combinations(objetivos_seleccionados, 2))
    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame(columns=["OBJETIVO A", "OBJETIVO B", "RELACIÓN"])

    df_existente = st.session_state['df_relaciones_objetivos']
    nuevas_filas = []

    for obj_a, obj_b in pares_actuales:
        existe = df_existente[((df_existente["OBJETIVO A"] == obj_a) & (df_existente["OBJETIVO B"] == obj_b)) |
                              ((df_existente["OBJETIVO A"] == obj_b) & (df_existente["OBJETIVO B"] == obj_a))]
        if existe.empty:
            nuevas_filas.append({"OBJETIVO A": obj_a, "OBJETIVO B": obj_b, "RELACIÓN": "Por definir"})

    if nuevas_filas:
        st.session_state['df_relaciones_objetivos'] = pd.concat([df_existente, pd.DataFrame(nuevas_filas)], ignore_index=True)
        guardar_datos_nube()

    df_rel_editado = st.data_editor(
        st.session_state['df_relaciones_objetivos'],
        column_config={
            "OBJETIVO A": st.column_config.TextColumn("OBJETIVO A", disabled=True, width="large"),
            "OBJETIVO B": st.column_config.TextColumn("OBJETIVO B", disabled=True, width="large"),
            "RELACIÓN": st.column_config.SelectboxColumn("DECISIÓN", options=["Por definir", "Complementario", "Excluyente"])
        },
        hide_index=True, use_container_width=True, key="tabla_rel_final"
    )

    if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
        st.session_state['df_relaciones_objetivos'] = df_rel_editado
        guardar_datos_nube(); st.rerun()

st.divider()

# --- 3. CONFIGURADOR JERÁRQUICO DE PAQUETES ---
st.subheader("📦 3. Constructor de Alternativas")

if not objetivos_seleccionados:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    with st.container(border=True):
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            nombre_alt = st.text_input("🚀 Nombre de la Alternativa:", placeholder="Ej: Alternativa de Optimización PTAR")
        with col_t2:
            st.write("") # Espacio
        
        st.markdown("---")
        st.write("### 🧩 Selección de Componentes")
        
        # 1. Selección de Objetivos para el Paquete
        objs_en_paquete = st.multiselect(
            "1. Seleccione los Objetivos que integrarán esta alternativa:",
            options=objetivos_seleccionados,
            help="Solo puede seleccionar objetivos que sean complementarios entre sí."
        )

        # Validación de complementariedad en tiempo real
        error_comp = False
        if len(objs_en_paquete) > 1:
            for o_a, o_b in itertools.combinations(objs_en_paquete, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_a))
                ]
                if not rel.empty:
                    decision = rel.iloc[0]["RELACIÓN"]
                    if decision == "Excluyente":
                        st.error(f"❌ Conflicto: Los objetivos '{o_a}' y '{o_b}' fueron marcados como EXCLUYENTES. No pueden ir juntos.")
                        error_comp = True
                    elif decision == "Por definir":
                        st.warning(f"⚠️ Definición pendiente: Determine si '{o_a}' y '{o_b}' son complementarios en la sección anterior.")
                        error_comp = True

        # 2. Selección de Actividades por cada Objetivo seleccionado
        actividades_finales = []
        if objs_en_paquete and not error_comp:
            st.info("2. Seleccione las actividades específicas que se ejecutarán para cada objetivo en esta alternativa:")
            for obj_p in objs_en_paquete:
                with st.expander(f"📌 Actividades para: {obj_p}", expanded=True):
                    # Filtramos actividades aprobadas que pertenecen a este padre
                    acts_aprobadas_obj = aprobadas[aprobadas["OBJETIVO"] == obj_p]["ACTIVIDAD"].tolist()
                    
                    sel_acts = st.multiselect(
                        f"Actividades a realizar para este objetivo:",
                        options=acts_aprobadas_obj,
                        default=acts_aprobadas_obj, # Por defecto todas las aprobadas
                        key=f"sel_act_{obj_p}"
                    )
                    if sel_acts:
                        actividades_finales.append({"objetivo": obj_p, "actividades": sel_acts})
        
        st.markdown("---")
        justificacion = st.text_area("✍️ Justificación técnica de la alternativa (opcional):")
        
        if st.button("🚀 Consolidar Alternativa", type="primary", use_container_width=True, disabled=error_comp or not actividades_finales):
            if nombre_alt:
                nueva_alt = {
                    "nombre": nombre_alt,
                    "configuracion": actividades_finales,
                    "justificacion": justificacion
                }
                if 'lista_alternativas' not in st.session_state or not isinstance(st.session_state['lista_alternativas'], list):
                    st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva_alt)
                guardar_datos_nube()
                st.success("¡Alternativa consolidada con éxito!")
                st.rerun()
            else:
                st.error("Debe asignar un nombre a la alternativa.")

# --- 4. VISUALIZACIÓN DE ALTERNATIVAS ---
alternativas = st.session_state.get('lista_alternativas')
if isinstance(alternativas, list) and len(alternativas) > 0:
    st.divider()
    st.subheader("📋 Alternativas Consolidadas")
    for idx, alt in enumerate(alternativas):
        with st.expander(f"🔹 {alt['nombre']}"):
            st.write(f"**Justificación:** {alt.get('justificacion', 'N/A')}")
            for config in alt.get('configuracion', []):
                st.markdown(f"**🎯 Objetivo:** {config['objetivo']}")
                for a in config['actividades']:
                    st.markdown(f"   - ✅ {a}")
            if st.button("🗑️ Eliminar", key=f"del_final_{idx}"):
                st.session_state['lista_alternativas'].pop(idx)
                guardar_datos_nube(); st.rerun()
