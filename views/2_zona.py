import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicializar
inicializar_session()
datos = st.session_state.get('datos_zona', {})

# --- ESTILOS CSS (Diseño Profesional Unificado) ---
st.markdown("""
    <style>
    .titulo-seccion {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #4F8BFF;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    .subtitulo-gris {
        font-size: 16px !important;
        color: #666;
        margin-bottom: 10px;
    }
    /* Estilo para inputs */
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"], .stTextArea textarea {
        background-color: #fcfdfe;
        border: 1px solid #e0e7ff;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #4F8BFF;
        box-shadow: 0 0 0 2px rgba(79, 139, 255, 0.1);
    }
    /* Hack imagen estática */
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    
    div[data-testid="stAlert"] { padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA INTEGRADA ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">🗺️ 2. Zona de Estudio</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Delimitación geográfica, límites y contexto económico.</div>', unsafe_allow_html=True)
    
    # --- CÁLCULO DE PROGRESO ---
    # Campos que revisamos para ver si están llenos
    campos_clave = ['pob_total', 'ubicacion', 'limites', 'economia', 'vias']
    llenos = sum(1 for c in campos_clave if datos.get(c) and str(datos.get(c)).strip())
    progreso = llenos / len(campos_clave)
    
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_logo:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA ---
def calcular_altura(texto, min_h=100):
    if not texto: return min_h
    texto_str = str(texto)
    # Calculamos líneas por 'Enter' y por longitud (ajustado a 60 caracteres por línea aprox)
    lineas = texto_str.count('\n') + (len(texto_str) // 60)
    return max(min_h, (lineas + 2) * 24)

# --- CONTEXTO: PROBLEMA CENTRAL ---
problema_actual = st.session_state.get('datos_problema', {}).get('problema_central', 'No definido aún.')
with st.expander("📌 Contexto: Problema Central (Solo Lectura)", expanded=True):
    st.info(f"**Problema Identificado:** {problema_actual}")

# --- FORMULARIO ESTRUCTURADO ---
st.subheader("📍 Detalles del Área")

# BLOQUE 1: POBLACIÓN (3 Columnas)
with st.container(border=True):
    st.markdown("##### 👥 Población Afectada")
    c1, c2, c3 = st.columns(3)
    with c1:
        p_total = st.number_input("Población Total", min_value=0, value=int(datos.get('pob_total', 0)))
    with c2:
        p_urbana = st.number_input("Urbana", min_value=0, value=int(datos.get('pob_urbana', 0)))
    with c3:
        p_rural = st.number_input("Rural", min_value=0, value=int(datos.get('pob_rural', 0)))

st.write("")

# BLOQUE 2: UBICACIÓN Y LÍMITES
with st.container(border=True):
    st.markdown("##### 🗺️ Ubicación Geográfica")
    
    # Campo Ubicación (Una sola línea como pediste)
    val_ubicacion = datos.get('ubicacion', "")
    ubicacion = st.text_input("Localización Específica (Municipio/Vereda)", value=val_ubicacion, placeholder="Ej: Municipio de Sogamoso, Vereda X")
    
    st.markdown("---")
    
    st.markdown("##### 🚧 Límites Geográficos")
    val_limites = datos.get('limites', "")
    # APLICAMOS AUTO-AJUSTE AQUÍ
    limites = st.text_area(
        "Norte, Sur, Oriente, Occidente...", 
        value=val_limites, 
        height=calcular_altura(val_limites),
        label_visibility="collapsed",
        placeholder="Defina los límites territoriales..."
    )

st.write("")

# BLOQUE 3: ECONOMÍA Y VÍAS (2 Columnas con Auto-Ajuste)
with st.container(border=True):
    st.markdown("##### 💰 Contexto Socioeconómico y Físico")
    
    col_a, col_b = st.columns(2, gap="large")
    
    with col_a:
        st.markdown("**Principal Actividad Económica**")
        val_eco = datos.get('economia', "")
        # APLICAMOS AUTO-AJUSTE AQUÍ
        economia = st.text_area(
            "Economia", 
            value=val_eco, 
            height=calcular_altura(val_eco),
            label_visibility="collapsed",
            placeholder="Ej: Agricultura, Minería..."
        )
        
    with col_b:
        st.markdown("**División del Territorio / Vías**")
        val_vias = datos.get('vias', "")
        # APLICAMOS AUTO-AJUSTE AQUÍ
        vias = st.text_area(
            "Vias", 
            value=val_vias, 
            height=calcular_altura(val_vias),
            label_visibility="collapsed",
            placeholder="Descripción de vías y acceso..."
        )

# --- GUARDADO AUTOMÁTICO ---
nueva_data = {
    'pob_total': p_total,
    'pob_urbana': p_urbana,
    'pob_rural': p_rural,
    'ubicacion': ubicacion,
    'limites': limites,
    'economia': economia,
    'vias': vias
}

if nueva_data != datos:
    st.session_state['datos_zona'] = nueva_data
    guardar_datos_nube()
    st.rerun()
