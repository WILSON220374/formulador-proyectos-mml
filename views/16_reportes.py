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

lista_causas = [c.get("texto") for c in (_a_lista_dicts(datos_h8.get("Causas Directas")) + _a_lista_dicts(datos_h8.get("Causas Indirectas"))) if isinstance(c, dict) and c.get("texto")]
lista_efectos = [e.get("texto") for e in (_a_lista_dicts(datos_h8.get("Efectos Directos")) + _a_lista_dicts(datos_h8.get("Efectos Indirectos"))) if isinstance(e, dict) and e.get("texto")]

filas_magnitud = []
if pc_txt:
    filas_magnitud.append({"Categoría": "PROBLEMA CENTRAL", "Descripción": pc_txt, "Magnitud": tabla_datos_prob.get("m_pc", ""), "Unidad": tabla_datos_prob.get("u_pc", ""), "Cantidad": tabla_datos_prob.get("c_pc", "")})
for i, txt in enumerate(lista_causas):
    filas_magnitud.append({"Categoría": f"CAUSA {i+1}", "Descripción": txt, "Magnitud": tabla_datos_prob.get(f"m_causa_{i}", ""), "Unidad": tabla_datos_prob.get(f"u_causa_{i}", ""), "Cantidad": tabla_datos_prob.get(f"c_causa_{i}", "")})
for i, txt in enumerate(lista_efectos):
    filas_magnitud.append({"Categoría": f"EFECTO {i+1}", "Descripción": txt, "Magnitud": tabla_datos_prob.get(f"m_efecto_{i}", ""), "Unidad": tabla_datos_prob.get(f"u_efecto_{i}", ""), "Cantidad": tabla_datos_prob.get(f"c_efecto_{i}", "")})

df_magnitud_reconstruida = pd.DataFrame(filas_magnitud)


# --- 7. POBLACIÓN (HOJA 9) ---
df_poblacion_general = pd.DataFrame([{
    "Población de Referencia": zona_data.get('poblacion_referencia', 0),
    "Población Afectada": zona_data.get('poblacion_afectada', 0),
    "Población Objetivo": zona_data.get('poblacion_objetivo', 0)
}])

genero_data = zona_data.get('poblacion_objetivo_genero', {})
df_pob_sexo = pd.DataFrame([{
    "Hombres": genero_data.get("Hombres", 0),
    "Mujeres": genero_data.get("Mujeres", 0)
}])

edad_data = zona_data.get('poblacion_objetivo_edad', {})
df_pob_edad = pd.DataFrame([{
    "0 - 14": edad_data.get("0-14", 0),
    "15 - 19": edad_data.get("15-19", 0),
    "20 - 59": edad_data.get("20-59", 0),
    "Mayor de 60 años": edad_data.get("Mayor de 60 años", 0)
}])

analisis_poblacion = str(zona_data.get('analisis_poblacion_objetivo', '')).strip()
if not analisis_poblacion:
    analisis_poblacion = 'No se ha registrado análisis de población.'


# --- 8. PARTICIPANTES (HOJA 3 Y 9) ---
df_matriz_interesados = st.session_state.get('df_interesados', pd.DataFrame())
if df_matriz_interesados is not None and not isinstance(df_matriz_interesados, pd.DataFrame):
    try: df_matriz_interesados = pd.DataFrame(df_matriz_interesados)
    except: df_matriz_interesados = pd.DataFrame()

texto_analisis_participantes = str(
    st.session_state.get('analisis_participantes') or 
    st.session_state.get('txt_analisis_participantes') or 
    st.session_state.get('descripcion_zona', {}).get('analisis_participantes', '')
).strip()

if not texto_analisis_participantes:
    texto_analisis_participantes = "No se ha registrado el análisis de los participantes."


# --- 9. OBJETIVOS (HOJA 7) ---
arbol_obj_datos = st.session_state.get('arbol_objetivos_final', {})
ref_obj_data = arbol_obj_datos.get('referencia_manual', {})

objetivo_general = str(ref_obj_data.get('objetivo', '')).strip()
if not objetivo_general:
    objetivo_general = "No se ha definido el objetivo general en la Hoja 7."

objetivos_especificos = ref_obj_data.get('especificos', [])
if not objetivos_especificos:
    objetivos_especificos = ["No se han definido objetivos específicos."]


# --- NUEVA LÓGICA DE EXTRACCIÓN PARA LA SECCIÓN 10 (HOJA 6) ---
lista_alts_evaluadas = st.session_state.get('lista_alternativas', [])

pesos = st.session_state.get('ponderacion_criterios', {"COSTO": 25, "FACILIDAD": 25, "BENEFICIOS": 25, "TIEMPO": 25})
df_criterios = pd.DataFrame([pesos]) # Tabla 1 de la sección 10

