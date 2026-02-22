import streamlit as st
import os
import io
import textwrap
import pandas as pd
import requests
from session_state import inicializar_session

# --- IMPORTACIÓN DE LIBRERÍAS ---
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

try:
    import graphviz
except ImportError:
    st.error("⚠️ Falta la librería Graphviz. Agrega 'graphviz' a tu requirements.txt")
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

nombres_formuladores = "No se encontraron formuladores registrados en la Hoja 0 (Equipo)"
nombres_display = nombres_formuladores

integrantes = st.session_state.get("integrantes", [])
if isinstance(integrantes, list):
    nombres_validos = []
    for p in integrantes:
        if isinstance(p, dict):
            nombre = str(p.get("Nombre Completo", "")).strip()
            if nombre:
                nombres_validos.append(nombre)
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
# 1 a 4. General
_plan_nombre = str(st.session_state.get('plan_nombre', '')).strip()
_plan_eje = str(st.session_state.get('plan_eje', '')).strip()
_plan_programa = str(st.session_state.get('plan_programa', '')).strip()

if any([_plan_nombre, _plan_eje, _plan_programa]):
    plan_desarrollo = (
        f"Nombre del Plan: {_plan_nombre if _plan_nombre else 'No definido'}\n"
        f"Eje: {_plan_eje if _plan_eje else 'No definido'}\n"
        f"Programa: {_plan_programa if _plan_programa else 'No definido'}"
    )
else:
    plan_desarrollo = st.session_state.get('plan_desarrollo', 'No se ha registrado información en la Hoja 15.')
    
justificacion = (
    st.session_state.get('justificacion_arbol_objetivos_final')
    or st.session_state.get('arbol_objetivos_final', {}).get('referencia_manual', {}).get('justificacion', '')
    or st.session_state.get('justificacion_proyecto')
    or 'No se ha registrado información en la Hoja 7.'
)

# 5. Localización (Hoja 9)
zona_data = st.session_state.get('descripcion_zona', {})
ruta_mapa = zona_data.get('ruta_mapa')
ruta_foto1 = zona_data.get('ruta_foto1')
ruta_foto2 = zona_data.get('ruta_foto2')


# --- LÓGICA DE EXTRACCIÓN PARA LA SECCIÓN 6 (HOJA 8 Y 10) ---
def _a_texto_dict(item):
    if isinstance(item, dict): return item
    if item is None: return None
    return {"texto": str(item)}

def _a_lista_dicts(valor):
    if valor is None: return []
    if isinstance(valor, list):
        out = []
        for it in valor:
            d = _a_texto_dict(it)
            if d is not None: out.append(d)
        return out
    if isinstance(valor, dict): return [valor]
    return [{"texto": str(valor)}]

desc_prob_data = st.session_state.get('descripcion_problema', {})

narrativa_problema = desc_prob_data.get('redaccion_narrativa', 'No se ha registrado descripción.')
if not narrativa_problema.strip(): narrativa_problema = 'No se ha registrado descripción.'

antecedentes_problema = desc_prob_data.get('antecedentes', 'No se han registrado antecedentes.')
if not antecedentes_problema.strip(): antecedentes_problema = 'No se han registrado antecedentes.'

tabla_datos_prob = desc_prob_data.get('tabla_datos', {})
datos_h8 = st.session_state.get('arbol_problemas_final', {})
if not isinstance(datos_h8, dict): datos_h8 = {}

pp_list = _a_lista_dicts(datos_h8.get("Problema Principal"))
pc_txt = pp_list[0].get("texto", "") if pp_list and isinstance(pp_list[0], dict) else ""

lista_causas = [c.get("texto") for c in (_a_lista_dicts(datos_h8.get("Causas Directas")) + _a_lista_dicts(datos_h8.get("Causas Indirectas"))) if isinstance(c, dict) and c.get
