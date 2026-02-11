import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# Asegurar que la sesión esté lista
inicializar_session()

st.title("📍 2. Zona de Estudio")

# --- FUNCIÓN DE AUTO-AJUSTE (Misma lógica de la Hoja 1) ---
def calcular_altura(texto, min_h=100):
    """Calcula la altura necesaria para que el texto sea siempre visible."""
    if not texto:
        return min_h
    lineas = texto.count('\n') + (len(texto) // 85)
    altura_calculada = max(min_h, (lineas + 1) * 23)
    return altura_calculada

# Recuperar datos actuales de la zona
# Si el diccionario está vacío, inicializamos las llaves estándar
if not st.session_state['datos_zona']:
    st.session_state['datos_zona'] = {
        "localizacion": "",
        "poblacion": "",
        "contexto": ""
    }

zona = st.session_state['datos_zona']

# --- SECCIÓN 1: LOCALIZACIÓN ---
with st.container(border=True):
    st.subheader("🗺️ Localización Geográfica")
    st.markdown("Describa la ubicación exacta, límites y accesibilidad del área del proyecto.")
    
    h_loc = calcular_altura(zona.get('localizacion', ""))
    localizacion = st.text_area(
        "Detalles de Ubicación:",
        value=zona.get('localizacion', ""),
        height=h_loc,
        key="txt_localizacion",
        placeholder="Ej: Municipio de Sogamoso, Vereda Morcá, sector nororiental..."
    )

# --- SECCIÓN 2: CARACTERÍSTICAS DE LA POBLACIÓN ---
with st.container(border=True):
    st.subheader("👥 Características de la Población")
    st.markdown("Defina el perfil de los beneficiarios: demografía, cultura y niveles socioeconómicos.")
    
    h_pob = calcular_altura(zona.get('poblacion', ""))
    poblacion = st.text_area(
        "Descripción de la Comunidad:",
        value=zona.get('poblacion', ""),
        height=h_pob,
        key="txt_poblacion"
    )

# --- SECCIÓN 3: CONTEXTO SOCIOECONÓMICO ---
with st.container(border=True):
    st.subheader("🏗️ Contexto y Entorno")
    st.markdown("Situación actual de la infraestructura, servicios públicos y principales actividades económicas.")
    
    h_con = calcular_altura(zona.get('contexto', ""))
    contexto = st.text_area(
        "Análisis del Entorno:",
        value=zona.get('contexto', ""),
        height=h_con,
        key="txt_contexto"
    )

# --- LÓGICA DE GUARDADO AUTOMÁTICO ---
# Detectar si hubo cambios para sincronizar con la nube
if (localizacion != zona.get('localizacion') or 
    poblacion != zona.get('poblacion') or 
    contexto != zona.get('contexto')):
    
    st.session_state['datos_zona'] = {
        "localizacion": localizacion,
        "poblacion": poblacion,
        "contexto": contexto
    }
    guardar_datos_nube()
    st.rerun() # Refresca para aplicar la nueva altura visual inmediatamente
