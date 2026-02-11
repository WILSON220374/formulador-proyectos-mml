import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# Inicialización de seguridad para variables de sesión
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
with st.expander("➕ Registrar Nueva Relación Técnica", expanded=False):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        m1 = st.selectbox("Medio Directo A", todos_los_medios_dir, key="sel_m1")
    with col2:
        m2 = st.selectbox("Medio Directo B", [m for m in todos_los_medios_dir if m != m1], key="sel_m2")
    with col3:
        tipo = st.radio("Vínculo", ["🤝 Complementario", "⚔️ Excluyente"])

    if st.button("Guardar Relación"):
        # Evitar duplicados en cualquier orden
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

# --- SECCIÓN 2: CONFIGURACIÓN DE PAQUETES (CON RESETEO TOTAL) ---
st.header("📦 2. Configuración de Paquetes (Alternativas)")

# Usamos el contador para generar llaves únicas que limpien los campos
ctrl = st.session_state['alt_counter']

with st.container(border=True):
    # Aplicamos llaves dinámicas a todos los campos de entrada
    nombre_alt = st.text_input(
        "Nombre de la Alternativa:", 
        placeholder="Ej: Rehabilitación Integral de PTAR",
        key=f"input_nombre_{ctrl}" # Llave dinámica
    )
    
    medios_seleccionados = st.multiselect(
        "Seleccione Medios Directos complementarios:", 
        options=todos_los_medios_dir,
        key=f"input_medios_{ctrl}" # Llave dinámica
    )
    
    # Validación de conflictos en tiempo real
    if medios_seleccionados:
        for m in medios_seleccionados:
            for rel in st.session_state['relaciones_medios']:
                if "Excluyente" in rel['Tipo']:
                    if (rel['Medio A'] == m and rel['Medio B'] in medios_seleccionados) or (rel['Medio B'] == m and rel['Medio A'] in medios_seleccionados):
                        st.error(f"❌ Conflicto: **{rel['Medio A']}** y **{rel['Medio B']}** son excluyentes.")

    justificacion = st.text_area(
        "Justificación técnica de la alternativa:",
        key=f"input_just_{ctrl}" # Llave dinámica
    )

    if st.button("🚀 Consolidar Alternativa"):
        if nombre_alt and medios_seleccionados:
            # Guardamos la información en la lista
            st.session_state['lista_alternativas'].append({
                "Nombre": nombre_alt,
                "Medios": ", ".join(medios_seleccionados),
                "Justificación": justificacion
            })
            
            # Aumentamos el contador para forzar la limpieza de los campos
            st.session_state['alt_counter'] += 1
            guardar_datos_nube()
            st.success(f"Alternativa '{nombre_alt}' registrada con éxito.")
            st.rerun()
        else:
            st.warning("Debe asignar un nombre y seleccionar al menos un medio.")

# --- SECCIÓN 3: RESUMEN Y GESTIÓN ---
if st.session_state.get('lista_alternativas'):
    st.divider()
    st.subheader("📋 Resumen y Gestión de Alternativas")
    st.info("💡 **Para borrar:** Selecciona la fila en el recuadro de la izquierda y usa el icono de papelera 🗑️ que aparecerá.")
    
    df_resumen = pd.DataFrame(st.session_state['lista_alternativas'])
    
    # Editor dinámico para permitir ajustes o borrados
    df_gestion = st.data_editor(
        df_resumen,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=False, 
        key="editor_gestion_alternativas"
    )
    
    # Limpieza de filas vacías para evitar el error de "None"
    df_limpio = df_gestion.dropna(subset=['Nombre'])
    df_limpio = df_limpio[df_limpio['Nombre'].str.strip() != ""]
    
    if len(df_limpio) != len(df_resumen):
        st.session_state['lista_alternativas'] = df_limpio.to_dict('records')
        guardar_datos_nube()
        st.rerun()
