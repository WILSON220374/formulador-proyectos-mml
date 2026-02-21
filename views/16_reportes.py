import streamlit as st
import os
from session_state import inicializar_session

# 1. Asegurar persistencia 
inicializar_session()

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 12rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    .header-tabla { font-weight: 800; color: #1E3A8A; margin-bottom: 10px; font-size: 1.1rem; text-transform: uppercase; border-bottom: 2px solid #1E3A8A; padding-bottom: 5px;}
    
    .card-opciones {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
    }
    .titulo-card {
        font-weight: 700;
        color: #334155;
        font-size: 1.05rem;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO Y AVANCE ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📄 16. Generador de Reportes</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Selecciona los componentes del proyecto que deseas incluir en tu documento final.</div>', unsafe_allow_html=True)
    st.progress(1.0) # Aquí ya estamos al 100% del uso de la herramienta
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- SECCIÓN 1: CONFIGURACIÓN DEL DOCUMENTO ---
st.markdown('<div class="header-tabla">⚙️ 1. Configuración de Portada</div>', unsafe_allow_html=True)
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    autor = st.text_input("Autor / Formulador", placeholder="Ej: Juan Pérez")
with col_c2:
    entidad = st.text_input("Entidad / Organización", placeholder="Ej: Alcaldía Municipal")
with col_c3:
    fecha_doc = st.date_input("Fecha del Documento")

st.divider()

# --- SECCIÓN 2: SELECCIÓN DE CONTENIDO ---
st.markdown('<div class="header-tabla">📑 2. Contenido a Exportar</div>', unsafe_allow_html=True)
st.write("Marca las casillas de los elementos que deseas compilar en el documento:")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card-opciones">', unsafe_allow_html=True)
    st.markdown('<div class="titulo-card">🔍 Identificación y Problema</div>', unsafe_allow_html=True)
    chk_participantes = st.checkbox("1. Análisis de Participantes", value=True)
    chk_problema = st.checkbox("2. Árbol de Problemas", value=True)
    chk_objetivos = st.checkbox("3. Árbol de Objetivos", value=True)
    chk_alternativas = st.checkbox("4. Análisis de Alternativas", value=False)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("") # Espaciador
    
    st.markdown('<div class="card-opciones">', unsafe_allow_html=True)
    st.markdown('<div class="titulo-card">📐 Estructuración y Riesgos</div>', unsafe_allow_html=True)
    chk_estudios = st.checkbox("5. Resumen de Estudios (Técnico, Legal, etc.)", value=False)
    chk_riesgos = st.checkbox("6. Matriz de Riesgos", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card-opciones">', unsafe_allow_html=True)
    st.markdown('<div class="titulo-card">📊 Marco Lógico y Metas</div>', unsafe_allow_html=True)
    chk_indicadores = st.checkbox("7. Fichas de Indicadores", value=False)
    chk_mml = st.checkbox("8. Matriz de Marco Lógico (MML)", value=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("") # Espaciador
    
    st.markdown('<div class="card-opciones">', unsafe_allow_html=True)
    st.markdown('<div class="titulo-card">📦 Producto y Necesidad</div>', unsafe_allow_html=True)
    chk_necesidad = st.checkbox("9. Análisis de Necesidad y Déficit", value=True)
    chk_producto = st.checkbox("10. Ficha de Producto y Proyecto", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- SECCIÓN 3: BOTONES DE EXPORTACIÓN ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)
st.info("💡 Haz clic en el formato deseado. El sistema recopilará la información guardada y generará el archivo.")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn1:
    # Botón visual (aún sin lógica)
    st.button("📝 Descargar en Word (.docx)", type="primary", use_container_width=True)

with col_btn2:
    # Botón visual (aún sin lógica)
    st.button("📄 Descargar en PDF (.pdf)", type="secondary", use_container_width=True)
