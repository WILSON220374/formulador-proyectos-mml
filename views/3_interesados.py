import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# Inicialización de seguridad para la memoria
inicializar_session()

st.title("👥 3. Análisis de Interesados")

# --- CONTEXTO ---
problema = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
st.info(f"**Problema Central:** {problema}")

# --- FUNCIONES DE SOPORTE ---
def calcular_altura_texto(texto, min_h=100):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 85)
    return max(min_h, (lineas + 1) * 23)

def calcular_altura_tabla(df):
    num_filas = len(df)
    return max(200, (num_filas + 2) * 35 + 50)

# Estilo para líneas divisorias gruesas
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
df_actual = st.session_state['df_interesados']
columnas_finales = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

# Limpieza y preparación
if "#" in df_actual.columns: df_actual = df_actual.drop(columns=["#"])
for col in columnas_finales:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_finales]
df_actual.index = range(1, len(df_actual) + 1)

h_tabla = calcular_altura_tabla(df_actual)

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
    hide_index=False,
    height=h_tabla,
    key="editor_final_H"
)

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

# --- PRIMER DIVISOR GRUESO ---
st.markdown(LINEA_GRUESA, unsafe_allow_html=True)

# --- 2. MAPA ESTRATÉGICO ---
st.subheader("📊 Mapa Estratégico de Actores")
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    def obtener_lista(p, i):
        filtro = df_editado[(df_editado['PODER'] == p) & (df_editado['INTERÉS'] == i) & (df_editado['NOMBRE'].notna())]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}** ({r['GRUPO']})" for _, r in filtro.iterrows()] or ["*Vacío*"]

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
else:
    st.warning("Complete la tabla superior para generar el mapa.")

# --- SEGUNDO DIVISOR GRUESO ---
st.markdown(LINEA_GRUESA, unsafe_allow_html=True)

# --- 3. ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")
txt_concl = st.session_state.get('analisis_participantes', "")
analisis = st.text_area(
    "Escriba sus conclusiones aquí:", 
    value=txt_concl, 
    height=calcular_altura_texto(txt_concl), 
    key="area_concl_vFinal"
)

if analisis != txt_concl:
    st.session_state['analisis_participantes'] = analisis
    guardar_datos_nube()
    st.rerun()
