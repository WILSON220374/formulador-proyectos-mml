import streamlit as st
import pandas as pd
import plotly.express as px

st.title("👥 3. Análisis de Interesados")

# 1. Traer el problema central de la primera hoja
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# Configuración de opciones para las columnas
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

# Función para calcular la estrategia automáticamente
def calcular_estrategia(row):
    p = row['PODER']
    i = row['INTERÉS']
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# 2-7. Configuración del Editor de Datos
df_actual = st.session_state['df_interesados']

df_editado = st.data_editor(
    df_actual,
    column_config={
        "ID": st.column_config.NumberColumn("ID", disabled=True), # Auto-diligenciado
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion, required=True),
        "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel, required=True),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel, required=True),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic",
    use_container_width=True,
    key="editor_interesados"
)

# 3 & 8. Lógica de automatización (ID y Estrategia)
if not df_editado.equals(df_actual):
    df_editado['ID'] = range(1, len(df_editado) + 1)
    df_editado['ESTRATEGIA DE INVOLUCRAMIENTO'] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    st.rerun()

# 8. Tarjeta de Análisis de Participantes
st.session_state['analisis_participantes'] = st.text_area(
    "📝 ANALISIS DE PARTICIPANTES", 
    value=st.session_state['analisis_participantes'],
    placeholder="Escriba aquí el análisis cualitativo..."
)

# 9. Gráfica de Cuadrantes (Matriz Poder/Interés)
st.subheader("📊 Matriz de Posicionamiento")

if not df_editado.empty:
    # Mapeo numérico para graficar "Alto/Bajo"
    mapa_grafico = {"Alto": 2, "Bajo": 1}
    df_plot = df_editado.copy()
    df_plot['x'] = df_plot['INTERÉS'].map(mapa_grafico)
    df_plot['y'] = df_plot['PODER'].map(mapa_grafico)

    fig = px.scatter(
        df_plot, x='x', y='y', text='NOMBRE',
        labels={'x': 'Interés', 'y': 'Poder'},
        range_x=[0.5, 2.5], range_y=[0.5, 2.5]
    )
    
    # Dibujar líneas de cuadrantes
    fig.add_hline(y=1.5, line_dash="dash", line_color="gray")
    fig.add_vline(x=1.5, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)
