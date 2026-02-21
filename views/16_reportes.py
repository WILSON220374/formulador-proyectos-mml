import streamlit as st
import os
import io
import pandas as pd
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
    st.markdown('<div class="subtitulo-gris">Prueba funcional: Exportación a Word y PDF.</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- 1. EXTRAER AUTORES AUTOMÁTICAMENTE ---
st.markdown('<div class="header-tabla">⚙️ 1. Configuración de Portada</div>', unsafe_allow_html=True)

nombres_formuladores = "No se encontraron formuladores registrados en la Hoja 1"
if "df_equipo" in st.session_state and isinstance(st.session_state["df_equipo"], pd.DataFrame):
    df = st.session_state["df_equipo"]
    if "Nombre" in df.columns:
        nombres_lista = df["Nombre"].dropna().astype(str).tolist()
        nombres_validos = [n for n in nombres_lista if n.strip() != ""]
        if nombres_validos:
            nombres_formuladores = ", ".join(nombres_validos)

st.write("**Autores / Formuladores:**")
st.markdown(f'<div class="readonly-box">{nombres_formuladores}</div><br>', unsafe_allow_html=True)

st.divider()

# --- 2. MENÚ DE SELECCIÓN DE DIAGNÓSTICO ---
st.markdown('<div class="header-tabla">📑 2. Selección de Contenido</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("**Hoja: Diagnóstico (Árbol de Problemas)**")
    chk_problema = st.checkbox("El Problema Central", value=True)
    chk_sintomas = st.checkbox("Síntomas (Efectos)", value=True)
    chk_causas = st.checkbox("Causas Inmediatas", value=True)

st.divider()

# --- EXTRACCIÓN DE TEXTOS DE LA MEMORIA ---
# (Ajusta los nombres de las variables si son diferentes en tu Hoja de Diagnóstico)
texto_prob = st.session_state.get('problema_central', 'No se ha redactado el problema central.')
texto_sintomas = st.session_state.get('efectos_directos', 'No se han registrado síntomas/efectos.')
texto_causas = st.session_state.get('causas_directas', 'No se han registrado causas inmediatas.')
fecha_actual = datetime.now().strftime("%d/%m/%Y")

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
    p.add_run(nombres_formuladores)
    
    doc.add_page_break()
    doc.add_heading("1. Diagnóstico y Problema", level=1)
    
    if chk_problema:
        doc.add_heading("1.1 El Problema Central", level=2)
        doc.add_paragraph(str(texto_prob))
    if chk_sintomas:
        doc.add_heading("1.2 Síntomas (Efectos)", level=2)
        doc.add_paragraph(str(texto_sintomas))
    if chk_causas:
        doc.add_heading("1.3 Causas Inmediatas", level=2)
        doc.add_paragraph(str(texto_causas))

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
    pdf.cell(0, 10, "Reporte de Formulación de Proyecto", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Fecha: {fecha_actual}", new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 10, f"Formuladores: {nombres_formuladores}")
    
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "1. Diagnostico y Problema", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    
    if chk_problema:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "1.1 El Problema Central", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8, str(texto_prob))
        pdf.ln(5)
        
    if chk_sintomas:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "1.2 Sintomas (Efectos)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8, str(texto_sintomas))
        pdf.ln(5)
        
    if chk_causas:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "1.3 Causas Inmediatas", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8, str(texto_causas))
        
    return pdf.output() # Genera el archivo en bytes listo para descargar

# --- 3. BOTONES DE DESCARGA ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)
st.info("💡 Haz clic en el formato deseado para descargar tu reporte.")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    buffer_w = generar_word()
    st.download_button(
        label="📝 Descargar Word (.docx)",
        data=buffer_w,
        file_name="Diagnostico_Proyecto.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )

with col_btn2:
    buffer_p = generar_pdf()
    st.download_button(
        label="📄 Descargar PDF (.pdf)",
        data=bytes(buffer_p),
        file_name="Diagnostico_Proyecto.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )
