import streamlit as st
import os
import uuid
from PIL import Image
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- BLOQUE DE AUTO-REPARACIÓN ---
if 'descripcion_zona' in st.session_state:
    datos = st.session_state['descripcion_zona']
    campos_requeridos = [
        "problema_central", "departamento", "provincia", "municipio", 
        "barrio_vereda", "latitud", "longitud", 
        "limites_geograficos", "limites_administrativos", "otros_limites", 
        "accesibilidad", 
        "poblacion_referencia", "poblacion_afectada", "poblacion_objetivo",
        "pie_mapa", "pie_foto1", "pie_foto2"
    ]
    for campo in campos_requeridos:
        if campo not in datos:
            datos[campo] = 0 if "poblacion" in campo else ""

    claves_poblacion = ["poblacion_referencia", "poblacion_afectada", "poblacion_objetivo"]
    for k in claves_poblacion:
        if isinstance(datos[k], str):
            try: datos[k] = int(datos[k]) if datos[k].strip() else 0
            except: datos[k] = 0

# --- CONFIGURACIÓN DE ALMACENAMIENTO ---
if 'descripcion_zona' not in st.session_state:
    st.session_state['descripcion_zona'] = {
        "problema_central": "",
        "departamento": "", "provincia": "", "municipio": "", 
        "barrio_vereda": "", "latitud": "", "longitud": "",
        "limites_geograficos": "", "limites_administrativos": "", "otros_limites": "",
        "accesibilidad": "",
        "ruta_mapa": None, "ruta_foto1": None, "ruta_foto2": None,
        "pie_mapa": "", "pie_foto1": "", "pie_foto2": "",
        "poblacion_referencia": 0, "poblacion_afectada": 0, "poblacion_objetivo": 0
    }

zona_data = st.session_state['descripcion_zona']
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)

