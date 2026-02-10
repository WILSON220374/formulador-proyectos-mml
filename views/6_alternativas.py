import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# Asegurar persistencia y memoria
inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")
st.markdown("""
En esta fase, deben identificar las **Estrategias de Solución**. 
Miren sus **Medios** y decidan cuáles pueden agruparse para formar una alternativa técnica y económicamente viable.
""")

# --- RECUPERAR DATOS DEL ÁRBOL ---
medios_directos = st.session_state['arbol_objetivos'].get("Medios Directos", [])
medios_indirectos = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])

# Unificar medios para la selección
todos_los_medios = []
for m in medios_directos:
    texto = m["texto"] if isinstance(m, dict) else m
    if texto: todos_los_medios.append(f"Directo: {texto}")
for m in medios_indirectos:
    texto = m["texto"] if isinstance(m, dict) else m
    if texto: todos_los_medios.append(f"Indirecto: {texto}")

if not todos_los_medios:
    st.warning("⚠️ No hay Medios definidos. Por favor, completa y guarda el Árbol de Objetivos primero.")
    st.stop()

# --- INTERFAZ DE CREACIÓN ---
with st.container(border=True):
    st.subheader("➕ Definir Nueva Alternativa")
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Construcción de Variante")
        medios_sel = st.multiselect("Medios incluidos en esta opción:", todos_los_medios)
    
    with col2:
        analisis = st.text_area("Justificación / Análisis:", placeholder="¿Por qué esta combinación es viable?")

    if st.button("🚀 Registrar Alternativa", use_container_width=True):
        if nombre_alt and medios_sel:
            # Inicializar lista si no existe
            if 'lista_alternativas' not in st.session_state:
                st.session_state['lista_alternativas'] = []
            
            # Guardar nueva alternativa
            st.session_state['lista_alternativas'].append({
                "Nombre": nombre_alt,
                "Medios": ", ".join(medios_sel),
                "Justificación": analisis
            })
            st.success(f"Alternativa '{nombre_alt}' registrada.")
            st.rerun()
        else:
            st.error("Completa el nombre y selecciona al menos un medio.")

# --- VISUALIZACIÓN DE RESULTADOS ---
if 'lista_alternativas' in st.session_state and st.session_state['lista_alternativas']:
    st.divider()
    st.subheader("📋 Comparativa de Estrategias")
    df_alt = pd.DataFrame(st.session_state['lista_alternativas'])
    st.dataframe(df_alt, use_container_width=True, hide_index=True)
    
    if st.button("🗑️ Borrar Todo", type="secondary"):
        st.session_state['lista_alternativas'] = []
        st.rerun()
