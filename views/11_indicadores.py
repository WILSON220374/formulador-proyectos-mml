import streamlit as st
import pandas as pd
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-seccion">📊 11. Indicadores</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Fase IV: Análisis de Objetivos - Construcción de Indicadores</div>', unsafe_allow_html=True)
st.divider()

# --- EXTRACCIÓN DE OBJETIVOS (HOJA 7) ---
arbol = st.session_state.get('arbol_objetivos_final', {})

lista_base = []
# Buscamos en los niveles principales del árbol de objetivos
niveles = ["Objetivo General", "Fines Directos", "Fines Indirectos", "Medios Directos", "Medios Indirectos"]

for nivel in niveles:
    items = arbol.get(nivel, [])
    for item in items:
        # Blindaje: extrae texto sea diccionario o string
        texto = item.get("texto", str(item)) if isinstance(item, dict) else str(item)
        if texto and texto.strip():
            lista_base.append({"Nivel": nivel, "Objetivo": texto})

if not lista_base:
    st.warning("⚠️ No se encontraron objetivos. Por favor, completa primero la Hoja 7 (Árbol de Objetivos Final).")
    st.stop()

# --- INICIALIZACIÓN DE DATOS LOCALES ---
if 'datos_indicadores' not in st.session_state:
    st.session_state['datos_indicadores'] = {}

# Preparar datos para la tabla
df_data = []
for row in lista_base:
    obj_texto = row["Objetivo"]
    guardado = st.session_state['datos_indicadores'].get(obj_texto, {})
    
    df_data.append({
        "Nivel": row["Nivel"],
        "Objetivo": obj_texto,
        "Objeto": guardado.get("Objeto", ""),
        "Condición Deseada (Verbo)": guardado.get("Condicion", ""),
        "Lugar": guardado.get("Lugar", ""),
        "Indicador (Automático)": guardado.get("Indicador", "")
    })

df = pd.DataFrame(df_data)

# --- TABLA INTERACTIVA TIPO EXCEL ---
st.info("💡 Diligencia las columnas Objeto, Condición y Lugar. El indicador se construirá automáticamente al guardar.")

edited_df = st.data_editor(
    df,
    column_config={
        "Nivel": st.column_config.TextColumn("Nivel", disabled=True),
        "Objetivo": st.column_config.TextColumn("Objetivo", disabled=True, width="large"),
        "Objeto": st.column_config.TextColumn("1. Objeto"),
        "Condición Deseada (Verbo)": st.column_config.TextColumn("2. Condición Deseada"),
        "Lugar": st.column_config.TextColumn("3. Lugar"),
        "Indicador (Automático)": st.column_config.TextColumn("Indicador Generado", disabled=True, width="large"),
    },
    hide_index=True,
    use_container_width=True,
    key="editor_indicadores"
)

# --- GUARDADO Y CÁLCULO ---
if st.button("💾 Generar Indicadores y Guardar", type="primary"):
    for index, row in edited_df.iterrows():
        # Capturar valores evitando nulos
        obj = str(row["Objeto"]) if pd.notna(row["Objeto"]) else ""
        cond = str(row["Condición Deseada (Verbo)"]) if pd.notna(row["Condición Deseada (Verbo)"]) else ""
        lugar = str(row["Lugar"]) if pd.notna(row["Lugar"]) else ""
        
        # Concatenar automáticamente
        indicador_calculado = f"{obj} {cond} {lugar}".strip().replace("  ", " ")
        
        # Guardar en la memoria global
        st.session_state['datos_indicadores'][row["Objetivo"]] = {
            "Objeto": obj,
            "Condicion": cond,
            "Lugar": lugar,
            "Indicador": indicador_calculado
        }
        
    guardar_datos_nube()
    st.success("✅ Indicadores generados y sincronizados en la nube.")
    st.rerun()
