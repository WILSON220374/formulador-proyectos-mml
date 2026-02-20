import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- DISEÑO ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-seccion">🛡️ 12. Supuestos y Riesgos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Fase IV: Análisis de Riesgos y Factores Externos</div>', unsafe_allow_html=True)
st.divider()

# --- EXTRACCIÓN DE OBJETIVOS (HOJA 7) ---
arbol = st.session_state.get('arbol_objetivos_final', {})
niveles = ["Objetivo General", "Fines Directos", "Fines Indirectos", "Medios Directos", "Medios Indirectos"]

objetivos_lista = []
for nivel in niveles:
    items = arbol.get(nivel, [])
    for item in items:
        texto = item.get("texto", str(item)) if isinstance(item, dict) else str(item)
        if texto and texto.strip():
            objetivos_lista.append(texto)

if not objetivos_lista:
    st.warning("⚠️ No se encontraron objetivos en la Hoja 7. Por favor, complétala antes de continuar.")
    st.stop()

# --- CONFIGURACIÓN DE LISTAS DESPLEGABLES ---
opciones_probabilidad = ["Muy Baja", "Baja", "Media", "Alta", "Muy Alta"]
opciones_impacto = ["Insignificante", "Menor", "Moderado", "Mayor", "Catastrófico"]
opciones_categoria = ["Financiero", "Operativo", "Social", "Ambiental", "Político", "Técnico"]

# --- INICIALIZACIÓN DE DATOS ---
if 'datos_riesgos' not in st.session_state:
    st.session_state['datos_riesgos'] = pd.DataFrame([
        {
            "Objetivo": obj,
            "Supuesto": "",
            "Riesgo": "",
            "Categoría": "Técnico",
            "Probabilidad": "Media",
            "Impacto": "Moderado",
            "Efecto": "",
            "Medida de Mitigación": ""
        } for obj in objetivos_lista
    ])

# --- TABLA EDITABLE (ESTILO EXCEL) ---
st.info("💡 Completa la matriz de riesgos. Las columnas de Categoría, Probabilidad e Impacto tienen menús desplegables.")

column_config = {
    "Objetivo": st.column_config.TextColumn("Objetivo (Fuente)", disabled=True, width="medium"),
    "Supuesto": st.column_config.TextColumn("Supuesto (Condición para éxito)", width="medium"),
    "Riesgo": st.column_config.TextColumn("Riesgo Identificado", width="medium"),
    "Categoría": st.column_config.SelectboxColumn("Categoría", options=opciones_categoria),
    "Probabilidad": st.column_config.SelectboxColumn("Probabilidad", options=opciones_probabilidad),
    "Impacto": st.column_config.SelectboxColumn("Impacto", options=opciones_impacto),
    "Efecto": st.column_config.TextColumn("Efecto del Riesgo"),
    "Medida de Mitigación": st.column_config.TextColumn("Medida de Mitigación/Control", width="large"),
}

# Editor de datos
edited_df = st.data_editor(
    st.session_state['datos_riesgos'],
    column_config=column_config,
    hide_index=True,
    use_container_width=True,
    key="editor_riesgos"
)

# --- BOTÓN DE GUARDADO ---
if st.button("💾 Guardar Matriz de Riesgos", type="primary"):
    st.session_state['datos_riesgos'] = edited_df
    guardar_datos_nube()
    st.success("✅ Matriz de riesgos actualizada y guardada en la nube.")
    st.rerun()
