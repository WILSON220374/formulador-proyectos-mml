import streamlit as st
import os
import io
import pandas as pd
from session_state import inicializar_session

# --- IMPORTACIÓN DE LIBRERÍAS (WORD Y PDF) ---
try:
    from docx import Document
    from docx.shared import Pt, Inches
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
    .readonly-autores { border: 1px solid #d1d5db; border-radius: 8px; padding: 10px; background-color: #f3f4f6; color: #374151; font-weight: 600; text-align: center; font-size: 1rem;}
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

nombre_proyecto = st.session_state.get('nombre_proyecto_libre', 'NOMBRE DEL PROYECTO NO DEFINIDO') 

st.write("**Nombre del Proyecto:**")
st.markdown(f'<div class="readonly-box">{nombre_proyecto.upper()}</div><br>', unsafe_allow_html=True)

col_up1, col_up2 = st.columns(2)
with col_up1:
    st.info("🖼️ **Logo de la Entidad** (Irá en el encabezado de todas las páginas)")
    logo_entidad = st.file_uploader("Sube el logo", type=["png", "jpg", "jpeg"], key="logo_portada")

with col_up2:
    st.info("📸 **Imagen Central** (Irá en el centro de la portada)")
    img_portada = st.file_uploader("Sube la imagen central", type=["png", "jpg", "jpeg"], key="img_portada")

if logo_entidad is not None or img_portada is not None:
    st.markdown("<p style='color: #1E3A8A; font-weight: bold;'>🔍 Vista previa de imágenes cargadas:</p>", unsafe_allow_html=True)
    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        if logo_entidad is not None:
            st.image(logo_entidad, width=150, caption="Logo listo para el encabezado")
    with col_prev2:
        if img_portada is not None:
            st.image(img_portada, width=300, caption="Imagen Central lista")

st.write("") 

nombres_formuladores = "No se encontraron formuladores registrados en la Hoja 1"
if "df_equipo" in st.session_state and isinstance(st.session_state["df_equipo"], pd.DataFrame):
    df = st.session_state["df_equipo"]
    if "Nombre" in df.columns:
        nombres_lista = df["Nombre"].dropna().astype(str).tolist()
        nombres_validos = [n for n in nombres_lista if n.strip() != ""]
        if nombres_validos:
            # En el Word quedarán uno debajo del otro
            nombres_formuladores = "\n".join(nombres_validos) 
            nombres_display = ", ".join(nombres_validos) 

st.write("**Presentado por (Equipo Formulador):**")
st.markdown(f'<div class="readonly-autores">{nombres_display if "nombres_display" in locals() else nombres_formuladores}</div><br>', unsafe_allow_html=True)

col_d1, col_d2 = st.columns(2)
with col_d1:
    entidad_formulo = st.text_input("Entidad que formula el proyecto", placeholder="Ej: Alcaldía de Tunja")
with col_d2:
    division = st.text_input("División / Dependencia", placeholder="Ej: Secretaría de Infraestructura")

col_d3, col_d4 = st.columns(2)
with col_d3:
    lugar_presentacion = st.text_input("Lugar de presentación", value="Tunja, Boyacá")
with col_d4:
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
# ⚙️ MOTOR DE GENERACIÓN WORD
# ==========================================
def generar_word():
    doc = Document()
    
    # ---------------------------------------------------------
    # CONFIGURACIÓN DEL ENCABEZADO (Aplica para todas las páginas)
    # ---------------------------------------------------------
    section = doc.sections[0]
    # Eliminamos la regla de "primera página diferente" para que el encabezado salga en la portada
    
    header = section.header
    htable = header.add_table(rows=1, cols=2, width=Inches(6))
    htable.autofit = False
    htable.columns[0].width = Inches(4.5) 
    htable.columns[1].width = Inches(1.5) 
    
    # Izquierda: Nombre
    h_izq = htable.cell(0, 0).paragraphs[0]
    h_izq.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_hizq = h_izq.add_run(nombre_proyecto.upper())
    r_hizq.font.size = Pt(9)
    r_hizq.bold = True
    
    # Derecha: Logo
    h_der = htable.cell(0, 1).paragraphs[0]
    h_der.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if logo_entidad is not None:
        logo_entidad.seek(0)
        r_hder = h_der.add_run()
        r_hder.add_picture(logo_entidad, width=Inches(0.6))
    
    # ---------------------------------------------------------
    # 1. CONSTRUCCIÓN DE LA PORTADA
    # ---------------------------------------------------------
    doc.add_paragraph("\n\n") # Espacio inicial para bajar el título un poco
    
    # Título Principal
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_titulo = p_titulo.add_run(nombre_proyecto.upper())
    r_titulo.bold = True
    r_titulo.font.size = Pt(20)
    
    doc.add_paragraph("\n")
    
    # Imagen Central
    if img_portada is not None:
        img_portada.seek(0)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(img_portada, width=Inches(3.8))
        
    doc.add_paragraph("\n")
    
    # Entidad
    if entidad_formulo:
        p_entidad = doc.add_paragraph()
        p_entidad.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_entidad.add_run(entidad_formulo.upper()).bold = True
        
    # División
    if division:
        p_div = doc.add_paragraph()
        p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_div.add_run(division.upper()).bold = True
        
    doc.add_paragraph("\n")
    
    # Equipo Formulador
    p_presentado = doc.add_paragraph()
    p_presentado.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_presentado.add_run("Presentado por:\n").italic = True
    p_presentado.add_run(nombres_formuladores).bold = True
    
    doc.add_paragraph("\n")
    
    # Pie de página de la portada
    p_pie = doc.add_paragraph()
    p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    texto_lugar = lugar_presentacion if lugar_presentacion else ""
    texto_anio = anio_presentacion if anio_presentacion else ""
    p_pie.add_run(f"{texto_lugar}\n{texto_anio}".strip()).bold = True
    
    # --- SALTO A LA PÁGINA 2 ---
    doc.add_page_break()
    
    # ---------------------------------------------------------
    # 2. INICIO DEL CONTENIDO (Página 2)
    # ---------------------------------------------------------
    
    p_tit_cont = doc.add_paragraph()
    p_tit_cont.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t_cont = p_tit_cont.add_run(nombre_proyecto.upper())
    r_t_cont.bold = True
    r_t_cont.font.size = Pt(16)
    
    doc.add_paragraph("\n") 
    
    p_prueba = doc.add_paragraph()
    p_prueba.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_prueba.add_run("(El resto del contenido está desconectado para esta prueba. Aquí iniciará el proyecto.)").italic = True

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte en PDF (Aún en construcción)", align="C", new_x="LMARGIN", new_y="NEXT")
    return pdf.output()

# --- 3. BOTONES DE DESCARGA ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button("📝 Descargar Word (.docx)", data=generar_word(), file_name="Reporte_Final.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
with col_btn2:
    st.download_button("📄 Descargar PDF (.pdf)", data=bytes(generar_pdf()), file_name="Reporte_Prueba.pdf", mime="application/pdf", type="primary", use_container_width=True)
