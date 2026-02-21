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

# 1. Traer el Nombre del Proyecto (de la hoja 15)
nombre_proyecto = st.session_state.get('nombre_proyecto_libre', 'NOMBRE DEL PROYECTO NO DEFINIDO') 

st.write("**Nombre del Proyecto:**")
st.markdown(f'<div class="readonly-box">{nombre_proyecto.upper()}</div><br>', unsafe_allow_html=True)

# 2. Carga de Imágenes
col_up1, col_up2 = st.columns(2)
with col_up1:
    st.info("🖼️ **Logo de la Entidad** (Irá en la esquina superior derecha)")
    logo_entidad = st.file_uploader("Sube el logo", type=["png", "jpg", "jpeg"], key="logo_portada")

with col_up2:
    st.info("📸 **Imagen Central** (Irá en el centro de la portada)")
    img_portada = st.file_uploader("Sube la imagen central", type=["png", "jpg", "jpeg"], key="img_portada")

if logo_entidad is not None or img_portada is not None:
    st.markdown("<p style='color: #1E3A8A; font-weight: bold;'>🔍 Vista previa de imágenes cargadas:</p>", unsafe_allow_html=True)
    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        if logo_entidad is not None:
            st.image(logo_entidad, width=150, caption="Logo listo")
    with col_prev2:
        if img_portada is not None:
            st.image(img_portada, width=300, caption="Imagen Central lista")

st.write("") 

# 3. Datos de los Formuladores
nombres_formuladores = "No se encontraron formuladores registrados en la Hoja 1"
if "df_equipo" in st.session_state and isinstance(st.session_state["df_equipo"], pd.DataFrame):
    df = st.session_state["df_equipo"]
    if "Nombre" in df.columns:
        nombres_lista = df["Nombre"].dropna().astype(str).tolist()
        nombres_validos = [n for n in nombres_lista if n.strip() != ""]
        if nombres_validos:
            nombres_formuladores = "\n".join(nombres_validos) 
            nombres_display = ", ".join(nombres_validos) 

st.write("**Presentado por (Equipo Formulador):**")
st.markdown(f'<div class="readonly-autores">{nombres_display if "nombres_display" in locals() else nombres_formuladores}</div><br>', unsafe_allow_html=True)

# 4. Datos a digitar
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
# 📑 2. MENÚ DE SELECCIÓN DE CONTENIDO (VISUAL SOLAMENTE)
# ==========================================
st.markdown('<div class="header-tabla">📑 2. Selección de Contenido</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("**Hoja: Diagnóstico (Árbol de Problemas)**")
    chk_problema = st.checkbox("El Problema Central", value=True)
    chk_sintomas = st.checkbox("Síntomas (Efectos)", value=True)
    chk_causas = st.checkbox("Causas Inmediatas", value=True)

st.divider()

# ==========================================
# ⚙️ MOTOR DE GENERACIÓN WORD (SOLO PORTADA - AJUSTADA)
# ==========================================
def generar_word():
    doc = Document()
    
    # --- CONSTRUCCIÓN DE LA PORTADA EN ORDEN JERÁRQUICO ---
    
    # 1. LOGO (Alineado a la derecha)
    if logo_entidad is not None:
        logo_entidad.seek(0)
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_logo = p_logo.add_run()
        r_logo.add_picture(logo_entidad, width=Inches(1.2)) # Logo un poco más pequeño
    else:
        # Menos espacio si no hay logo
        p_logo = doc.add_paragraph()
        p_logo.add_run().font.size = Pt(1) 
    
    doc.add_paragraph("\n") # Solo un Enter
    
    # 2. NOMBRE DEL PROYECTO (Centrado y Grande)
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_titulo = p_titulo.add_run(nombre_proyecto.upper())
    r_titulo.bold = True
    r_titulo.font.size = Pt(20) # Reduje un par de puntos la letra
    
    doc.add_paragraph("\n") # Solo un Enter
    
    # 3. IMAGEN CENTRAL (Centrada)
    if img_portada is not None:
        img_portada.seek(0)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_img = p_img.add_run()
        r_img.add_picture(img_portada, width=Inches(3.8)) # Imagen ajustada para no consumir tanto alto
        
    doc.add_paragraph("\n") # Solo un Enter
    
    # 4. ENTIDAD QUE FORMULA (Centrado)
    if entidad_formulo:
        p_entidad = doc.add_paragraph()
        p_entidad.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_entidad = p_entidad.add_run(entidad_formulo.upper())
        r_entidad.bold = True
        r_entidad.font.size = Pt(14)
        
    # 5. DIVISIÓN (Centrado) - Sin espacios extra entre Entidad y División
    if division:
        p_div = doc.add_paragraph()
        p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_div = p_div.add_run(division.upper())
        r_div.bold = True
        r_div.font.size = Pt(12)
        
    doc.add_paragraph("\n") # Solo un Enter
    
    # 6. PRESENTADO POR (Centrado)
    p_presentado = doc.add_paragraph()
    p_presentado.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    r_presentado_lbl = p_presentado.add_run("Presentado por:\n")
    r_presentado_lbl.font.size = Pt(11)
    r_presentado_lbl.italic = True
    
    r_autores = p_presentado.add_run(nombres_formuladores)
    r_autores.bold = True
    r_autores.font.size = Pt(12)
    
    doc.add_paragraph("\n") # Solo un Enter
    
    # 7. LUGAR Y AÑO (Centrado al final de la página)
    p_pie = doc.add_paragraph()
    p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    texto_lugar = lugar_presentacion if lugar_presentacion else ""
    texto_anio = anio_presentacion if anio_presentacion else ""
    
    r_pie = p_pie.add_run(f"{texto_lugar}\n{texto_anio}".strip())
    r_pie.bold = True
    r_pie.font.size = Pt(12)
    
    # --- FIN DE LA PORTADA ---
    doc.add_page_break()
    
    p_prueba = doc.add_paragraph()
    p_prueba.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_prueba = p_prueba.add_run("(El resto del contenido está desconectado para esta prueba. Aquí iniciará el proyecto.)")
    r_prueba.italic = True

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
    st.download_button("📝 Descargar Word (.docx)", data=generar_word(), file_name="Reporte_Solo_Portada.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
with col_btn2:
    st.download_button("📄 Descargar PDF (.pdf)", data=bytes(generar_pdf()), file_name="Reporte_Prueba.pdf", mime="application/pdf", type="primary", use_container_width=True)
