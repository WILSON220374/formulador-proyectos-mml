import streamlit as st
import os
import io
import pandas as pd
from session_state import inicializar_session

# --- IMPORTACIÓN DE LIBRERÍAS (WORD Y PDF) ---
try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
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
    st.markdown('<div class="subtitulo-gris">Configuración de portada y exportación del documento final.</div>', unsafe_allow_html=True)
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
# 📑 2. SELECCIÓN Y DILIGENCIAMIENTO DE CONTENIDO
# ==========================================
st.markdown('<div class="header-tabla">📑 2. Configuración del Contenido</div>', unsafe_allow_html=True)
st.write("Diligencia las siguientes secciones que se incluirán al inicio de tu documento:")

instrucciones_resumen = "El resumen es el elemento fundamental para dar contexto sobre el proyecto, en este sentido escriba en máximo 15 líneas de manera clara, sencilla, directa y concisa el resumen del contenido del proyecto, que permitan dar una idea sobre el alcance, componentes y productos esperados."
texto_resumen = st.text_area("2. RESUMEN DEL PROYECTO", placeholder=instrucciones_resumen, height=150)

texto_normativo = st.text_area("3. MARCO NORMATIVO", placeholder="Escriba aquí el marco normativo del proyecto...", height=150)

st.divider()

# ==========================================
# 📥 EXTRACCIÓN DE DATOS DE LA MEMORIA
# ==========================================
# Hoja 15, 8, 9, 10
plan_desarrollo = st.session_state.get('plan_desarrollo', 'No se ha registrado información en la Hoja 15.')
justificacion = st.session_state.get('justificacion_proyecto', 'No se ha registrado información en la Hoja 8.')
loc_localizacion = st.session_state.get('loc_localizacion', 'No se ha registrado localización.')
loc_limites = st.session_state.get('loc_limites', 'No se han registrado límites.')
loc_accesibilidad = st.session_state.get('loc_accesibilidad', 'No se ha registrado accesibilidad.')
mapa_area = st.session_state.get('mapa_area_estudio', None) 
# Nuevas fotos del mapa (Hoja 9)
foto_area_1 = st.session_state.get('foto_area_1', None)
foto_area_2 = st.session_state.get('foto_area_2', None)

arbol_img = st.session_state.get('arbol_problemas_img', None) 
df_magnitud = st.session_state.get('df_magnitud_problema', None) 
desc_problema = st.session_state.get('desc_detallada_problema', 'No se ha registrado descripción.')
antecedentes = st.session_state.get('antecedentes_problema', 'No se han registrado antecedentes.')

# Datos Hoja 9 (Población)
df_poblacion_general = st.session_state.get('df_poblacion_general', None)
df_pob_sexo = st.session_state.get('df_pob_sexo', None)
df_pob_edad = st.session_state.get('df_pob_edad', None)
analisis_poblacion = st.session_state.get('analisis_poblacion', 'No se ha registrado análisis de población.')

# Datos Hoja 3 (Participantes)
df_matriz_interesados = st.session_state.get('df_matriz_interesados', None)
df_mapa_influencia = st.session_state.get('df_mapa_influencia', None)
df_analisis_participantes = st.session_state.get('df_analisis_participantes', None)

# Datos Hoja 7 (Objetivos)
arbol_objetivos_img = st.session_state.get('arbol_objetivos_img', None)
objetivo_general = st.session_state.get('objetivo_general', 'No se ha definido el objetivo general.')
objetivos_especificos = st.session_state.get('objetivos_especificos_lista', 'No se han definido objetivos específicos.')

# Datos Hoja de Alternativas
alternativas_consolidadas = st.session_state.get('alternativas_consolidadas', 'No se han registrado alternativas consolidadas.')
df_evaluacion_alt = st.session_state.get('df_evaluacion_alt', None)
alternativa_seleccionada = st.session_state.get('alternativa_seleccionada', 'No se ha seleccionado ninguna alternativa.')


# ==========================================
# ⚙️ MOTOR DE GENERACIÓN WORD
# ==========================================
def agregar_tabla_word(doc, df):
    """Función ayudante para imprimir DataFrames como tablas en Word de forma automática"""
    if isinstance(df, pd.DataFrame) and not df.empty:
        t = doc.add_table(rows=1, cols=len(df.columns))
        t.style = 'Table Grid'
        hdr_cells = t.rows[0].cells
        for i, column in enumerate(df.columns):
            hdr_cells[i].text = str(column)
            hdr_cells[i].paragraphs[0].runs[0].bold = True
        for index, row in df.iterrows():
            row_cells = t.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)
    else:
        doc.add_paragraph("No se registraron datos en esta tabla.", style='Italic')

