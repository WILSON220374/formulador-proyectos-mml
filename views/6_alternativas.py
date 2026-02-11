import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia: Carga de datos al inicio
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- CONTEXTO: OBTENER DATOS DEL PASO 5 ---
# Usamos las llaves internas del árbol de objetivos
objetivos_especificos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
actividades = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# --- 1. EVALUACIÓN MEDIANTE TARJETAS (OPCIÓN 1) ---
st.subheader("📋 1. Evaluación de Relevancia y Alcance")

# LÓGICA DE SEGURIDAD: Inicialización y validación de columnas
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
                "ALCANCE": "NO"
            })
    return pd.DataFrame(datos)

# Si la tabla no existe, es vieja o está vacía, la reiniciamos
if 'df_evaluacion_alternativas' not in st.session_state or \
   st.session_state['df_evaluacion_alternativas'].empty or \
   'ENFOQUE' not in st.session_state['df_evaluacion_alternativas'].columns:
    st.session_state['df_evaluacion_alternativas'] = inicializar_tabla_evaluacion()

df_temp = st.session_state['df_evaluacion_alternativas']

# RENDERIZADO DE TARJETAS CON TEXTO COMPLETO
for index, row in df_temp.iterrows():
    with st.container(border=True):
        st.markdown(f"**📍 COMBINACIÓN {index + 1}**")
        
        # Mostramos el texto completo (sin cortes)
        st.write(f"**Objetivo Específico:** {row['OBJETIVO']}")
        st.write(f"**Actividad:** {row['ACTIVIDAD']}")
        
        c1, c2, c3 = st.columns([1, 1, 1])
        
        with c1:
            # Validación defensiva para evitar el KeyError en el selectbox
            val_enfoque = row.get("ENFOQUE", "NO")
            nuevo_enfoque = st.selectbox(
                "¿Atiende el enfoque?", ["SI", "NO"], 
                index=0 if val_enfoque == "SI" else 1,
                key=f"enf_{index}"
            )
        with c2:
            val_alcance = row.get("ALCANCE", "NO")
            nuevo_alcance = st.selectbox(
                "¿Está en el alcance?", ["SI", "NO"], 
                index=0 if val_alcance == "SI" else 1,
                key=f"alc_{index}"
            )
        with c3:
            # Indicador de estado basado en la lógica SI+SI
            if nuevo_enfoque == "SI" and nuevo_alcance == "SI":
                st.success("✅ SELECCIONADO")
            else:
                st.error("❌ DESCARTADO")

        # Guardar cambios si hay interacción
        if nuevo_enfoque != row.get("ENFOQUE") or nuevo_alcance != row.get("ALCANCE"):
            st.session_state['df_evaluacion_alternativas'].at[index, "ENFOQUE"] = nuevo_enfoque
            st.session_state['df_evaluacion_alternativas'].at[index, "ALCANCE"] = nuevo_alcance
            guardar_datos_nube()
            st.rerun()

st.divider()

# --- 2. CONFIGURACIÓN DE PAQUETES ---
st.subheader("📦 2. Configuración de Paquetes (Alternativas)")

# Filtro de aprobados (SI + SI)
opciones_aprobadas = st.session_state['df_evaluacion_alternativas'][
    (st.session_state['df_evaluacion_alternativas'].get("ENFOQUE") == "SI") & 
    (st.session_state['df_evaluacion_alternativas'].get("ALCANCE") == "SI")
]

if opciones_aprobadas.empty:
    st.warning("⚠️ DEBE SELECCIONAR POR LO MENOS UNA COMBINACION DE OBJETIVO Y ACTIVIDAD RESPONDIENDO SI A AMBOS CRITERIOS")
else:
    with st.container(border=True):
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Solución Integral de PTAR")
        
        # Solo muestra actividades que pasaron la evaluación
        items_alt = st.multiselect(
            "Seleccione componentes para esta alternativa:",
            options=opciones_aprobadas["ACTIVIDAD"].unique().tolist()
        )
        
        justificacion = st.text_area("Justificación técnica:")
        
        if st.button("🚀 Consolidar Alternativa", type="primary"):
            if nombre_alt and items_alt:
                nueva_alt = {"nombre": nombre_alt, "componentes": items_alt, "justificacion": justificacion}
                if 'lista_alternativas' not in st.session_state:
                    st.session_state['lista_alternativas'] = []
                st.session_state['lista_alternativas'].append(nueva_alt)
                guardar_datos_nube()
                st.rerun()
            else:
                st.error("Asigne un nombre y seleccione componentes.")

# --- 3. VISUALIZACIÓN ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Alternativas Definidas")
    for idx, alt in enumerate(st.session_state['lista_alternativas']):
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
