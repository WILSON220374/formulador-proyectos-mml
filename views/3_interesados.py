import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# Inicialización de seguridad
inicializar_session()

# --- ENCABEZADO CON LOGO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")

with col_titulo:
    st.title("👥 3. Análisis de Interesados")

with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- CONTEXTO ---
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# --- FUNCIONES DE SOPORTE ---
def calcular_altura_texto(texto, min_h=150):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 85)
    return max(min_h, (lineas + 1) * 23)

def calcular_altura_tabla(df):
    num_filas = len(df)
    return max(200, (num_filas + 2) * 35 + 50)

LINEA_GRUESA = "<hr style='border: 3px solid #31333F; border-radius: 5px; opacity: 0.3;'>"

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# --- 1. MATRIZ DE DATOS ---
st.subheader("📝 Matriz de Datos")
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
columnas_finales = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]

# Asegurar estructura de la tabla
for col in columnas_finales:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_finales]

df_editado = st.data_editor(
    df_actual,
    column_config={
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]),
        "PODER": st.column_config.SelectboxColumn("PODER", options=["Alto", "Bajo"]),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=["Alto", "Bajo"]),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic", use_container_width=True, height=calcular_altura_tabla(df_actual),
    key="editor_interesados_final"
)

# Guardado de tabla
if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.markdown(LINEA_GRUESA, unsafe_allow_html=True)

# --- 2. MAPA ESTRATÉGICO (Restaurado) ---
st.subheader("📊 Mapa Estratégico de Actores")
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    
    def obtener_lista(p, i):
        filtro = df_editado[(df_editado['PODER'] == p) & (df_editado['INTERÉS'] == i) & (df_editado['NOMBRE'].notna())]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}** ({r['GRUPO']})" for _, r in filtro.iterrows()] or ["*Sin actores*"]

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **CONSULTAR Y MANTENER SATISFECHOS**")
            for actor in obtener_lista("Alto", "Bajo"): st.markdown(actor)
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR**")
            for actor in obtener_lista("Bajo", "Bajo"): st.markdown(actor)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y MANTENER CERCA**")
            for actor in obtener_lista("Alto", "Alto"): st.markdown(actor)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS**")
            for actor in obtener_lista("Bajo", "Alto"): st.markdown(actor)
    
    st.caption("📌 **Leyenda de Actitud:** 🔴 Opositor | 🔵 Cooperante | 🟢 Beneficiario | 🟣 Perjudicado")
else:
    st.warning("Complete la tabla para visualizar el mapa.")

st.markdown(LINEA_GRUESA, unsafe_allow_html=True)

# --- 3. ANÁLISIS FINAL (Caja de texto) ---
st.subheader("📝 Análisis de Participantes")

analisis_actual = st.session_state.get('analisis_participantes', "")
h_analisis = calcular_altura_texto(analisis_actual)

analisis_input = st.text_area(
    "Escriba aquí el análisis cualitativo del mapa de actores...",
    value=analisis_actual,
    height=h_analisis,
    key="txt_analisis_participantes",
    label_visibility="collapsed"
)

# Guardado automático de la caja de texto
if analisis_input != analisis_actual:
    st.session_state['analisis_participantes'] = analisis_input
    guardar_datos_nube()
    st.rerun()
