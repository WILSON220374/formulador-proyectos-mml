import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# Inicialización de seguridad para la memoria
inicializar_session()

st.title("👥 3. Análisis de Interesados")

# --- CONTEXTO DEL PROYECTO ---
# Recuperar el problema central de la Hoja 1
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA ---
def calcular_altura(texto, min_h=100):
    """Calcula la altura dinámica según el contenido para evitar cortes."""
    if not texto:
        return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 85)
    return max(min_h, (lineas + 1) * 23)

# Configuración de columnas y opciones
columnas_ordenadas = ["#", "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]
color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# --- TABLA DE DATOS (Corrección de Doble Numeración) ---
df_actual = st.session_state['df_interesados']
for col in columnas_ordenadas:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_ordenadas]

st.subheader("📝 Matriz de Datos")
# hide_index=True ELIMINA LA COLUMNA GRIS DE LA IZQUIERDA
df_editado = st.data_editor(
    df_actual,
    column_config={
        "#": st.column_config.NumberColumn("#", disabled=True, help="Autocompletado automático"),
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion),
        "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic", 
    use_container_width=True, 
    hide_index=True, # <--- MODIFICACIÓN CRÍTICA
    key="editor_interesados_vFINAL" # Cambio de llave para forzar refresco
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
        with st.container(border=True):
            st.error("🤝 **CONSULTAR Y MANTENER SATISFECHOS**")
            for item in obtener_lista_cuadrante("Alto", "Bajo"): st.markdown(item)
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR**")
            for item in obtener_lista_cuadrante("Bajo", "Bajo"): st.markdown(item)

    with col_der:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y MANTENER CERCA**")
            for item in obtener_lista_cuadrante("Alto", "Alto"): st.markdown(item)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS**")
            for item in obtener_lista_cuadrante("Bajo", "Alto"): st.markdown(item)
else:
    st.warning("Ingrese los datos en la tabla para ver la clasificación.")

# --- CONCLUSIONES CON AUTO-AJUSTE DE ALTURA ---
st.divider()
st.subheader("📝 Análisis de Participantes")
texto_conclusiones = st.session_state.get('analisis_participantes', "")
analisis_input = st.text_area(
    "Conclusiones:", 
    value=texto_conclusiones, 
    height=calcular_altura(texto_conclusiones), # Auto-ajuste de altura
    key="area_conclusiones"
)

if analisis_input != texto_conclusiones:
    st.session_state['analisis_participantes'] = analisis_input
    guardar_datos_nube()
    st.rerun()
