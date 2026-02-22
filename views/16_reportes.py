import streamlit as st
import os
import io
import textwrap
import pandas as pd
import requests
from session_state import inicializar_session, conectar_db

# --- IMPORTACIÓN DE LIBRERÍAS ---
try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
except ImportError:
    st.error("📌 Falta instalar python-docx. Agrega 'python-docx' en requirements.txt")
    st.stop()

try:
    from fpdf import FPDF
except ImportError:
    st.error("📌 Falta instalar fpdf2. Agrega 'fpdf2' en requirements.txt")
    st.stop()

# 1. Asegurar persistencia
inicializar_session()

# --- ESTADO LOCAL HOJA 16 (Reportes) ---
# Nota: estos datos se persistirán en nube cuando session_state.py los incluya en guardar_datos_nube()/cargar_datos_nube().
if "datos_reportes" not in st.session_state or not isinstance(st.session_state.get("datos_reportes"), dict):
    st.session_state["datos_reportes"] = {}
datos_reportes = st.session_state["datos_reportes"]

def _get_bucket_name() -> str:
    return st.secrets.get("SUPABASE_BUCKET", "uploads")

def _upload_to_supabase_storage_reportes(uploaded_file, tipo_key: str):
    """Replica el patrón de Hoja 9: sube a Supabase Storage y retorna (public_url, storage_path)."""
    user_id = st.session_state.get("usuario_id")
    if not user_id or uploaded_file is None:
        return None, None

    # firma simple para evitar re-subidas en cada rerun
    signature = f"{getattr(uploaded_file, 'name', '')}:{getattr(uploaded_file, 'size', '')}"
    sig_key = f"sig_{tipo_key}"
    if datos_reportes.get(sig_key) == signature and datos_reportes.get(f"ruta_{tipo_key}") and datos_reportes.get(f"path_{tipo_key}"):
        return datos_reportes.get(f"ruta_{tipo_key}"), datos_reportes.get(f"path_{tipo_key}")

    try:
        db = conectar_db()
        bucket = _get_bucket_name()

        original_name = getattr(uploaded_file, "name", "") or "archivo"
        ext = original_name.split(".")[-1].lower() if "." in original_name else "png"
        content_type = getattr(uploaded_file, "type", None) or "image/png"

        import uuid
        storage_path = f"{user_id}/reportes/{tipo_key}/{uuid.uuid4().hex}.{ext}"

        uploaded_file.seek(0)
        file_bytes = uploaded_file.getvalue()

        db.storage.from_(bucket).upload(
            storage_path,
            file_bytes,
            file_options={"content-type": content_type, "upsert": "true"},
        )

        public_url = db.storage.from_(bucket).get_public_url(storage_path)
        # Supabase python puede devolver dict o str dependiendo de versión
        if isinstance(public_url, dict):
            public_url = public_url.get("publicUrl") or public_url.get("public_url")

        # almacenar en estado local
        datos_reportes[f"ruta_{tipo_key}"] = public_url
        datos_reportes[f"path_{tipo_key}"] = storage_path
        datos_reportes[sig_key] = signature

        return public_url, storage_path
    except Exception:
        return None, None

def _download_image_bytes(url: str) -> bytes | None:
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        pass
    return None


