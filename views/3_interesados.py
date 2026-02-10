import streamlit as st
import pandas as pd
import plotly.express as px
from session_state import guardar_datos_nube

st.title("👥 3. Análisis de Interesados")

# Traer el problema central
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# Definir el orden exacto de las columnas que quieres ver
columnas_ordenadas = [
    "#", "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", 
    "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"
]

# Opciones para los menús desplegables
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

def calcular_estrategia(row):
    p = str(row.get('PODER', '')).strip()
    i = str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# 1. Asegurar que el DataFrame tenga todas las columnas en orden
df_actual = st.session_state['df_interesados']
for col in columnas_ordenadas:
    if col not in df_actual.columns:
        df_actual[col] = None
df_actual = df_actual[columnas_ordenadas]

# --- EL EDITOR DE DATOS ---
st.subheader("📝 Matriz de Interesados")
df_editado = st.data_editor(
    df_actual,
    column_config={
        "#": st.column_config.NumberColumn("#", disabled=True),
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion),
        "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # <--- ESTO ELIMINA LA COLUMNA GRIS CON EL LÁPIZ
    key="editor_interesados_v2"
)

# Detectar cambios y procesar
if not df_editado.equals(df_actual):
    if not df_editado.empty:
        # Numeración automática 1, 2, 3...
        df_editado["#"] = range(1, len(df_editado) + 1)
        # Cálculo de estrategia
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube() # Guardado automático en Supabase
    st.rerun()

# --- ANÁLISIS CUALITATIVO ---
st.divider()
st.subheader("📌 Conclusiones del Análisis")
analisis_txt = st.text_area(
    "Escriba aquí el análisis de la matriz:", 
    value=st.session_state.get('analisis_participantes', ""),
    height=150
)

if analisis_txt != st.session_state.get('analisis_participantes', ""):
    st.session_state['analisis_participantes'] = analisis_txt
    guardar_datos_nube()

# --- GRÁFICA ---
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    st.subheader("📊 Matriz de Poder e Interés")
    mapa_val = {"Alto": 2, "Bajo": 1}
    df_plot = df_editado.copy().dropna(subset=['PODER', 'INTERÉS', 'NOMBRE'])
    
    if not df_plot.empty:
        df_plot['x'] = df_plot['INTERÉS'].map(mapa_val)
        df_plot['y'] = df_plot['PODER'].map(mapa_val)
        fig = px.scatter(df_plot, x='x', y='y', text='NOMBRE', range_x=[0.5, 2.5], range_y=[0.5, 2.5])
        fig.add_hline(y=1.5, line_dash="dash")
        fig.add_vline(x=1.5, line_dash="dash")
        st.plotly_chart(fig, use_container_width=True)
