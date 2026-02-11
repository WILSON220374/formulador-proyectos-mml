import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO MAESTRO UNIFICADO ---
st.markdown("""
    <style>
    /* 1. Tipografía general */
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    
    /* 2. Botón de Guardar (Primario): Texto blanco siempre visible */
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* 3. Botón Cerrar Sesión (Sidebar): Negro y sin negrilla */
    [data-testid="stSidebar"] .stButton button:not([kind="primary"]) p {
        color: black !important;
        font-weight: normal !important;
        font-size: 1rem;
    }
    
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.header("2. Caracterización de la Zona de Estudio")

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA OPTIMIZADA ---
def calcular_altura(texto, min_h=100, en_columna=False):
    """Calcula la altura dinámica según el contenido y el ancho del contenedor."""
    if not texto: return min_h
    # Si está en columna (ancho reducido), el texto se corta antes (~40 carac. vs ~85)
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
        # Ajustamos el cálculo para que reconozca el ancho de columna
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
