import streamlit as st
import time

# --- TÍTULO Y ESTADO ---
st.header("2. Caracterización de la Zona de Estudio")

if 'datos_zona' not in st.session_state:
    st.session_state['datos_zona'] = {}

datos = st.session_state['datos_zona']

# --- CONTEXTO: TRAER EL PROBLEMA DE LA FASE ANTERIOR ---
# Recuperamos lo que escribiste en la página 1
problema_fase_1 = st.session_state.get('datos_problema', {}).get('problema_central', "⚠️ No has definido el problema aún en la Fase 1.")

with st.expander("📌 Ver Problema Central (Referencia)", expanded=True):
    st.info(f"**PROBLEMA CENTRAL:** {problema_fase_1}")

# --- BARRA DE PROGRESO ---
# Contamos cuántos campos tienen datos
campos_totales = 7
campos_llenos = 0
lista_campos = ['pob_total', 'pob_urbana', 'pob_rural', 'ubicacion', 'limites', 'economia', 'vias']
for campo in lista_campos:
    if datos.get(campo): campos_llenos += 1

progreso = campos_llenos / campos_totales
st.progress(progreso, text=f"Progreso de la Fase: {int(progreso * 100)}%")

# --- TARJETA 1: ANÁLISIS DEMOGRÁFICO ---
with st.container(border=True):
    st.subheader("👥 Población Afectada")
    st.markdown("Estime la cantidad de personas involucradas directa o indirectamente.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pob_total = st.number_input(
            "Población Total", 
            min_value=0, 
            value=datos.get('pob_total', 0),
            help="Suma total de habitantes en el área de influencia."
        )
    with col2:
        pob_urbana = st.number_input(
            "Urbana", 
            min_value=0, 
            value=datos.get('pob_urbana', 0),
            help="Habitantes en cabeceras municipales."
        )
    with col3:
        pob_rural = st.number_input(
            "Rural", 
            min_value=0, 
            value=datos.get('pob_rural', 0),
            help="Habitantes en veredas o campo."
        )

# --- TARJETA 2: GEOGRAFÍA Y TERRITORIO ---
with st.container(border=True):
    st.subheader("🗺️ Ubicación Geográfica")
    
    ubicacion = st.text_input(
        "Localización Específica", 
        value=datos.get('ubicacion', ""),
        placeholder="Ej: Vereda El Rosal, Municipio de Soracá...",
        help="¿Dónde se ejecutará físicamente el proyecto?"
    )
    
    limites = st.text_area(
        "Límites Geográficos",
        value=datos.get('limites', ""),
        height=100,
        placeholder="Norte:..., Sur:..., Oriente:...",
        help="Delimite el área de estudio."
    )

# --- TARJETA 3: ECONOMÍA Y ACCESO ---
with st.container(border=True):
    st.subheader("💰 Economía y Accesibilidad")
    
    col_a, col_b = st.columns(2)
    with col_a:
        economia = st.text_area(
            "Principal Actividad Económica",
            value=datos.get('economia', ""),
            height=120,
            help="¿De qué vive la gente en la zona? (Agricultura, Comercio, etc.)"
        )
    with col_b:
        vias = st.text_area(
            "Estado de Vías / Acceso",
            value=datos.get('vias', ""),
            height=120,
            help="Descripción de la infraestructura de transporte actual."
        )

# --- BOTÓN DE GUARDADO ---
st.markdown("###")
col_izq, col_der = st.columns([1, 2])

with col_izq:
    if st.button("💾 Guardar Zona", type="primary", use_container_width=True):
        # Guardar en memoria
        st.session_state['datos_zona'].update({
            'pob_total': pob_total,
            'pob_urbana': pob_urbana,
            'pob_rural': pob_rural,
            'ubicacion': ubicacion,
            'limites': limites,
            'economia': economia,
            'vias': vias
        })
        
        # Feedback visual
        st.toast("✅ ¡Información territorial guardada!", icon="🗺️")
        time.sleep(0.5)
        st.rerun()
