import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicializar memoria y configuración
inicializar_session()

# --- ENCABEZADO SUPERIOR CON LOGO (ZONA AMARILLA) ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")

with col_titulo:
    st.title("🎯 1. Diagnóstico del Problema")

with col_logo:
    # Ubicación en la parte superior derecha con alta resolución
    # Se actualiza use_container_width por width="stretch" para evitar avisos en logs
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", width="stretch")

# --- CÁLCULO DE PROGRESO ---
datos = st.session_state['datos_problema']
campos = [datos['problema_central'], datos['sintomas'], datos['causas_inmediatas'], datos['factores_agravantes']]
completos = sum(1 for c in campos if c and len(c.strip()) > 10)
progreso = completos / len(campos)
st.progress(progreso)
st.caption(f"Nivel de Completitud: {int(progreso * 100)}%")

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA ---
def calcular_altura(texto, min_h=150):
    if not texto: return min_h
    lineas = texto.count('\n') + (len(texto) // 80)
    return max(min_h, (lineas + 1) * 22)

# --- SECCIÓN 1: EL PROBLEMA CENTRAL ---
with st.container(border=True):
    st.subheader("🎯 El Problema Central")
    st.markdown("Defina claramente la situación negativa.")
    
    h_p = calcular_altura(datos['problema_central'])
    p_central = st.text_area(
        "Descripción", value=datos['problema_central'], height=h_p,
        key="txt_p_central", label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- SECCIÓN 2: ANÁLISIS DE CAUSAS Y EFECTOS ---
st.subheader("🔍 Análisis de Causas y Efectos")
c1, c2 = st.columns(2)

with c1:
    with st.container(border=True):
        st.subheader("📉 Síntomas")
        h_s = calcular_altura(datos['sintomas'])
        sintomas = st.text_area("S", value=datos['sintomas'], height=h_s, key="txt_sintomas", label_visibility="collapsed")

with c2:
    with st.container(border=True):
        st.subheader("🛠️ Causas Inmediatas")
        h_c = calcular_altura(datos['causas_inmediatas'])
        causas = st.text_area("C", value=datos['causas_inmediatas'], height=h_c, key="txt_causas", label_visibility="collapsed")

# --- SECCIÓN 3: FACTORES AGRAVANTES ---
with st.container(border=True):
    st.subheader("⚠️ Factores Agravantes")
    h_a = calcular_altura(datos['factores_agravantes'])
    agravantes = st.text_area("A", value=datos['factores_agravantes'], height=h_a, key="txt_agravantes", label_visibility="collapsed")

# --- LÓGICA DE GUARDADO AUTOMÁTICO ---
# Se corrigió 'síntomas' por 'sintomas' para evitar el NameError
if (p_central != datos['problema_central'] or sintomas != datos['sintomas'] or 
    causas != datos['causas_inmediatas'] or agravantes != datos['factores_agravantes']):
    st.session_state['datos_problema'] = {
        "problema_central": p_central, "sintomas": sintomas,
        "causas_inmediatas": causas, "factores_agravantes": agravantes
    }
    guardar_datos_nube()
    st.rerun()
