import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- DISEÑO PROFESIONAL Y ESTILO CSS PARA AGGRID ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    
    /* Formato para los encabezados de AgGrid */
    .ag-header-cell-label { justify-content: center; }
    .ag-header { background-color: #1E3A8A !important; }
    .ag-header-cell-text { color: white !important; font-weight: bold !important; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Estructura operativa: Objetivos, Indicadores, Metas y Supuestos.</div>', unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
def preparar_matriz():
    arbol = st.session_state.get('arbol_objetivos_final', {})
    ind_db = st.session_state.get('datos_indicadores', {})
    riesgos_df = st.session_state.get('datos_riesgos', pd.DataFrame())
    
    filas = []
    # Definimos el orden lógico de la MML
    mapeo = [
        ("Objetivo General", "FIN / OBJETIVO GENERAL"),
        ("Fines Directos", "PROPÓSITO"),
        ("Medios Directos", "COMPONENTE"),
        ("Medios Indirectos", "ACTIVIDAD")
    ]

    for nivel_orig, nivel_mml in mapeo:
        items = arbol.get(nivel_orig, [])
        for item in items:
            texto_obj = item.get("texto", str(item)) if isinstance(item, dict) else str(item)
            
            # Buscar Indicador (Hoja 11)
            indicador = ind_db.get(texto_obj, {}).get("Indicador", "")
            
            # Buscar Supuesto (Hoja 12)
            supuesto = ""
            if not riesgos_df.empty and "Objetivo" in riesgos_df.columns:
                match = riesgos_df[riesgos_df["Objetivo"] == texto_obj]
                if not match.empty:
                    supuesto = match.iloc[0].get("Supuesto", "")

            filas.append({
                "TIPO": nivel_mml,
                "OBJETIVOS": texto_obj,
                "INDICADOR": indicador,
                "META / MEDIO VERIFICACIÓN": "",
                "SUPUESTOS": supuesto
            })
    return pd.DataFrame(filas)

# Cargar o inicializar
if 'mml_data' not in st.session_state or st.session_state['mml_data'].empty:
    st.session_state['mml_data'] = preparar_matriz()

df_mml = st.session_state['mml_data']

# --- BARRA DE AVANCE ---
# Calculamos avance basado en si la columna "META" tiene contenido
metas_llenadas = df_mml["META / MEDIO VERIFICACIÓN"].apply(lambda x: str(x).strip() != "").sum()
total_filas = len(df_mml)
avance = metas_llenadas / total_filas if total_filas > 0 else 0
st.progress(avance)
st.caption(f"Progreso de la Matriz: {int(avance*100)}%")

# --- CONFIGURACIÓN DE AGGRID ---
gb = GridOptionsBuilder.from_dataframe(df_mml)

# Configuración Global: Centrado de texto y autoajuste (Wrap Text)
gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=True,
    wrapText=True,        # <-- Esto hace que el texto baje
    autoHeight=True,      # <-- Esto ajusta la altura de la celda
    cellStyle={'textAlign': 'center'}
)

# Configuración específica de columnas
gb.configure_column("TIPO", width=150, editable=False, cellStyle={'fontWeight': 'bold', 'backgroundColor': '#f0f4f8'})
gb.configure_column("OBJETIVOS", width=300, editable=False)
gb.configure_column("INDICADOR", width=300, editable=False)
gb.configure_column("META / MEDIO VERIFICACIÓN", width=350, cellStyle={'backgroundColor': '#fffbeb'})
gb.configure_column("SUPUESTOS", width=250, editable=False)

# Opciones de la grilla
grid_options = gb.build()

# Estilo de encabezado (Azul oscuro vía inyección de CSS en AgGrid)
grid_response = AgGrid(
    df_mml,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme='streamlit', # O 'balham', 'alpine'
    key="mml_aggrid"
)

# --- GUARDADO ---
if st.button("💾 Guardar Matriz de Marco Lógico", type="primary"):
    st.session_state['mml_data'] = pd.DataFrame(grid_response['data'])
    guardar_datos_nube()
    st.success("✅ ¡Matriz guardada con éxito!")
    st.rerun()
