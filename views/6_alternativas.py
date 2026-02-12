import streamlit as st
import pandas as pd
import itertools
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos y persistencia total
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
        hide_index=True, use_container_width=True, key="tabla_rel_v8"
    )

    if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
        st.session_state['df_relaciones_objetivos'] = df_rel_editado
        guardar_datos_nube(); st.rerun()

st.divider()

# --- 3. CONSTRUCTOR DE PAQUETES ---
st.subheader("📦 3. Constructor de Alternativas")

if objetivos_seleccionados:
    with st.container(border=True):
        nombre_alt = st.text_input("🚀 Nombre de la Alternativa:")
        st.info("1. Seleccione los Objetivos:")
        objs_en_paquete = []
        for obj_opcion in objetivos_seleccionados:
            if st.checkbox(obj_opcion, key=f"paq_obj_{obj_opcion}"):
                objs_en_paquete.append(obj_opcion)

        conflicto = False
        if len(objs_en_paquete) > 1:
            for o_a, o_b in itertools.combinations(objs_en_paquete, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_a))
                ]
                if not rel.empty and rel.iloc[0]["RELACIÓN"] == "Excluyente":
                    st.error(f"❌ Conflicto: '{o_a}' y '{o_b}' son EXCLUYENTES."); conflicto = True

        config_final = []
        if objs_en_paquete and not conflicto:
            st.write("---")
            for obj_p in objs_en_paquete:
                with st.expander(f"📌 Configurar: {obj_p[:50]}...", expanded=True):
                    st.markdown(f"**Objetivo:** {obj_p}")
                    acts_aprob = aprobadas[aprobadas["OBJETIVO"] == obj_p]["ACTIVIDAD"].tolist()
                    sel_del_obj = []
                    for act in acts_aprob:
                        if st.checkbox(act, value=True, key=f"paq_act_{obj_p}_{act}"):
                            sel_del_obj.append(act)
                    if sel_del_obj:
                        config_final.append({"objetivo": obj_p, "actividades": sel_del_obj})

        if st.button("🚀 Consolidar Alternativa", type="primary", use_container_width=True, disabled=conflicto or not config_final):
            if nombre_alt:
                st.session_state['lista_alternativas'].append({"nombre": nombre_alt, "configuracion": config_final})
                guardar_datos_nube(); st.rerun()

st.divider()

# --- 4. VISUALIZACIÓN DE ALTERNATIVAS (CON NUMERACIÓN Y COLORES) ---
if st.session_state.get('lista_alternativas'):
    st.subheader("📋 4. Alternativas Consolidadas")
    colores = [":blue", ":green", ":orange", ":red", ":violet", ":rainbow"]
    
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        color_tema = colores[idx % len(colores)]
        nombre_limpio = str(alt.get('nombre', 'Sin nombre')).strip().upper()
        
        # Formato numerado y coloreado
        with st.expander(f"{color_tema}[**{idx + 1}. {nombre_limpio}**]", expanded=True):
            for item in alt.get('configuracion', []):
                st.markdown(f"**🎯 {str(item['objetivo']).strip()}**")
                for a in item.get('actividades', []):
                    st.markdown(f"   - {str(a).strip()}")
            
            if st.button(f"🗑️ Eliminar Alternativa {idx + 1}", key=f"del_final_{idx}"):
                st.session_state['lista_alternativas'].pop(idx); guardar_datos_nube(); st.rerun()

st.divider()

# --- 5. EVALUACIÓN MULTICRITERIO (TABLA COMPLETA) ---
st.subheader("📊 5. Evaluación de Alternativas")

alts = st.session_state.get('lista_alternativas', [])

if not alts:
    st.info("Debe consolidar alternativas para habilitar la evaluación.")
else:
    # 5.1 Configuración de Pesos
    with st.expander("⚙️ Configurar Ponderación de Criterios (Suma = 100%)", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        p = st.session_state.get('ponderacion_criterios', {"COSTO": 25.0, "FACILIDAD": 25.0, "BENEFICIOS": 25.0, "TIEMPO": 25.0})
        
        with c1: pc = st.number_input("Costo (%)", 0, 100, int(p['COSTO']), key="wc")
        with c2: pf = st.number_input("Facilidad (%)", 0, 100, int(p['FACILIDAD']), key="wf")
        with c3: pb = st.number_input("Beneficios (%)", 0, 100, int(p['BENEFICIOS']), key="wb")
        with c4: pt = st.number_input("Tiempo (%)", 0, 100, int(p['TIEMPO']), key="wt")
        
        if (pc + pf + pb + pt) == 100:
            st.success("Suma total: 100% ✅")
            st.session_state['ponderacion_criterios'] = {"COSTO": pc, "FACILIDAD": pf, "BENEFICIOS": pb, "TIEMPO": pt}
        else:
            st.error(f"La suma actual es {pc+pf+pb+pt}%. Debe ser 100%.")

    # 5.2 Matriz de Calificación
    st.markdown(f"### Matriz de Decisión (Rango de puntaje: 1 a {len(alts)})")
    nombres_alts = [a['nombre'] for a in alts]
    criterios = ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]
    
    # Inicializamos si cambió el número de alternativas
    if st.session_state['df_calificaciones'].empty or set(st.session_state['df_calificaciones'].index) != set(nombres_alts):
        st.session_state['df_calificaciones'] = pd.DataFrame(1, index=nombres_alts, columns=criterios)

    df_scores = st.data_editor(
        st.session_state['df_calificaciones'],
        column_config={c: st.column_config.NumberColumn(min_value=1, max_value=len(alts)) for c in criterios},
        use_container_width=True, key="ed_scores"
    )

    if not df_scores.equals(st.session_state['df_calificaciones']):
        st.session_state['df_calificaciones'] = df_scores
        guardar_datos_nube(); st.rerun()

    # 5.3 Tabla de Resultados Finales (Estilo Excel)
    st.markdown("### 📈 Tabla de Resultados Finales")
    res_finales = []
    pesos = st.session_state['ponderacion_criterios']
    
    for alt_n in nombres_alts:
        fila = {"Alternativa": alt_n}
        p_final = 0
        for crit in criterios:
            sc = df_scores.loc[alt_n, crit]
            w = pesos[crit] / 100
            fila[crit] = sc
            fila[f"Peso {crit}"] = f"{pesos[crit]}%"
            fila[f"Total {crit}"] = round(sc * w, 2)
            p_final += sc * w
        fila["CALIFICACIÓN FINAL"] = round(p_final, 2)
        res_finales.append(fila)

    df_final = pd.DataFrame(res_finales)
    st.dataframe(df_final, use_container_width=True, hide_index=True)

    # Identificación de la alternativa ganadora
    ganadora = df_final.loc[df_final['CALIFICACIÓN FINAL'].idxmax()]
    st.success(f"🏆 **Alternativa Seleccionada:** {ganadora['Alternativa']} (Puntaje: {ganadora['CALIFICACIÓN FINAL']})")
