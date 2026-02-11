import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

st.title("👥 3. Análisis de Interesados")

# Contexto
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# Función auto-ajuste
def calcular_altura(texto, min_h=100):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 85)
    return max(min_h, (lineas + 1) * 23)

# Columnas SIN el '#' manual
columnas_finales = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# Preparar DataFrame
df_actual = st.session_state['df_interesados']
if "#" in df_actual.columns: df_actual = df_actual.drop(columns=["#"])
for col in columnas_finales:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_finales]

# Asegurar que el índice empiece en 1 para la vista
df_actual.index = range(1, len(df_actual) + 1)

st.subheader("📝 Matriz de Datos")
df_editado = st.data_editor(
    df_actual,
    column_config={
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion),
        "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA", disabled=True),
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=False, # MOSTRAMOS EL ÍNDICE DEL SISTEMA COMO ÚNICA NUMERACIÓN
    key="editor_interesados_SISTEMA"
)

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        # Solo calculamos la estrategia, el índice lo maneja el sistema
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

# --- MAPA ESTRATÉGICO ---
st.divider()
st.subheader("📊 Mapa Estratégico de Actores")
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    def obtener_lista(p, i):
        filtro = df_editado[(df_editado['PODER'] == p) & (df_editado['INTERÉS'] == i) & (df_editado['NOMBRE'].notna())]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}**" for _, r in filtro.iterrows()] or ["*Vacío*"]

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **CONSULTAR Y MANTENER SATISFECHOS**")
            for i in obtener_lista("Alto", "Bajo"): st.markdown(i)
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR**")
            for i in obtener_lista("Bajo", "Bajo"): st.markdown(i)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y MANTENER CERCA**")
            for i in obtener_lista("Alto", "Alto"): st.markdown(i)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS**")
            for i in obtener_lista("Bajo", "Alto"): st.markdown(i)

# --- CONCLUSIONES CON AUTO-AJUSTE ---
st.divider()
st.subheader("📝 Análisis de Participantes")
txt_concl = st.session_state.get('analisis_participantes', "")
analisis = st.text_area(
    "Conclusiones:", 
    value=txt_concl, 
    height=calcular_altura(txt_concl), 
    key="area_concl"
)

if analisis != txt_concl:
    st.session_state['analisis_participantes'] = analisis
    guardar_datos_nube()
    st.rerun()
