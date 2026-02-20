import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from session_state import inicializar_session, guardar_datos_nube

# ---------------------------------------------
# 13. MATRIZ MARCO LÓGICO (DISEÑO)
# - Sin enlaces a datos (no trae información de otras hojas)
# - Tabla vacía con formato y guardado
# ---------------------------------------------
inicializar_session()

# --- ESTILO CSS (encabezados azul oscuro + tipografías) ---
st.markdown(
    """
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }

    /* Encabezados AgGrid */
    .ag-header-cell-label { justify-content: center; }
    .ag-header { background-color: #1E3A8A !important; }
    .ag-header-cell-text { color: white !important; font-weight: bold !important; text-transform: uppercase; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Diseño de tabla (sin carga automática). Diligencia manualmente y guarda en nube.</div>', unsafe_allow_html=True)

# --- ESTRUCTURA VACÍA (SIN ENLACES A OTRAS HOJAS) ---
COLUMNAS = ["TIPO", "OBJETIVOS", "INDICADOR", "META", "SUPUESTOS"]

def _tabla_vacia(n_filas: int = 8) -> pd.DataFrame:
    # filas vacías para que el usuario pueda diligenciar desde el inicio
    return pd.DataFrame([{c: "" for c in COLUMNAS} for _ in range(max(int(n_filas), 1))])

if "mml_data" not in st.session_state or not isinstance(st.session_state.get("mml_data"), pd.DataFrame):
    st.session_state["mml_data"] = _tabla_vacia(8)

df_mml = st.session_state["mml_data"].copy()

# Asegurar columnas (por compatibilidad si existía una versión previa)
for c in COLUMNAS:
    if c not in df_mml.columns:
        df_mml[c] = ""
df_mml = df_mml[COLUMNAS]

# --- BARRA DE AVANCE (BASADA EN META) ---
metas_llenadas = df_mml["META"].apply(lambda x: str(x).strip() != "").sum()
total_filas = len(df_mml)
avance = metas_llenadas / total_filas if total_filas > 0 else 0.0
st.progress(avance)
st.caption(f"Progreso de la Matriz: {int(avance * 100)}%")

# --- CONFIGURACIÓN AGGRID ---
gb = GridOptionsBuilder.from_dataframe(df_mml)

gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=True,
    wrapText=True,      # texto baja al reducir ancho
    autoHeight=True,    # filas crecen verticalmente
    cellStyle={"textAlign": "center"},
)

gb.configure_column("TIPO", width=170, cellStyle={"fontWeight": "bold", "backgroundColor": "#f0f4f8"})
gb.configure_column("OBJETIVOS", width=340)
gb.configure_column("INDICADOR", width=340)
gb.configure_column("META", width=260, cellStyle={"backgroundColor": "#fffbeb"})
gb.configure_column("SUPUESTOS", width=300)

grid_options = gb.build()

grid_response = AgGrid(
    df_mml,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme="streamlit",
    key="mml_aggrid",
)

# --- GUARDADO ---
if st.button("💾 Guardar Matriz de Marco Lógico", type="primary"):
    st.session_state["mml_data"] = pd.DataFrame(grid_response["data"])[COLUMNAS]
    guardar_datos_nube()
    st.success("✅ ¡Matriz guardada con éxito!")
    st.rerun()
