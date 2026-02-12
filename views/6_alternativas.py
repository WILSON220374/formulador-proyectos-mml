import streamlit as st
import pandas as pd
import itertools
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos con persistencia en nube
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: DATOS DEL ÁRBOL DE OBJETIVOS ---
obj_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. SELECCIÓN: EVALUACIÓN DE RELEVANCIA Y ALCANCE ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    datos = []
    for obj in obj_especificos:
        o_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == o_txt]
        for a_txt in hijas:
            datos.append({"OBJETIVO": o_txt, "ACTIVIDAD": a_txt, "ENFOQUE": "NO", "ALCANCE": "NO"})
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos)

# Renderizado de tarjetas de selección
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

# --- 2. COMPARACIÓN: EVALUACIÓN DE RELACIONES TÉCNICAS ---
st.subheader("🤝 2. Evaluación de Relaciones Técnicas")

# Filtramos solo las combinaciones aprobadas
aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
].reset_index(drop=True)

if aprobadas.empty:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    st.info("Compare cada combinación con las demás. Indique si son **Complementarias** (pueden ir juntas) o **Excluyentes** (son caminos diferentes).")
    
    # Generamos pares únicos para comparar
    indices = aprobadas.index.tolist()
    pares = list(itertools.combinations(indices, 2))
    
    if not pares:
        st.info("Solo hay una combinación seleccionada. Es complementaria por defecto.")
    else:
        # Sincronización de la tabla de relaciones
        if 'df_relaciones_tecnicas' not in st.session_state:
            rel_iniciales = []
            for i, j in pares:
                txt_a = f"{aprobadas.iloc[i]['ACTIVIDAD']}"
                txt_b = f"{aprobadas.iloc[j]['ACTIVIDAD']}"
                rel_iniciales.append({
                    "COMBINACIÓN A": txt_a, "COMBINACIÓN B": txt_b, "RELACIÓN": "Complementaria"
                })
            st.session_state['df_relaciones_tecnicas'] = pd.DataFrame(rel_iniciales)

        # Editor de Relaciones Cara a Cara
        df_rel_editado = st.data_editor(
            st.session_state['df_relaciones_tecnicas'],
            column_config={
                "COMBINACIÓN A": st.column_config.TextColumn("COMBINACIÓN A", disabled=True, width="large"),
                "COMBINACIÓN B": st.column_config.TextColumn("COMBINACIÓN B", disabled=True, width="large"),
                "RELACIÓN": st.column_config.SelectboxColumn("RELACIÓN", options=["Complementaria", "Excluyente"])
            },
            hide_index=True, use_container_width=True, key="evaluador_pares"
        )

        if not df_rel_editado.equals(st.session_state['df_relaciones_tecnicas']):
            st.session_state['df_relaciones_tecnicas'] = df_rel_editado
            # Guardamos las exclusiones para validar paquetes
            st.session_state['relaciones_medios'] = df_rel_editado[df_rel_editado["RELACIÓN"] == "Excluyente"].values.tolist()
            guardar_datos_nube(); st.rerun()

st.divider()

# --- 3. CONSOLIDACIÓN: CONFIGURACIÓN DE PAQUETES ---
st.subheader("📦 3. Configuración de Paquetes (Alternativas)")

if not aprobadas.empty:
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa A: Rehabilitación")
        lista_opciones = aprobadas["ACTIVIDAD"].tolist()
        seleccion_alt = st.multiselect("Seleccione componentes para este paquete:", options=lista_opciones)
        
        # Validación de exclusividad en tiempo real
        conflicto = False
        if seleccion_alt and 'df_relaciones_tecnicas' in st.session_state:
            for _, rel in st.session_state['df_relaciones_tecnicas'].iterrows():
                if rel["RELACIÓN"] == "Excluyente" and rel["COMBINACIÓN A"] in seleccion_alt and rel["COMBINACIÓN B"] in seleccion_alt:
                    st.error(f"❌ Conflicto: '{rel['COMBINACIÓN A']}' y '{rel['COMBINACIÓN B']}' son EXCLUYENTES.")
                    conflicto = True
        
        justificacion = st.text_area("Justificación técnica de la alternativa:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary", disabled=conflicto):
            if nombre_alt and seleccion_alt:
                nueva = {"nombre": nombre_alt, "componentes": seleccion_alt, "justificacion": justificacion}
                if 'lista_alternativas' not in st.session_state or not isinstance(st.session_state['lista_alternativas'], list):
                    st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva)
                guardar_datos_nube(); st.rerun()

# --- 4. VISUALIZACIÓN PROTEGIDA ---
alternativas = st.session_state.get('lista_alternativas')
if isinstance(alternativas, list) and len(alternativas) > 0:
    st.divider()
    st.subheader("📋 Alternativas Consolidadas")
    for idx, alt in enumerate(alternativas):
        if isinstance(alt, dict) and 'nombre' in alt:
            with st.expander(f"🔹 {alt['nombre']}"):
                st.write(alt.get('justificacion', 'N/A'))
                for comp in alt.get('componentes', []): st.markdown(f"- {comp}")
                if st.button("🗑️ Eliminar", key=f"del_{idx}"):
                    st.session_state['lista_alternativas'].pop(idx)
                    guardar_datos_nube(); st.rerun()
