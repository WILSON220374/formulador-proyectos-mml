import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia: Carga de datos al inicio
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: OBTENER DATOS DEL PASO 5 ---
# Usamos las etiquetas actualizadas: Medios Directos -> Objetivos Específicos | Medios Indirectos -> Actividades
objetivos_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN MEDIANTE TARJETAS (OPCIÓN 1) ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")
st.info("Lea cada combinación y evalúe si debe ser parte de la solución técnica del proyecto.")

# Preparación de la base de datos interna si no existe
if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    datos_iniciales = []
    for idx_obj, obj in enumerate(objetivos_especificos):
        obj_txt = obj["texto"] if isinstance(obj, dict) else obj
        hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == obj_txt]
        for act_txt in hijas:
            datos_iniciales.append({
                "OBJETIVO": obj_txt,
                "ACTIVIDAD": act_txt,
                "ENFOQUE": "NO",
                "ALCANCE": "NO"
            })
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos_iniciales)

# RENDERIZADO DE TARJETAS VERTICALES
df_temp = st.session_state['df_evaluacion_alternativas'].copy()

for index, row in df_temp.iterrows():
    with st.container(border=True):
        # Encabezado de la Tarjeta
        st.markdown(f"**📍 COMBINACIÓN {index + 1}**")
        
        # Texto Completo (Sin cortes)
        st.markdown(f"**Objetivo Específico:** {row['OBJETIVO']}")
        st.markdown(f"**Actividad:** {row['ACTIVIDAD']}")
        
        # Columnas de Evaluación dentro de la tarjeta
        c1, c2, c3 = st.columns([1, 1, 1])
        
        with c1:
            nuevo_enfoque = st.selectbox(
                "¿Atiende el enfoque?", 
                ["SI", "NO"], 
                index=0 if row["ENFOQUE"] == "SI" else 1,
                key=f"enf_{index}",
                help="¿El objetivo atiende el enfoque propuesto?"
            )
        with c2:
            nuevo_alcance = st.selectbox(
                "¿Está en el alcance?", 
                ["SI", "NO"], 
                index=0 if row["ALCANCE"] == "SI" else 1,
                key=f"alc_{index}",
                help="¿Está dentro del alcance de quienes desarrollarán el proyecto?"
            )
        with c3:
            # Indicador visual de selección
            if nuevo_enfoque == "SI" and nuevo_alcance == "SI":
                st.success("✅ SELECCIONADO")
            else:
                st.error("❌ DESCARTADO")

        # Actualización en tiempo real de la base de datos
        if nuevo_enfoque != row["ENFOQUE"] or nuevo_alcance != row["ALCANCE"]:
            st.session_state['df_evaluacion_alternativas'].at[index, "ENFOQUE"] = nuevo_enfoque
            st.session_state['df_evaluacion_alternativas'].at[index, "ALCANCE"] = nuevo_alcance
            guardar_datos_nube()
            st.rerun()

st.divider()

# --- 2. CONFIGURACIÓN DE PAQUETES (ALTERNATIVAS) ---
st.subheader("📦 2. Configuración de Paquetes (Alternativas)")

# Filtramos solo lo que tiene SI + SI
opciones_aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas']["ENFOQUE"] == "SI") & 
    (st.session_state['df_evaluacion_alternativas']["ALCANCE"] == "SI")
]

if opciones_aprobadas.empty:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Solución Tecnológica Integral")
        
        # Multiselect dinámico con actividades aprobadas
        items_alternativa = st.multiselect(
            "Seleccione componentes para esta alternativa:",
            options=opciones_aprobadas["ACTIVIDAD"].unique().tolist()
        )
        
        justificacion = st.text_area("Justificación técnica de la alternativa:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary"):
            if nombre_alt and items_alternativa:
                nueva_alt = {
                    "nombre": nombre_alt,
                    "componentes": items_alternativa,
                    "justificacion": justificacion
                }
                if 'lista_alternativas' not in st.session_state:
                    st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva_alt)
                guardar_datos_nube()
                st.success(f"Alternativa '{nombre_alt}' guardada.")
                st.rerun()
            else:
                st.error("Asigne un nombre y seleccione al menos un componente.")

# --- 3. VISUALIZACIÓN DE RESULTADOS ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Alternativas Definidas")
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        with st.expander(f"🔹 Alternativa {idx+1}: {alt.get('nombre', 'Sin nombre')}"):
            st.write(f"**Justificación:** {alt.get('justificacion', 'N/A')}")
            st.write("**Componentes incluidos:**")
            for comp in alt.get('componentes', []):
                st.markdown(f"- {comp}")
            if st.button("🗑️ Eliminar", key=f"del_alt_{idx}"):
                st.session_state['lista_alternativas'].pop(idx)
                guardar_datos_nube()
                st.rerun()
