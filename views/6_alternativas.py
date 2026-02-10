import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# Inicialización de seguridad
inicializar_session()

if 'relaciones_medios' not in st.session_state:
    st.session_state['relaciones_medios'] = []
if 'lista_alternativas' not in st.session_state:
    st.session_state['lista_alternativas'] = []

st.title("⚖️ 6. Análisis de Alternativas")

# --- 1. RECUPERAR SOLO MEDIOS DIRECTOS ---
arbol = st.session_state.get('arbol_objetivos', {})
medios_dir = arbol.get("Medios Directos", [])

todos_los_medios_dir = []
for m in medios_dir:
    texto = m["texto"] if isinstance(m, dict) else m
    if texto:
        todos_los_medios_dir.append(texto)

if not todos_los_medios_dir:
    st.warning("⚠️ No se detectaron Medios Directos. Asegúrate de haber guardado el Árbol de Objetivos en la Fase 5.")
    st.stop()

# --- SECCIÓN 1: EVALUACIÓN DE RELACIONES ---
st.header("🧩 1. Evaluación de Relaciones (Medios Directos)")
st.markdown("Definan las relaciones técnicas. El sistema evitará que dupliquen parejas ya existentes.")

with st.expander("➕ Registrar Nueva Relación Técnica", expanded=True):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        m1 = st.selectbox("Medio Directo A", todos_los_medios_dir, key="sel_m1")
    with col2:
        # Evitar seleccionar el mismo medio
        opciones_m2 = [m for m in todos_los_medios_dir if m != m1]
        m2 = st.selectbox("Medio Directo B", opciones_m2, key="sel_m2")
    with col3:
        tipo = st.radio("Vínculo", ["🤝 Complementario", "⚔️ Excluyente"])

    if st.button("Guardar Relación", use_container_width=True):
        # VALIDACIÓN DE DUPLICADOS (A-B o B-A)
        existe = any(
            (rel['Medio A'] == m1 and rel['Medio B'] == m2) or 
            (rel['Medio A'] == m2 and rel['Medio B'] == m1) 
            for rel in st.session_state['relaciones_medios']
        )
        
        if existe:
            st.error(f"⚠️ Ya existe una relación registrada entre estos dos medios. No es necesario duplicarla.")
        else:
            nueva_rel = {"Medio A": m1, "Medio B": m2, "Tipo": tipo}
            st.session_state['relaciones_medios'].append(nueva_rel)
            guardar_datos_nube()
            st.success("Relación técnica registrada con éxito.")
            st.rerun()

# Tabla de relaciones
if st.session_state['relaciones_medios']:
    df_rel = pd.DataFrame(st.session_state['relaciones_medios'])
    st.table(df_rel)
    if st.button("🗑️ Borrar Todas las Relaciones"):
        st.session_state['relaciones_medios'] = []
        guardar_datos_nube()
        st.rerun()

st.divider()

# --- SECCIÓN 2: EMPAQUETAMIENTO DINÁMICO ---
st.header("📦 2. Configuración de Paquetes (Alternativas)")
st.info("El sistema solo permite empaquetar medios que hayan sido marcados como **Complementarios** entre sí.")

with st.container(border=True):
    nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa de Optimización Estructural")
    
    # Lógica de filtrado por complementariedad
    seleccionados = st.session_state.get('temp_seleccion', [])
    
    if not seleccionados:
        opciones_finales = todos_los_medios_dir
    else:
        # Solo mostrar medios que sean complementarios a TODOS los ya seleccionados
        complementos_posibles = set(todos_los_medios_dir)
        for s in seleccionados:
            mis_complementos = {s} # Incluirse a sí mismo
            for rel in st.session_state['relaciones_medios']:
                if "Complementario" in rel['Tipo']:
                    if rel['Medio A'] == s: mis_complementos.add(rel['Medio B'])
                    if rel['Medio B'] == s: mis_complementos.add(rel['Medio A'])
            complementos_posibles &= mis_complementos # Intersección de complementos
        
        opciones_finales = list(complementos_posibles)

    medios_paquete = st.multiselect(
        "Seleccione Medios Directos compatibles:", 
        options=opciones_finales,
        key="temp_seleccion"
    )
    
    justificacion = st.text_area("Justificación técnica del paquete:")

    if st.button("🚀 Consolidar Alternativa"):
        if nombre_alt and medios_paquete:
            nueva_alt = {
                "Nombre": nombre_alt,
                "Medios": ", ".join(medios_paquete),
                "Justificación": justificacion
            }
            st.session_state['lista_alternativas'].append(nueva_alt)
            # Limpiar selección temporal para el siguiente paquete
            if 'temp_seleccion' in st.session_state:
                st.session_state['temp_seleccion'] = []
            guardar_datos_nube()
            st.success(f"Alternativa '{nombre_alt}' guardada.")
            st.rerun()

if st.session_state.get('lista_alternativas'):
    st.subheader("📋 Resumen de Alternativas")
    st.dataframe(pd.DataFrame(st.session_state['lista_alternativas']), use_container_width=True, hide_index=True)
