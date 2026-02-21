import streamlit as st
import os
import io
import pandas as pd
from datetime import datetime
from session_state import inicializar_session

# Importar la librería para crear el Word
try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    st.error("⚠️ Falta instalar la librería para generar Word. Ve a tu terminal y ejecuta: pip install python-docx")
    st.stop()

# 1. Asegurar persistencia 
inicializar_session()

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 12rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    .header-tabla { font-weight: 800; color: #1E3A8A; margin-bottom: 10px; font-size: 1.1rem; text-transform: uppercase; border-bottom: 2px solid #1E3A8A; padding-bottom: 5px;}
    .readonly-box { border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background-color: #f3f4f6; color: #374151; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📄 16. Generador de Reportes</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Prueba funcional: Exportación del módulo de Diagnóstico a Word.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- 1. EXTRAER AUTORES AUTOMÁTICAMENTE ---
st.markdown('<div class="header-tabla">⚙️ 1. Configuración de Portada</div>', unsafe_allow_html=True)

nombres_formuladores = "No se encontraron formuladores registrados"

# Buscar la tabla del equipo en la memoria
if "df_equipo" in st.session_state and isinstance(st.session_state["df_equipo"], pd.DataFrame):
    df = st.session_state["df_equipo"]
    if "Nombre" in df.columns:
        nombres_lista = df["Nombre"].dropna().astype(str).tolist()
        nombres_validos = [n for n in nombres_lista if n.strip() != ""]
        if nombres_validos:
            nombres_formuladores = ", ".join(nombres_validos)

st.write("**Autores / Formuladores (Extraídos de Hoja 1):**")
st.markdown(f'<div class="readonly-box">{nombres_formuladores}</div><br>', unsafe_allow_html=True)

st.divider()

# --- 2. MENÚ DE SELECCIÓN DE DIAGNÓSTICO ---
st.markdown('<div class="header-tabla">📑 2. Selección de Contenido (Diagnóstico)</div>', unsafe_allow_html=True)
st.write("Selecciona qué elementos del árbol de problemas quieres incluir en tu documento Word:")

with st.container(border=True):
    st.markdown("**Hoja: Diagnóstico (Árbol de Problemas)**")
    chk_problema = st.checkbox("El Problema Central", value=True)
    chk_sintomas = st.checkbox("Síntomas (Efectos)", value=True)
    chk_causas = st.checkbox("Causas Inmediatas", value=True)

st.divider()

# --- 3. MOTOR DE GENERACIÓN DEL WORD ---
def generar_documento_word():
    doc = Document()
    
    # --- Título Principal ---
    titulo = doc.add_heading("Reporte de Formulación de Proyecto", 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # --- Datos de Portada ---
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    doc.add_paragraph(f"Fecha de generación: {fecha_actual}")
    p_autores = doc.add_paragraph()
    p_autores.add_run("Formuladores: ").bold = True
    p_autores.add_run(nombres_formuladores)
    
    doc.add_page_break() # Salto de página
    
    # --- Sección de Diagnóstico ---
    doc.add_heading("1. Diagnóstico y Problema", level=1)
    
    # 1. Problema Central
    if chk_problema:
        doc.add_heading("1.1 El Problema Central", level=2)
        # Extrae de la memoria (Ajusta 'problema_central' si tu variable se llama distinto en esa hoja)
        texto_prob = st.session_state.get('problema_central', 'No se ha redactado el problema central en la hoja correspondiente.')
        doc.add_paragraph(str(texto_prob))
        
    # 2. Síntomas (Efectos)
    if chk_sintomas:
        doc.add_heading("1.2 Síntomas (Efectos)", level=2)
        # Extrae de la memoria (Ajusta 'efectos_directos' si tu variable se llama distinto)
        texto_sintomas = st.session_state.get('efectos_directos', 'No se han registrado síntomas/efectos.')
        doc.add_paragraph(str(texto_sintomas))
        
    # 3. Causas Inmediatas
    if chk_causas:
        doc.add_heading("1.3 Causas Inmediatas", level=2)
        # Extrae de la memoria (Ajusta 'causas_directas' si tu variable se llama distinto)
        texto_causas = st.session_state.get('causas_directas', 'No se han registrado causas inmediatas.')
        doc.add_paragraph(str(texto_causas))

    # Guardar en memoria virtual para la descarga
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. BOTÓN DE DESCARGA REAL ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)

# Creamos el documento solo si el usuario hace clic (para ahorrar recursos)
buffer_word = generar_documento_word()

st.download_button(
    label="📝 Generar y Descargar Word (.docx)",
    data=buffer_word,
    file_name="Diagnostico_Proyecto.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    type="primary"
)