# --- DISEÑO PROFESIONAL (C) ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem;}
    h1 {text-align: center; font-size: 2.2em;}
    h2 {font-size: 1.6em; color: #005B96;}
    .info-box {background: #f5f5f5; padding: 10px; border-radius: 8px; border-left: 5px solid #005B96;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📌 1. PORTADA Y DATOS GENERALES
# ==========================================
st.markdown("<h1>📄 Generación de Reporte Final</h1>", unsafe_allow_html=True)

nombre_proyecto = st.session_state.get("nombre_proyecto_libre", "Proyecto sin nombre")
st.markdown(f"<div class='info-box'><b>Nombre del Proyecto:</b> {nombre_proyecto}</div><br>", unsafe_allow_html=True)

# --- LIMPIEZA VISUAL DE LAS IMÁGENES ---
col_up1, col_up2 = st.columns(2)
with col_up1:
    logo_entidad = st.file_uploader("🖼️ Sube el Logo de la Entidad", type=["png", "jpg", "jpeg"], key="logo_portada")
with col_up2:
    img_portada = st.file_uploader("📸 Sube la Imagen Central", type=["png", "jpg", "jpeg"], key="img_portada")

if logo_entidad is not None or img_portada is not None:
    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        if logo_entidad is not None:
            st.image(logo_entidad, width=150)
    with col_prev2:
        if img_portada is not None:
            st.image(img_portada, width=300)

# --- Persistencia de imágenes de Hoja 16 (patrón Hoja 9: Storage + ruta_/path_) ---
# Nota: aquí solo se actualiza st.session_state["datos_reportes"]; la persistencia en nube se habilita cuando session_state.py lo guarde.
if logo_entidad is not None:
    _upload_to_supabase_storage_reportes(logo_entidad, "logo_portada")
if img_portada is not None:
    _upload_to_supabase_storage_reportes(img_portada, "img_portada")

st.write("") 

nombres_formuladores = "No se encontraron formuladores registrados en la Hoja 0 (Equipo)"
nombres_display = nombres_formuladores

integrantes = st.session_state.get("integrantes", [])
if isinstance(integrantes, list):
    nombres_validos = []
   
    for i in integrantes:
        nombre = i.get("nombre", "").strip()
        if nombre:
            primer_nombre = nombre.split()[0]
            nombres_validos.append(primer_nombre)
   
    if nombres_validos:
        nombres_formuladores = ", ".join(nombres_validos)
        nombres_display = nombres_formuladores

st.markdown(f"<div class='info-box'><b>Presentado por:</b><br>{nombres_display if 'nombres_display' in locals() else nombres_formuladores}</div><br>", unsafe_allow_html=True)

# --- Inicialización de campos de Hoja 16 desde datos_reportes (sin reasignar claves de widgets después de render) ---
if "rep_entidad_formulo" not in st.session_state:
    st.session_state["rep_entidad_formulo"] = datos_reportes.get("entidad_formulo", "")
if "rep_division" not in st.session_state:
    st.session_state["rep_division"] = datos_reportes.get("division", "")
if "rep_lugar_presentacion" not in st.session_state:
    st.session_state["rep_lugar_presentacion"] = datos_reportes.get("lugar_presentacion", "Tunja, Boyacá")
if "rep_anio_presentacion" not in st.session_state:
    st.session_state["rep_anio_presentacion"] = datos_reportes.get("anio_presentacion", "2026")
if "texto_resumen" not in st.session_state:
    st.session_state["texto_resumen"] = datos_reportes.get("texto_resumen", "")
if "texto_normativo" not in st.session_state:
    st.session_state["texto_normativo"] = datos_reportes.get("texto_normativo", "")

col_d1, col_d2 = st.columns(2)
with col_d1:
    entidad_formulo = st.text_input("Entidad que formula el proyecto", placeholder="Ej: Alcaldía de Tunja", key="rep_entidad_formulo")
with col_d2:
    division = st.text_input("División / Dependencia", placeholder="Ej: Secretaría de Infraestructura", key="rep_division")

col_d3, col_d4 = st.columns(2)
with col_d3:
    lugar_presentacion = st.text_input("Lugar de presentación", key="rep_lugar_presentacion")
with col_d4:
    anio_presentacion = st.text_input("Año", key="rep_anio_presentacion")

st.divider()

# ==========================================
# 📑 2. SELECCIÓN Y DILIGENCIAMIENTO DE CONTENIDO
# ==========================================

st.markdown("<h2>📌 Secciones del Documento</h2>", unsafe_allow_html=True)

# --- RESUMEN DEL PROYECTO ---
instrucciones_resumen = "En esta sección deberá escribir un resumen narrativo del contenido del proyecto, que permitan dar una idea sobre el alcance, componentes y productos esperados."

curr_resumen = st.session_state.get("texto_resumen", "")
h_res = int(max(150, (curr_resumen.count('\n') + (len(curr_resumen) / 100) + 1) * 25 + 40))
texto_resumen = st.text_area("2. RESUMEN DEL PROYECTO", placeholder=instrucciones_resumen, height=h_res, key="texto_resumen")

curr_norm = st.session_state.get("texto_normativo", "")
h_norm = int(max(150, (curr_norm.count('\n') + (len(curr_norm) / 100) + 1) * 25 + 40))
texto_normativo = st.text_area("3. MARCO NORMATIVO", placeholder="Escriba aquí el marco normativo del proyecto...", height=h_norm, key="texto_normativo")

# --- Persistencia local de los campos diligenciados en Hoja 16 ---
datos_reportes["entidad_formulo"] = st.session_state.get("rep_entidad_formulo", "")
datos_reportes["division"] = st.session_state.get("rep_division", "")
datos_reportes["lugar_presentacion"] = st.session_state.get("rep_lugar_presentacion", "")
datos_reportes["anio_presentacion"] = st.session_state.get("rep_anio_presentacion", "")
datos_reportes["texto_resumen"] = st.session_state.get("texto_resumen", "")
datos_reportes["texto_normativo"] = st.session_state.get("texto_normativo", "")

st.divider()

# ==========================================
# 📥 EXTRACCIÓN DE DATOS DE LA MEMORIA
# ==========================================
# 1 a 4. General
_plan_nombre = str(st.session_state.get('plan_nombre', '')).strip()
_plan_eje = str(st.session_state.get('plan_eje', '')).strip()
_plan_programa = str(st.session_state.get('plan_programa', '')).strip()

if (not _plan_nombre) and isinstance(st.session_state.get('plan_desarrollo'), dict):
    pdict = st.session_state.get('plan_desarrollo', {})
    _plan_nombre = str(pdict.get('nombre', '')).strip()
    _plan_eje = str(pdict.get('eje', '')).strip()
    _plan_programa = str(pdict.get('programa', '')).strip()

plan_nombre = _plan_nombre or "No diligenciado"
plan_eje = _plan_eje or "No diligenciado"
plan_programa = _plan_programa or "No diligenciado"

# 4. Justificación (Hoja 7)
justificacion = st.session_state.get("justificacion_arbol_objetivos_final", "")
if not justificacion:
    arbol_final = st.session_state.get("arbol_objetivos_final", {})
    if isinstance(arbol_final, dict):
        ref = arbol_final.get("referencia_manual", {})
        if isinstance(ref, dict):
            justificacion = ref.get("justificacion", "") or ""

justificacion = justificacion or "No se diligenció justificación en Hoja 7."

# 5. Localización (Hoja 9)
dz = st.session_state.get("descripcion_zona", {})
if not isinstance(dz, dict):
    dz = {}
texto_zona = dz.get("descripcion", dz.get("texto", "")) or ""
ruta_mapa = dz.get("ruta_mapa") or None
ruta_foto1 = dz.get("ruta_foto1") or None
ruta_foto2 = dz.get("ruta_foto2") or None

# ==========================================
# 🔥 6. PROBLEMA (Hoja 8 + Hoja 10) - REPARADO
# ==========================================
def _a_texto_dict(obj):
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in ("texto", "value", "descripcion", "contenido"):
            if k in obj and obj[k]:
                return str(obj[k])
    return str(obj)

def _a_lista_dicts(obj):
    if obj is None:
        return []
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        if "items" in obj and isinstance(obj["items"], list):
            return [x for x in obj["items"] if isinstance(x, dict)]
    return []

# Hoja 8: árbol de problemas final
arbol_problemas_final = st.session_state.get("arbol_problemas_final", {})
if not isinstance(arbol_problemas_final, dict):
    arbol_problemas_final = {}

# Hoja 10: descripción del problema
descripcion_problema = st.session_state.get("descripcion_problema", {})
if not isinstance(descripcion_problema, dict):
    descripcion_problema = {}

tabla_datos = descripcion_problema.get("tabla_datos", [])
if not isinstance(tabla_datos, list):
    tabla_datos = []

df_magnitud_reconstruida = pd.DataFrame()
try:
    if tabla_datos:
        base_df = pd.DataFrame(tabla_datos)
        if not base_df.empty:
            cols_esperadas = ["Indicador", "Numerador", "Denominador", "Resultado", "Observación"]
            for c in cols_esperadas:
                if c not in base_df.columns:
                    base_df[c] = ""

            factores = _a_lista_dicts(arbol_problemas_final.get("Factores", []))
            if factores:
                filas = []
                for f in factores:
                    ind = _a_texto_dict(f.get("Indicador", f.get("indicador")))
                    num = _a_texto_dict(f.get("Numerador", f.get("numerador")))
                    den = _a_texto_dict(f.get("Denominador", f.get("denominador")))
                    res = _a_texto_dict(f.get("Resultado", f.get("resultado")))
                    obs = _a_texto_dict(f.get("Observación", f.get("observacion")))
                    filas.append({
                        "Indicador": ind,
                        "Numerador": num,
                        "Denominador": den,
                        "Resultado": res,
                        "Observación": obs
                    })
                df_magnitud_reconstruida = pd.DataFrame(filas)
            else:
                df_magnitud_reconstruida = base_df[cols_esperadas].copy()
except Exception:
    df_magnitud_reconstruida = pd.DataFrame()

redaccion_narrativa = descripcion_problema.get("redaccion_narrativa", "") or ""
antecedentes = descripcion_problema.get("antecedentes", "") or ""

# ==========================================
# 🧾 FUNCIÓN WORD (Conectada)
# ==========================================
def agregar_tabla_word(doc, df, titulo):
    doc.add_paragraph(titulo).runs[0].bold = True
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            row_cells[i].text = str(row[col])

def descargar_y_pegar_imagen(doc, url, ancho):
    if url:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.add_run().add_picture(io.BytesIO(response.content), width=Inches(ancho))
                return True
        except Exception as e:
            pass
    return False

def generar_word():
    doc = Document()

    # --- Encabezado ---
    section = doc.sections[0]
    header = section.header
    hdr_obj = header.paragraphs[0]
    hdr_obj.clear()

    htable = header.add_table(rows=1, cols=2, width=Inches(6.5))
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
    else:
        _url_logo = datos_reportes.get("ruta_logo_portada")
        if _url_logo:
            _b = _download_image_bytes(_url_logo)
            if _b:
                h_der.add_run().add_picture(io.BytesIO(_b), width=Inches(0.6))

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

    # --- Portada ---
    doc.add_paragraph()
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_titulo = p_titulo.add_run(nombre_proyecto.upper())
    r_titulo.bold = True
    r_titulo.font.size = Pt(20)

    doc.add_paragraph()
    if img_portada is not None:
        img_portada.seek(0)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(io.BytesIO(img_portada.getvalue()), width=Inches(3.8))
    else:
        _url_portada = datos_reportes.get("ruta_img_portada")
        if _url_portada:
            _b = _download_image_bytes(_url_portada)
            if _b:
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.add_run().add_picture(io.BytesIO(_b), width=Inches(3.8))

    doc.add_paragraph()
    if entidad_formulo:
        doc.add_paragraph(entidad_formulo.upper()).alignment = WD_ALIGN_PARAGRAPH.CENTER
    if division:
        doc.add_paragraph(division.upper()).alignment = WD_ALIGN_PARAGRAPH.CENTER
    if lugar_presentacion:
        doc.add_paragraph(lugar_presentacion).alignment = WD_ALIGN_PARAGRAPH.CENTER
    if anio_presentacion:
        doc.add_paragraph(anio_presentacion).alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # --- Sección 2. Resumen ---
    doc.add_paragraph("2. RESUMEN DEL PROYECTO").runs[0].bold = True
    doc.add_paragraph(texto_resumen)

    # --- Sección 3. Marco normativo ---
    doc.add_paragraph("3. MARCO NORMATIVO").runs[0].bold = True
    doc.add_paragraph(texto_normativo)

    # --- Sección 4. Justificación ---
    doc.add_paragraph("4. JUSTIFICACIÓN").runs[0].bold = True
    doc.add_paragraph(justificacion)

    # --- Sección 5. Localización ---
    doc.add_paragraph("5. LOCALIZACIÓN").runs[0].bold = True
    if texto_zona:
        doc.add_paragraph(texto_zona)

    if ruta_mapa:
        descargar_y_pegar_imagen(doc, ruta_mapa, 5.5)
    if ruta_foto1:
        descargar_y_pegar_imagen(doc, ruta_foto1, 5.5)
    if ruta_foto2:
        descargar_y_pegar_imagen(doc, ruta_foto2, 5.5)

    # --- Sección 6. Problema ---
    doc.add_paragraph("6. PROBLEMA").runs[0].bold = True
    if antecedentes:
        doc.add_paragraph("6.1 Antecedentes").runs[0].bold = True
        doc.add_paragraph(antecedentes)
    if redaccion_narrativa:
        doc.add_paragraph("6.2 Descripción del problema").runs[0].bold = True
        doc.add_paragraph(redaccion_narrativa)
    if not df_magnitud_reconstruida.empty:
        agregar_tabla_word(doc, df_magnitud_reconstruida, "6.3 Magnitud del problema")

    # --- Sección 7. Árbol de objetivos ---
    doc.add_paragraph("7. ÁRBOL DE OBJETIVOS").runs[0].bold = True
    arbol_objetivos_final = st.session_state.get("arbol_objetivos_final", {})
    if isinstance(arbol_objetivos_final, dict) and arbol_objetivos_final:
        doc.add_paragraph("Se cargó información desde Hoja 7.")

    # --- Sección 8. Indicadores ---
    doc.add_paragraph("8. INDICADORES").runs[0].bold = True
    medios_verificacion = st.session_state.get("medios_verificacion", [])
    if isinstance(medios_verificacion, list) and medios_verificacion:
        try:
            df_medios = pd.DataFrame(medios_verificacion)
            if not df_medios.empty:
                agregar_tabla_word(doc, df_medios, "8.1 Medios de verificación")
        except Exception:
            pass

    # --- Sección 9. Riesgos ---
    doc.add_paragraph("9. RIESGOS").runs[0].bold = True
    datos_riesgos = st.session_state.get("datos_riesgos", [])
    if isinstance(datos_riesgos, list) and datos_riesgos:
        try:
            df_riesgos = pd.DataFrame(datos_riesgos)
            if not df_riesgos.empty:
                agregar_tabla_word(doc, df_riesgos, "9.1 Matriz de riesgos")
        except Exception:
            pass

    # --- Sección 10. Articulación con Plan ---
    doc.add_paragraph("10. ARTICULACIÓN CON EL PLAN DE DESARROLLO").runs[0].bold = True
    doc.add_paragraph(f"Plan: {plan_nombre}")
    doc.add_paragraph(f"Eje: {plan_eje}")
    doc.add_paragraph(f"Programa: {plan_programa}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==========================================
# 📄 PDF (Placeholder)
# ==========================================
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "PDF en construcción. Por ahora use Word.")
    buffer = io.BytesIO(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)
    return buffer

# ==========================================
# ✅ BOTONES DE DESCARGA
# ==========================================
st.markdown("<h2>⬇️ Descargar Reporte</h2>", unsafe_allow_html=True)

col_b1, col_b2 = st.columns(2)

with col_b1:
    if st.button("📄 Generar Word"):
        word_file = generar_word()
        st.download_button(
            label="✅ Descargar Word",
            data=word_file,
            file_name=f"{nombre_proyecto}_Reporte.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

with col_b2:
    if st.button("📑 Generar PDF"):
        pdf_file = generar_pdf()
        st.download_button(
            label="✅ Descargar PDF",
            data=pdf_file,
            file_name=f"{nombre_proyecto}_Reporte.pdf",
            mime="application/pdf"
        )
