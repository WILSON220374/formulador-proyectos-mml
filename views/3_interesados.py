import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización
inicializar_session()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 32px !important; font-weight: 800 !important; color: #4F8BFF; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 10px; }
    
    .card-interesado {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 2px 4px 12px rgba(0,0,0,0.05);
        border-left: 10px solid #ddd;
        display: flex;
        flex-direction: column;
        min-height: 200px;
    }
    .status-cooperante { border-left-color: #28a745 !important; }
    .status-opositor { border-left-color: #dc3545 !important; }
    .status-beneficiario { border-left-color: #17a2b8 !important; }
    .status-perjudicado { border-left-color: #ffc107 !important; }

    .nombre-actor { font-size: 19px; font-weight: 800; color: #1E3A8A; margin-bottom: 2px; }
    .grupo-actor { font-size: 13px; color: #666; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; }
    
    .label-mini { font-size: 11px; color: #999; text-transform: uppercase; font-weight: bold; margin-top: 8px; }
    .texto-detalle { font-size: 14px; color: #333; line-height: 1.3; }
    
    .pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        background-color: #f0f2f6;
        margin-right: 5px;
    }
    
    [data-testid="stImage"] img { pointer-events: none; user-select: none; border-radius: 10px; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Gestión estratégica de actores y sus niveles de influencia.</div>', unsafe_allow_html=True)
    
    df_actual = st.session_state.get('df_interesados', pd.DataFrame())
    analisis_txt = st.session_state.get('analisis_participantes', "")
    progreso = (0.5 if not df_actual.empty and df_actual['NOMBRE'].dropna().any() else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Completitud: {int(progreso * 100)}%")

with col_logo:
    logo_path = "unnamed.jpg" if os.path.exists("unnamed.jpg") else "unnamed-1.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

st.divider()

# --- SECCIÓN 1: VISTA DE FICHAS (CORREGIDA) ---
st.subheader("👥 Actores Identificados")

if not df_actual.empty and df_actual['NOMBRE'].dropna().any():
    fichas_cols = st.columns(2)
    actores_validos = df_actual[df_actual['NOMBRE'].notna() & (df_actual['NOMBRE'] != "")]
    
    # --- CAMBIO CLAVE: Usamos enumerate(..., start=0) para tener un contador i seguro ---
    for i, (idx, row) in enumerate(actores_validos.iterrows()):
        pos = str(row.get('POSICIÓN', '')).lower()
        clase_status = ""
        if "cooperante" in pos: clase_status = "status-cooperante"
        elif "opositor" in pos: clase_status = "status-opositor"
        elif "beneficiario" in pos: clase_status = "status-beneficiario"
        elif "perjudicado" in pos: clase_status = "status-perjudicado"
        
        # Usamos 'i' en lugar de 'idx' para el cálculo de la columna
        with fichas_cols[i % 2]:
            st.markdown(f"""
                <div class="card-interesado {clase_status}">
                    <div class="nombre-actor">{row['NOMBRE']}</div>
                    <div class="grupo-actor">{row.get('GRUPO', 'Sin Grupo')}</div>
                    <div>
                        <span class="pill">⚡ Poder: {row.get('PODER', 'N/A')}</span>
                        <span class="pill">🧐 Interés: {row.get('INTERÉS', 'N/A')}</span>
                    </div>
                    <div class="label-mini">Expectativa Principal</div>
                    <div class="texto-detalle">{row.get('EXPECTATIVA', 'No definida')}</div>
                    <div class="label-mini">Estrategia Sugerida</div>
                    <div class="texto-detalle"><b>{row.get('ESTRATEGIA DE INVOLUCRAMIENTO', 'Sin definir')}</b></div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Aún no hay actores registrados. Use el editor al final de la página para agregarlos.")

st.divider()

# --- SECCIÓN 2: EDITOR ---
with st.expander("⚙️ Configuración: Editar Matriz de Datos"):
    df_editado = st.data_editor(
        df_actual,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_fichas_v4"
    )
    
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

# --- SECCIÓN 3: ANÁLISIS ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Analisis", value=analisis_txt, height=200, 
    key="txt_analisis_final", label_visibility="collapsed"
)

if analisis_actual != analisis_txt:
    st.session_state['analisis_participantes'] = analisis_actual
    guardar_datos_nube()
    st.rerun()
