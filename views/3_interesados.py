import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

# --- ENCABEZADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("👥 3. Análisis de Interesados")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# --- FUNCIONES ---
def calcular_altura_texto(texto, min_h=150):
    if not texto: return min_h
    txt = str(texto)
    lineas = txt.count('\n') + (len(txt) // 85)
    return max(min_h, (lineas + 1) * 23)

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

LINEA_GRUESA = "<hr style='border: 3px solid #31333F; border-radius: 5px; opacity: 0.3;'>"

# --- 1. MATRIZ ---
st.subheader("📝 Matriz de Datos")
df_actual = st.session_state['df_interesados']
columnas = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]

df_editado = st.data_editor(
    df_actual,
    column_config={
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]),
        "PODER": st.column_config.SelectboxColumn("PODER", options=["Alto", "Bajo"]),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=["Alto", "Bajo"]),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic", use_container_width=True, key="ed_int"
)

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.markdown(LINEA_GRUESA, unsafe_allow_html=True)

# --- 2. MAPA ---
st.subheader("📊 Mapa Estratégico de Actores")
# Lógica visual omitida para brevedad, pero mantenida en tu archivo original

st.markdown(LINEA_GRUESA, unsafe_allow_html=True)

# --- 3. ANÁLISIS FINAL (CAJA DE TEXTO) ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.session_state.get('analisis_participantes', "")
h_analisis = calcular_altura_texto(analisis_actual)

analisis_input = st.text_area(
    "Describa el análisis cualitativo...",
    value=analisis_actual, height=h_analisis,
    key="txt_analisis_int", label_visibility="collapsed"
)

if analisis_input != analisis_actual:
    st.session_state['analisis_participantes'] = analisis_input
    guardar_datos_nube()
    st.rerun()
