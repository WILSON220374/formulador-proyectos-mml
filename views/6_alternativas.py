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

if st.session_state['df_evaluacion_alternativas'].empty:
    datos_nuevos = []
    for obj in obj_especificos:
        o_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == o_txt]
        for a_txt in hijas:
            datos_nuevos.append({"OBJETIVO": o_txt, "ACTIVIDAD": a_txt, "ENFOQUE": "NO", "ALCANCE": "NO"})
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos_nuevos)
    guardar_datos_nube()

df_master = st.session_state['df_evaluacion_alternativas']

for index, row in df_master.iterrows():
    with st.container(border=True):
        st.markdown(f"**📍 COMBINACIÓN {int(index) + 1}**")
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

# --- 2. ANÁLISIS DE RELACIONES ---
st.subheader("🔄 2. Análisis de Relaciones")

aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
]
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

    df_rel_editado = st.data_editor(
        st.session_state['df_relaciones_objetivos'],
        column_config={
            "OBJETIVO A": st.column_config.TextColumn("OBJETIVO A", disabled=True, width="large"),
            "OBJETIVO B": st.column_config.TextColumn("OBJETIVO B", disabled=True, width="large"),
            "RELACIÓN": st.column_config.SelectboxColumn("DECISIÓN", options=["Por definir", "Complementario", "Excluyente"])
        },
        hide_index=True, use_container_width=True, key="tabla_rel_final_v7"
    )

    if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
        st.session_state['df_relaciones_objetivos'] = df_rel_editado
        guardar_datos_nube(); st.rerun()

st.divider()

# --- 3. CONSTRUCTOR DE ALTERNATIVAS (SELECCIÓN POR CLIC) ---
st.subheader("📦 3. Constructor de Alternativas")

if objetivos_seleccionados:
    with st.container(border=True):
        nombre_alt = st.text_input("🚀 Nombre de la Alternativa:")
        
        st.info("1. Seleccione los Objetivos (Haga clic para incluir):")
        objs_en_paquete = []
        for obj_opcion in objetivos_seleccionados:
            if st.checkbox(obj_opcion, key=f"obj_paq_{obj_opcion}"):
                objs_en_paquete.append(obj_opcion)

        conflicto = False
        if len(objs_en_paquete) > 1:
            for o_a, o_b in itertools.combinations(objs_en_paquete, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_a))
                ]
                if not rel.empty:
                    if rel.iloc[0]["RELACIÓN"] == "Excluyente":
                        st.error(f"❌ Conflicto: '{o_a}' y '{o_b}' son EXCLUYENTES."); conflicto = True
                    elif rel.iloc[0]["RELACIÓN"] == "Por definir":
                        st.warning(f"⚠️ Defina la relación entre '{o_a}' y '{o_b}' arriba."); conflicto = True

        config_final = []
        if objs_en_paquete and not conflicto:
            st.write("---")
            st.info("2. Marque las actividades específicas para este paquete:")
            for obj_p in objs_en_paquete:
                with st.expander(f"📌 Configurar actividades para: {obj_p[:60]}...", expanded=True):
                    st.markdown(f"**Objetivo:** {obj_p}")
                    acts_aprob = aprobadas[aprobadas["OBJETIVO"] == obj_p]["ACTIVIDAD"].tolist()
                    sel_del_obj = []
                    for act in acts_aprob:
                        if st.checkbox(act, value=True, key=f"act_paq_{obj_p}_{act}"):
                            sel_del_obj.append(act)
                    if sel_del_obj:
                        config_final.append({"objetivo": obj_p, "actividades": sel_del_obj})

        if st.button("🚀 Consolidar Alternativa", type="primary", use_container_width=True, disabled=conflicto or not config_final):
            if nombre_alt:
                st.session_state['lista_alternativas'].append({"nombre": nombre_alt, "configuracion": config_final})
                guardar_datos_nube(); st.rerun()

# --- 4. VISUALIZACIÓN DE RESULTADOS (FORMATO AJUSTADO) ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Alternativas Consolidadas")
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        with st.expander(f"🔹 {alt.get('nombre', 'Sin nombre')}", expanded=True):
            for item in alt.get('configuracion', []):
                # Aplicamos negrilla consistente a todos los objetivos
                st.markdown(f"**🎯 {item['objetivo']}**")
                for a in item.get('actividades', []):
                    st.markdown(f"   - {a}")
            
            if st.button("🗑️ Eliminar Alternativa", key=f"del_paq_{idx}"):
                st.session_state['lista_alternativas'].pop(idx); guardar_datos_nube(); st.rerun()