# --- DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    .form-header {
        background-color: #e0f2fe; color: #1E3A8A; font-weight: 800; font-size: 1.1rem;
        padding: 10px; border-radius: 5px; margin-top: 25px; margin-bottom: 15px; border-left: 5px solid #1E3A8A;
    }
    .img-display {
        border: 2px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-bottom: 10px;
    }
    .main .stButton button {
        border: 1px solid #ef4444 !important; background: transparent !important;
        color: #ef4444 !important; font-size: 0.9rem !important; margin-top: 5px !important;
    }
    .sub-header { font-weight: 700; color: #1E3A8A; margin-bottom: 5px; display: block; }
    div[data-testid="stNumberInput"] input { background-color: #f0f9ff; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

def calc_altura(texto):
    if not texto: return 100
    lineas = str(texto).count('\n') + (len(str(texto)) // 90) + 1
    return max(80, lineas * 25)

# --- ENCABEZADO ---
col_t, col_img_head = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🗺️ 9. DESCRIPCIÓN GENERAL DE LA ZONA DE ESTUDIO</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Caracterización de límites, accesibilidad y población.</div>', unsafe_allow_html=True)

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
        
        # Borrar anterior si existe
        ruta_anterior = st.session_state['descripcion_zona'].get(f"ruta_{tipo_imagen_key}")
        if ruta_anterior and os.path.exists(ruta_anterior):
            try: os.remove(ruta_anterior)
            except: pass

        st.session_state['descripcion_zona'][f"ruta_{tipo_imagen_key}"] = file_path
        guardar_datos_nube()
        st.rerun() # Recargar para ocultar el uploader y mostrar la imagen

def eliminar_imagen(tipo_imagen_key):
    ruta = st.session_state['descripcion_zona'].get(f"ruta_{tipo_imagen_key}")
    if ruta and os.path.exists(ruta):
        try: os.remove(ruta)
        except: pass
    st.session_state['descripcion_zona'][f"ruta_{tipo_imagen_key}"] = None
    guardar_datos_nube()
    st.rerun()

# --- FORMULARIO ---

# 1. PROBLEMA CENTRAL
st.markdown('<div class="form-header">PROBLEMA CENTRAL</div>', unsafe_allow_html=True)
st.text_area("Descripción del Problema Central:", value=zona_data.get('problema_central', ''), key="temp_problema_central", height=calc_altura(zona_data.get('problema_central', '')), on_change=update_field, args=("problema_central",))

# 2. LOCALIZACIÓN
st.markdown('<div class="form-header">LOCALIZACIÓN</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: st.text_input("Departamento:", value=zona_data.get('departamento', ''), key="temp_departamento", on_change=update_field, args=("departamento",))
with c2: st.text_input("Provincia:", value=zona_data.get('provincia', ''), key="temp_provincia", on_change=update_field, args=("provincia",))
with c3: st.text_input("Municipio:", value=zona_data.get('municipio', ''), key="temp_municipio", on_change=update_field, args=("municipio",))
with c4: st.text_input("Barrio o Vereda:", value=zona_data.get('barrio_vereda', ''), key="temp_barrio_vereda", on_change=update_field, args=("barrio_vereda",))

st.caption("Coordenadas:")
c_lat, c_lon = st.columns(2)
with c_lat: st.text_input("Latitud:", value=zona_data.get('latitud', ''), key="temp_latitud", placeholder="Ej: 5.715", on_change=update_field, args=("latitud",))
with c_lon: st.text_input("Longitud:", value=zona_data.get('longitud', ''), key="temp_longitud", placeholder="Ej: -72.933", on_change=update_field, args=("longitud",))

# 3. DEFINICIÓN DE LÍMITES
st.markdown('<div class="form-header">DEFINICIÓN DE LÍMITES</div>', unsafe_allow_html=True)
st.text_area("Límites Geográficos:", value=zona_data.get('limites_geograficos', ''), key="temp_limites_geograficos", height=calc_altura(zona_data.get('limites_geograficos', '')), on_change=update_field, args=("limites_geograficos",))
st.text_area("Límites Administrativos:", value=zona_data.get('limites_administrativos', ''), key="temp_limites_administrativos", height=calc_altura(zona_data.get('limites_administrativos', '')), on_change=update_field, args=("limites_administrativos",))
st.text_area("Otros Límites:", value=zona_data.get('otros_limites', ''), key="temp_otros_limites", height=calc_altura(zona_data.get('otros_limites', '')), on_change=update_field, args=("otros_limites",))

# 4. ACCESIBILIDAD
st.markdown('<div class="form-header">CONDICIONES DE ACCESIBILIDAD</div>', unsafe_allow_html=True)
st.text_area("Existencia y estado de las vías de acceso:", value=zona_data.get('accesibilidad', ''), key="temp_accesibilidad", height=calc_altura(zona_data.get('accesibilidad', '')), on_change=update_field, args=("accesibilidad",))

# 5. MAPA Y FOTOS (LÓGICA CARGAR/VER/BORRAR)
st.markdown('<div class="form-header">MAPA DEL ÁREA DE ESTUDIO Y FOTOS</div>', unsafe_allow_html=True)

# --- MAPA ---
st.markdown('<span class="sub-header">Mapa del área de estudio</span>', unsafe_allow_html=True)
ruta_mapa = zona_data.get("ruta_mapa")
if ruta_mapa and os.path.exists(ruta_mapa):
    st.image(ruta_mapa, use_container_width=True)
    if st.button("🗑️ Eliminar Mapa", key="btn_del_mapa"):
        eliminar_imagen("mapa")
else:
    up_mapa = st.file_uploader("Cargar Mapa", type=['png', 'jpg', 'jpeg'], key="up_mapa", label_visibility="collapsed")
    if up_mapa: manejar_subida_imagen(up_mapa, "mapa")

# --- FOTOS ---
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown('<span class="sub-header">FOTO 1</span>', unsafe_allow_html=True)
    ruta_f1 = zona_data.get("ruta_foto1")
    if ruta_f1 and os.path.exists(ruta_f1):
        st.image(ruta_f1, use_container_width=True)
        if st.button("🗑️ Eliminar Foto 1", key="btn_del_f1"):
            eliminar_imagen("foto1")
    else:
        up_f1 = st.file_uploader("Cargar Foto 1", type=['png', 'jpg', 'jpeg'], key="up_foto1", label_visibility="collapsed")
        if up_f1: manejar_subida_imagen(up_f1, "foto1")

with col_f2:
    st.markdown('<span class="sub-header">FOTO 2</span>', unsafe_allow_html=True)
    ruta_f2 = zona_data.get("ruta_foto2")
    if ruta_f2 and os.path.exists(ruta_f2):
        st.image(ruta_f2, use_container_width=True)
        if st.button("🗑️ Eliminar Foto 2", key="btn_del_f2"):
            eliminar_imagen("foto2")
    else:
        up_f2 = st.file_uploader("Cargar Foto 2", type=['png', 'jpg', 'jpeg'], key="up_foto2", label_visibility="collapsed")
        if up_f2: manejar_subida_imagen(up_f2, "foto2")

# 6. POBLACIÓN
st.markdown('<div class="form-header">POBLACIÓN</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.number_input("POBLACIÓN DE REFERENCIA:", min_value=0, step=1, format="%d", value=int(zona_data.get('poblacion_referencia', 0)), key="temp_poblacion_referencia", on_change=update_field, args=("poblacion_referencia",))
with c2: st.number_input("POBLACIÓN AFECTADA:", min_value=0, step=1, format="%d", value=int(zona_data.get('poblacion_afectada', 0)), key="temp_poblacion_afectada", on_change=update_field, args=("poblacion_afectada",))
with c3: st.number_input("POBLACIÓN OBJETIVO:", min_value=0, step=1, format="%d", value=int(zona_data.get('poblacion_objetivo', 0)), key="temp_poblacion_objetivo", on_change=update_field, args=("poblacion_objetivo",))

st.success("✅ Imágenes ajustadas: Carga única con opción de eliminar.")
