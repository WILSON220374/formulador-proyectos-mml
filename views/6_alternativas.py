import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. EJECUTAR INICIALIZACIÓN (Esto crea los "cajones" de memoria si no existen)
inicializar_session()

# 2. SEGURIDAD ADICIONAL: Verificar llaves específicas para evitar el KeyError
if 'relaciones_medios' not in st.session_state:
    st.session_state['relaciones_medios'] = []
if 'lista_alternativas' not in st.session_state:
    st.session_state['lista_alternativas'] = []

st.title("⚖️ 6. Análisis de Alternativas")

# --- RECUPERAR MEDIOS DEL ÁRBOL ---
# Usamos .get() con una lista vacía por seguridad
arbol = st.session_state.get('arbol_objetivos', {})
medios_dir = arbol.get("Medios Directos", [])
medios_ind = arbol.get("Medios Indirectos", [])

# Extraer solo el texto de las tarjetas
todos_los_medios = []
for m in (medios_dir + medios_ind):
    texto = m["texto"] if isinstance(m, dict) else m
    if texto:
        todos_los_medios.append(texto)

if not todos_los_medios:
    st.warning("⚠️ No se detectaron Medios en el Árbol de Objetivos. Por favor, asegúrate de haberlos guardado en la Fase 5.")
    st.stop()

# --- SECCIÓN 1: EVALUACIÓN DE RELACIONES ---
st.header("🧩 1. Evaluación de Relaciones entre Medios")
st.info("Antes de armar paquetes, definan qué medios son complementarios y cuáles se excluyen entre sí.")

with st.expander("➕ Definir Nueva Relación", expanded=True):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        m1 = st.selectbox("Seleccione Medio A", todos_los_medios, key="sel_m1")
    with col2:
        opciones_m2 = [m for m in todos_los_medios if m != m1]
        m2 = st.selectbox("Seleccione Medio B", opciones_m2, key="sel_m2")
    with col3:
        tipo = st.radio("Relación", ["🤝 Complementario", "⚔️ Excluyente"])

    if st.button("Registrar Vínculo", use_container_width=True):
        nueva_rel = {"Medio A": m1, "Medio B": m2, "Tipo": tipo}
        st.session_state['relaciones_medios'].append(nueva_rel)
        guardar_datos_nube() # Sincroniza con Supabase
        st.success("Relación registrada correctamente.")
        st.rerun()

# Mostrar tabla de relaciones existentes
if st.session_state['relaciones_medios']:
    st.subheader("Cuadro de Interrelaciones")
    df_rel = pd.DataFrame(st.session_state['relaciones_medios'])
    st.table(df_rel)
    if st.button("🗑️ Borrar Todas las Relaciones"):
        st.session_state['relaciones_medios'] = []
        guardar_datos_nube()
        st.rerun()

st.divider()

# --- SECCIÓN 2: EMPAQUETAMIENTO (ALTERNATIVAS) ---
st.header("📦 2. Configuración de Paquetes (Alternativas)")
st.markdown("Agrupen los medios para formar una Alternativa técnica viable.")

with st.container(border=True):
    nombre_alt = st.text_input("Nombre de la Alternativa:", placeholder="Ej: Alternativa de Mantenimiento Preventivo")
    medios_seleccionados = st.multiselect("Seleccione los Medios para este paquete:", todos_los_medios)
    
    # VALIDACIÓN LÓGICA EN TIEMPO REAL
    for rel in st.session_state['relaciones_medios']:
        if rel['Medio A'] in medios_seleccionados and rel['Medio B'] in medios_seleccionados:
            if "Excluyente" in rel['Tipo']:
                st.error(f"❌ ERROR LÓGICO: Estás mezclando medios EXCLUYENTES: **{rel['Medio A']}** y **{rel['Medio B']}**.")

    justificacion = st.text_area("Justificación técnica/económica de esta alternativa:")

    if st.button("🚀 Consolidar Alternativa"):
        if nombre_alt and medios_seleccionados:
            nueva_alt = {
                "Nombre": nombre_alt,
                "Medios": ", ".join(medios_seleccionados),
                "Análisis": justificacion
            }
            st.session_state['lista_alternativas'].append(nueva_alt)
            guardar_datos_nube()
            st.success(f"La Alternativa '{nombre_alt}' ha sido guardada en la nube.")
            st.rerun()
        else:
            st.warning("Completen el nombre y seleccionen al menos un medio.")

# --- TABLA DE RESULTADOS ---
if st.session_state['lista_alternativas']:
    st.divider()
    st.subheader("📋 Resumen de Alternativas Creadas")
    st.dataframe(pd.DataFrame(st.session_state['lista_alternativas']), use_container_width=True, hide_index=True)
