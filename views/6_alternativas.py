import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- RECUPERAR MEDIOS DEL ÁRBOL ---
medios_dir = st.session_state['arbol_objetivos'].get("Medios Directos", [])
medios_ind = st.session_state['arbol_objetivos'].get("Medios Indirectos", [])
todos_los_medios = [m["texto"] if isinstance(m, dict) else m for m in medios_dir + medios_ind if m]

if not todos_los_medios:
    st.warning("⚠️ No hay medios definidos en el Árbol de Objetivos. Regresa al paso 5.")
    st.stop()

# --- SECCIÓN 1: EVALUACIÓN DE RELACIONES ---
st.header("🧩 1. Evaluación de Relaciones entre Medios")
st.markdown("Identifiquen qué medios se potencian (complementarios) y cuáles son opciones diferentes para el mismo fin (excluyentes).")

with st.expander("➕ Definir Relación entre Medios", expanded=True):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        m1 = st.selectbox("Medio A", todos_los_medios, key="m1")
    with col2:
        # Filtramos para no comparar un medio consigo mismo
        opciones_m2 = [m for m in todos_los_medios if m != m1]
        m2 = st.selectbox("Medio B", opciones_m2, key="m2")
    with col3:
        tipo = st.radio("Tipo", ["🤝 Complementario", "⚔️ Excluyente"])

    if st.button("Registrar Relación"):
        nueva_rel = {"Medio A": m1, "Medio B": m2, "Tipo": tipo}
        st.session_state['relaciones_medios'].append(nueva_rel)
        guardar_datos_nube()
        st.rerun()

if st.session_state['relaciones_medios']:
    df_rel = pd.DataFrame(st.session_state['relaciones_medios'])
    st.table(df_rel)
    if st.button("🗑️ Limpiar Relaciones"):
        st.session_state['relaciones_medios'] = []
        guardar_datos_nube()
        st.rerun()

st.divider()

# --- SECCIÓN 2: EMPAQUETAMIENTO (ALTERNATIVAS) ---
st.header("📦 2. Configuración de Paquetes (Alternativas)")
st.markdown("Ahora, agrupen los medios complementarios para formar una Alternativa viable.")

with st.container(border=True):
    nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa Tecnológica")
    medios_seleccionados = st.multiselect("Seleccione los Medios para este paquete:", todos_los_medios)
    
    # Lógica de validación visual
    for rel in st.session_state['relaciones_medios']:
        if rel['Medio A'] in medios_seleccionados and rel['Medio B'] in medios_seleccionados:
            if "Excluyente" in rel['Tipo']:
                st.error(f"⚠️ ¡Cuidado! Estás mezclando medios EXCLUYENTES: **{rel['Medio A']}** y **{rel['Medio B']}**.")

    justificacion = st.text_area("Justificación del Paquete (Análisis técnico/económico):")

    if st.button("🚀 Crear Paquete / Alternativa"):
        if nombre_alt and medios_seleccionados:
            nueva_alt = {
                "Nombre": nombre_alt,
                "Medios": ", ".join(medios_seleccionados),
                "Análisis": justificacion
            }
            if 'lista_alternativas' not in st.session_state:
                st.session_state['lista_alternativas'] = []
            
            st.session_state['lista_alternativas'].append(nueva_alt)
            guardar_datos_nube()
            st.success(f"Paquete '{nombre_alt}' creado exitosamente.")
            st.rerun()

# --- TABLA FINAL ---
if st.session_state.get('lista_alternativas'):
    st.subheader("📋 Alternativas Consolidadas")
    st.dataframe(pd.DataFrame(st.session_state['lista_alternativas']), use_container_width=True, hide_index=True)
