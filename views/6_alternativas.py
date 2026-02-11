import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia: Carga de datos al inicio
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: OBTENER DATOS DEL PASO 5 ---
# Usamos las llaves internas definidas en session_state
objetivos_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN DE OBJETIVOS Y ACTIVIDADES ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")
st.info("Solo las combinaciones con 'SI' en ambas preguntas serán elegibles para conformar alternativas.")

# Preparación de datos para la tabla de evaluación
datos_evaluacion = []
for idx_obj, obj in enumerate(objetivos_especificos):
    obj_txt = obj["texto"] if isinstance(obj, dict) else obj
    # Buscamos actividades vinculadas a este objetivo
    hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == obj_txt]
    
    for idx_act, act_txt in enumerate(hijas):
        datos_evaluacion.append({
            "OBJETIVO": f"{idx_obj + 1}. {obj_txt[:50]}...",
            "ACTIVIDAD": act_txt,
            "ATIENDE EL ENFOQUE": "NO",
            "DENTRO DEL ALCANCE": "NO",
            "ESTADO": "NO SELECCIONADO"
        })

# Inicializar dataframe en session_state para persistencia
if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos_evaluacion)

# Editor de tabla con lógica de selección automática
df_editado = st.data_editor(
    st.session_state['df_evaluacion_alternativas'],
    column_config={
        "OBJETIVO": st.column_config.TextColumn("OBJETIVO", disabled=True),
        "ACTIVIDAD": st.column_config.TextColumn("ACTIVIDAD", disabled=True),
        "ATIENDE EL ENFOQUE": st.column_config.SelectboxColumn("¿ENFOQUE?", options=["SI", "NO"]),
        "DENTRO DEL ALCANCE": st.column_config.SelectboxColumn("¿ALCANCE?", options=["SI", "NO"]),
        "ESTADO": st.column_config.TextColumn("ESTADO", disabled=True)
    },
    use_container_width=True,
    hide_index=True,
    key="tabla_evaluacion_alternativas"
)

# Lógica de actualización de ESTADO
def actualizar_seleccion(df):
    def calcular_estado(row):
        if row["ATIENDE EL ENFOQUE"] == "SI" and row["DENTRO DEL ALCANCE"] == "SI":
            return "✅ SELECCIONADO"
        return "❌ NO SELECCIONADO"
    df["ESTADO"] = df.apply(calcular_estado, axis=1)
    return df

if not df_editado.equals(st.session_state['df_evaluacion_alternativas']):
    st.session_state['df_evaluacion_alternativas'] = actualizar_seleccion(df_editado)
    guardar_datos_nube()
    st.rerun()

st.divider()

# --- 2. CONFIGURACIÓN DE PAQUETES (ALTERNATIVAS) ---
st.subheader("📦 2. Configuración de Paquetes (Alternativas)")

# Filtramos solo lo seleccionado en la fase anterior
opciones_seleccionadas = st.session_state['df_evaluacion_alternativas'][
    st.session_state['df_evaluacion_alternativas']["ESTADO"] == "✅ SELECCIONADO"
]

if opciones_seleccionadas.empty:
    st.warning("Debe seleccionar al menos una combinación de Objetivo/Actividad en la tabla superior (SI + SI).")
else:
    # Formulario para consolidar alternativas
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Rehabilitación Integral de PTAR")
        with col2:
            st.write("") # Espaciador
            
        # Multiselect que solo muestra lo filtrado
        items_seleccionados = st.multiselect(
            "Seleccione los componentes complementarios para esta alternativa:",
            options=opciones_seleccionadas["ACTIVIDAD"].tolist(),
            help="Solo aparecen las actividades aprobadas en la evaluación superior."
        )
        
        justificacion = st.text_area("Justificación técnica de la alternativa:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary"):
            if nombre_alt and items_seleccionados:
                nueva_alt = {
                    "nombre": nombre_alt,
                    "componentes": items_shared,
                    "justificacion": justificacion
                }
                if 'lista_alternativas' not in st.session_state:
                    st.session_state['lista_alternativas'] = []
                
                st.session_state['lista_alternativas'].append(nueva_alt)
                guardar_datos_nube()
                st.success(f"Alternativa '{nombre_alt}' guardada con éxito.")
                st.rerun()
            else:
                st.error("Por favor, asigne un nombre y seleccione al menos una actividad.")

# --- 3. VISUALIZACIÓN DE ALTERNATIVAS CONSOLIDADAS ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Alternativas Definidas")
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        with st.expander(f"🔹 Alternativa {idx+1}: {alt['nombre']}"):
            st.write(f"**Justificación:** {alt['justificacion']}")
            st.write("**Componentes incluidos:**")
            for comp in alt['componentes']:
                st.markdown(f"- {comp}")
            if st.button("🗑️ Eliminar", key=f"del_alt_{idx}"):
                st.session_state['lista_alternativas'].pop(idx)
                guardar_datos_nube()
                st.rerun()
