import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 150px !important; }

    /* Estilos generales */
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Tabla Limpia */
    div[data-testid="stDataEditor"] {
        border: none !important;
        background-color: transparent !important;
    }

    /* KPIs */
    .kpi-card {
        background: #f8f9fa; padding: 15px; border-radius: 8px;
        text-align: center; border: 1px solid #eee;
    }
    .kpi-val { font-size: 24px; font-weight: 800; color: #000000; }
    .kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }

    [data-testid="stImage"] img { border-radius: 12px; pointer-events: none; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Matriz de actores clave y mapeo de influencias estratégicas.</div>', unsafe_allow_html=True)
    
    # Verificación de datos segura
    tiene_datos = False
    if isinstance(df_actual, pd.DataFrame) and not df_actual.empty and 'NOMBRE' in df_actual.columns:
        tiene_datos = df_actual['NOMBRE'].dropna().any()
        
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Completitud: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- 1. LIMPIEZA PROFUNDA DE DATOS (ESTO BORRA EL ÍNDICE FANTASMA) ---
# Definimos estrictamente qué columnas queremos. Todo lo demás (índices, números raros) se borra.
columnas_validas = [
    "NOMBRE", "GRUPO", "POSICIÓN", "EXPECTATIVA", 
    "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA"
]

if df_actual.empty: 
    df_clean = pd.DataFrame(columns=columnas_validas)
else:
    # 1. Aseguramos que existan las columnas
    for col in columnas_validas:
        if col not in df_actual.columns:
            df_actual[col] = ""
    
    # 2. FILTRO DRÁSTICO: Creamos una copia SOLO con las columnas válidas.
    # Esto elimina cualquier columna "0", "Unnamed: 0", "index", etc.
    df_clean = df_actual[columnas_validas].copy()
    
    # 3. Mapeo de Iconos (si no los tienen)
    mapeo_iconos = {
        "Opositor": "🔴 Opositor", "Cooperante": "🟢 Cooperante", 
        "Beneficiario": "🔵 Beneficiario", "Perjudicado": "🟣 Perjudicado",
        "Alto": "⚡ Alto", "Bajo": "🔅 Bajo"
    }
    for col in ["POSICIÓN", "PODER", "INTERÉS"]:
        df_clean[col] = df_clean[col].apply(lambda x: mapeo_iconos.get(str(x).strip(), x) if str(x).strip() in mapeo_iconos else x)

# --- KPIs ---
if tiene_datos:
    total = len(df_clean.dropna(subset=["NOMBRE"]))
    opos = len(df_clean[df_clean["POSICIÓN"].astype(str).str.contains("Opositor", case=False, na=False)])
    coop = len(df_clean[df_clean["POSICIÓN"].astype(str).str.contains("Cooperante", case=False, na=False)])
    p_alto = len(df_clean[df_clean["PODER"].astype(str).str.contains("Alto", case=False, na=False)])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{total}</div><div class="kpi-label">Total</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{opos}</div><div class="kpi-label">Opositores</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{coop}</div><div class="kpi-label">Cooperantes</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{p_alto}</div><div class="kpi-label">Poder Alto</div></div>', unsafe_allow_html=True)

# --- MATRIZ DE DATOS ---
st.subheader("📝 Matriz de Datos")

opciones_pos = ["🔴 Opositor", "🟢 Cooperante", "🔵 Beneficiario", "🟣 Perjudicado"]
opciones_niv = ["⚡ Alto", "🔅 Bajo"]

config_columnas = {
    "NOMBRE": st.column_config.TextColumn("👤 Nombre del Actor", width="medium", required=True),
    "GRUPO": st.column_config.TextColumn("🏢 Grupo", width="small"),
    "POSICIÓN": st.column_config.SelectboxColumn("🚩 Posición", options=opciones_pos, width="small"),
    "EXPECTATIVA": st.column_config.TextColumn("🎯 Expectativa", width="large"),
    "CONTRIBUCION AL PROYECTO": st.column_config.TextColumn("💡 Contribución", width="medium"),
    "PODER": st.column_config.SelectboxColumn("⚡ Poder", options=opciones_niv, width="small"),
    "INTERÉS": st.column_config.SelectboxColumn("👁️ Interés", options=opciones_niv, width="small"),
    "ESTRATEGIA": st.column_config.TextColumn("🚀 Estrategia", disabled=True, width="medium")
}

# RENDERIZADO
# Al usar df_clean, garantizamos que no hay columnas extrañas que Streamlit confunda con datos.
df_editado = st.data_editor(
    df_clean,
    column_config=config_columnas,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # AHORA SÍ DEBERÍA FUNCIONAR PORQUE EL DF ESTÁ LIMPIO
    key="editor_interesados_final_clean_v3"
)

# --- LÓGICA DE ESTRATEGIA (CON TUS TEXTOS) ---
def calcular_estrategia(row):
    # Limpiamos iconos para calcular
    p = str(row.get('PODER', '')).replace("⚡ ", "").replace("🔅 ", "").strip()
    i = str(row.get('INTERÉS', '')).replace("⚡ ", "").replace("🔅 ", "").strip()
    
    if p == "Alto" and i == "Bajo": return "INVOLUCRAR - MANTENER SATISFECHOS"
    if p == "Alto" and i == "Alto": return "INVOLUCRAR Y ATRAER EFECTIVAMENTE"
    if p == "Bajo" and i == "Alto": return "MANTENER INFORMADOS"
    if p == "Bajo" and i == "Bajo": return "MONITOREAR"
    return ""

# Guardado Inteligente
if not df_editado.equals(df_actual): # Comparamos con el original para detectar cambios
    if not df_editado.empty:
        df_editado["ESTRATEGIA"] = df_editado.apply(calcular_estrategia, axis=1)
    
    # Guardamos la versión limpia en la nube
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
                if k in pos_txt: icono = v; break
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
