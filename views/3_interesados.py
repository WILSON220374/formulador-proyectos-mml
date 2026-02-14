import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización de seguridad
inicializar_session()

# --- ESTILOS CSS (Diseño de Tabla Profesional) ---
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
    /* Enmarcar la tabla para que parezca un módulo de software */
    div[data-testid="stDataEditor"] {
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .stTextArea textarea {
        background-color: #fcfdfe;
        border: 1px solid #e0e7ff;
        border-radius: 8px;
    }
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    .linea-gruesa {
        border: none; height: 3px; background-color: #31333F; opacity: 0.1; margin: 30px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA INTEGRADA ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Identificación de actores y estrategias de involucramiento.</div>', unsafe_allow_html=True)
    
    # Progreso
    df_actual = st.session_state.get('df_interesados', pd.DataFrame())
    analisis_txt = st.session_state.get('analisis_participantes', "")
    tiene_datos = not df_actual.empty and df_actual['NOMBRE'].dropna().any() if 'NOMBRE' in df_actual.columns else False
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_logo:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- FUNCIONES DE SOPORTE (Tus funciones originales) ---
def calcular_altura_texto(texto, min_h=150):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 85)
    return max(min_h, (lineas + 2) * 24)

def calcular_altura_tabla(df):
    return max(250, (len(df) + 2) * 35 + 80)

def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# --- CONTEXTO: PROBLEMA CENTRAL ---
problema_actual = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
with st.expander("📌 Contexto: Problema Central (Solo Lectura)", expanded=False):
    st.info(f"**Problema Identificado:** {problema_actual}")

# --- 1. MATRIZ DE DATOS (CON DISEÑO) ---
st.subheader("📝 Matriz de Datos")
columnas_finales = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]

if df_actual.empty: df_actual = pd.DataFrame(columns=columnas_finales)
if "#" in df_actual.columns: df_actual = df_actual.drop(columns=["#"])
for col in columnas_finales:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_finales]

df_editado = st.data_editor(
    df_actual,
    column_config={
        "NOMBRE": st.column_config.TextColumn("Nombre del Actor", width="medium"),
        "GRUPO": st.column_config.TextColumn("Grupo / Entidad", width="small"),
        "POSICIÓN": st.column_config.SelectboxColumn("Posición", options=["Opositor", "Beneficiario", "Cooperante", "Perjudicado"], width="small"),
        "EXPECTATIVA": st.column_config.TextColumn("Expectativa Principal", width="large"),
        "CONTRIBUCION AL PROYECTO": st.column_config.TextColumn("Contribución", width="medium"),
        "PODER": st.column_config.SelectboxColumn("Poder", options=["Alto", "Bajo"], width="small"),
        "INTERÉS": st.column_config.SelectboxColumn("Interés", options=["Alto", "Bajo"], width="small"),
        "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("Estrategia (Auto)", disabled=True, width="medium"),
    },
    num_rows="dynamic", use_container_width=True, hide_index=True,
    height=calcular_altura_tabla(df_actual),
    key="editor_interesados_vfinal"
)

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.markdown('<hr class="linea-gruesa">', unsafe_allow_html=True)

# --- 2. MAPA ESTRATÉGICO (CUADRANTES) ---
st.subheader("📊 Mapa Estratégico de Actores")
if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    def obtener_lista(p, i):
        filtro = df_editado[(df_editado['PODER'] == p) & (df_editado['INTERÉS'] == i) & (df_editado['NOMBRE'].notna())]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}**" for _, r in filtro.iterrows()] or ["*Sin actores*"]

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **CONSULTAR Y MANTENER SATISFECHOS**")
            for item in obtener_lista("Alto", "Bajo"): st.markdown(item)
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR**")
            for item in obtener_lista("Bajo", "Bajo"): st.markdown(item)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y MANTENER CERCA**")
            for item in obtener_lista("Alto", "Alto"): st.markdown(item)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS**")
            for item in obtener_lista("Bajo", "Alto"): st.markdown(item)
else:
    st.info("Complete la matriz para visualizar el mapa estratégico.")

st.divider()

# --- 3. ANÁLISIS CUALITATIVO ---
st.subheader("📝 Análisis de Participantes")
analisis_previo = st.session_state.get('analisis_participantes', "")
analisis_actual = st.text_area(
    "Analisis", value=analisis_previo, height=calcular_altura_texto(analisis_previo), 
    key="txt_analisis_participantes", label_visibility="collapsed"
)

if analisis_actual != analisis_previo:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
