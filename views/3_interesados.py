import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización de seguridad y datos
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS (Diseño Limpio) ---
st.markdown("""
    <style>
    /* Ajuste de scroll */
    .block-container { padding-bottom: 150px !important; }

    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Contenedor del Panel de Datos (Tabla) */
    div[data-testid="stDataEditor"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Estilo para Tarjetas de KPI */
    .kpi-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f1f5f9;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-val { font-size: 24px; font-weight: 800; color: #000000; } /* Números en negro */
    .kpi-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }

    [data-testid="stImage"] img { border-radius: 12px; pointer-events: none; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores clave y mapeo de influencias estratégicas.</div>', unsafe_allow_html=True)
    
    tiene_datos = not df_actual.empty and 'NOMBRE' in df_actual.columns and df_actual['NOMBRE'].dropna().any()
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Completitud: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- KPIs ---
if tiene_datos:
    # Cálculos seguros
    total = len(df_actual.dropna(subset=["NOMBRE"]))
    # Convertimos a string por si hay valores nulos o diferentes tipos
    opos = len(df_actual[df_actual["POSICIÓN"].astype(str) == "Opositor"])
    coop = len(df_actual[df_actual["POSICIÓN"].astype(str) == "Cooperante"])
    p_alto = len(df_actual[df_actual["PODER"].astype(str) == "Alto"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{total}</div><div class="kpi-label">Total Actores</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{opos}</div><div class="kpi-label">Opositores</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{coop}</div><div class="kpi-label">Cooperantes</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{p_alto}</div><div class="kpi-label">Poder Alto</div></div>', unsafe_allow_html=True)

# --- MATRIZ DE DATOS (NATIVA) ---
st.subheader("📝 Matriz de Datos")

# Configuración de columnas (Sin AgGrid, usando el editor nativo mejorado)
config_columnas = {
    "NOMBRE": st.column_config.TextColumn("Nombre del Actor", width="medium", required=True),
    "GRUPO": st.column_config.TextColumn("Grupo / Entidad", width="small"),
    "POSICIÓN": st.column_config.SelectboxColumn("Posición", options=["Opositor", "Beneficiario", "Cooperante", "Perjudicado"], width="small"),
    "EXPECTATIVA": st.column_config.TextColumn("Expectativa Principal", width="large"),
    "CONTRIBUCION AL PROYECTO": st.column_config.TextColumn("Contribución", width="medium"),
    "PODER": st.column_config.SelectboxColumn("Poder", options=["Alto", "Bajo"], width="small"),
    "INTERÉS": st.column_config.SelectboxColumn("Interés", options=["Alto", "Bajo"], width="small"),
    "ESTRATEGIA": st.column_config.TextColumn("Estrategia Sugerida", disabled=True, width="medium")
}

# Preparar DataFrame
cols_orden = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA"]
if df_actual.empty: df_actual = pd.DataFrame(columns=cols_orden)
# Asegurar columnas
for c in cols_orden:
    if c not in df_actual.columns: df_actual[c] = ""
df_actual = df_actual[cols_orden]

# Renderizado NATIVO (Permite agregar filas automáticamente al escribir abajo)
df_editado = st.data_editor(
    df_actual,
    column_config=config_columnas,
    num_rows="dynamic", # Esto activa el botón "+" nativo abajo
    use_container_width=True,
    hide_index=True,
    key="editor_interesados_nativo_restored"
)

# Lógica de cálculo
def calcular_estrategia(row):
    p, i = str(row.get('PODER', '')).strip(), str(row.get('INTERÉS', '')).strip()
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

# Guardado
if not df_editado.equals(df_actual):
    if not df_editado.empty:
        df_editado["ESTRATEGIA"] = df_editado.apply(calcular_estrategia, axis=1)
    st.session_state['df_interesados'] = df_editado
    guardar_datos_nube()
    st.rerun()

st.write("")

# --- MAPA ESTRATÉGICO ---
st.subheader("📊 Mapa de Influencia")
if tiene_datos:
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    def obtener_lista(p, i):
        f = df_editado[(df_editado['PODER'] == p) & (df_editado['INTERÉS'] == i) & (df_editado['NOMBRE'].notna()) & (df_editado['NOMBRE'] != "")]
        return [f"{color_map.get(r['POSICIÓN'], '⚪')} **{r['NOMBRE']}**" for _, r in f.iterrows()] or ["*Sin actores*"]

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **CONSULTAR / SATISFACER** (P:Alto / I:Bajo)")
            for item in obtener_lista("Alto", "Bajo"): st.markdown(item)
        with st.container(border=True):
            st.warning("🔍 **MONITORIZAR** (P:Bajo / I:Bajo)")
            for item in obtener_lista("Bajo", "Bajo"): st.markdown(item)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR ATENTAMENTE** (P:Alto / I:Alto)")
            for item in obtener_lista("Alto", "Alto"): st.markdown(item)
        with st.container(border=True):
            st.info("📧 **MANTENER INFORMADOS** (P:Bajo / I:Alto)")
            for item in obtener_lista("Bajo", "Alto"): st.markdown(item)
else:
    st.info("Complete la matriz para activar el mapa estratégico.")

st.divider()

# --- ANÁLISIS FINAL ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, height=200, 
    key="txt_analisis_final_panel", label_visibility="collapsed",
    placeholder="Escriba aquí el análisis cualitativo..."
)

if analisis_actual != analisis_txt:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
