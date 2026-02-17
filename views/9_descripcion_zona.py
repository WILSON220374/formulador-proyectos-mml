import streamlit as st
import os
import uuid
import base64
from PIL import Image
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- BLOQUE DE BÚSQUEDA AUTOMÁTICA (SIN BOTÓN) ---
if 'descripcion_zona' not in st.session_state:
    st.session_state['descripcion_zona'] = {
        "problema_central": "", "departamento": "", "provincia": "", "municipio": "", 
        "barrio_vereda": "", "latitud": "", "longitud": "",
        "limites_geograficos": "", "limites_administrativos": "", "otros_limites": "",
        "accesibilidad": "", "ruta_mapa": None, "ruta_foto1": None, "ruta_foto2": None,
        "pie_mapa": "", "pie_foto1": "", "pie_foto2": "",
        "poblacion_referencia": 0, "poblacion_afectada": 0, "poblacion_objetivo": 0
    }

# Lógica de importación automática: Si el campo está vacío, lo trae de Hoja 8
if not st.session_state['descripcion_zona'].get('problema_central'):
    # Intento 1: Buscar en la tabla sincronizada de la Hoja 8
    prob_fuente = st.session_state.get('arbol_problemas_final', {}).get('referencia_manual_prob', {}).get('problema_central', "")
    
    # Intento 2: Si la tabla no se sincronizó, buscar directo en la tarjeta del árbol
    if not prob_fuente:
        pp_cards = st.session_state.get('arbol_problemas_final', {}).get('Problema Principal', [])
        if pp_cards and len(pp_cards) > 0:
            prob_fuente = pp_cards[0].get('texto', "")
    
    if prob_fuente:
        st.session_state['descripcion_zona']['problema_central'] = prob_fuente
        guardar_datos_nube()

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
    .main .stButton button {
        border: 1px solid #ef4444 !important; background: transparent !important;
        color: #ef4444 !important; font-size: 0.9rem !important; margin-top: 5px !important; width: 100%;
    }
    .sub-header { font-weight: 700; color: #1E3A8A; margin-bottom: 5px; display: block; }
    </style>
""", unsafe_allow_html=True)

def calc_altura(texto):
    if not texto: return 100
    return max(80, (str(texto).count('\n') + (len(str(texto)) // 90) + 1) * 25)

def mostrar_imagen_simetrica(ruta_imagen, altura_px):
    if not ruta_imagen or not os.path.exists(ruta_imagen): return
    with open(ruta_imagen, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f'<div style="width: 100%; height: {altura_px}px; overflow: hidden; border-radius: 8px; border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 5px;"><img src="data:image/jpeg;base64,{data}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;"></div>', unsafe_allow_html=True)

def update_field(key):
    temp_key = f"temp_{key}"
    if temp_key in st.session_state:
        st.session_state['descripcion_zona'][key] = st.session_state[temp_key]
        guardar_datos_nube()

# --- ENCABEZADO CON BARRA DE PROGRESO ---
col_t, col_img_head = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🗺️ 9. DESCRIPCIÓN GENERAL DE LA ZONA DE ESTUDIO</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Caracterización de límites, accesibilidad y población.</div>', unsafe_allow_html=True)
    
    campos = [zona_data.get('problema_central'), zona_data.get('departamento'), zona_data.get('municipio'), zona_data.get('ruta_mapa')]
    llenados = len([c for c in campos if (isinstance(c, str) and c.strip()) or (c is not None and not isinstance(c, (str, int, float)))])
    st.progress(llenados / len(campos) if campos else 0)

with col_img_head:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- FORMULARIO ---
st.markdown('<div class="form-header">PROBLEMA CENTRAL</div>', unsafe_allow_html=True)
st.text_area("Descripción del Problema Central:", value=st.session_state['descripcion_zona']['problema_central'], key="temp_problema_central", height=calc_altura(st.session_state['descripcion_zona']['problema_central']), on_change=update_field, args=("problema_central",))

st.markdown('<div class="form-header">LOCALIZACIÓN</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: st.text_input("Departamento:", value=zona_data.get('departamento', ''), key="temp_departamento", on_change=update_field, args=("departamento",))
with c2: st.text_input("Provincia:", value=zona_data.get('provincia', ''), key="temp_provincia", on_change=update_field, args=("provincia",))
with c3: st.text_input("Municipio:", value=zona_data.get('municipio', ''), key="temp_municipio", on_change=update_field, args=("municipio",))
with c4: st.text_input("Barrio o Vereda:", value=zona_data.get('barrio_vereda', ''), key="temp_barrio_vereda", on_change=update_field, args=("barrio_vereda",))

st.markdown('<div class="form-header">MAPA Y FOTOS</div>', unsafe_allow_html=True)
ruta_mapa = zona_data.get("ruta_mapa")
if ruta_mapa and os.path.exists(ruta_mapa):
    mostrar_imagen_simetrica(ruta_mapa, 400)
    if st.button("🗑️ Eliminar Mapa", key="del_m"): 
        st.session_state['descripcion_zona']['ruta_mapa'] = None; guardar_datos_nube(); st.rerun()
else:
    up_m = st.file_uploader("Mapa", type=['png','jpg'], key="up_m", label_visibility="collapsed")
    if up_m: 
        path = f"uploads/map_{uuid.uuid4()}.jpg"
        with open(path, "wb") as f: f.write(up_m.getbuffer())
        st.session_state['descripcion_zona']['ruta_mapa'] = path; guardar_datos_nube(); st.rerun()

st.markdown('<div class="form-header">POBLACIÓN</div>', unsafe_allow_html=True)
cx1, cx2, cx3 = st.columns(3)
with cx1: st.number_input("POBLACIÓN DE REFERENCIA:", min_value=0, value=int(zona_data.get('poblacion_referencia', 0)), key="temp_pob_r", on_change=update_field, args=("poblacion_referencia",))
with cx2: st.number_input("POBLACIÓN AFECTADA:", min_value=0, value=int(zona_data.get('poblacion_afectada', 0)), key="temp_pob_a", on_change=update_field, args=("poblacion_afectada",))
with cx3: st.number_input("POBLACIÓN OBJETIVO:", min_value=0, value=int(zona_data.get('poblacion_objetivo', 0)), key="temp_pob_o", on_change=update_field, args=("poblacion_objetivo",))
