import streamlit as st
import pandas as pd
import itertools
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos con persistencia
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: DATOS DEL PASO 5 ---
obj_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN DE RELEVANCIA Y ALCANCE (TARJETAS) ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    datos = []
    for obj in obj_especificos:
        o_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == o_txt]
        for a_txt in hijas:
            datos.append({"OBJETIVO": o_txt, "ACTIVIDAD": a_txt, "ENFOQUE": "NO", "ALCANCE": "NO"})
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos)

# Renderizado de selección
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

# --- 2. ANÁLISIS DE RELACIONES ENTRE OBJETIVOS (NUEVA TABLA) ---
st.subheader("🔄 2. Análisis de Relaciones entre Objetivos")

# Filtramos los objetivos que tienen al menos una actividad aprobada
aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
]
objetivos_seleccionados = aprobadas["OBJETIVO"].unique().tolist()

if len(objetivos_seleccionados) < 1:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
elif len(objetivos_seleccionados) == 1:
    st.info("Solo hay un objetivo seleccionado. No requiere comparación de exclusividad.")
else:
    st.info("Compare los objetivos seleccionados para decidir si pueden ejecutarse juntos o si son excluyentes.")
    
    # Generar todos los pares de objetivos para comparar
    pares = list(itertools.combinations(objetivos_seleccionados, 2))
    
    # Inicializar o actualizar la tabla de relaciones en session_state
    if 'df_relaciones_objetivos' not in st.session_state:
        rel_datos = []
        for obj_a, obj_b in pares:
            rel_datos.append({"OBJETIVO A": obj_a, "OBJETIVO B": obj_b, "RELACIÓN": "Complementario"})
        st.session_state['df_relaciones_objetivos'] = pd.DataFrame(rel_datos)

    # Tabla para que el formulador decida
    df_rel_editado = st.data_editor(
        st.session_state['df_relaciones_objetivos'],
        column_config={
            "OBJETIVO A": st.column_config.TextColumn("OBJETIVO A", disabled=True, width="large"),
            "OBJETIVO B": st.column_config.TextColumn("OBJETIVO B", disabled=True, width="large"),
            "RELACIÓN": st.column_config.SelectboxColumn("DECISIÓN TÉCNICA", options=["Complementario", "Excluyente"])
        },
        hide_index=True, use_container_width=True, key="tabla_decisoria_objetivos"
    )

    if not df_rel_editado.equals(st.session_state['df_relaciones_objetivos']):
        st.session_state['df_relaciones_objetivos'] = df_rel_editado
        guardar_datos_nube(); st.rerun()

st.divider()

# --- 3. CONSOLIDACIÓN DE PAQUETES ---
st.subheader("📦 3. Configuración de Paquetes (Alternativas)")

if not aprobadas.empty:
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa Tecnológica")
        
        # El usuario selecciona Actividades, el sistema valida la exclusividad de sus Objetivos
        seleccion_actividades = st.multiselect(
            "Seleccione componentes para esta alternativa:", 
            options=aprobadas["ACTIVIDAD"].unique().tolist()
        )
        
        # VALIDACIÓN DE EXCLUSIVIDAD EN TIEMPO REAL
        conflicto = False
        if seleccion_actividades and 'df_relaciones_objetivos' in st.session_state:
            # Obtener los objetivos de las actividades seleccionadas
            objs_en_pack = aprobadas[aprobadas["ACTIVIDAD"].isin(seleccion_actividades)]["OBJETIVO"].unique().tolist()
            
            # Revisar si algún par en el paquete fue marcado como Excluyente
            for obj_a, obj_b in itertools.combinations(objs_en_pack, 2):
                rel = st.session_state['df_relaciones_objetivos'][
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == obj_a) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == obj_b)) |
                    ((st.session_state['df_relaciones_objetivos']["OBJETIVO A"] == obj_b) & (st.session_state['df_relaciones_objetivos']["OBJETIVO B"] == obj_a))
                ]
                if not rel.empty and rel.iloc[0]["RELACIÓN"] == "Excluyente":
                    st.error(f"❌ Conflicto: Los objetivos de estas actividades son EXCLUYENTES entre sí.")
                    conflicto = True
                    break
        
        justificacion = st.text_area("Justificación técnica:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary", disabled=conflicto):
            if nombre_alt and seleccion_actividades:
                nueva = {"nombre": nombre_alt, "componentes": seleccion_actividades, "justificacion": justificacion}
                if 'lista_alternativas' not in st.session_state or not isinstance(st.session_state['lista_alternativas'], list):
                    st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva)
                guardar_datos_nube(); st.rerun()

# --- 4. VISUALIZACIÓN ---
alternativas = st.session_state.get('lista_alternativas')
if isinstance(alternativas, list) and len(alternativas) > 0:
    st.divider()
    st.subheader("📋 Alternativas Consolidadas")
    for idx, alt in enumerate(alternativas):
        if isinstance(alt, dict) and 'nombre' in alt:
            with st.expander(f"🔹 {alt['nombre']}"):
                st.write(alt.get('justificacion', ''))
                for comp in alt.get('componentes', []): st.markdown(f"- {comp}")
                if st.button("🗑️ Eliminar", key=f"del_{idx}"):
                    st.session_state['lista_alternativas'].pop(idx)
                    guardar_datos_nube(); st.rerun()
