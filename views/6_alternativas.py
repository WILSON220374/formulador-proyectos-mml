import streamlit as st
import pandas as pd
import itertools
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos con persistencia
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: DATOS DEL ÁRBOL DE OBJETIVOS ---
obj_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. SELECCIÓN DE ACTIVIDADES ---
st.subheader("📋 1. Selección de Actividades a Atender")

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

# --- 2. ANÁLISIS DE RELACIONES (SINCRONIZACIÓN DINÁMICA) ---
st.subheader("🔄 2. Análisis de Relaciones entre Objetivos")

aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
]
objetivos_seleccionados = aprobadas["OBJETIVO"].unique().tolist()

if len(objetivos_seleccionados) < 2:
    st.info("Seleccione actividades de al menos dos objetivos diferentes para realizar el análisis de exclusividad.")
else:
    # Generar todos los pares posibles matemáticamente
    pares_actuales = list(itertools.combinations(objetivos_seleccionados, 2))
    
    # Lógica de Sincronización: No borrar lo que el usuario ya evaluó
    if 'df_relaciones_objetivos' not in st.session_state:
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame(columns=["OBJETIVO A", "OBJETIVO B", "RELACIÓN"])

    df_existente = st.session_state['df_relaciones_objetivos']
    nuevas_filas = []

    for obj_a, obj_b in pares_actuales:
        # Verificar si este par ya existe en la tabla (en cualquier orden)
        existe = df_existente[
            ((df_existente["OBJETIVO A"] == obj_a) & (df_existente["OBJETIVO B"] == obj_b)) |
            ((df_existente["OBJETIVO A"] == obj_b) & (df_existente["OBJETIVO B"] == obj_a))
        ]
        if existe.empty:
            nuevas_filas.append({"OBJETIVO A": obj_a, "OBJETIVO B": obj_b, "RELACIÓN": "Por definir"})

    if nuevas_filas:
        st.session_state['df_relaciones_objetivos'] = pd.concat([df_existente, pd.DataFrame(nuevas_filas)], ignore_index=True)
        guardar_datos_nube()

    # Filtramos la tabla para mostrar solo pares cuyos objetivos siguen seleccionados
    df_mostrar = st.session_state['df_relaciones_objetivos'][
        st.session_state['df_relaciones_objetivos']["OBJETIVO A"].isin(objetivos_seleccionados) &
        st.session_state['df_relaciones_objetivos']["OBJETIVO B"].isin(objetivos_seleccionados)
    ]

    df_rel_editado = st.data_editor(
        df_mostrar,
        column_config={
            "OBJETIVO A": st.column_config.TextColumn("OBJETIVO A", disabled=True, width="large"),
            "OBJETIVO B": st.column_config.TextColumn("OBJETIVO B", disabled=True, width="large"),
            "RELACIÓN": st.column_config.SelectboxColumn("DECISIÓN TÉCNICA", options=["Por definir", "Complementario", "Excluyente"])
        },
        hide_index=True, use_container_width=True, key="tabla_rel_final"
    )

    if not df_rel_editado.equals(df_mostrar):
        # Actualizamos la memoria principal con los cambios del editor
        for idx, row in df_rel_editado.iterrows():
            st.session_state['df_relaciones_objetivos'].loc[idx, "RELACIÓN"] = row["RELACIÓN"]
        guardar_datos_nube(); st.rerun()

st.divider()

# --- 3. CONSOLIDACIÓN DE PAQUETES ---
st.subheader("📦 3. Configuración de Paquetes (Alternativas)")

if not aprobadas.empty:
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:")
        seleccion_act = st.multiselect("Componentes:", options=aprobadas["ACTIVIDAD"].unique().tolist())
        
        conflicto = False
        if seleccion_act:
            objs_en_pack = aprobadas[aprobadas["ACTIVIDAD"].isin(seleccion_act)]["OBJETIVO"].unique().tolist()
            # Validar contra la tabla de decisiones
            for o_a, o_b in itertools.combinations(objs_en_pack, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == o_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == o_a))
                ]
                if not rel.empty:
                    if rel.iloc[0]["RELACIÓN"] == "Excluyente":
                        st.error(f"❌ Conflicto: '{o_a}' y '{o_b}' son EXCLUYENTES.")
                        conflicto = True
                    elif rel.iloc[0]["RELACIÓN"] == "Por definir":
                        st.warning(f"⚠️ Pendiente: Debe definir la relación entre '{o_a}' y '{o_b}' arriba.")
                        conflicto = True

        if st.button("🚀 Consolidar Alternativa", type="primary", disabled=conflicto):
            if nombre_alt and seleccion_act:
                nueva = {"nombre": nombre_alt, "componentes": seleccion_act, "justificacion": st.text_area("Justificación:")}
                if 'lista_alternativas' not in st.session_state: st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva)
                guardar_datos_nube(); st.rerun()
