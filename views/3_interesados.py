import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización
inicializar_session()

# --- ESTILOS CSS (Diseño Profesional Unificado) ---
st.markdown("""
    <style>
    .titulo-seccion {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #4F8BFF;
        margin-bottom: 5px;
    }
    .subtitulo-gris {
        font-size: 16px !important;
        color: #666;
        margin-bottom: 10px;
    }
    /* Estilo para las tarjetas de KPI arriba de la tabla */
    .kpi-box {
        background-color: #f8faff;
        border: 1px solid #e0e7ff;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .kpi-val { font-size: 20px; font-weight: bold; color: #1E3A8A; }
    .kpi-lab { font-size: 12px; color: #666; text-transform: uppercase; }
    
    /* Hack imagen estática */
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA INTEGRADA ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Identificación de actores, posiciones y poder de influencia.</div>', unsafe_allow_html=True)
    
    # --- CÁLCULO DE PROGRESO ---
    df_actual = st.session_state.get('df_interesados', pd.DataFrame())
    analisis_txt = st.session_state.get('analisis_participantes', "")
    tiene_datos = not df_actual.empty and df_actual['NOMBRE'].dropna().any()
    tiene_analisis = len(str(analisis_txt).strip()) > 20
    progreso = (0.5 if tiene_datos else 0) + (0.5 if tiene_analisis else 0)
    st.progress(progreso, text=f"Completitud: {int(progreso * 100)}%")

with col_logo:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- RESUMEN RÁPIDO (KPIs) ---
if not df_actual.empty and "POSICIÓN" in df_actual.columns:
    st.markdown("##### 📊 Resumen de la Matriz")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-box"><div class="kpi-val">{len(df_actual.dropna(subset=["NOMBRE"]))}</div><div class="kpi-lab">Actores</div></div>', unsafe_allow_html=True)
    with k2:
        coop = len(df_actual[df_actual["POSICIÓN"] == "Cooperante"])
        st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:green;">{coop}</div><div class="kpi-lab">Cooperantes</div></div>', unsafe_allow_html=True)
    with k3:
        opos = len(df_actual[df_actual["POSICIÓN"] == "Opositor"])
        st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:red;">{opos}</div><div class="kpi-lab">Opositores</div></div>', unsafe_allow_html=True)
    with k4:
        p_alto = len(df_actual[df_actual["PODER"] == "Alto"])
        st.markdown(f'<div class="kpi-box"><div class="kpi-val">{p_alto}</div><div class="kpi-lab">Poder Alto</div></div>', unsafe_allow_html=True)

st.write("")

# --- 1. MATRIZ DE DATOS (VISUALIZACIÓN MEJORADA) ---
st.subheader("📝 Matriz de Datos")

# Configuración visual de columnas
column_config = {
    "NOMBRE": st.column_config.TextColumn("👤 Nombre / Actor", help="Nombre del interesado", width="medium"),
    "GRUPO": st.column_config.TextColumn("🏛️ Grupo", width="small"),
    "POSICIÓN": st.column_config.SelectboxColumn(
        "🚩 Actitud", 
        options=["Cooperante", "Beneficiario", "Opositor", "Perjudicado"],
        width="small"
    ),
    "EXPECTATIVA": st.column_config.TextColumn("🎯 Expectativa", width="large"),
    "CONTRIBUCION AL PROYECTO": st.column_config.TextColumn("🤝 Contribución"),
    "PODER": st.column_config.SelectboxColumn("⚡ Poder", options=["Alto", "Bajo"], width="small"),
    "INTERÉS": st.column_config.SelectboxColumn("🧐 Interés", options=["Alto", "Bajo"], width="small"),
    "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("🚀 Estrategia", disabled=True)
}

# Editor de datos mejorado
df_editado = st.data_editor(
    df_actual,
    column_config=column_config,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # Quitamos el índice para que se vea más limpio
    key="editor_interesados_pro"
)

# Lógica de guardado y cálculo de estrategia (Mantenida)
def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.write("")
# --- 2. ANÁLISIS CUALITATIVO (AUTO-AJUSTABLE) ---
st.subheader("📝 Análisis de Participantes")
analisis_previo = st.session_state.get('analisis_participantes', "")

# Función de altura (Ajustada para párrafos anchos)
lineas = str(analisis_previo).count('\n') + (len(str(analisis_previo)) // 100)
h_calc = max(150, (lineas + 2) * 24)

analisis_actual = st.text_area(
    "Analisis", value=analisis_previo, height=h_calc, 
    key="txt_analisis_final", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo general de los actores..."
)

if analisis_actual != analisis_previo:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
