import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicializar memoria y configuración
inicializar_session()

# --- ENCABEZADO SUPERIOR CON LOGO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")

with col_titulo:
    st.title("🎯 1. Diagnóstico del Problema")

with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- CÁLCULO DE PROGRESO (Ajuste de seguridad con .get) ---
datos = st.session_state.get('datos_problema', {})
# Usamos .get() para evitar el KeyError si la llave no existe
p_central_val = datos.get('problema_central', "")
sintomas_val = datos.get('sintomas', "")
causas_val = datos.get('causas_inmediatas', "")
agravantes_val = datos.get('factores_agravantes', "")

campos = [p_central_val, sintomas_val, causas_val, agravantes_val]
completos = sum(1 for c in campos if c and len(str(c).strip()) > 10)
progreso = completos / len(campos)
st.progress(progreso)
st.caption(f"Nivel de Completitud: {int(progreso * 100)}%")

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA ---
def calcular_altura(texto, min_h=150):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 80)
    return max(min_h, (lineas + 1) * 22)

# --- SECCIÓN 1: EL PROBLEMA CENTRAL ---
with st.container(border=True):
    st.subheader("🎯 El Problema Central")
    st.markdown("Defina claramente la situación negativa.")
    
    h_p = calcular_altura(p_central_val)
    p_central = st.text_area(
        "Descripción", value=p_central_val, height=h_p,
        key="txt_p_central", label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- SECCIÓN 2: ANÁLISIS DE CAUSAS Y EFECTOS ---
st.subheader("🔍 Análisis de Causas y Efectos")
c1, c2 = st.columns(2)

with c1:
    with st.container(border=True):
        st.subheader("📉 Síntomas")
        h_s = calcular_altura(sintomas_val)
        sintomas = st.text_area("S", value=sintomas_val, height=h_s, key="txt_sintomas", label_visibility="collapsed")

with c2:
    with st.container(border=True):
        st.subheader("🛠️ Causas Inmediatas")
        h_c = calcular_altura(causas_val)
        causas = st.text_area("C", value=causas_val, height=h_c, key="txt_causas", label_visibility="collapsed")

# --- SECCIÓN 3: FACTORES AGRAVANTES ---
with st.container(border=True):
    st.subheader("⚠️ Factores Agravantes")
    h_a = calcular_altura(agravantes_val)
    agravantes = st.text_area("A", value=agravantes_val, height=h_a, key="txt_agravantes", label_visibility="collapsed")

# --- LÓGICA DE GUARDADO AUTOMÁTICO (Corregida) ---
if (p_central != p_central_val or sintomas != sintomas_val or 
    causas != causas_val or agravantes != agravantes_val):
    st.session_state['datos_problema'] = {
        "problema_central": p_central, 
        "sintomas": sintomas,
        "causas_inmediatas": causas, 
        "factores_agravantes": agravantes
    }
    guardar_datos_nube()
    st.rerun()