def generar_word():
    doc = Document()
    
    # --- CONFIGURACIÓN DE ENCABEZADO Y PIE DE PÁGINA ---
    section = doc.sections[0]
    section.different_first_page_header_footer = True 
    
    def crear_encabezado(hdr_obj):
        htable = hdr_obj.add_table(rows=1, cols=2, width=Inches(6.5))
        htable.autofit = False
        htable.columns[0].width = Inches(5.0) 
        htable.columns[1].width = Inches(1.5) 
        h_izq = htable.cell(0, 0).paragraphs[0]
        h_izq.alignment = WD_ALIGN_PARAGRAPH.LEFT
        h_izq.add_run(nombre_proyecto.upper()).bold = True
        h_der = htable.cell(0, 1).paragraphs[0]
        h_der.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if logo_entidad is not None:
            logo_entidad.seek(0)
            h_der.add_run().add_picture(io.BytesIO(logo_entidad.getvalue()), width=Inches(0.6))
        p_line = hdr_obj.add_paragraph()
        pPr = p_line._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'auto')
        pBdr.append(bottom)
        pPr.append(pBdr)

    crear_encabezado(section.first_page_header)
    crear_encabezado(section.header)
    
    footer = section.footer
    p_line_f = footer.paragraphs[0]
    pPr_f = p_line_f._p.get_or_add_pPr()
    pBdr_f = OxmlElement('w:pBdr')
    bottom_f = OxmlElement('w:bottom')
    bottom_f.set(qn('w:val'), 'single')
    bottom_f.set(qn('w:sz'), '6') 
    bottom_f.set(qn('w:space'), '1')
    bottom_f.set(qn('w:color'), 'auto')
    pBdr_f.append(bottom_f)
    pPr_f.append(pBdr_f)
    
    ftable = footer.add_table(rows=1, cols=3, width=Inches(6.5))
    ftable.autofit = False
    ftable.columns[0].width = Inches(0.5)
    ftable.columns[1].width = Inches(5.5) 
    ftable.columns[2].width = Inches(0.5)
    
    f_centro = ftable.cell(0, 1).paragraphs[0]
    f_centro.alignment = WD_ALIGN_PARAGRAPH.CENTER
    texto_entidad = entidad_formulo if entidad_formulo else ""
    texto_div = division if division else ""
    if texto_entidad:
        r_centro1 = f_centro.add_run(texto_entidad.upper())
        r_centro1.font.size = Pt(9)
        r_centro1.italic = True
        r_centro1.font.color.rgb = RGBColor(128, 128, 128)
    if texto_entidad and texto_div:
        f_centro.add_run("\n")
    if texto_div:
        r_centro2 = f_centro.add_run(texto_div.upper())
        r_centro2.font.size = Pt(9)
        r_centro2.italic = True
        r_centro2.font.color.rgb = RGBColor(128, 128, 128)
    
    f_der = ftable.cell(0, 2).paragraphs[0]
    f_der.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_num = f_der.add_run()
    r_num.font.size = Pt(10)
    r_num.font.color.rgb = RGBColor(128, 128, 128)
    
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    
    r_num._r.append(fldChar1)
    r_num._r.append(instrText)
    r_num._r.append(fldChar2)
    r_num._r.append(fldChar3)

    # --- 1. PORTADA ---
    doc.add_paragraph("\n\n") 
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_titulo = p_titulo.add_run(nombre_proyecto.upper())
    r_titulo.bold = True
    r_titulo.font.size = Pt(20)
    
    doc.add_paragraph("\n")
    if img_portada is not None:
        img_portada.seek(0)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(io.BytesIO(img_portada.getvalue()), width=Inches(3.8))
        
    doc.add_paragraph("\n")
    if entidad_formulo:
        doc.add_paragraph(entidad_formulo.upper()).alignment = WD_ALIGN_PARAGRAPH.CENTER
    if division:
        doc.add_paragraph(division.upper()).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    doc.add_paragraph("\n")
    p_presentado = doc.add_paragraph()
    p_presentado.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_presentado.add_run("Presentado por:\n").italic = True
    p_presentado.add_run(nombres_formuladores).bold = True
    
    doc.add_paragraph("\n")
    p_pie = doc.add_paragraph()
    p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    texto_lugar = lugar_presentacion if lugar_presentacion else ""
    texto_anio = anio_presentacion if anio_presentacion else ""
    p_pie.add_run(f"{texto_lugar}\n{texto_anio}".strip()).bold = True
    
    doc.add_page_break()
    
    # --- 2. INICIO DEL CONTENIDO ---
    p_tit_cont = doc.add_paragraph()
    p_tit_cont.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t_cont = p_tit_cont.add_run(nombre_proyecto.upper())
    r_t_cont.bold = True
    r_t_cont.font.size = Pt(16)
    
    doc.add_paragraph("\n") 
    
    # 1 a 4
    doc.add_heading("1. Articulación con el plan de desarrollo", level=1)
    doc.add_paragraph(str(plan_desarrollo))
    doc.add_heading("2. Resumen del proyecto", level=1)
    doc.add_paragraph(str(texto_resumen))
    doc.add_heading("3. Marco normativo", level=1)
    doc.add_paragraph(str(texto_normativo))
    doc.add_heading("4. Justificación", level=1)
    doc.add_paragraph(str(justificacion))
    
    # 5. Localización
    doc.add_heading("5. Localización del proyecto", level=1)
    doc.add_heading("5.1 Localización", level=2)
    doc.add_paragraph(str(loc_localizacion))
    doc.add_heading("5.2 Definición de límites", level=2)
    doc.add_paragraph(str(loc_limites))
    doc.add_heading("5.3 Condiciones de accesibilidad", level=2)
    doc.add_paragraph(str(loc_accesibilidad))
    
    if mapa_area is not None:
        try:
            p_mapa = doc.add_paragraph()
            p_mapa.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_mapa.add_run().add_picture(io.BytesIO(mapa_area.getvalue()), width=Inches(5.0))
        except:
            pass 
            
    # 6. Problema
    doc.add_heading("6. Identificación y descripción del problema", level=1)
    if arbol_img is not None:
        try:
            p_arbol = doc.add_paragraph()
            p_arbol.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_arbol.add_run().add_picture(io.BytesIO(arbol_img.getvalue()), width=Inches(6.0))
        except:
            pass
            
    doc.add_heading("6.1 Magnitud del problema", level=2)
    agregar_tabla_word(doc, df_magnitud)
    
    doc.add_paragraph("\n")
    doc.add_heading("Descripción detallada (Problema - Causa - Efecto)", level=3)
    doc.add_paragraph(str(desc_problema))
    doc.add_heading("Antecedentes: ¿Qué se ha hecho previamente con el problema?", level=3)
    doc.add_paragraph(str(antecedentes))
    
    # 6.2 Fotos adicionales (NUEVO)
    if foto_area_1 is not None or foto_area_2 is not None:
        doc.add_heading("Registro Fotográfico del Problema", level=3)
        if foto_area_1 is not None:
            try:
                p_f1 = doc.add_paragraph()
                p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_f1.add_run().add_picture(io.BytesIO(foto_area_1.getvalue()), width=Inches(4.5))
            except: pass
        if foto_area_2 is not None:
            try:
                p_f2 = doc.add_paragraph()
                p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_f2.add_run().add_picture(io.BytesIO(foto_area_2.getvalue()), width=Inches(4.5))
            except: pass

    # 7. POBLACIÓN (NUEVO)
    doc.add_heading("7. Población", level=1)
    agregar_tabla_word(doc, df_poblacion_general)
    
    doc.add_heading("1. Población objetivo por sexo", level=2)
    agregar_tabla_word(doc, df_pob_sexo)
    
    doc.add_heading("2. Población objetivo por rango de edad", level=2)
    agregar_tabla_word(doc, df_pob_edad)
    
    doc.add_heading("Análisis de la población objetivo", level=2)
    doc.add_paragraph(str(analisis_poblacion))

    # 8. PARTICIPANTES (NUEVO)
    doc.add_heading("8. Análisis de Participantes", level=1)
    doc.add_heading("Matriz de Interesados", level=2)
    agregar_tabla_word(doc, df_matriz_interesados)
    doc.add_heading("Mapa de Influencia Estratégico", level=2)
    agregar_tabla_word(doc, df_mapa_influencia)
    doc.add_heading("Análisis de Participantes", level=2)
    agregar_tabla_word(doc, df_analisis_participantes)

    # 9. OBJETIVOS (NUEVO)
    doc.add_heading("9. Objetivos y Resultados Esperados", level=1)
    if arbol_objetivos_img is not None:
        try:
            p_arbol_obj = doc.add_paragraph()
            p_arbol_obj.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_arbol_obj.add_run().add_picture(io.BytesIO(arbol_objetivos_img.getvalue()), width=Inches(6.0))
        except:
            pass
            
    doc.add_heading("9.1 Objetivo General", level=2)
    doc.add_paragraph(str(objetivo_general))
    
    doc.add_heading("9.2 Objetivos Específicos", level=2)
    doc.add_paragraph(str(objetivos_especificos))

    # 10. ALTERNATIVAS (NUEVO)
    doc.add_heading("10. Alternativas", level=1)
    doc.add_heading("Alternativas Consolidadas", level=2)
    doc.add_paragraph(str(alternativas_consolidadas))
    
    doc.add_heading("Evaluación de Alternativas", level=2)
    agregar_tabla_word(doc, df_evaluacion_alt)
    
    doc.add_heading("Alternativa Seleccionada", level=2)
    # Crear el recuadro verde con la alternativa ganadora
    t_verde = doc.add_table(rows=1, cols=1)
    celda = t_verde.cell(0, 0)
    celda.text = str(alternativa_seleccionada)
    
    # Pintar la celda de verde claro
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:val'), 'clear')
    shading_elm.set(qn('w:color'), 'auto')
    shading_elm.set(qn('w:fill'), 'E2F0D9') # Color verde pastel (Hex: E2F0D9)
    celda._tc.get_or_add_tcPr().append(shading_elm)
    
    # Poner la letra en negrita para resaltarlo más
    for paragraph in celda.paragraphs:
        for run in paragraph.runs:
            run.bold = True

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

# --- BOTONES DE DESCARGA ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button("📝 Descargar Word (.docx)", data=generar_word(), file_name="Proyecto_Formulado.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
with col_btn2:
    st.download_button("📄 Descargar PDF (.pdf)", data=bytes(generar_pdf()), file_name="Reporte_Prueba.pdf", mime="application/pdf", type="primary", use_container_width=True)
