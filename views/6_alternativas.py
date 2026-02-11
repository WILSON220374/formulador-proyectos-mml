import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia: Carga de datos al inicio
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: OBTENER DATOS DEL PASO 5 ---
objetivos_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN DE RELEVANCIA Y ALCANCE ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

def inicializar_tabla_evaluacion():
    datos = []
    for idx_obj, obj in enumerate(objetivos_especificos):
        obj_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == obj_txt]
        for act_txt in hijas:
            datos.append({
                "OBJETIVO": obj_txt,
                "ACTIVIDAD": act_txt,
                "ENFOQUE": "NO",
                "ALCANCE": "NO",
                "NATURALEZA": "Complementaria"
            })
    return pd.DataFrame(datos)

if 'df_evaluacion_alternativas' not in st.session_state or \
   st.session_state['df_evaluacion_alternativas'].empty or \
   'NATURALEZA' not in st.session_state['df_evaluacion_alternativas'].columns:
    st.session_state['df_evaluacion_alternativas'] = inicializar_tabla_evaluacion()

df_master = st.session_state['df_evaluacion_alternativas']

for index, row in df_master.iterrows():
    with st.container(border=True):
        st.markdown(f"**📍 COMBINACIÓN {index + 1}**")
        st.write(f"**Objetivo Específico:** {row['OBJETIVO']}")
        st.write(f"**Actividad:** {row['ACTIVIDAD']}")
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            nuevo_enfoque = st.selectbox("¿Atiende el enfoque?", ["SI", "NO"], 
                                         index=0 if row["ENFOQUE"] == "SI" else 1, key=f"enf_{index}")
        with c2:
            nuevo_alcance = st.selectbox("¿Está en el alcance?", ["SI", "NO"], 
                                         index=0 if row["ALCANCE"] == "SI" else 1, key=f"alc_{index}")
        with c3:
            if nuevo_enfoque == "SI" and nuevo_alcance == "SI":
                st.success("✅ SELECCIONADO")
            else:
                st.error("❌ DESCARTADO")

        if nuevo_enfoque != row["ENFOQUE"] or nuevo_alcance != row["ALCANCE"]:
            st.session_state['df_evaluacion_alternativas'].at[index, "ENFOQUE"] = nuevo_enfoque
            st.session_state['df_evaluacion_alternativas'].at[index, "ALCANCE"] = nuevo_alcance
            guardar_datos_nube()
            st.rerun()

st.divider()

# --- 2. ANÁLISIS DE COMPLEMENTARIEDAD Y EXCLUSIVIDAD ---
st.subheader("🛠️ 2. Análisis de Complementariedad y Exclusividad")

opciones_aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
].copy()

if opciones_aprobadas.empty:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    st.info("Identifique si las actividades seleccionadas pueden ejecutarse juntas (Complementarias) o si son excluyentes.")
    
    df_naturaleza = st.data_editor(
        opciones_aprobadas,
        column_config={
            "OBJETIVO": st.column_config.TextColumn("OBJETIVO", disabled=True),
            "ACTIVIDAD": st.column_config.TextColumn("ACTIVIDAD", disabled=True),
            "ENFOQUE": None, "ALCANCE": None,
            "NATURALEZA": st.column_config.SelectboxColumn("NATURALEZA TÉCNICA", options=["Complementaria", "Excluyente"])
        },
        use_container_width=True, hide_index=True, key="editor_naturaleza_tecnica"
    )

    if not df_naturaleza.equals(opciones_aprobadas):
        for idx, row in df_naturaleza.iterrows():
            st.session_state['df_evaluacion_alternativas'].at[idx, "NATURALEZA"] = row["NATURALEZA"]
        guardar_datos_nube()
        st.rerun()

    st.divider()

    # --- 3. CONFIGURACIÓN DE PAQUETES ---
    st.subheader("📦 3. Configuración de Paquetes (Alternativas)")
    
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa 1: Solución Biológica")
        opciones_formateadas = [f"{r['ACTIVIDAD']} ({r['NATURALEZA']})" for _, r in df_naturaleza.iterrows()]
        items_sel_raw = st.multiselect("Seleccione componentes complementarios:", options=opciones_formateadas)
        items_limpios = [item.split(" (")[0] for item in items_sel_raw]
        justificacion = st.text_area("Justificación técnica de la alternativa:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary"):
            if nombre_alt and items_limpios:
                excluyentes_en_pack = [i for i in items_sel_raw if "Excluyente" in i]
                if len(excluyentes_en_pack) > 1:
                    st.error("⚠️ Error técnico: Ha seleccionado más de una actividad 'Excluyente'.")
                else:
                    nueva_alt = {"nombre": nombre_alt, "componentes": items_limpios, "justificacion": justificacion}
                    # Inicialización segura de la lista
                    if 'lista_alternativas' not in st.session_state or not isinstance(st.session_state['lista_alternativas'], list):
                        st.session_state['lista_alternativas'] = []
                    
                    st.session_state['lista_alternativas'].append(nueva_alt)
                    guardar_datos_nube()
                    st.rerun()

# --- 4. VISUALIZACIÓN PROTEGIDA (SOLUCIÓN AL KEYERROR) ---
# Solo intentamos mostrar alternativas si la lista existe y no es basura técnica
alternativas_guardadas = st.session_state.get('lista_alternativas')

if isinstance(alternativas_guardadas, list) and len(alternativas_guardadas) > 0:
    st.divider()
    st.subheader("📋 Alternativas Consolidadas")
    
    for idx, alt in enumerate(alternativas_guardadas):
        # PROTECCIÓN CRÍTICA: Verificamos que sea un diccionario con nombre antes de dibujar
        if isinstance(alt, dict) and 'nombre' in alt:
            with st.expander(f"🔹 Alternativa {idx+1}: {alt['nombre']}"):
                st.write(f"**Justificación:** {alt.get('justificacion', 'No definida')}")
                st.write("**Componentes:**")
                for comp in alt.get('componentes', []):
                    st.markdown(f"- {comp}")
                
                if st.button("🗑️ Eliminar", key=f"del_alt_{idx}"):
                    st.session_state['lista_alternativas'].pop(idx)
                    guardar_datos_nube()
                    st.rerun()
