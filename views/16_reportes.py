import streamlit as st
import os
import io
from datetime import datetime
from session_state import inicializar_session

# --- IMPORTACIÓN DE LIBRERÍAS (WORD Y PDF) ---
try:
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    st.error("⚠️ Falta la librería para Word. Agrega 'python-docx' a tu requirements.txt")
    st.stop()

try:
    from fpdf import FPDF
except ImportError:
    st.error("⚠️ Falta la librería para PDF. Agrega 'fpdf2' a tu requirements.txt")
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
    .readonly-box { border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background-color: #f3f4f6; color: #1E3A8A; font-weight: 800; text-align: center; font-size: 1.2rem;}
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📄 16. Generador de Reportes</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Configuración de portada y exportación de documentos.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# ==========================================
# 📘 1. CONFIGURACIÓN DE LA PORTADA
# ==========================================
st.markdown('<div class="header-tabla">📘 1. Configuración de la Portada</div>', unsafe_allow_html=True)

# 1. Traer el Nombre del Proyecto
nombre_proyecto = st.session_state.get('nombre_proyecto_libre', 'ESTUDIOS PTAR') # Usando el de tu ejemplo si no hay nada

st.write("**Nombre del Proyecto:**")
st.markdown(f'<div class="readonly-box">{nombre_proyecto.upper()}</div><br>', unsafe_allow_html=True)

# 2. Carga de Imágenes (Separada de la visualización)
col_up1, col_up2 = st.columns(2)
with col_up1:
    st.info("🖼️ **Logo de la Entidad** (Irá en la esquina superior derecha)")
    logo_entidad = st.file_uploader("Sube el logo", type=["png", "jpg", "jpeg"], key="logo_portada")

with col_up2:
    st.info("📸 **Imagen Central** (Irá en el centro de la portada)")
    img_portada = st.file_uploader("Sube la imagen central", type=["png", "jpg", "jpeg"], key="img_portada")

# 2.1 VISTA PREVIA DE LAS IMÁGENES (Ahora en su propio espacio)
if logo_entidad is not None or img_portada is not None:
    st.markdown("<p style='color: #1E3A8A; font-weight: bold;'>🔍 Vista previa de imágenes cargadas:</p>", unsafe_allow_html=True)
    col_prev1, col_prev2 = st.columns(2)
    
    with col_prev1:
        if logo_entidad is not None:
            # Dibujamos directamente el archivo cargado
            st.image(logo_entidad, width=150, caption="Logo listo")
            
    with col_prev2:
        if img_portada is not None:
            # Dibujamos directamente el archivo cargado
            st.image(img_portada, width=300, caption="Imagen Central lista")

st.write("") # Espacio

# 3. Datos a digitar
col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
with col_d1:
    entidad_formulo = st.text_input("Entidad que formula el proyecto", placeholder="Ej: Alcaldía de Tunja")
with col_d2:
    lugar_presentacion = st.text_input("Lugar de presentación", placeholder="Ej: Tunja, Boyacá")
with col_d3:
    anio_presentacion = st.text_input("Año", value="2026")

st.divider()

# ==========================================
# 📑 2. MENÚ DE SELECCIÓN DE CONTENIDO
# ==========================================
st.markdown('<div class="header-tabla">📑 2. Selección de Contenido</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("**Hoja: Diagnóstico (Árbol de Problemas)**")
    chk_problema = st.checkbox("El Problema Central", value=True)
    chk_sintomas = st.checkbox("Síntomas (Efectos)", value=True)
    chk_causas = st.checkbox("Causas Inmediatas", value=True)

st.divider()

# ==========================================
# 🛑 TEXTOS DE PRUEBA INTERNOS
# ==========================================
texto_prob_prueba = "Texto de prueba: La alta tasa de accidentalidad en la vía principal debido a la falta de mantenimiento."
texto_sintomas_prueba = "Texto de prueba: 1. Incremento en tiempos de traslado. 2. Daños constantes a los vehículos."
texto_causas_prueba = "Texto de prueba: 1. Deterioro de la capa asfáltica. 2. Ausencia de mantenimiento."

# ==========================================
# ⚙️ MOTORES DE GENERACIÓN (Aún sin conectar las fotos al papel)
# ==========================================
def generar_word():
    doc = Document()
    titulo = doc.add_heading("Reporte de Formulación de Proyecto", 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    doc.add_page_break()
    doc.add_heading("1. Diagnóstico y Problema", level=1)
    
    if chk_problema:
        doc.add_heading("1.1 El Problema Central", level=2)
        doc.add_paragraph(texto_prob_prueba)
    if chk_sintomas:
        doc.add_heading("1.2 Síntomas (Efectos)", level=2)
        doc.add_paragraph(texto_sintomas_prueba)
    if chk_causas:
        doc.add_heading("1.3 Causas Inmediatas", level=2)
        doc.add_paragraph(texto_causas_prueba)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte de Formulacion de Proyecto", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "1. Diagnostico y Problema", new_x="LMARGIN", new_y="NEXT")
    return pdf.output()

# --- 3. BOTONES DE DESCARGA ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button("📝 Descargar Word (.docx)", data=generar_word(), file_name="Reporte_Prueba.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
with col_btn2:
    st.download_button("📄 Descargar PDF (.pdf)", data=bytes(generar_pdf()), file_name="Reporte_Prueba.pdf", mime="application/pdf", type="primary", use_container_width=True)
