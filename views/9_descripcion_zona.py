iimport streamlit as st
import os
import uuid
from PIL import Image
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- CONFIGURACIÓN DE ALMACENAMIENTO ---
if 'descripcion_zona' not in st.session_state:
    st.session_state['descripcion_zona'] = {
        # Localización
        "departamento": "", "provincia": "", "municipio": "", 
        "vereda_corregimiento": "", 
        "latitud": "", "longitud": "", # <--- COORDENADAS SEPARADAS
        # Características Físicas
        "clima_temperatura": "", "altitud": "", "topografia_suelos": "", "hidrografia": "",
        # Aspectos Socioambientales
        "ecosistemas_clave": "", "uso_suelo": "", "poblacion_beneficiaria": "",
        "actividades_economicas": "", "vias_acceso": "", "infraestructura_servicios": "",
        # Rutas de Imágenes
        "ruta_mapa": None, "ruta_foto1": None, "ruta_foto2": None,
        # Pies de Foto
        "pie_mapa": "", "pie_foto1": "", "pie_foto2": ""
    }

# Referencia corta
zona_data = st.session_state['descripcion_zona']

# Carpeta para guardar imágenes
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    .form-header {
        color: #1E3A8A; font-weight: 700; font-size: 1.1rem; margin-top: 20px;
        margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;
    }
    .img-preview-container {
        border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px;
        text-align: center; background-color: #f8fafc; min-height: 200px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .main .stButton button {
        border: none !important; background: transparent !important;
        color: #ef4444 !important; font-size: 1.2rem !important; margin-top: -10px !important;
    }
    /* Estilo limpio para áreas de texto */
    div[data-testid="stTextArea"] textarea {
        background-color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN INTELIGENTE: CALCULAR ALTURA DINÁMICA ---
def calc_altura(texto):
    # Calcula aprox 90 caracteres por línea visual + saltos de línea reales
    # Base mínima de 100px para comodidad
    if not texto: return 100
    lineas = str(texto).count('\n') + (len(str(texto)) // 90) + 1
    return max(100, lineas * 25)

# --- ENCABEZADO ---
col_t, col_img_head = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🗺️ 9. Descripción General de la Zona de Estudio</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Caracterización geográfica, ambiental y socioeconómica.</div>', unsafe_allow_html=True)
    
    campos_texto = [v for k, v in zona_data.items() if isinstance(v, str) and not k.startswith('ruta') and not k.startswith('pie')]
    progreso = len([c for c in campos_texto if c.strip() != ""]) / len(campos_texto) if campos_texto else 0
    st.progress(progreso)

with col_img_head:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- FUNCIONES ---
def update_field(key):
    temp_key = f"temp_{key}"
    if temp_key in st.session_state:
        st.session_state['descripcion_zona'][key] = st.session_state[temp_key]
        guardar_datos_nube()

def manejar_subida_imagen(uploaded_file, tipo_imagen_key):
    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{tipo_imagen_key}_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        
        ruta_anterior = st.session_state['descripcion_zona'].get(f"ruta_{tipo_imagen_key}")
        if ruta_anterior and os.path.exists(ruta_anterior):
            try: os.remove(ruta_anterior)
            except: pass

        st.session_state['descripcion_zona'][f"ruta_{tipo_imagen_key}"] = file_path
        guardar_datos_nube()
        st.toast(f"✅ Imagen cargada correctamente.")

# --- FORMULARIO ---

# 1. LOCALIZACIÓN GEOGRÁFICA
st.markdown('<div class="form-header">📍 1. Localización Geográfica</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: st.text_input("Departamento:", value=zona_data['departamento'], key="temp_departamento", on_change=update_field, args=("departamento",))
with c2: st.text_input("Provincia:", value=zona_data.get('provincia', ''), key="temp_provincia", on_change=update_field, args=("provincia",))
with c3: st.text_input("Municipio:", value=zona_data['municipio'], key="temp_municipio", on_change=update_field, args=("municipio",))
with c4: st.text_input("Barrio / Vereda:", value=zona_data['vereda_corregimiento'], key="temp_vereda_corregimiento", on_change=update_field, args=("vereda_corregimiento",))

# --- COORDENADAS SEPARADAS ---
st.markdown("**Coordenadas Geográficas:**")
c_lat, c_lon = st.columns(2)
with c_lat:
    st.text_input("Latitud:", value=zona_data.get('latitud', ''), placeholder="Ej: 5.715", key="temp_latitud", on_change=update_field, args=("latitud",))
with c_lon:
    st.text_input("Longitud:", value=zona_data.get('longitud', ''), placeholder="Ej: -72.933", key="temp_longitud", on_change=update_field, args=("longitud",))

# 2. CARACTERÍSTICAS FÍSICAS
st.markdown('<div class="form-header">⛰️ 2. Características Físicas y Ambientales</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.text_input("Clima / Temperatura:", value=zona_data['clima_temperatura'], key="temp_clima_temperatura", on_change=update_field, args=("clima_temperatura",))
    st.text_area("Topografía / Suelos:", value=zona_data['topografia_suelos'], key="temp_topografia_suelos", 
                 height=calc_altura(zona_data['topografia_suelos']), on_change=update_field, args=("topografia_suelos",))
    st.text_input("Ecosistemas Clave:", value=zona_data['ecosistemas_clave'], key="temp_ecosistemas_clave", on_change=update_field, args=("ecosistemas_clave",))
with c2:
    st.text_input("Altitud (m.s.n.m.):", value=zona_data['altitud'], key="temp_altitud", on_change=update_field, args=("altitud",))
    st.text_area("Hidrografía:", value=zona_data['hidrografia'], key="temp_hidrografia", 
                 height=calc_altura(zona_data['hidrografia']), on_change=update_field, args=("hidrografia",))
    st.text_input("Uso del Suelo:", value=zona_data['uso_suelo'], key="temp_uso_suelo", on_change=update_field, args=("uso_suelo",))

# 3. ASPECTOS SOCIOECONÓMICOS
st.markdown('<div class="form-header">👥 3. Aspectos Socioeconómicos</div>', unsafe_allow_html=True)
st.text_area("Población Beneficiaria:", value=zona_data['poblacion_beneficiaria'], key="temp_poblacion_beneficiaria", 
             height=calc_altura(zona_data['poblacion_beneficiaria']), on_change=update_field, args=("poblacion_beneficiaria",))

c1, c2 = st.columns(2)
with c1: st.text_area("Actividades Económicas:", value=zona_data['actividades_economicas'], key="temp_actividades_economicas", 
                     height=calc_altura(zona_data['actividades_economicas']), on_change=update_field, args=("actividades_economicas",))
with c2: st.text_area("Vías de Acceso:", value=zona_data['vias_acceso'], key="temp_vias_acceso", 
                     height=calc_altura(zona_data['vias_acceso']), on_change=update_field, args=("vias_acceso",))

st.text_area("Infraestructura y Servicios:", value=zona_data['infraestructura_servicios'], key="temp_infraestructura_servicios", 
             height=calc_altura(zona_data['infraestructura_servicios']), on_change=update_field, args=("infraestructura_servicios",))

st.divider()

# 4. EVIDENCIA GRÁFICA
st.markdown('<div class="form-header">📸 4. Evidencia Gráfica</div>', unsafe_allow_html=True)
col_mapa, col_foto1, col_foto2 = st.columns(3)

with col_mapa:
    st.markdown("**Mapa**")
    up = st.file_uploader("Subir Mapa", type=['png', 'jpg'], key="up_mapa", label_visibility="collapsed")
    if up: manejar_subida_imagen(up, "mapa"); st.rerun()
    
    st.markdown('<div class="img-preview-container">', unsafe_allow_html=True)
    if zona_data.get("ruta_mapa") and os.path.exists(zona_data["ruta_mapa"]): st.image(zona_data["ruta_mapa"], use_container_width=True)
    else: st.markdown('<span style="color:#ccc;">Sin Mapa</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.text_input("Pie de foto:", value=zona_data['pie_mapa'], key="temp_pie_mapa", on_change=update_field, args=("pie_mapa",))

with col_foto1:
    st.markdown("**Foto 1**")
    up = st.file_uploader("Subir Foto 1", type=['png', 'jpg'], key="up_foto1", label_visibility="collapsed")
    if up: manejar_subida_imagen(up, "foto1"); st.rerun()
    
    st.markdown('<div class="img-preview-container">', unsafe_allow_html=True)
    if zona_data.get("ruta_foto1") and os.path.exists(zona_data["ruta_foto1"]): st.image(zona_data["ruta_foto1"], use_container_width=True)
    else: st.markdown('<span style="color:#ccc;">Sin Foto 1</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.text_input("Pie de foto:", value=zona_data['pie_foto1'], key="temp_pie_foto1", on_change=update_field, args=("pie_foto1",))

with col_foto2:
    st.markdown("**Foto 2**")
    up = st.file_uploader("Subir Foto 2", type=['png', 'jpg'], key="up_foto2", label_visibility="collapsed")
    if up: manejar_subida_imagen(up, "foto2"); st.rerun()
    
    st.markdown('<div class="img-preview-container">', unsafe_allow_html=True)
    if zona_data.get("ruta_foto2") and os.path.exists(zona_data["ruta_foto2"]): st.image(zona_data["ruta_foto2"], use_container_width=True)
    else: st.markdown('<span style="color:#ccc;">Sin Foto 2</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.text_input("Pie de foto:", value=zona_data['pie_foto2'], key="temp_pie_foto2", on_change=update_field, args=("pie_foto2",))
