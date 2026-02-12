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

# Lógica Dinámica: Inicializamos solo si la tabla está realmente vacía
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
        # SOLUCIÓN AL TYPEERROR: Convertimos el index a entero
        st.markdown(f"**📍 COMBINACIÓN {int(index) + 1}**")
        st.write(f"**Objetivo:** {row['OBJETIVO']}")
        st.write(f"**Actividad:** {row['ACTIVIDAD']}")
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            nuevo_enf = st.selectbox("¿Enfoque?", ["SI", "NO"], 
                                     index=0 if row["ENFOQUE"]=="SI" else 1, key=f"e_{index}")
        with c2:
            nuevo_alc = st.selectbox("¿Alcance?", ["SI", "NO"], 
                                     index=0 if row["ALCANCE"]=="SI" else 1, key=f"a_{index}")
        with c3:
            if nuevo_enf == "SI" and nuevo_alc == "SI": st.success("✅ SELECCIONADO")
            else: st.error("❌ DESCARTADO")
        
        if nuevo_enf != row["ENFOQUE"] or nuevo_alc != row["ALCANCE"]:
            st.session_state['df_evaluacion_alternativas'].at[index, "ENFOQUE"] = nuevo_enf
            st.session_state['df_evaluacion_alternativas'].at[index, "ALCANCE"] = nuevo_alc
            guardar_datos_nube(); st.rerun()

st.divider()

# --- 2. ANÁLISIS DE RELACIONES (SINCRONIZACIÓN DINÁMICA) ---
st.subheader("🔄 2. Análisis de Relaciones entre Objetivos")

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
        hide_index=True, use_container_width=True, key="tabla_rel_final_v4"
    )

    if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
        st.session_state['df_relaciones_objetivos'] = df_rel_editado
        guardar_datos_nube(); st.rerun()
else:
    st.info("Seleccione actividades de al menos dos objetivos diferentes.")

st.divider()

# --- 3. CONSTRUCTOR DE PAQUETES ---
st.subheader("📦 3. Constructor de Alternativas")

if objetivos_seleccionados:
    with st.container(border=True):
        nombre_alt = st.text_input("🚀 Nombre de la Alternativa:")
        objs_en_paquete = st.multiselect("1. Seleccione los Objetivos:", options=objetivos_seleccionados)

        conflicto = False
        if len(objs_en_paquete) > 1:
            for o_a, o_b in itertools.combinations(objs_en_paquete, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_a))
                ]
                if not rel.empty:
                    res_rel = rel.iloc[0]["RELACIÓN"]
                    if res_rel == "Excluyente":
                        st.error(f"❌ Conflicto: '{o_a}' y '{o_b}' son EXCLUYENTES."); conflicto = True
                    elif res_rel == "Por definir":
                        st.warning(f"⚠️ Defina la relación entre '{o_a}' y '{o_b}'."); conflicto = True

        config_final = []
        if objs_en_paquete and not conflicto:
            for obj_p in objs_en_paquete:
                with st.expander(f"📌 Actividades: {obj_p}", expanded=True):
                    acts_aprob = aprobadas[aprobadas["OBJETIVO"] == obj_p]["ACTIVIDAD"].tolist()
                    sel = st.multiselect("Marque actividades:", options=acts_aprob, default=acts_aprob, key=f"m_{obj_p}")
                    if sel: config_final.append({"objetivo": obj_p, "actividades": sel})

        if st.button("🚀 Consolidar Alternativa", type="primary", disabled=conflicto or not config_final):
            if nombre_alt:
                st.session_state['lista_alternativas'].append({"nombre": nombre_alt, "configuracion": config_final, "justificacion": ""})
                guardar_datos_nube(); st.rerun()

# --- 4. VISUALIZACIÓN ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        with st.expander(f"🔹 {alt.get('nombre')}"):
            for c in alt.get('configuracion', []):
                st.write(f"**🎯 {c['objetivo']}**")
                for a in c['actividades']: st.write(f"- {a}")
            if st.button("🗑️ Eliminar", key=f"d_{idx}"):
                st.session_state['lista_alternativas'].pop(idx); guardar_datos_nube(); st.rerun()
