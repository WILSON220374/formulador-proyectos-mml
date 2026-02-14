import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización de persistencia
inicializar_session()

# --- ESTILOS CSS (Diseño de Tabla Gerencial) ---
st.markdown("""
    <style>
    .titulo-seccion {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #4F8BFF;
        margin-bottom: 5px;
    }
    .subtitulo-gris {
        font-size: 16px !important;
        color: #666;
        margin-bottom: 10px;
    }
    
    /* Enmarcamos el editor para que parezca un módulo de software */
    div[data-testid="stDataEditor"] {
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }

    /* Hack para imagen estática */
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA UNIFICADA ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores y definición de estrategias de involucramiento.</div>', unsafe_allow_html=True)
    
    # Progreso basado en la existencia de datos
    df_actual = st.session_state.get('df_interesados', pd.DataFrame())
    progreso = 1.0 if not df_actual.empty and df_actual['NOMBRE'].dropna().any() else 0.0
    st.progress(progreso, text=f"Fase de Identificación: {int(progreso * 100)}%")

with col_logo:
    logo_path = "unnamed.jpg" if os.path.exists("unnamed.jpg") else "unnamed-1.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

st.divider()

# --- CONTEXTO (Referencia visual) ---
problema_actual = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
with st.expander("📌 Contexto del Problema (Referencia)", expanded=False):
    st.info(f"**Problema Central:** {problema_actual}")

# --- MATRIZ DE DATOS (CONFIGURACIÓN PROFESIONAL) ---
st.subheader("📝 Matriz de Datos")

# Definición de opciones para las columnas de selección
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

# Asegurar que el DataFrame tenga la estructura correcta
columnas_finales = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA"]
if df_actual.empty:
    df_actual = pd.DataFrame(columns=columnas_finales)

# Limpieza de columnas sobrantes (como el índice '#' si existe)
if "#" in df_actual.columns: 
    df_actual = df_actual.drop(columns=["#"])

# CONFIGURACIÓN DE COLUMNAS (Aquí le damos el formato)
configuracion_columnas = {
    "NOMBRE": st.column_config.TextColumn(
        "Nombre del Actor", 
        width="medium", 
        required=True,
        placeholder="Ej: Alcaldía de Sogamoso"
    ),
    "GRUPO": st.column_config.TextColumn(
        "Grupo / Entidad", 
        width="small"
    ),
    "POSICIÓN": st.column_config.SelectboxColumn(
        "Posición", 
        options=opciones_posicion, 
        width="small"
    ),
    "EXPECTATIVA": st.column_config.TextColumn(
        "Expectativa Principal", 
        width="large"
    ),
    "CONTRIBUCION AL PROYECTO": st.column_config.TextColumn(
        "Contribución", 
        width="medium"
    ),
    "PODER": st.column_config.SelectboxColumn(
        "Poder", 
        options=opciones_nivel, 
        width="small"
    ),
    "INTERÉS": st.column_config.SelectboxColumn(
        "Interés", 
        options=opciones_nivel, 
        width="small"
    ),
    "ESTRATEGIA": st.column_config.TextColumn(
        "Estrategia Sugerida", 
        disabled=True, # No editable porque es calculada
        width="medium"
    )
}

# EL EDITOR DE DATOS FORMATEADO
df_editado = st.data_editor(
    df_actual,
    column_config=configuracion_columnas,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # ESTO ES CLAVE: Quita la columna de números tipo Excel
    key="editor_interesados_gerencial"
)

# Lógica de cálculo automático para la columna ESTRATEGIA
def definir_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# Detección de cambios y guardado
if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA"] = df_editado.apply(definir_estrategia, axis=1)
    
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.divider()

# --- ANÁLISIS CUALITATIVO (AUTO-AJUSTABLE) ---
st.subheader("📝 Análisis de Participantes")
analisis_previo = st.session_state.get('analisis_participantes', "")

# Calculamos altura dinámica (aprox 24px por línea de texto)
lineas = str(analisis_previo).count('\n') + (len(str(analisis_previo)) // 100)
h_final = max(200, (lineas + 2) * 24)

analisis_actual = st.text_area(
    "Escriba el análisis cualitativo aquí:",
    value=analisis_previo,
    height=h_final,
    key="txt_analisis_participantes_mml",
    label_visibility="collapsed",
    placeholder="Describa la situación general de los actores respecto al Problema Central..."
)

if analisis_actual != analisis_previo:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
