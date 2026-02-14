import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización de seguridad
inicializar_session()

# --- ESTILOS CSS (Diseño Profesional Unificado) ---
st.markdown("""
    <style>
    .titulo-seccion {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #4F8BFF;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    .subtitulo-gris {
        font-size: 16px !important;
        color: #666;
        margin-bottom: 10px;
    }
    /* Estilo para las cajas de texto y el editor */
    .stTextArea textarea {
        background-color: #fcfdfe;
        border: 1px solid #e0e7ff;
        border-radius: 8px;
    }
    /* Hack imagen estática */
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    
    div[data-testid="stAlert"] { padding: 10px; border-radius: 10px; }
    
    /* Línea divisoria gruesa sutil */
    .linea-gruesa {
        border: none;
        height: 3px;
        background-color: #31333F;
        opacity: 0.1;
        border-radius: 5px;
        margin: 30px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA INTEGRADA CON LOGO Y PROGRESO ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Identificación de actores, posiciones y estrategias de involucramiento.</div>', unsafe_allow_html=True)
    
    # --- CÁLCULO DE PROGRESO ---
    df_actual = st.session_state.get('df_interesados', pd.DataFrame())
    analisis_txt = st.session_state.get('analisis_participantes', "")
    
    # Progreso: 50% por tener al menos 1 actor con nombre, 50% por análisis cualitativo
    tiene_datos = not df_actual.empty and df_actual['NOMBRE'].dropna().any()
    tiene_analisis = len(str(analisis_txt).strip()) > 20
    progreso = (0.5 if tiene_datos else 0) + (0.5 if tiene_analisis else 0)
    
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_logo:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- FUNCIONES DE SOPORTE ---
def calcular_altura_texto(texto, min_h=150):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 85)
    return max(min_h, (lineas + 2) * 24)

def calcular_altura_tabla(df):
    num_filas = len(df)
    return max(200, (num_filas + 2) * 35 + 80)

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# --- CONTEXTO: PROBLEMA CENTRAL ---
problema_actual = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
with st.expander("📌 Contexto: Problema Central (Solo Lectura)", expanded=True):
    st.info(f"**Problema Identificado:** {problema_actual}")

# --- 1. MATRIZ DE DATOS ---
st.subheader("📝 Matriz de Datos")
columnas_finales = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

# Limpieza y preparación del DataFrame
if df_actual.empty:
    df_actual = pd.DataFrame(columns=columnas_finales)

if "#" in df_actual.columns: df_actual = df_actual.drop(columns=["#"])
for col in columnas_finales:
    if col not in df_actual.columns: df_actual[col] = None

df_actual = df_actual[columnas_finales]
df_actual.index = range(1, len(df_actual) + 1)

df_editado = st.data_editor(
    df_actual,
    column_config={
        "POSICIÓN": st.column_config.SelectboxColumn("POSICIÓN", options=opciones_posicion),
        "PODER": st.column_config.SelectboxColumn("PODER", options=opciones_nivel),
        "INTERÉS": st.column_config.SelectboxColumn("INTERÉS", options=opciones_nivel),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("ESTRATEGIA (AUTO)", disabled=True),
    },
    num_rows="dynamic", use_container_width=True, hide_index=False,
    height=calcular_altura_tabla(df_actual),
    key="editor_interesados_v3"
)

# Lógica de guardado y cálculo automático de estrategia
if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.markdown('<hr class="linea-gruesa">', unsafe_allow_html=True)

# --- 2. MAPA ESTRATÉGICO DE ACTORES ---
st.subheader("📊 Mapa Estratégico de Actores")
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    
    def obtener_lista(p, i):
        filtro = df_editado[(df_editado['PODER'] == p) & (df_editado['INTERÉS'] == i) & (df_editado['NOMBRE'].notna())]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}** ({r['GRUPO']})" for _, r in filtro.iterrows()] or ["*Sin actores*"]

    # Distribución en cuadrantes
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **CONSULTAR Y MANTENER SATISFECHOS** (P:Alto / I:Bajo)")
            for item in obtener_lista("Alto", "Bajo"): st.markdown(item)
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR** (P:Bajo / I:Bajo)")
            for item in obtener_lista("Bajo", "Bajo"): st.markdown(item)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y MANTENER CERCA** (P:Alto / I:Alto)")
            for item in obtener_lista("Alto", "Alto"): st.markdown(item)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS** (P:Bajo / I:Alto)")
            for item in obtener_lista("Bajo", "Alto"): st.markdown(item)
    
    st.caption("📌 **Leyenda:** 🔴 Opositor | 🔵 Cooperante | 🟢 Beneficiario | 🟣 Perjudicado")
else:
    st.info("Complete la matriz de datos para generar el mapa estratégico.")

st.markdown('<hr class="linea-gruesa">', unsafe_allow_html=True)

# --- 3. ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")
st.caption("Escriba a continuación el análisis cualitativo de la situación de los actores:")

analisis_previo = st.session_state.get('analisis_participantes', "")
h_analisis = calcular_altura_texto(analisis_previo)

with st.container(border=True):
    analisis_actual = st.text_area(
        "Texto de análisis", 
        value=analisis_previo, 
        height=h_analisis, 
        key="txt_analisis_participantes", 
        label_visibility="collapsed",
        placeholder="Describa las estrategias de negociación, alianzas o mitigación de riesgos..."
    )

# Guardado automático del análisis
if analisis_actual != analisis_previo:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
