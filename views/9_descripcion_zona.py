iimport streamlit as st
import os
import uuid
import base64
from PIL import Image
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- CONFIGURACIÓN DE ALMACENAMIENTO E INICIALIZACIÓN ---
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

# --- SINCRONIZACIÓN AUTOMÁTICA SILENCIOSA CON HOJA 8 ---
# Si el campo local está vacío, busca automáticamente en la Hoja 8
if not st.session_state['descripcion_zona'].get('problema_central'):
    prob_fuente = st.session_state.get('arbol_problemas_final', {}).get('referencia_manual_prob', {}).get('problema_central', "")
    if prob_fuente:
        st.session_state['descripcion_zona']['problema_central'] = prob_fuente

# --- BLOQUE DE AUTO-REPARACIÓN DE CAMPOS ---
datos = st.session_state['descripcion_zona']
campos_requeridos = [
    "problema_central", "departamento", "provincia", "municipio", 
    "barrio_vereda", "latitud", "longitud", 
    "limites_geograficos", "limites_administrativos", "otros_limites", 
    "accesibilidad", "poblacion_referencia", "poblacion_afectada", "poblacion_objetivo"
]
for campo in campos_requeridos:
    if campo not in datos:
        datos[campo] = 0 if "poblacion" in campo else ""

zona_data = st.session_state['descripcion_zona']
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    .form-header {
        background-color: #e0f2fe; color: #1E3A8A; font-weight: 800; font-size: 1.1rem;
        padding: 10px; border-radius: 5px; margin-top: 25px; margin-bottom: 15px; border-left: 5px solid #1E3A8A;
    }
    .main .stButton button {
        border: 1px solid #ef4444 !important; background: transparent !important;
        color: #ef4444 !important; font-size: 0.9rem !important; margin-top: 5px !important; width: 100%;
    }
    .sub-header { font-weight: 700; color: #1E3A8A; margin-bottom: 5px; display: block; }
    div[data-testid="stNumberInput"] input { background-color: #f0f9ff; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

def calc_altura(texto):
    if not texto: return 100
    lineas = str(texto).count('\n') + (len(str(texto)) // 90) + 1
    return max(80, lineas * 25)

def mostrar_imagen_simetrica(ruta_imagen, altura_px):
    if not ruta_imagen or not os.path.exists(ruta_imagen): return
    with open(ruta_imagen, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    html_code = f"""
    <div style="width: 100%; height: {altura_px}px; overflow: hidden; border-radius: 8px; border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 5px;">
        <img src="data:image/jpeg;base64,{data}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;">
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# --- FUNCIÓN DE GUARDADO ROBUSTO ---
def update_field(key):
    """Sincroniza el valor del input con el estado global y guarda en la nube."""
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
        st.rerun()

def eliminar_imagen(tipo_imagen_key):
    ruta = st.session_state['descripcion_zona'].get(f"ruta_{tipo_imagen_key}")
    if ruta and os.path.exists(ruta):
        try: os.remove(ruta)
        except: pass
    st.session_state['descripcion_zona'][f"ruta_{tipo_imagen_key}"] = None
    guardar_datos_nube()
    st.rerun()

# --- ENCABEZADO ---
col_t, col_img_head = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🗺️ 9. DESCRIPCIÓN GENERAL DE LA ZONA DE ESTUDIO</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Caracterización de límites, accesibilidad y población.</div>', unsafe_allow_html=True)

with col_img_head:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- FORMULARIO ---

# 1. PROBLEMA CENTRAL
st.markdown('<div class="form-header">PROBLEMA CENTRAL</div>', unsafe_allow_html=True)
st.text_area("Descripción del Problema Central:", value=st.session_state['descripcion_zona']['problema_central'], key="temp_problema_central", height=calc_altura(st.session_state['descripcion_zona']['problema_central']), on_change=update_field, args=("problema_central",))

# 2. LOCALIZACIÓN
st.markdown('<div class="form-header">LOCALIZACIÓN</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: st.text_input("Departamento:", value=zona_data.get('departamento', ''), key="temp_departamento", on_change=update_field, args=("departamento",))
with c2: st.text_input("Provincia:", value=zona_data.get('provincia', ''), key="temp_provincia", on_change=update_field, args=("provincia",))
with c3: st.text_input("Municipio:", value=zona_data.get('municipio', ''), key="temp_municipio", on_change=update_field, args=("municipio",))
with c4: st.text_input("Barrio o Vereda:", value=zona_data.get('barrio_vereda', ''), key="temp_barrio_vereda", on_change=update_field, args=("barrio_vereda",))

st.caption("Coordenadas:")
cl1, cl2 = st.columns(2)
with cl1: st.text_input("Latitud:", value=zona_data.get('latitud', ''), key="temp_latitud", placeholder="Ej: 5.715", on_change=update_field, args=("latitud",))
with cl2: st.text_input("Longitud:", value=zona_data.get('longitud', ''), key="temp_longitud", placeholder="Ej: -72.933", on_change=update_field, args=("longitud",))

# 3. DEFINICIÓN DE LÍMITES
st.markdown('<div class="form-header">DEFINICIÓN DE LÍMITES</div>', unsafe_allow_html=True)
st.text_area("Límites Geográficos:", value=zona_data.get('limites_geograficos', ''), key="temp_limites_geograficos", height=calc_altura(zona_data.get('limites_geograficos', '')), on_change=update_field, args=("limites_geograficos",))
st.text_area("Límites Administrativos:", value=zona_data.get('limites_administrativos', ''), key="temp_limites_administrativos", height=calc_altura(zona_data.get('limites_administrativos', '')), on_change=update_field, args=("limites_administrativos",))
st.text_area("Otros Límites:", value=zona_data.get('otros_limites', ''), key="temp_otros_limites", height=calc_altura(zona_data.get('otros_limites', '')), on_change=update_field, args=("otros_limites",))

# 4. CONDICIONES DE ACCESIBILIDAD
st.markdown('<div class="form-header">CONDICIONES DE ACCESIBILIDAD</div>', unsafe_allow_html=True)
st.text_area("Vías de acceso:", value=zona_data.get('accesibilidad', ''), key="temp_accesibilidad", height=calc_altura(zona_data.get('accesibilidad', '')), on_change=update_field, args=("accesibilidad",))

# 5. MAPA Y FOTOS
st.markdown('<div class="form-header">MAPA DEL ÁREA DE ESTUDIO Y FOTOS</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-header">Mapa del área de estudio</span>', unsafe_allow_html=True)
ruta_mapa = zona_data.get("ruta_mapa")
if ruta_mapa and os.path.exists(ruta_mapa):
    mostrar_imagen_simetrica(ruta_mapa, 400) # Altura mantenida en 400px
    if st.button("🗑️ Eliminar Mapa", key="btn_del_mapa"): eliminar_imagen("mapa")
else:
    up_mapa = st.file_uploader("Cargar Mapa", type=['png', 'jpg', 'jpeg'], key="up_mapa", label_visibility="collapsed")
    if up_mapa: manejar_subida_imagen(up_mapa, "mapa")

st.write("")
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.markdown('<span class="sub-header">FOTO 1</span>', unsafe_allow_html=True)
    rf1 = zona_data.get("ruta_foto1")
    if rf1 and os.path.exists(rf1):
        mostrar_imagen_simetrica(rf1, 300)
        if st.button("🗑️ Eliminar Foto 1", key="btn_del_f1"): eliminar_imagen("foto1")
    else:
        uf1 = st.file_uploader("Cargar Foto 1", type=['png', 'jpg', 'jpeg'], key="up_foto1", label_visibility="collapsed")
        if uf1: manejar_subida_imagen(uf1, "foto1")
with col_f2:
    st.markdown('<span class="sub-header">FOTO 2</span>', unsafe_allow_html=True)
    rf2 = zona_data.get("ruta_foto2")
    if rf2 and os.path.exists(rf2):
        mostrar_imagen_simetrica(rf2, 300)
        if st.button("🗑️ Eliminar Foto 2", key="btn_del_f2"): eliminar_imagen("foto2")
    else:
        uf2 = st.file_uploader("Cargar Foto 2", type=['png', 'jpg', 'jpeg'], key="up_foto2", label_visibility="collapsed")
        if uf2: manejar_subida_imagen(uf2, "foto2")

# 6. POBLACIÓN
st.markdown('<div class="form-header">POBLACIÓN</div>', unsafe_allow_html=True)
cp1, cp2, cp3 = st.columns(3)
with cp1: st.number_input("POBLACIÓN DE REFERENCIA:", min_value=0, step=1, format="%d", value=int(zona_data.get('poblacion_referencia', 0)), key="temp_poblacion_referencia", on_change=update_field, args=("poblacion_referencia",))
with cp2: st.number_input("POBLACIÓN AFECTADA:", min_value=0, step=1, format="%d", value=int(zona_data.get('poblacion_afectada', 0)), key="temp_poblacion_afectada", on_change=update_field, args=("poblacion_afectada",))
with cp3: st.number_input("POBLACIÓN OBJETIVO:", min_value=0, step=1, format="%d", value=int(zona_data.get('poblacion_objetivo', 0)), key="temp_poblacion_objetivo", on_change=update_field, args=("poblacion_objetivo",))
