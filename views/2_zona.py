import streamlit as st
import time
from session_state import inicializar_session, guardar_datos_nube

# Asegurar persistencia y memoria
inicializar_session()

st.header("2. Caracterización de la Zona de Estudio")

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA ---
def calcular_altura(texto, min_h=100):
    """Calcula la altura dinámica para que el texto sea siempre visible."""
    if not texto:
        return min_h
    # Contamos líneas por saltos de línea y por longitud de caracteres (aprox 85 por línea)
    lineas = str(texto).count('\n') + (len(str(texto)) // 85)
    return max(min_h, (lineas + 1) * 23)

if 'datos_zona' not in st.session_state:
    st.session_state['datos_zona'] = {}

datos = st.session_state['datos_zona']

# --- CONTEXTO: PROBLEMA CENTRAL ---
problema_fase_1 = st.session_state.get('datos_problema', {}).get('problema_central', "⚠️ No definido en Fase 1.")
with st.expander("📌 PROBLEMA CENTRAL", expanded=True):
    st.info(f" {problema_fase_1}")

# --- BARRA DE PROGRESO ---
campos_totales = 7
lista_campos = ['pob_total', 'pob_urbana', 'pob_rural', 'ubicacion', 'limites', 'economia', 'vias']
campos_llenos = sum(1 for campo in lista_campos if datos.get(campo))

progreso = campos_llenos / campos_totales
st.progress(progreso, text=f"Progreso de la Fase: {int(progreso * 100)}%")

# --- TARJETA 1: ANÁLISIS DEMOGRÁFICO ---
with st.container(border=True):
    st.subheader("👥 Población Afectada")
    col1, col2, col3 = st.columns(3)
    with col1:
        pob_total = st.number_input("Población Total", min_value=0, value=int(datos.get('pob_total', 0)))
    with col2:
        pob_urbana = st.number_input("Urbana", min_value=0, value=int(datos.get('pob_urbana', 0)))
    with col3:
        pob_rural = st.number_input("Rural", min_value=0, value=int(datos.get('pob_rural', 0)))

# --- TARJETA 2: GEOGRAFÍA Y TERRITORIO ---
with st.container(border=True):
    st.subheader("🗺️ Ubicación Geográfica")
    
    ubicacion = st.text_input(
        "Localización Específica", 
        value=datos.get('ubicacion', ""),
        placeholder="Ej: Vereda Morcá, Sogamoso..."
    )
    
    # Aplicación de altura dinámica al campo Límites
    texto_limites = datos.get('limites', "")
    limites = st.text_area(
        "Límites Geográficos",
        value=texto_limites,
        height=calcular_altura(texto_limites),
        placeholder="Norte:..., Sur:..."
    )

# --- TARJETA 3: ECONOMÍA Y ACCESO ---
with st.container(border=True):
    st.subheader("💰 Economía y Accesibilidad")
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Aplicación de altura dinámica al campo Economía
        texto_economia = datos.get('economia', "")
        economia = st.text_area(
            "Principal Actividad Económica",
            value=texto_economia,
            height=calcular_altura(texto_economia)
        )
        
    with col_b:
        # Aplicación de altura dinámica al campo División
        texto_vias = datos.get('vias', "")
        vias = st.text_area(
            "División del territorio",
            value=texto_vias,
            height=calcular_altura(texto_vias)
        )

# --- BOTÓN DE GUARDADO ---
st.markdown("###")
if st.button("💾 Guardar Información de Zona", type="primary", use_container_width=True):
    st.session_state['datos_zona'].update({
        'pob_total': pob_total, 'pob_urbana': pob_urbana, 'pob_rural': pob_rural,
        'ubicacion': ubicacion, 'limites': limites, 'economia': economia, 'vias': vias
    })
    guardar_datos_nube() #
    st.toast("✅ ¡Información territorial guardada!", icon="🗺️")
    time.sleep(0.5)
    st.rerun()
