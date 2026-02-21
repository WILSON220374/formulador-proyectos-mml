import streamlit as st
import os

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 12rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    .header-tabla { font-weight: 800; color: #1E3A8A; margin-bottom: 10px; font-size: 1.1rem; text-transform: uppercase; border-bottom: 2px solid #1E3A8A; padding-bottom: 5px;}
    .readonly-box { border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background-color: #f3f4f6; color: #374151; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📄 16. Generador de Reportes</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Configuración visual del documento final (Maqueta sin conexión a datos).</div>', unsafe_allow_html=True)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- 1. CONFIGURACIÓN DE PORTADA (MAQUETA) ---
st.markdown('<div class="header-tabla">⚙️ 1. Configuración de Portada</div>', unsafe_allow_html=True)

st.write("**Autores / Formuladores (Se extraerán de la Hoja 1 automáticamente):**")
# Caja visual de ejemplo
st.markdown('<div class="readonly-box">Ejemplo: Juan Pérez, María Gómez, Carlos Ramírez</div><br>', unsafe_allow_html=True)

st.divider()

# --- 2. MENÚ DE SELECCIÓN (MAQUETA) ---
st.markdown('<div class="header-tabla">📑 2. Selección de Contenido</div>', unsafe_allow_html=True)
st.write("Selecciona qué secciones deseas incluir en tu documento final:")

# Bloque visual para Diagnóstico
with st.container(border=True):
    st.markdown("**Hoja: Diagnóstico (Árbol de Problemas)**")
    st.checkbox("El Problema Central", value=True, key="mock_prob")
    st.checkbox("Síntomas (Efectos)", value=True, key="mock_sint")
    st.checkbox("Causas Inmediatas", value=True, key="mock_caus")

# Un espacio para que veas cómo se verían otras hojas a futuro
with st.expander("Ver otras secciones de la aplicación (Próximamente)..."):
    st.write("Aquí se irán agregando las opciones para Matriz de Marco Lógico, Alternativas, Necesidad, Producto, etc.")

st.divider()

# --- 3. BOTONES DE DESCARGA (VISUALES) ---
st.markdown('<div class="header-tabla">📥 3. Generar Documento</div>', unsafe_allow_html=True)
st.info("💡 Estos botones son de prueba, aún no generan el archivo real.")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # Botón visual simple (sin función de descarga)
    st.button("📝 Descargar Word (.docx)", type="primary", use_container_width=True)

with col_btn2:
    # Botón visual simple (sin función de descarga)
    st.button("📄 Descargar PDF (.pdf)", type="primary", use_container_width=True)
