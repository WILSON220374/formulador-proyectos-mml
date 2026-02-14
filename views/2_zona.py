import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicializar
inicializar_session()
datos_zona = st.session_state.get('datos_zona', {})

# --- ESTILOS CSS (Consistente con Diagnóstico) ---
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
        margin-bottom: 10px; /* Reducido para pegar más la barra */
    }
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"] {
        background-color: #fcfdfe;
        border-radius: 8px;
    }
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    
    div[data-testid="stAlert"] {
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA INTEGRADA CON BARRA DE PROGRESO ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">🗺️ 2. Zona de Estudio</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Delimitación geográfica y demográfica del área de influencia.</div>', unsafe_allow_html=True)
    
    # --- CÁLCULO DE PROGRESO (Para la barra azul) ---
    # Verificamos 4 campos clave para determinar el avance
    hay_poblacion = int(datos_zona.get('poblacion_total', 0)) > 0
    hay_depto = len(datos_zona.get('departamento', '')) > 2
    hay_muni = len(datos_zona.get('municipio', '')) > 2
    hay_vias = len(datos_zona.get('vias', '')) > 10
    
    items_check = [hay_poblacion, hay_depto, hay_muni, hay_vias]
    progreso = sum(items_check) / 4
    
    # LA BARRA AZUL DE ARMONÍA
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_logo:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- REFERENCIA: EL PROBLEMA ---
problema_actual = st.session_state.get('datos_problema', {}).get('problema_central', 'No definido aún.')

with st.expander("📌 Contexto: Problema Central (Solo Lectura)", expanded=True):
    st.info(f"**Problema Identificado:** {problema_actual}")

# --- FORMULARIO DE ZONA ---
st.subheader("📍 Detalles del Área")

with st.container(border=True):
    # BLOQUE 1: POBLACIÓN
    st.markdown("##### 👥 Población Afectada")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        pob_total = st.number_input("Población Total", min_value=0, value=int(datos_zona.get('poblacion_total', 0)))
    with c2:
        pob_urbana = st.number_input("Urbana", min_value=0, value=int(datos_zona.get('poblacion_urbana', 0)))
    with c3:
        pob_rural = st.number_input("Rural", min_value=0, value=int(datos_zona.get('poblacion_rural', 0)))

    st.markdown("---")

    # BLOQUE 2: UBICACIÓN
    st.markdown("##### 🌍 Localización Geográfica")
    c4, c5 = st.columns(2)
    with c4:
        departamento = st.text_input("Departamento / Estado", value=datos_zona.get('departamento', ''), placeholder="Ej: Boyacá")
        municipio = st.text_input("Municipio / Ciudad", value=datos_zona.get('municipio', ''), placeholder="Ej: Sogamoso")
    with c5:
        vereda = st.text_input("Vereda / Localidad", value=datos_zona.get('vereda', ''), placeholder="Ej: Sector Norte")
        coordenadas = st.text_input("Coordenadas (Opcional)", value=datos_zona.get('coordenadas', ''), placeholder="Lat, Long")

    st.markdown("---")

    # BLOQUE 3: DESCRIPCIÓN FÍSICA
    st.markdown("##### 🛣️ Descripción del Área (Vías, Clima, Topografía)")
    desc_vias = st.text_area(
        "Detalles físicos", 
        value=datos_zona.get('vias', ''),
        height=120,
        placeholder="Describa el estado de las vías de acceso, condiciones climáticas...",
        label_visibility="collapsed"
    )

    if st.button("💾 GUARDAR ZONA DE ESTUDIO", type="primary", use_container_width=True):
        nueva_zona = {
            "poblacion_total": pob_total,
            "poblacion_urbana": pob_urbana,
            "poblacion_rural": pob_rural,
            "departamento": departamento,
            "municipio": municipio,
            "vereda": vereda,
            "coordenadas": coordenadas,
            "vias": desc_vias
        }
        st.session_state['datos_zona'] = nueva_zona
        guardar_datos_nube()
        st.toast("✅ Información de zona actualizada")
        st.rerun() # Recarga para actualizar la barra azul

# --- GUARDADO AUTOMÁTICO DE RESPALDO ---
nueva_zona_auto = {
    "poblacion_total": pob_total,
    "poblacion_urbana": pob_urbana,
    "poblacion_rural": pob_rural,
    "departamento": departamento,
    "municipio": municipio,
    "vereda": vereda,
    "coordenadas": coordenadas,
    "vias": desc_vias
}

if nueva_zona_auto != datos_zona:
    st.session_state['datos_zona'] = nueva_zona_auto
    guardar_datos_nube()
