import streamlit as st
import os
import pandas as pd
from session_state import inicializar_session

# 1. Asegurar persistencia 
inicializar_session()

# --- DISEÑO DE ALTO IMPACTO (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Estilo base de las tarjetas */
    .card-mml {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Contenido de los datos alineado verticalmente */
    .col-content {
        font-size: 0.95rem;
        color: #334155;
        text-align: left;
        line-height: 1.4;
        display: flex;
        align-items: center;
    }

    /* Encabezado global de la tabla */
    .header-global {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 0.85rem;
        text-transform: uppercase;
        text-align: center;
        border-bottom: 2px solid #1E3A8A;
        padding-bottom: 10px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: row;
        gap: 15px;
    }

    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Etiquetas de nivel (Badges) */
    .tipo-badge {
        color: white;
        padding: 8px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        text-align: center;
        display: inline-block;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON IMAGEN Y AVANCE ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Revisión de la estructura operativa y coherencia del proyecto.</div>', unsafe_allow_html=True)
    st.progress(0.90)
    
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- CONFIGURACIÓN DE COLORES POR NIVEL ---
CONFIG_NIVELES = {
    "OBJETIVO GENERAL":       {"color": "#4338CA", "bg": "#EEF2FF"}, # Índigo
    "OBJETIVO ESPECÍFICO":    {"color": "#2563EB", "bg": "#EFF6FF"}, # Azul
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}  # Ámbar
}

# --- EXTRACCIÓN DE DATOS REALES (MÉTODO DINÁMICO HOJA 11) ---
mapa = st.session_state.get("indicadores_mapa_objetivo", {})
datos_ind = st.session_state.get("datos_indicadores", {})
seleccion = st.session_state.get("seleccion_indicadores", {})
metas = st.session_state.get("meta_resultados_parciales", {})
riesgos_df = st.session_state.get("datos_riesgos", pd.DataFrame())

if isinstance(riesgos_df, pd.DataFrame) and not riesgos_df.empty:
    riesgos = riesgos_df.to_dict(orient="records")
else:
    riesgos = []

datos_reales = []

# Reconstruimos la información cruzando las memorias
for kmap, k in mapa.items():
    partes = kmap.split("||")
    if len(partes) != 2:
        continue
        
    nivel_original = partes[0]
    objetivo_texto = partes[1]
    
    # 1. Verificar si el indicador fue seleccionado y validado (P1 a P5)
    sel = seleccion.get(k, {})
    p_cols = ["P1", "P2", "P3", "P4", "P5"]
    is_selected = True if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in p_cols) else False
    
    if not is_selected:
        continue # Si no fue seleccionado, lo omitimos de la Matriz Final
        
    # 2. Extraer indicador formulado y meta
    ind_data = datos
