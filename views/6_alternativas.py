import streamlit as st
import pandas as pd
import itertools
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos y persistencia
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: DATOS DEL ÁRBOL DE OBJETIVOS ---
obj_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. SELECCIÓN DE ACTIVIDADES A ATENDER ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    datos = []
    for obj in obj_especificos:
        o_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == o_txt]
        for a_txt in hijas:
            datos.append({"OBJETIVO": o_txt, "ACTIVIDAD": a_txt, "ENFOQUE": "NO", "ALCANCE": "NO"})
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos)

df_master = st.session_state['df_evaluacion_alternativas']
for index, row in df_master.iterrows():
    with st.container(border=True):
        st.markdown(f"**📍 COMBINACIÓN {index + 1}**")
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

# --- 2. ANÁLISIS DE RELACIONES ENTRE OBJETIVOS (DINÁMICO) ---
st.subheader("🔄 2. Análisis de Relaciones entre Objetivos")

# Filtro: Solo objetivos que tengan al menos una actividad seleccionada
aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
]
objetivos_seleccionados = aprobadas["OBJETIVO"].unique().tolist()

if len(objetivos_seleccionados) < 2:
    st.info("Seleccione actividades de al menos dos objetivos diferentes para analizar su relación.")
else:
    pares = list(itertools.combinations(objetivos_seleccionados, 2))
    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame(columns=["OBJETIVO A", "OBJETIVO B", "RELACIÓN"])

    df_existente = st.session_state['df_relaciones_objetivos']
    nuevas_filas = []

    for obj_a, obj_b in pares:
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
        hide_index=True, use_container_width=True, key="tabla_rel_final_v2"
    )

    if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
        st.session_state['df_relaciones_objetivos'] = df_rel_editado
        guardar_datos_nube(); st.rerun()

st.divider()

# --- 3. CONSTRUCTOR MANUAL DE PAQUETES ---
st.subheader("📦 3. Constructor de Alternativas")

if not objetivos_seleccionados:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    with st.container(border=True):
        nombre_alt = st.text_input("🚀 Nombre de la Alternativa:")
        
        # 1. Selección de Objetivos para el Paquete
        objs_en_paquete = st.multiselect(
            "1. Seleccione los Objetivos que desea integrar en esta alternativa:",
            options=objetivos_seleccionados
        )

        # Validación de exclusividad
        conflicto = False
        if len(objs_en_paquete) > 1:
            for o_a, o_b in itertools.combinations(objs_en_paquete, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_a))
                ]
                if not rel.empty:
                    res = rel.iloc[0]["RELACIÓN"]
                    if res == "Excluyente":
                        st.error(f"❌ Conflicto: '{o_a}' y '{o_b}' son EXCLUYENTES.")
                        conflicto = True
                    elif res == "Por definir":
                        st.warning(f"⚠️ Debe definir la relación entre '{o_a}' y '{o_b}' en la sección 2.")
                        conflicto = True

        # 2. Selección de Actividades Manual
        actividades_finales = []
        if objs_en_paquete and not conflicto:
            st.write("---")
            st.info("2. Seleccione las actividades específicas de cada objetivo para este paquete:")
            for obj_p in objs_en_paquete:
                with st.expander(f"📌 Actividades del Objetivo: {obj_p}", expanded=True):
                    acts_aprobadas_obj = aprobadas[aprobadas["OBJETIVO"] == obj_p]["ACTIVIDAD"].tolist()
                    sel_acts = st.multiselect(
                        "Marque las actividades que incluirá:",
                        options=acts_aprobadas_obj,
                        default=acts_aprobadas_obj,
                        key=f"manual_sel_{obj_p}"
                    )
                    if sel_acts:
                        actividades_finales.append({"objetivo": obj_p, "actividades": sel_acts})

        st.write("---")
        justificacion = st.text_area("✍️ Justificación técnica:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary", use_container_width=True, disabled=conflicto or not actividades_finales):
            if nombre_alt:
                nueva_alt = {"nombre": nombre_alt, "configuracion": actividades_finales, "justificacion": justificacion}
                if 'lista_alternativas' not in st.session_state or not isinstance(st.session_state['lista_alternativas'], list):
                    st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva_alt)
                guardar_datos_nube(); st.rerun()

# --- 4. VISUALIZACIÓN ---
alternativas = st.session_state.get('lista_alternativas')
if isinstance(alternativas, list) and len(alternativas) > 0:
    st.divider()
    st.subheader("📋 Alternativas Consolidadas")
    for idx, alt in enumerate(alternativas):
        with st.expander(f"🔹 {alt.get('nombre', 'Sin nombre')}"):
            st.write(f"**Justificación:** {alt.get('justificacion', 'N/A')}")
            for config in alt.get('configuracion', []):
                st.markdown(f"**🎯 Objetivo:** {config['objetivo']}")
                for a in config['actividades']: st.markdown(f"   - ✅ {a}")
            if st.button("🗑️ Eliminar", key=f"del_final_{idx}"):
                st.session_state['lista_alternativas'].pop(idx); guardar_datos_nube(); st.rerun()
