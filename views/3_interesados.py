import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización de persistencia
inicializar_session()

# --- ESTILOS CSS (Diseño de Tabla y Dashboard) ---
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
    
    /* Contenedor para que la tabla no parezca Excel */
    div[data-testid="stDataEditor"] {
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* Estilo para los cuadrantes de estrategia */
    .cuadrante-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #eee;
    }

    /* Hack imagen estática */
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA INTEGRADA (Armonía visual) ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores y mapa estratégico de involucramiento.</div>', unsafe_allow_html=True)
    
    # Progreso de la fase
    df_actual = st.session_state.get('df_interesados', pd.DataFrame())
    tiene_datos = not df_actual.empty and df_actual['NOMBRE'].dropna().any()
    progreso = 1.0 if tiene_datos else 0.0
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_logo:
    logo_path = "unnamed.jpg" if os.path.exists("unnamed.jpg") else "unnamed-1.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

st.divider()

# --- CONTEXTO: PROBLEMA CENTRAL ---
problema_actual = st.session_state.get('datos_problema', {}).get('problema_central', "No definido")
with st.expander("📌 Contexto: Problema Central (Referencia)", expanded=False):
    st.info(f"**Problema:** {problema_actual}")

# --- 1. MATRIZ DE DATOS (DISEÑO MEJORADO) ---
st.subheader("📝 Matriz de Datos de Interesados")

columnas_orden = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "PODER", "INTERÉS", "ESTRATEGIA"]
opciones_posicion = ["Opositor", "Beneficiario", "Cooperante", "Perjudicado"]
opciones_nivel = ["Alto", "Bajo"]

# Asegurar estructura del DataFrame
if df_actual.empty:
    df_actual = pd.DataFrame(columns=columnas_orden)

# Editor con configuración de diseño de tabla
df_editado = st.data_editor(
    df_actual,
    column_config={
        "NOMBRE": st.column_config.TextColumn("Nombre del Actor", width="medium", required=True),
        "GRUPO": st.column_config.TextColumn("Entidad / Grupo", width="small"),
        "POSICIÓN": st.column_config.SelectboxColumn("Posición", options=opciones_posicion, width="small"),
        "EXPECTATIVA": st.column_config.TextColumn("Expectativa Principal", width="large"),
        "PODER": st.column_config.SelectboxColumn("Poder", options=opciones_nivel, width="small"),
        "INTERÉS": st.column_config.SelectboxColumn("Interés", options=opciones_nivel, width="small"),
        "ESTRATEGIA": st.column_config.TextColumn("Estrategia Sugerida", disabled=True, width="medium"),
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="editor_interesados_pro_final"
)

# Lógica de guardado y cálculo automático
def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.write("")

# --- 2. MAPA ESTRATÉGICO (LOS CUADRANTES IMPORTANTES) ---
st.subheader("📊 Mapa Estratégico de Actores")

if not df_editado.empty and df_editado['NOMBRE'].dropna().any():
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    
    def obtener_lista(p, i):
        filtro = df_editado[(df_editado['PODER'] == p) & (df_editado['INTERÉS'] == i) & (df_editado['NOMBRE'].notna())]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}**" for _, r in filtro.iterrows()] or ["*Sin actores*"]

    # Distribución en 2x2
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("🤝 **SATISFACER (P:Alto / I:Bajo)**")
            for item in obtener_lista("Alto", "Bajo"): st.markdown(item)
        with st.container(border=True):
            st.markdown("🔍 **MONITORIZAR (P:Bajo / I:Bajo)**")
            for item in obtener_lista("Bajo", "Bajo"): st.markdown(item)
    with c2:
        with st.container(border=True):
            st.markdown("🚀 **INVOLUCRAR (P:Alto / I:Alto)**")
            for item in obtener_lista("Alto", "Alto"): st.markdown(item)
        with st.container(border=True):
            st.markdown("📧 **INFORMAR (P:Bajo / I:Alto)**")
            for item in obtener_lista("Bajo", "Alto"): st.markdown(item)
    
    st.caption("📌 **Actitud:** 🔴 Opositor | 🔵 Cooperante | 🟢 Beneficiario | 🟣 Perjudicado")
else:
    st.warning("Ingrese datos en la tabla para visualizar el mapa estratégico.")

st.divider()

# --- 3. ANÁLISIS CUALITATIVO ---
st.subheader("📝 Análisis de Participantes")
analisis_previo = st.session_state.get('analisis_participantes', "")

analisis_actual = st.text_area(
    "Escriba el análisis cualitativo aquí:",
    value=analisis_previo,
    height=200,
    key="txt_analisis_participantes_final"
)

if analisis_actual != analisis_previo:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
