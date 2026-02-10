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

# Extraer texto de medios directos
todos_los_medios_dir = []
for m in medios_dir:
    texto = m["texto"] if isinstance(m, dict) else m
    if texto:
        todos_los_medios_dir.append(texto)

if not todos_los_medios_dir:
    st.warning("⚠️ No se detectaron Medios Directos en el Árbol de Objetivos. Por favor, asegúrate de haberlos guardado en la Fase 5.")
    st.stop()

# --- SECCIÓN 1: EVALUACIÓN DE RELACIONES (SOLO DIRECTOS) ---
st.header("🧩 1. Evaluación de Relaciones (Medios Directos)")
st.markdown("Definan qué medios directos son **Complementarios** (se necesitan ambos) o **Excluyentes** (son opciones distintas para el mismo fin).")

with st.expander("➕ Registrar Nueva Relación Técnica", expanded=True):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        m1 = st.selectbox("Medio Directo A", todos_los_medios_dir, key="sel_m1")
    with col2:
        opciones_m2 = [m for m in todos_los_medios_dir if m != m1]
        m2 = st.selectbox("Medio Directo B", opciones_m2, key="sel_m2")
    with col3:
        tipo = st.radio("Vínculo", ["🤝 Complementario", "⚔️ Excluyente"])

    if st.button("Guardar Relación", use_container_width=True):
        nueva_rel = {"Medio A": m1, "Medio B": m2, "Tipo": tipo}
        st.session_state['relaciones_medios'].append(nueva_rel)
        guardar_datos_nube()
        st.success("Relación técnica registrada.")
        st.rerun()

# Tabla de relaciones filtrada
if st.session_state['relaciones_medios']:
    df_rel = pd.DataFrame(st.session_state['relaciones_medios'])
    st.table(df_rel)
    if st.button("🗑️ Borrar Relaciones"):
        st.session_state['relaciones_medios'] = []
        guardar_datos_nube()
        st.rerun()

st.divider()

# --- SECCIÓN 2: EMPAQUETAMIENTO DINÁMICO ---
st.header("📦 2. Configuración de Paquetes (Alternativas)")
st.info("Seleccione un medio para iniciar. El sistema solo le mostrará los medios que son **Complementarios** al seleccionado.")

with st.container(border=True):
    nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa de Infraestructura Pesada")
    
    # --- LÓGICA DE FILTRADO DINÁMICO ---
    # 1. Ver qué medios han seleccionado ya
    seleccionados = st.session_state.get('temp_seleccion', [])
    
    # 2. Determinar opciones disponibles
    if not seleccionados:
        opciones_finales = todos_los_medios_dir
    else:
        # Buscar todos los complementos de CUALQUIERA de los seleccionados
        complementos = set()
        for s in seleccionados:
            for rel in st.session_state['relaciones_medios']:
                if "Complementario" in rel['Tipo']:
                    if rel['Medio A'] == s: complementos.add(rel['Medio B'])
                    if rel['Medio B'] == s: complementos.add(rel['Medio A'])
        
        # Las opciones son: lo ya seleccionado + sus complementarios
        opciones_finales = list(set(seleccionados) | complementos)

    medios_paquete = st.multiselect(
        "Medios Directos Complementarios:", 
        options=opciones_finales,
        key="temp_seleccion"
    )
    
    justificacion = st.text_area("Análisis de viabilidad de este paquete:")

    if st.button("🚀 Consolidar Alternativa"):
        if nombre_alt and medios_paquete:
            nueva_alt = {
                "Nombre": nombre_alt,
                "Medios": ", ".join(medios_paquete),
                "Justificación": justificacion
            }
            st.session_state['lista_alternativas'].append(nueva_alt)
            # Limpiar selección temporal
            del st.session_state['temp_seleccion']
            guardar_datos_nube()
            st.success(f"Alternativa '{nombre_alt}' registrada.")
            st.rerun()
        else:
            st.warning("Debes dar un nombre y elegir al menos un medio.")

# --- RESUMEN FINAL ---
if st.session_state['lista_alternativas']:
    st.divider()
    st.subheader("📋 Alternativas Definidas")
    st.dataframe(pd.DataFrame(st.session_state['lista_alternativas']), use_container_width=True, hide_index=True)
