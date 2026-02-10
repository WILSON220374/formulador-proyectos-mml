import streamlit as st
import pandas as pd
import plotly.express as px
from session_state import guardar_datos_nube # Importamos la función de la nube

st.title("👥 3. Análisis de Interesados")

# 1. Traer el problema central de la primera hoja
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.markdown(f"> **Problema Central:** {problema}")

# Opciones para las listas desplegables
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

# Función para calcular la estrategia automáticamente
def calcular_estrategia(row):
    p = str(row['PODER']).strip()
    i = str(row['INTERÉS']).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# --- CONFIGURACIÓN DEL EDITOR ---
config_columnas = {
    "#": st.column_config.NumberColumn("#", disabled=True, help="Autocompletado automático"),
    "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion, required=True),
    "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel, required=True),
    "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel, required=True),
    "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
}

# Mostrar el editor de datos
df_actual = st.session_state['df_interesados']

df_editado = st.data_editor(
    df_actual,
    column_config=config_columnas,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # <--- MODIFICACIÓN: Aquí eliminamos la doble numeración
    key="editor_interesados"
)

# Lógica de automatización al detectar cambios
if not df_editado.equals(df_actual):
    if not df_editado.empty:
        # Llenado automático de '#' y Estrategia
        df_editado["#"] = range(1, len(df_editado) + 1)
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    
    st.session_state['df_interesados'] = df_editado
    
    # GUARDAR EN LA NUBE AUTOMÁTICAMENTE
    guardar_datos_nube()
    st.rerun()

# --- ANÁLISIS CUALITATIVO ---
st.subheader("📝 ANÁLISIS DE PARTICIPANTES")
analisis_txt = st.text_area(
    "Escriba sus conclusiones aquí:", 
    value=st.session_state['analisis_participantes'],
    height=150
)

# Guardar el texto si cambia y sincronizar con la nube
if analisis_txt != st.session_state['analisis_participantes']:
    st.session_state['analisis_participantes'] = analisis_txt
    guardar_datos_nube()

# --- GRÁFICA DE CUADRANTES ---
st.subheader("📊 Matriz de Poder e Interés")
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    mapa_val = {"Alto": 2, "Bajo": 1}
    df_plot = df_editado.copy().dropna(subset=['PODER', 'INTERÉS', 'NOMBRE'])
    
    if not df_plot.empty:
        df_plot['x'] = df_plot['INTERÉS'].map(mapa_val)
        df_plot['y'] = df_plot['PODER'].map(mapa_val)

        fig = px.scatter(
            df_plot, x='x', y='y', text='NOMBRE',
            labels={'x': 'INTERÉS', 'y': 'PODER'},
            range_x=[0.5, 2.5], range_y=[0.5, 2.5]
        )
        
        fig.add_hline(y=1.5, line_dash="dash", line_color="black")
        fig.add_vline(x=1.5, line_dash="dash", line_color="black")
        fig.update_traces(textposition='top center', marker=dict(size=12, color='red'))
        
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Ingrese al menos un interesado con Nombre, Poder e Interés para ver la gráfica.")
