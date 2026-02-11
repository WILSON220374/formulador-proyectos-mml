import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# Inicializar memoria al cargar la página
inicializar_session()

st.title("🎯 1. Diagnóstico del Problema")

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA ---
def calcular_altura(texto, min_h=150):
    """Calcula la altura necesaria según la cantidad de caracteres y saltos de línea."""
    if not texto:
        return min_h
    # Estimamos 80 caracteres por línea y sumamos los saltos de línea reales
    lineas = texto.count('\n') + (len(texto) // 80)
    # Cada línea suele ocupar unos 22 píxeles
    altura_calculada = max(min_h, (lineas + 1) * 22)
    return altura_calculada

# --- CÁLCULO DE COMPLETITUD ---
datos = st.session_state['datos_problema']
campos = [datos['problema_central'], datos['sintomas'], datos['causas_inmediatas'], datos['factores_agravantes']]
completos = sum(1 for c in campos if c and len(c.strip()) > 10)
progreso = completos / len(campos)

st.progress(progreso)
st.caption(f"Nivel de Completitud: {int(progreso * 100)}%")

# --- SECCIÓN 1: EL PROBLEMA CENTRAL ---
with st.container(border=True):
    st.subheader("🎯 El Problema Central")
    st.markdown("Defina claramente la situación negativa. No lo confunda con la falta de una solución.")
    
    # Altura dinámica para el Problema Central
    h_p = calcular_altura(datos['problema_central'])
    p_central = st.text_area(
        "Descripción del Problema",
        value=datos['problema_central'],
        height=h_p,
        key="txt_p_central",
        help="Ej: La inoperancia de la PTAR genera contaminación en el río Chicamocha."
    )

# --- SECCIÓN 2: ANÁLISIS DE CAUSAS Y EFECTOS ---
st.subheader("🔍 Análisis de Causas y Efectos")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("**Síntomas (Efectos Visibles)**")
        h_s = calcular_altura(datos['sintomas'])
        sintomas = st.text_area(
            "Evidencias del problema:",
            value=datos['sintomas'],
            height=h_s,
            key="txt_sintomas"
        )

with col2:
    with st.container(border=True):
        st.markdown("**Causas Inmediatas**")
        h_c = calcular_altura(datos['causas_inmediatas'])
        causas = st.text_area(
            "¿Por qué ocurre el problema?",
            value=datos['causas_inmediatas'],
            height=h_c,
            key="txt_causas"
        )

# --- SECCIÓN 3: FACTORES AGRAVANTES ---
with st.container(border=True):
    st.subheader("⚠️ Factores Agravantes")
    st.markdown("Factores externos o del entorno que empeoran la situación.")
    h_a = calcular_altura(datos['factores_agravantes'])
    agravantes = st.text_area(
        "Factores externos:",
        value=datos['factores_agravantes'],
        height=h_a,
        key="txt_agravantes"
    )

# --- LÓGICA DE GUARDADO AUTOMÁTICO ---
# Si algún campo cambió, actualizamos sesión y nube
if (p_central != datos['problema_central'] or 
    sintomas != datos['sintomas'] or 
    causas != datos['causas_inmediatas'] or 
    agravantes != datos['factores_agravantes']):
    
    st.session_state['datos_problema'] = {
        "problema_central": p_central,
        "sintomas": sintomas,
        "causas_inmediatas": causas,
        "factores_agravantes": agravantes
    }
    guardar_datos_nube()
    st.rerun() # Refresca para aplicar la nueva altura calculada
