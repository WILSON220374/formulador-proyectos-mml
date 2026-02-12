import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicializar memoria y configuración
inicializar_session()

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA (Se mantiene) ---
def calcular_altura(texto, min_h=150):
    if not texto:
        return min_h
    lineas = texto.count('\n') + (len(texto) // 80)
    altura_calculada = max(min_h, (lineas + 1) * 22)
    return altura_calculada

# --- FUNCIÓN PARA MOSTRAR IMAGEN LATERAL ---
# Esta función se encarga de verificar y mostrar la imagen en su columna
def mostrar_logo_lateral():
    if os.path.exists("unnamed-1.jpg"):
        # use_container_width=True hará que la imagen ocupe todo el ancho de su columna,
        # mejorando la resolución y el tamaño.
        st.image("unnamed-1.jpg", use_container_width=True)

st.title("🎯 1. Diagnóstico del Problema")

# --- CÁLCULO DE PROGRESO ---
datos = st.session_state['datos_problema']
campos = [datos['problema_central'], datos['sintomas'], datos['causas_inmediatas'], datos['factores_agravantes']]
completos = sum(1 for c in campos if c and len(c.strip()) > 10)
progreso = completos / len(campos)
st.progress(progreso)
st.caption(f"Nivel de Completitud: {int(progreso * 100)}%")

# --- SECCIÓN 1: EL PROBLEMA CENTRAL ---
with st.container(border=True):
    st.subheader("🎯 El Problema Central")
    st.markdown("Defina claramente la situación negativa.")
    
    # DIVISIÓN EN COLUMNAS: [70% Texto | 30% Imagen]
    col_txt, col_img = st.columns([2.5, 1], vertical_alignment="center")
    
    with col_txt:
        h_p = calcular_altura(datos['problema_central'])
        p_central = st.text_area(
            "Descripción del Problema",
            value=datos['problema_central'],
            height=h_p,
            key="txt_p_central",
            label_visibility="collapsed"
        )
    with col_img:
        mostrar_logo_lateral()

st.markdown("<br>", unsafe_allow_html=True)

# --- SECCIÓN 2: ANÁLISIS DE CAUSAS Y EFECTOS ---
st.subheader("🔍 Análisis de Causas y Efectos")
main_col1, main_col2 = st.columns(2)

# Sub-sección Síntomas
with main_col1:
    with st.container(border=True):
        st.subheader("📉 Síntomas")
        st.caption("Efectos Visibles")
        
        # Columnas internas para esta sub-sección
        c_txt, c_img = st.columns([2, 1], vertical_alignment="center")
        with c_txt:
            h_s = calcular_altura(datos['sintomas'])
            sintomas = st.text_area(
                "Evidencias:",
                value=datos['sintomas'],
                height=h_s,
                key="txt_sintomas",
                label_visibility="collapsed"
            )
        with c_img:
             mostrar_logo_lateral()

# Sub-sección Causas
with main_col2:
    with st.container(border=True):
        st.subheader("🛠️ Causas Inmediatas")
        st.caption("Origen del Problema")
        
        # Columnas internas para esta sub-sección
        c_txt, c_img = st.columns([2, 1], vertical_alignment="center")
        with c_txt:
            h_c = calcular_altura(datos['causas_inmediatas'])
            causas = st.text_area(
                "¿Por qué ocurre?",
                value=datos['causas_inmediatas'],
                height=h_c,
                key="txt_causas",
                label_visibility="collapsed"
            )
        with c_img:
             mostrar_logo_lateral()

# --- SECCIÓN 3: FACTORES AGRAVANTES ---
with st.container(border=True):
    st.subheader("⚠️ Factores Agravantes")
    st.markdown("Factores externos que empeoran la situación.")
    
    # DIVISIÓN EN COLUMNAS: [70% Texto | 30% Imagen]
    col_txt, col_img = st.columns([2.5, 1], vertical_alignment="center")
    
    with col_txt:
        h_a = calcular_altura(datos['factores_agravantes'])
        agravantes = st.text_area(
            "Factores externos:",
            value=datos['factores_agravantes'],
            height=h_a,
            key="txt_agravantes",
            label_visibility="collapsed"
        )
    with col_img:
        mostrar_logo_lateral()

# --- LÓGICA DE GUARDADO AUTOMÁTICO ---
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
    st.rerun()
