import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia: Carga de datos al inicio
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: OBTENER DATOS DEL PASO 5 ---
objetivos_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN DE OBJETIVOS Y ACTIVIDADES ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

# Texto de las preguntas completas para los tooltips
pregunta_enfoque = "¿EL OBJETIVO ATIENDE EL ENFOQUE PROPUESTO?"
pregunta_alcance = "¿ESTA DENTRO DEL ALCANCE DE QUIENES DESARROLLARAN EL PROYECTO?"

# Preparación de datos para la tabla
datos_evaluacion = []
for idx_obj, obj in enumerate(objetivos_especificos):
    obj_txt = obj["texto"] if isinstance(obj, dict) else obj
    hijas = [h["texto"] for h in actividades if isinstance(h, dict) and h.get("padre") == obj_txt]
    
    for act_txt in hijas:
        datos_evaluacion.append({
            "OBJETIVO": obj_txt,
            "ACTIVIDAD": act_txt,
            "ENFOQUE": "NO",
            "ALCANCE": "NO",
            "ESTADO": "❌ NO SELECCIONADO"
        })

if 'df_evaluacion_alternativas' not in st.session_state or st.session_state['df_evaluacion_alternativas'].empty:
    st.session_state['df_evaluacion_alternativas'] = pd.DataFrame(datos_evaluacion)

# Editor de tabla corregido (con tooltips y visualización optimizada)
df_editado = st.data_editor(
    st.session_state['df_evaluacion_alternativas'],
    column_config={
        "OBJETIVO": st.column_config.TextColumn("OBJETIVO", disabled=True, width="medium"),
        "ACTIVIDAD": st.column_config.TextColumn("ACTIVIDAD", disabled=True, width="medium"),
        "ENFOQUE": st.column_config.SelectboxColumn("¿ENFOQUE?", options=["SI", "NO"], help=pregunta_enfoque),
        "ALCANCE": st.column_config.SelectboxColumn("¿ALCANCE?", options=["SI", "NO"], help=pregunta_alcance),
        "ESTADO": st.column_config.TextColumn("ESTADO", disabled=True)
    },
    use_container_width=True,
    hide_index=True,
    key="tabla_evaluacion_alt_v2"
)

# Lógica de actualización de ESTADO
def actualizar_seleccion(df):
    def calcular_estado(row):
        if row["ENFOQUE"] == "SI" and row["ALCANCE"] == "SI":
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

# Filtramos solo lo seleccionado
opciones_seleccionadas = st.session_state['df_evaluacion_alternativas'][
    st.session_state['df_evaluacion_alternativas']["ESTADO"] == "✅ SELECCIONADO"
]

# VALIDACIÓN CRÍTICA: Si no hay nada seleccionado, mostramos el mensaje solicitado
if opciones_seleccionadas.empty:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Rehabilitación Integral")
        items_shared = st.multiselect(
            "Seleccione componentes aprobados para esta alternativa:",
            options=opciones_seleccionadas["ACTIVIDAD"].unique().tolist()
        )
        justificacion = st.text_area("Justificación técnica:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary"):
            if nombre_alt and items_shared:
                nueva_alt = {
                    "nombre": nombre_alt,
                    "componentes": items_shared,
                    "justificacion": justificacion
                }
                if 'lista_alternativas' not in st.session_state:
                    st.session_state['lista_alternativas'] = []
                
                st.session_state['lista_alternativas'].append(nueva_alt)
                guardar_datos_nube()
                st.rerun()
            else:
                st.error("Complete el nombre y seleccione componentes.")

# --- 3. VISUALIZACIÓN DE ALTERNATIVAS (PROTECCIÓN CONTRA KEYERROR) ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Alternativas Definidas")
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
        # Verificamos que 'nombre' exista en el diccionario antes de intentar usarlo
        if isinstance(alt, dict) and 'nombre' in alt:
            with st.expander(f"🔹 Alternativa {idx+1}: {alt['nombre']}"):
                st.write(f"**Justificación:** {alt.get('justificacion', 'N/A')}")
                st.write("**Componentes:**")
                for comp in alt.get('componentes', []):
                    st.markdown(f"- {comp}")
                if st.button("🗑️ Eliminar", key=f"del_alt_{idx}"):
                    st.session_state['lista_alternativas'].pop(idx)
                    guardar_datos_nube()
                    st.rerun()
