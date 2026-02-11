import streamlit as st
import pandas as pd
import numpy as np
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos y seguridad
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: DATOS DEL ÁRBOL DE OBJETIVOS ---
objetivos_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN DE RELEVANCIA Y ALCANCE ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

# Lógica de persistencia para la tabla de selección inicial
if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    datos = []
    for idx_obj, obj in enumerate(objetivos_especificos):
        obj_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == obj_txt]
        for act_txt in hijas:
            datos.append({"OBJETIVO": obj_txt, "ACTIVIDAD": act_txt, "ENFOQUE": "NO", "ALCANCE": "NO"})
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos)

# Renderizado de tarjetas (mantenemos tu flujo actual de selección)
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

# --- 2. MATRIZ DE COMPATIBILIDAD TÉCNICA (NUEVA SECCIÓN) ---
st.subheader("🔄 2. Matriz de Interrelaciones Técnicas")

# Filtramos solo las combinaciones aprobadas
aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
].copy()

if aprobadas.empty:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    st.info("Compare cada combinación con las demás. Use **C** para Complementaria y **E** para Excluyente.")
    
    # Creamos identificadores cortos para la matriz (C1, C2...)
    aprobadas['ID'] = [f"C{i+1}" for i in range(len(aprobadas))]
    ids = aprobadas['ID'].tolist()
    labels = [f"{r['ID']}: {r['ACTIVIDAD'][:40]}..." for _, r in aprobadas.iterrows()]
    
    # Leyenda para el formulador
    with st.expander("Ver leyenda de combinaciones"):
        for l in labels: st.caption(l)

    # Inicialización de la matriz de compatibilidad en memoria
    if 'matriz_compatibilidad' not in st.session_state:
        st.session_state['matriz_compatibilidad'] = pd.DataFrame(
            "C", index=ids, columns=ids
        )
    
    # Editor de Matriz
    df_matriz = st.data_editor(
        st.session_state['matriz_compatibilidad'],
        column_config={id: st.column_config.SelectboxColumn(id, options=["C", "E"]) for id in ids},
        use_container_width=True,
        key="editor_matriz_interrelacion"
    )

    if not df_matriz.equals(st.session_state['matriz_compatibilidad']):
        st.session_state['matriz_compatibilidad'] = df_matriz
        guardar_datos_nube(); st.rerun()

    st.divider()

    # --- 3. CONFIGURACIÓN DE PAQUETES (ALTERNATIVAS) ---
    st.subheader("📦 3. Configuración de Paquetes (Alternativas)")
    
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa A: Rehabilitación")
        opciones_multiselect = [f"{r['ID']} - {r['ACTIVIDAD']}" for _, r in aprobadas.iterrows()]
        seleccion_alt = st.multiselect("Seleccione componentes para este paquete:", options=opciones_multiselect)
        
        # Lógica de validación de exclusividad en tiempo real
        if seleccion_alt:
            ids_sel = [s.split(" - ")[0] for s in seleccion_alt]
            hay_conflicto = False
            for i in ids_sel:
                for j in ids_sel:
                    if st.session_state['matriz_compatibilidad'].at[i, j] == "E":
                        st.error(f"❌ Conflicto: {i} y {j} son marcados como EXCLUYENTES. No pueden estar en el mismo paquete.")
                        hay_conflicto = True
                        break
                if hay_conflicto: break
            
            justificacion = st.text_area("Justificación técnica:")
            
            if st.button("🚀 Consolidar Alternativa", type="primary", disabled=hay_conflicto):
                nueva = {"nombre": nombre_alt, "componentes": seleccion_alt, "justificacion": justificacion}
                if 'lista_alternativas' not in st.session_state: st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva)
                guardar_datos_nube(); st.rerun()

# --- 4. VISUALIZACIÓN FINAL ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Alternativas Consolidadas")
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        if isinstance(alt, dict) and 'nombre' in alt:
            with st.expander(f"🔹 {alt['nombre']}"):
                st.write(alt['justificacion'])
                for comp in alt['componentes']: st.markdown(f"- {comp}")
                if st.button("🗑️ Eliminar", key=f"d_{idx}"):
                    st.session_state['lista_alternativas'].pop(idx)
                    guardar_datos_nube(); st.rerun()
