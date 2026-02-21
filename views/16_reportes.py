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
    .readonly-box { border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background-color: #f3f4f6; color: #374151; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📄 16. Generador de Reportes</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Prueba funcional con datos de demostración aislados.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# ==========================================
# 🛑 TEXTOS DE PRUEBA (DESCONECTADOS DEL RESTO)
# ==========================================
nombres_formuladores_prueba = "Juan Pérez, María Gómez (Datos de Prueba)"
texto_prob_prueba = "Este es un texto de prueba para el PROBLEMA CENTRAL. La alta tasa de accidentalidad en la vía principal del municipio debido a la falta de mantenimiento."
texto_sintomas_prueba = "Este es un texto de prueba para los SÍNTOMAS. 1. Incremento en los tiempos de traslado. 2. Daños constantes a los vehículos. 3. Aumento en los costos de transporte."
texto_causas_prueba = "Este es un texto de prueba para las CAUSAS. 1. Falta de señalización adecuada. 2. Deterioro de la capa asfáltica por lluvias. 3. Ausencia de un plan de mantenimiento preventivo."
fecha_actual = datetime.now().strftime("%d/%m/%Y")

# --- 1. CONFIGURACIÓN DE PORTADA ---
st.markdown('<div class="header-tabla">⚙️ 1. Configuración de Portada</div>', unsafe_allow_html=True)
st.write("**Autores / Formuladores (Simulados):**")
st.markdown(f'<div class="readonly-box">{nombres_formuladores_prueba}</div><br>', unsafe_allow_html=True)

st.divider()

# --- 2. MENÚ DE SELECCIÓN ---
st.markdown('<div class="header-tabla">📑 2. Selección de Contenido</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("**Hoja: Diagnóstico (Árbol de Problemas)**")
    chk_problema = st.checkbox("El Problema Central", value=True)
    chk_sintomas = st.checkbox("Síntomas (Efectos)", value=True)
    chk_causas = st.checkbox("Causas Inmediatas", value=True)

st.divider()

# ==========================================
# ⚙️ MOTOR DE GENERACIÓN WORD
# ==========================================
def generar_word():
    doc = Document()
    titulo = doc.add_heading("Reporte de Formulación de Proyecto", 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Fecha: {fecha_actual}")
    
    p = doc.add_paragraph()
    p.add_run("Formuladores: ").bold = True
    p.add_run(nombres_formuladores_prueba)
    
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

# ==========================================
# ⚙️ MOTOR DE GENERACIÓN PDF
# ==========================================
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Portada
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte de Formulacion de Proyecto", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Fecha: {fecha_actual}", new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 10, f"Formuladores: {nombres_formuladores_prueba}")
    
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "1. Diagnostico y Problema", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    if chk_problema:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "1.1 El Problema Central", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8, texto_prob_prueba)
        pdf.ln(5)
        
    if chk_sintomas:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "1.2 Sintomas (Efectos)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8, texto_sintomas_prueba)
        pdf.ln(5)
        
    if chk_causas:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "1.3 Causas Inmediatas", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8, texto_causas_prueba)
        
    return pdf.output()

# --- 3. BOTONES DE DESCARGA (AHORA SÍ FUNCIONAN) ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)
st.info("💡 Haz clic para descargar los documentos generados con los textos de prueba.")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    buffer_w = generar_word()
    st.download_button(
        label="📝 Descargar Word (.docx)",
        data=buffer_w,
        file_name="Reporte_Prueba.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )

with col_btn2:
    buffer_p = generar_pdf()
    st.download_button(
        label="📄 Descargar PDF (.pdf)",
        data=bytes(buffer_p),
        file_name="Reporte_Prueba.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )
