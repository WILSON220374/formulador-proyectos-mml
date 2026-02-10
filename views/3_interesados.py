import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np # Necesario para el "ruido" visual
from session_state import guardar_datos_nube

st.title("👥 3. Análisis de Interesados")

# Traer el problema central
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# Definir el orden de las columnas
columnas_ordenadas = [
    "#", "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", 
    "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"
]

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

# Asegurar estructura del DataFrame
df_actual = st.session_state['df_interesados']
for col in columnas_ordenadas:
    if col not in df_actual.columns:
        df_actual[col] = None
df_actual = df_actual[columnas_ordenadas]

# --- EDITOR DE DATOS ---
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
    hide_index=True,
    key="editor_interesados_v3"
)

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["#"] = range(1, len(df_editado) + 1)
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

# --- CONCLUSIONES ---
st.divider()
st.subheader("📌 Conclusiones del Análisis")
analisis_txt = st.text_area(
    "Escriba aquí el análisis de la matriz:", 
    value=st.session_state.get('analisis_participantes', ""),
    height=100
)

if analisis_txt != st.session_state.get('analisis_participantes', ""):
    st.session_state['analisis_participantes'] = analisis_txt
    guardar_datos_nube()

# --- GRÁFICA CON JITTERING (DISPERSIÓN) ---
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    st.subheader("📊 Matriz de Poder e Interés (Visualización)")
    
    mapa_val = {"Alto": 2, "Bajo": 1}
    df_plot = df_editado.copy().dropna(subset=['PODER', 'INTERÉS', 'NOMBRE'])
    
    if not df_plot.empty:
        # Aplicamos un pequeño ruido aleatorio (+/- 0.1) para evitar superposición
        df_plot['x_jitter'] = df_plot['INTERÉS'].map(mapa_val) + np.random.uniform(-0.12, 0.12, len(df_plot))
        df_plot['y_jitter'] = df_plot['PODER'].map(mapa_val) + np.random.uniform(-0.12, 0.12, len(df_plot))

        fig = px.scatter(
            df_plot, 
            x='x_jitter', 
            y='y_jitter', 
            text='NOMBRE',
            labels={'x_jitter': 'Nivel de Interés', 'y_jitter': 'Nivel de Poder'},
            hover_name='NOMBRE',
            hover_data={'x_jitter': False, 'y_jitter': False, 'ESTRATEGIA DE INVOLUCRAMIENTO': True}
        )

        # Configuración estética de la matriz
        fig.update_xaxes(tickvals=[1, 2], ticktext=["Bajo", "Alto"], range=[0.5, 2.5])
        fig.update_yaxes(tickvals=[1, 2], ticktext=["Bajo", "Alto"], range=[0.5, 2.5])
        
        # Líneas divisorias de cuadrantes
        fig.add_hline(y=1.5, line_dash="dash", line_color="gray")
        fig.add_vline(x=1.5, line_dash="dash", line_color="gray")
        
        fig.update_traces(
            textposition='top center', 
            marker=dict(size=14, color='royalblue', line=dict(width=2, color='white'))
        )
        
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Ingrese interesados con Nombre, Poder e Interés para generar la gráfica.")
