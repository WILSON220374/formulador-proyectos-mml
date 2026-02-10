import streamlit as st
import pandas as pd
from session_state import guardar_datos_nube

st.title("👥 3. Análisis de Interesados")

# --- CONTEXTO DEL PROYECTO ---
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# Configuración de columnas y opciones
columnas_ordenadas = ["#", "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

color_map = {
    "Opositor": "🔴", "Beneficiario": "🟢", 
    "Cooperante": "🔵", "Perjudicado": "🟣"
}

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# --- TABLA DE DATOS ---
df_actual = st.session_state['df_interesados']
for col in columnas_ordenadas:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_ordenadas]

st.subheader("📝 Matriz de Datos")
df_editado = st.data_editor(
    df_actual,
    column_config={
        "#": st.column_config.NumberColumn("#", disabled=True),
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion),
        "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic", use_container_width=True, hide_index=True, key="editor_v7"
)

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["#"] = range(1, len(df_editado) + 1)
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

# --- CLASIFICACIÓN POR ESTRATEGIA (CUADRANTES) ---
st.divider()
st.subheader("📊 Mapa Estratégico de Actores")

if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    def obtener_lista_cuadrante(poder, interes):
        filtro = df_editado[(df_editado['PODER'] == poder) & (df_editado['INTERÉS'] == interes) & (df_editado['NOMBRE'].notna())]
        items = []
        for _, row in filtro.iterrows():
            emoji = color_map.get(row['POSICIÓN'], "⚪")
            items.append(f"{emoji} **{row['NOMBRE']}** ({row['GRUPO']})")
        return items if items else ["*Sin actores asignados*"]

    col_izq, col_der = st.columns(2)

    with col_izq:
        # Cuadrante Poder Alto / Interés Bajo
        with st.container(border=True):
            st.error("🤝 **CONSULTAR Y MANTENER SATISFECHOS**")
            for item in obtener_lista_cuadrante("Alto", "Bajo"):
                st.markdown(item)

        # Cuadrante Poder Bajo / Interés Bajo
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR**")
            for item in obtener_lista_cuadrante("Bajo", "Bajo"):
                st.markdown(item)

    with col_der:
        # Cuadrante Poder Alto / Interés Alto
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y MANTENER CERCA**")
            for item in obtener_lista_cuadrante("Alto", "Alto"):
                st.markdown(item)

        # Cuadrante Poder Bajo / Interés Alto
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS**")
            for item in obtener_lista_cuadrante("Bajo", "Alto"):
                st.markdown(item)
    
    st.caption("Leyenda: 🔴 Opositor | 🔵 Cooperante | 🟢 Beneficiario | 🟣 Perjudicado")

else:
    st.warning("Ingrese los datos en la tabla para ver la clasificación.")

# --- SECCIÓN DE CONCLUSIONES ---
st.divider()
st.subheader("📝 Análisis de Participantes")
analisis_input = st.text_area("Conclusiones:", value=st.session_state.get('analisis_participantes', ""), height=120)
if analisis_input != st.session_state.get('analisis_participantes', ""):
    st.session_state['analisis_participantes'] = analisis_input
    guardar_datos_nube()
