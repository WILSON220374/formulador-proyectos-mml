import streamlit as st
import os # <--- Importante para verificar la existencia del logo
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO MAESTRO UNIFICADO ---
st.markdown("""
    <style>
    html, body, .stApp {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO (MISMA LÓGICA QUE HOJA 1) ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")

with col_titulo:
    st.title("🗺️ 2. Zona de Estudio") # Título en formato grande

with col_logo:
    # Ubicación en la parte superior derecha con alta resolución
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA ---
def calcular_altura(texto, min_h=100, en_columna=False):
    if not texto: return min_h
    divisor = 40 if en_columna else 85
    lineas = str(texto).count('\n') + (len(str(texto)) // divisor)
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

# --- SECCIONES DE CAPTURA ---
with st.container(border=True):
    st.subheader("👥 Población Afectada")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_total = st.number_input("Población Total", min_value=0, value=int(datos.get('pob_total', 0)))
    with col2:
        p_urbana = st.number_input("Urbana", min_value=0, value=int(datos.get('pob_urbana', 0)))
    with col3:
        p_rural = st.number_input("Rural", min_value=0, value=int(datos.get('pob_rural', 0)))

with st.container(border=True):
    st.subheader("🗺️ Ubicación Geográfica")
    ubicacion = st.text_input("Localización Específica", value=datos.get('ubicacion', ""))
    
    txt_lim = datos.get('limites', "")
    limites = st.text_area("Límites Geográficos", value=txt_lim, height=calcular_altura(txt_lim))

with st.container(border=True):
    st.subheader("💰 Economía y Accesibilidad")
    col_a, col_b = st.columns(2)
    with col_a:
        txt_eco = datos.get('economia', "")
        economia = st.text_area("Principal Actividad Económica", value=txt_eco, height=calcular_altura(txt_eco, en_columna=True))
    with col_b:
        txt_vias = datos.get('vias', "")
        vias = st.text_area("División del territorio", value=txt_vias, height=calcular_altura(txt_vias, en_columna=True))

# --- LÓGICA DE GUARDADO AUTOMÁTICO ---
if (p_total != datos.get('pob_total') or 
    p_urbana != datos.get('pob_urbana') or 
    p_rural != datos.get('pob_rural') or 
    ubicacion != datos.get('ubicacion') or 
    limites != datos.get('limites') or 
    economia != datos.get('economia') or 
    vias != datos.get('vias')):
    
    st.session_state['datos_zona'] = {
        'pob_total': p_total,
        'pob_urbana': p_urbana,
        'pob_rural': p_rural,
        'ubicacion': ubicacion,
        'limites': limites,
        'economia': economia,
        'vias': vias
    }
    guardar_datos_nube()
    st.rerun()
