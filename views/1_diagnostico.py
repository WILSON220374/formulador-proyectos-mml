import streamlit as st
import time

# --- CONFIGURACIÓN Y ESTADO ---
st.header("1. Diagnóstico del Problema")

if 'datos_problema' not in st.session_state:
    st.session_state['datos_problema'] = {}

datos = st.session_state['datos_problema']

# --- LÓGICA DE PROGRESO ---
campos_totales = 4
campos_llenos = 0
if datos.get('problema_central'): campos_llenos += 1
if datos.get('sintomas'): campos_llenos += 1
if datos.get('causas_inmediatas'): campos_llenos += 1
if datos.get('factores_agravantes'): campos_llenos += 1

progreso = campos_llenos / campos_totales
st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

# --- TARJETA 1: EL NÚCLEO ---
with st.container(border=True):
    st.subheader("🎯 El Problema Central")
    st.markdown("Defina claramente la situación negativa. No lo confunda con la falta de una solución.")
    
    problema = st.text_area(
        "Descripción del Problema",
        value=datos.get('problema_central', ""),
        height=100,
        placeholder="Ej: Aumento de tiempos de viaje en el corredor Soracá-Tunja...",
        help="Debe ser una situación existente y negativa. Evite frases como 'Falta de...' o 'No hay...'"
    )

# --- TARJETA 2: ANÁLISIS CAUSAL ---
with st.container(border=True):
    st.subheader("🔍 Análisis de Causas y Efectos")
    col1, col2 = st.columns(2)
    
    with col1:
        sintomas = st.text_area(
            "Síntomas (Efectos Visibles)",
            value=datos.get('sintomas', ""),
            height=150,
            help="¿Qué evidencia visible demuestra que el problema existe? (Ej: Huecos, accidentes, quejas)",
            placeholder="Describa lo que se ve..."
        )
    
    with col2:
        causas = st.text_area(
            "Causas Inmediatas",
            value=datos.get('causas_inmediatas', ""),
            height=150,
            help="¿Por qué está ocurriendo esto? Busque el origen directo.",
            placeholder="Describa el origen..."
        )

# --- TARJETA 3: CONTEXTO ---
with st.container(border=True):
    st.subheader("⚠️ Factores Agravantes")
    agravantes = st.text_area(
        "Factores externos",
        value=datos.get('factores_agravantes', ""),
        help="Elementos que no causan el problema pero lo empeoran (Ej: Clima, Topografía)",
        placeholder="Ej: Temporada de lluvias intensa..."
    )

# --- BOTÓN DE ACCIÓN ---
st.markdown("###") # Espacio extra
col_izq, col_der = st.columns([1, 2])

with col_izq:
    if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
        # Guardado en Memoria
        st.session_state['datos_problema']['problema_central'] = problema
        st.session_state['datos_problema']['sintomas'] = sintomas
        st.session_state['datos_problema']['causas_inmediatas'] = causas
        st.session_state['datos_problema']['factores_agravantes'] = agravantes
        
        # Notificación Toast (Estilo moderno)
        st.toast("✅ ¡Diagnóstico guardado exitosamente!", icon="🎉")
        time.sleep(0.5) # Pequeña pausa para efecto visual
        st.rerun() # Recargar para actualizar la barra de progreso
