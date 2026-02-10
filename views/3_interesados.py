import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from session_state import guardar_datos_nube

st.title("👥 3. Análisis de Interesados")

# Problema Central
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# Configuración de columnas
columnas_ordenadas = ["#", "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

color_map = {
    "Opositor": "#EF553B", "Beneficiario": "#00CC96", 
    "Cooperante": "#636EFA", "Perjudicado": "#AB63FA"
}

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# Datos y Editor
df_actual = st.session_state['df_interesados']
for col in columnas_ordenadas:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_ordenadas]

df_editado = st.data_editor(
    df_actual,
    column_config={
        "#": st.column_config.NumberColumn("#", disabled=True),
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion),
        "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic", use_container_width=True, hide_index=True, key="editor_v5"
)

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["#"] = range(1, len(df_editado) + 1)
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

# --- GRÁFICA GIGANTE SIN SUPERPOSICIÓN ---
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    st.subheader("📊 Visualización de Cuadrantes (Zoom Extendido)")
    
    mapa_val = {"Alto": 2, "Bajo": 1}
    df_plot = df_editado.copy().dropna(subset=['PODER', 'INTERÉS', 'NOMBRE'])
    
    if not df_plot.empty:
        # Jittering más agresivo para separar nombres
        df_plot['x_j'] = df_plot['INTERÉS'].map(mapa_val) + np.random.uniform(-0.35, 0.35, len(df_plot))
        df_plot['y_j'] = df_plot['PODER'].map(mapa_val) + np.random.uniform(-0.35, 0.35, len(df_plot))

        fig = px.scatter(
            df_plot, x='x_j', y='y_j', text='NOMBRE', color='POSICIÓN',
            color_discrete_map=color_map,
            height=700, # <--- GRÁFICA MÁS ALTA PARA DAR ESPACIO
            labels={'x_j': 'Interés', 'y_j': 'Poder'}
        )

        fig.update_xaxes(tickvals=[1, 2], ticktext=["Bajo", "Alto"], range=[0.3, 2.7], gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(tickvals=[1, 2], ticktext=["Bajo", "Alto"], range=[0.3, 2.7], gridcolor='rgba(0,0,0,0.05)')
        
        fig.add_hline(y=1.5, line_dash="dash", line_color="gray", opacity=0.3)
        fig.add_vline(x=1.5, line_dash="dash", line_color="gray", opacity=0.3)
        
        fig.update_traces(
            textposition='middle right', # Texto al lado del punto, no encima
            textfont_size=9, 
            marker=dict(size=18, line=dict(width=1.5, color='white'), opacity=0.8)
        )

        fig.update_layout(
            plot_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=150, t=50, b=20) # Margen derecho amplio para textos largos
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Área de conclusiones
st.divider()
st.subheader("📝 Conclusiones")
st.session_state['analisis_participantes'] = st.text_area("Análisis:", value=st.session_state.get('analisis_participantes', ""), height=100)