df_calif = st.session_state.get('df_calificaciones', pd.DataFrame())
df_evaluacion_alt = pd.DataFrame()
alternativa_seleccionada = "No se ha seleccionado ninguna alternativa."

if not df_calif.empty:
    df_eval = df_calif.copy()
    df_eval["TOTAL"] = 0.0
    for c in ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]:
        if c in df_eval.columns:
            df_eval["TOTAL"] += df_eval[c] * (pesos.get(c, 0) / 100.0)
    
    # Encontrar la ganadora matemáticamente
    ganadora_idx = df_eval["TOTAL"].idxmax()
    puntaje_ganador = df_eval["TOTAL"].max()
    alternativa_seleccionada = f"Alternativa Seleccionada: {ganadora_idx} ({puntaje_ganador:.2f} pts)"
    
    # Preparar tabla final para Word
    df_eval = df_eval.round(2).reset_index().rename(columns={"index": "Alternativa"})
    df_evaluacion_alt = df_eval


# ==========================================
# ⚙️ MOTORES DE DIBUJO Y GENERACIÓN WORD
# ==========================================
def agregar_tabla_word(doc, df):
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
        p = doc.add_paragraph()
        p.add_run("No se registraron datos en esta tabla.").italic = True
        
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

def redibujar_arbol_problemas(arbol_data):
    """Motor que dibuja a la fuerza el árbol con Graphviz si la foto temporal no existe"""
    try:
        dot = graphviz.Digraph(format='png')
        dot.attr(rankdir='BT')
        dot.attr('node', shape='box', style='filled', fontname='Helvetica', margin='0.2')

        pp_list = _a_lista_dicts(arbol_data.get("Problema Principal", arbol_data.get("problema")))
        pc_txt = pp_list[0].get("texto", "Problema Central") if pp_list else "Problema Central"
        dot.node('PC', str(pc_txt), fillcolor='#FCA5A5')

        c_dir = _a_lista_dicts(arbol_data.get("Causas Directas", arbol_data.get("causas")))
        c_ind = _a_lista_dicts(arbol_data.get("Causas Indirectas", []))
        causas = c_dir + c_ind
        for i, ca in enumerate(causas):
            if ca.get('texto'):
                dot.node(f'C_{i}', ca.get('texto'), fillcolor='#FEF3C7')
                dot.edge(f'C_{i}', 'PC')

        e_dir = _a_lista_dicts(arbol_data.get("Efectos Directos", arbol_data.get("efectos")))
        e_ind = _a_lista_dicts(arbol_data.get("Efectos Indirectos", []))
        efectos = e_dir + e_ind
        for i, ef in enumerate(efectos):
            if ef.get('texto'):
                dot.node(f'E_{i}', ef.get('texto'), fillcolor='#DBEAFE')
                dot.edge('PC', f'E_{i}')

        return io.BytesIO(dot.pipe())
    except Exception as e:
        return None

def redibujar_arbol_objetivos(datos):
    """Motor de respaldo para dibujar el Árbol de Objetivos si falta la foto."""
    try:
        CONFIG_OBJ = {
            "Fin Último":        {"color": "#0E6251"},
            "Fines Indirectos":  {"color": "#154360"},
            "Fines Directos":    {"color": "#1F618D"},
            "Objetivo General":  {"color": "#C0392B"},
            "Medios Directos":   {"color": "#F1C40F"},
            "Medios Indirectos": {"color": "#D35400"}
        }
        claves_graficas = [k for k in datos.keys() if k != 'referencia_manual']
        if not any(datos.get(k) for k in claves_graficas): return None

        dot = graphviz.Digraph(format='png')
        dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
        dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')
        
        def limpiar(t): return "\\n".join(textwrap.wrap(str(t).upper(), width=25))
        
        obj_gen = [it for it in datos.get("Objetivo General", []) if isinstance(it, dict) and it.get('texto')]
        if obj_gen: 
            dot.node("OG", limpiar(obj_gen[0]['texto']), fillcolor=CONFIG_OBJ["Objetivo General"]["color"], fontcolor='white', color='none', width='4.5')
            
        for tipo, p_id, h_tipo in [("Fines Directos", "OG", "Fines Indirectos"), ("Medios Directos", "OG", "Medios Indirectos")]:
            items = [it for it in datos.get(tipo, []) if isinstance(it, dict) and it.get('texto')]
            for i, item in enumerate(items):
                n_id = f"{tipo[:2]}{i}"
                dot.node(n_id, limpiar(item['texto']), fillcolor=CONFIG_OBJ[tipo]["color"], fontcolor='white' if "Fin" in tipo else 'black', color='none')
                if "Fin" in tipo: dot.edge("OG", n_id)
                else: dot.edge(n_id, "OG")
                hijos = [h for h in datos
