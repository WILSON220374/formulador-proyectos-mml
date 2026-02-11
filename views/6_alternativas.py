import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# --- 1. RECUPERAR MEDIOS DIRECTOS ---
arbol = st.session_state.get('arbol_objetivos', {})
medios_dir = arbol.get("Medios Directos", [])
todos_los_medios_dir = [m["texto"] if isinstance(m, dict) else m for m in medios_dir if m]

if not todos_los_medios_dir:
    st.warning("⚠️ No hay Medios Directos definidos. Asegúrate de guardar el Árbol de Objetivos en la Fase 5.")
    st.stop()

# --- SECCIÓN 1: EVALUACIÓN DE RELACIONES ---
st.header("🧩 1. Evaluación de Relaciones")
with st.expander("➕ Registrar Nueva Relación Técnia", expanded=False):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        m1 = st.selectbox("Medio Directo A", todos_los_medios_dir, key="sel_m1")
    with col2:
        m2 = st.selectbox("Medio Directo B", [m for m in todos_los_medios_dir if m != m1], key="sel_m2")
    with col3:
        tipo = st.radio("Vínculo", ["🤝 Complementario", "⚔️ Excluyente"])

    if st.button("Guardar Relación"):
        existe = any((rel['Medio A'] == m1 and rel['Medio B'] == m2) or (rel['Medio A'] == m2 and rel['Medio B'] == m1) for rel in st.session_state['relaciones_medios'])
        if existe:
            st.error("⚠️ Esta relación ya existe.")
        else:
            st.session_state['relaciones_medios'].append({"Medio A": m1, "Medio B": m2, "Tipo": tipo})
            guardar_datos_nube()
            st.rerun()

if st.session_state['relaciones_medios']:
    st.table(pd.DataFrame(st.session_state['relaciones_medios']))
    if st.button("🗑️ Borrar Todas las Relaciones"):
        st.session_state['relaciones_medios'] = []
        guardar_datos_nube()
        st.rerun()

st.divider()

# --- SECCIÓN 2: CONFIGURACIÓN DE PAQUETES ---
st.header("📦 2. Configuración de Paquetes (Alternativas)")
with st.container(border=True):
    nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Rehabilitación Integral de PTAR")
    ms_key = f"temp_sel_{st.session_state['alt_counter']}"
    
    medios_seleccionados = st.multiselect(
        "Seleccione Medios Directos complementarios:", 
        options=todos_los_medios_dir,
        key=ms_key
    )
    
    # Validación lógica
    if medios_seleccionados:
        for m in medios_seleccionados:
            for rel in st.session_state['relaciones_medios']:
                if "Excluyente" in rel['Tipo']:
                    if (rel['Medio A'] == m and rel['Medio B'] in medios_seleccionados) or (rel['Medio B'] == m and rel['Medio A'] in medios_seleccionados):
                        st.error(f"❌ Conflicto: **{rel['Medio A']}** y **{rel['Medio B']}** son excluyentes.")

    justificacion = st.text_area("Justificación técnica de la alternativa:")

    if st.button("🚀 Consolidar Alternativa"):
        if nombre_alt and medios_seleccionados:
            st.session_state['lista_alternativas'].append({
                "Nombre": nombre_alt,
                "Medios": ", ".join(medios_seleccionados),
                "Justificación": justificacion
            })
            st.session_state['alt_counter'] += 1
            guardar_datos_nube()
            st.success(f"Alternativa '{nombre_alt}' registrada.")
            st.rerun()

# --- SECCIÓN 3: RESUMEN Y GESTIÓN (NUEVO) ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Resumen y Gestión de Alternativas")
    st.info("💡 Para borrar una alternativa, selecciónala en la tabla y presiona la tecla 'Suprimir' o usa el icono de papelera.")
    
    df_resumen = pd.DataFrame(st.session_state['lista_alternativas'])
    
    # Usamos data_editor con num_rows="dynamic" para permitir borrado individual
    df_gestion = st.data_editor(
        df_resumen,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        key="editor_gestion_alternativas"
    )
    
    # Si el usuario borró alguna fila, actualizamos la memoria y la nube
    if not df_gestion.equals(df_resumen):
        st.session_state['lista_alternativas'] = df_gestion.to_dict('records')
        guardar_datos_nube()
        st.rerun()
