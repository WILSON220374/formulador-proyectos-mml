import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización de seguridad y datos
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS (Diseño Limpio + Scrollbars Visibles) ---
st.markdown("""
    <style>
    /* Ajuste de scroll de la página completa */
    .block-container { padding-bottom: 150px !important; }

    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Contenedor de la Tabla */
    div[data-testid="stDataEditor"] {
        background-color: #ffffff;
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* --- TRUCO PARA FORZAR SCROLLBARS SIEMPRE VISIBLES --- */
    div[data-testid="stDataEditor"] ::-webkit-scrollbar {
        -webkit-appearance: none;
        width: 12px !important;  /* Ancho vertical */
        height: 12px !important; /* Alto horizontal */
        display: block !important;
        background: #f1f1f1;
    }
    div[data-testid="stDataEditor"] ::-webkit-scrollbar-thumb {
        background-color: #c1c1c1; /* Color de la barra */
        border-radius: 6px;
        border: 2px solid #f1f1f1; /* Espacio alrededor */
    }
    div[data-testid="stDataEditor"] ::-webkit-scrollbar-thumb:hover {
        background-color: #a8a8a8; /* Color al pasar el mouse */
    }
    div[data-testid="stDataEditor"] ::-webkit-scrollbar-corner {
        background: transparent;
    }
    
    /* Tarjetas de KPI */
    .kpi-card {
        background: white; padding: 15px; border-radius: 10px;
        border: 1px solid #f1f5f9; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-val { font-size: 24px; font-weight: 800; color: #000000; }
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

# --- MIGRACIÓN AUTOMÁTICA DE DATOS ---
if not df_actual.empty:
    mapeo_iconos = {
        "Opositor": "🔴 Opositor", "Cooperante": "🟢 Cooperante", 
        "Beneficiario": "🔵 Beneficiario", "Perjudicado": "🟣 Perjudicado",
        "Alto": "⚡ Alto", "Bajo": "🔅 Bajo"
    }
    for col in ["POSICIÓN", "PODER", "INTERÉS"]:
        if col in df_actual.columns:
            df_actual[col] = df_actual[col].apply(lambda x: mapeo_iconos.get(str(x).strip(), x) if str(x).strip() in mapeo_iconos else x)

# --- KPIs ---
if tiene_datos:
    total = len(df_actual.dropna(subset=["NOMBRE"]))
    opos = len(df_actual[df_actual["POSICIÓN"].astype(str).str.contains("Opositor", case=False, na=False)])
    coop = len(df_actual[df_actual["POSICIÓN"].astype(str).str.contains("Cooperante", case=False, na=False)])
    p_alto = len(df_actual[df_actual["PODER"].astype(str).str.contains("Alto", case=False, na=False)])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{total}</div><div class="kpi-label">Total Actores</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{opos}</div><div class="kpi-label">Opositores</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{coop}</div><div class="kpi-label">Cooperantes</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{p_alto}</div><div class="kpi-label">Poder Alto</div></div>', unsafe_allow_html=True)

# --- MATRIZ DE DATOS ---
st.subheader("📝 Matriz de Datos")

opciones_pos = ["🔴 Opositor", "🟢 Cooperante", "🔵 Beneficiario", "🟣 Perjudicado"]
opciones_niv = ["⚡ Alto", "🔅 Bajo"]

config_columnas = {
    "NOMBRE": st.column_config.TextColumn("👤 Nombre del Actor", width="medium", required=True),
    "GRUPO": st.column_config.TextColumn("🏢 Grupo / Entidad", width="small"),
    "POSICIÓN": st.column_config.SelectboxColumn("🚩 Posición", options=opciones_pos, width="small"),
    "EXPECTATIVA": st.column_config.TextColumn("🎯 Expectativa Principal", width="large"),
    "CONTRIBUCION AL PROYECTO": st.column_config.TextColumn("💡 Contribución", width="medium"),
    "PODER": st.column_config.SelectboxColumn("⚡ Poder", options=opciones_niv, width="small"),
    "INTERÉS": st.column_config.SelectboxColumn("👁️ Interés", options=opciones_niv, width="small"),
    "ESTRATEGIA": st.column_config.TextColumn("🚀 Estrategia Sugerida", disabled=True, width="large")
}

# Preparar DataFrame
cols_orden = ["NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA"]
if df_actual.empty: df_actual = pd.DataFrame(columns=cols_orden)
for c in cols_orden:
    if c not in df_actual.columns: df_actual[c] = ""
df_actual = df_actual[cols_orden]

# Renderizado
df_editado = st.data_editor(
    df_actual,
    column_config=config_columnas,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="editor_interesados_scroll_visible"
)

# Lógica de cálculo (Según tu imagen)
def calcular_estrategia(row):
    p = str(row.get('PODER', '')).replace("⚡ ", "").replace("🔅 ", "").strip()
    i = str(row.get('INTERÉS', '')).replace("⚡ ", "").replace("🔅 ", "").strip()
    
    if p == "Alto" and i == "Bajo": return "INVOLUCRAR - MANTENER SATISFECHOS"
    if p == "Alto" and i == "Alto": return "INVOLUCRAR Y ATRAER EFECTIVAMENTE"
    if p == "Bajo" and i == "Alto": return "MANTENER INFORMADOS"
    if p == "Bajo" and i == "Bajo": return "MONITOREAR"
    return ""

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
    
    def obtener_lista(p_key, i_key):
        f = df_editado[
            (df_editado['PODER'].astype(str).str.contains(p_key)) & 
            (df_editado['INTERÉS'].astype(str).str.contains(i_key)) & 
            (df_editado['NOMBRE'].notna()) & (df_editado['NOMBRE'] != "")
        ]
        res = []
        for _, r in f.iterrows():
            pos_txt = str(r['POSICIÓN'])
            icono = "⚪"
            for k, v in color_map.items():
                if k in pos_txt:
                    icono = v
                    break
            res.append(f"{icono} **{r['NOMBRE']}**")
        return res or ["*Sin actores*"]

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.error("🤝 **INVOLUCRAR - MANTENER SATISFECHOS** (P:Alto / I:Bajo)")
            for item in obtener_lista("Alto", "Bajo"): st.markdown(item)
        with st.container(border=True):
            st.warning("🔍 **MONITOREAR** (P:Bajo / I:Bajo)")
            for item in obtener_lista("Bajo", "Bajo"): st.markdown(item)
    with c2:
        with st.container(border=True):
            st.success("🚀 **INVOLUCRAR Y ATRAER EFECTIVAMENTE** (P:Alto / I:Alto)")
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
