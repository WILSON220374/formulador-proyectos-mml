import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- CONFIGURACIÓN DE LA MATRIZ ---
if 'matriz_marco_logico' not in st.session_state:
    st.session_state['matriz_marco_logico'] = {
        "fin": {"resumen": "", "indicadores": "", "medios": "", "supuestos": ""},
        "proposito": {"resumen": "", "indicadores": "", "medios": "", "supuestos": ""},
        "componentes": {"resumen": "", "indicadores": "", "medios": "", "supuestos": ""},
        "actividades": {"resumen": "", "indicadores": "", "medios": "", "supuestos": ""}
    }

mml = st.session_state['matriz_marco_logico']

# --- SINCRONIZACIÓN AUTOMÁTICA CON HOJA 7 Y 8 ---
def sincronizar_mml():
    # 1. Traer datos de Hoja 7 (Objetivos)
    obj_data = st.session_state.get('arbol_objetivos_final', {}).get('referencia_manual', {})
    
    # Propósito (Objetivo General)
    if not mml['proposito']['resumen']:
        mml['proposito']['resumen'] = obj_data.get('objetivo', "")
    
    # Componentes (Objetivos Específicos)
    if not mml['componentes']['resumen']:
        especificos = obj_data.get('especificos', [])
        mml['componentes']['resumen'] = "\n".join([f"• {item}" for item in especificos])
    
    # Actividades
    if not mml['actividades']['resumen']:
        actividades = obj_data.get('actividades', [])
        mml['actividades']['resumen'] = "\n".join([f"• {item}" for item in actividades])
    
    # 2. Traer Fin (De los Fines Directos del Árbol de Hoja 7)
    if not mml['fin']['resumen']:
        fines = st.session_state.get('arbol_objetivos_final', {}).get('Fines Directos', [])
        if fines:
            mml['fin']['resumen'] = "\n".join([f"• {f.get('texto', '')}" for f in fines if f.get('texto')])

# Ejecutar sincronización al cargar
sincronizar_mml()

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    .mml-header {
        background-color: #1E3A8A; color: white; font-weight: bold; text-align: center;
        padding: 10px; border-radius: 5px; margin-bottom: 10px; font-size: 0.9rem;
    }
    .mml-row-label {
        background-color: #f1f5f9; color: #1E3A8A; font-weight: 800;
        padding: 10px; border-radius: 5px; height: 100%; display: flex; align-items: center;
        border-left: 5px solid #1E3A8A; font-size: 0.85rem;
    }
    .stTextArea textarea { font-size: 0.85rem !important; }
    .btn-save button {
        background-color: #10B981 !important; color: white !important;
        font-weight: bold !important; border: none !important; padding: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 10. MATRIZ DE MARCO LÓGICO (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Resumen narrativo y estructura de seguimiento del proyecto.</div>', unsafe_allow_html=True)

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- ESTRUCTURA DE LA MATRIZ ---
def render_mml_row(label, key_row):
    st.markdown(f"### {label}")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown('<div class="mml-header">Resumen Narrativo</div>', unsafe_allow_html=True)
        mml[key_row]['resumen'] = st.text_area("R", value=mml[key_row]['resumen'], key=f"res_{key_row}", label_visibility="collapsed", height=150)
    
    with c2:
        st.markdown('<div class="mml-header">Indicadores</div>', unsafe_allow_html=True)
        mml[key_row]['indicadores'] = st.text_area("I", value=mml[key_row]['indicadores'], key=f"ind_{key_row}", label_visibility="collapsed", height=150)
    
    with c3:
        st.markdown('<div class="mml-header">Medios de Verificación</div>', unsafe_allow_html=True)
        mml[key_row]['medios'] = st.text_area("M", value=mml[key_row]['medios'], key=f"med_{key_row}", label_visibility="collapsed", height=150)
    
    with c4:
        st.markdown('<div class="mml-header">Supuestos</div>', unsafe_allow_html=True)
        mml[key_row]['supuestos'] = st.text_area("S", value=mml[key_row]['supuestos'], key=f"sup_{key_row}", label_visibility="collapsed", height=150)
    st.markdown("---")

# Renderizar las 4 filas reglamentarias
render_mml_row("🟢 FIN (Impacto)", "fin")
render_mml_row("🔵 PROPÓSITO (Objetivo General)", "proposito")
render_mml_row("🟡 COMPONENTES (Entregables)", "componentes")
render_mml_row("🟠 ACTIVIDADES", "actividades")

# --- BOTÓN DE GUARDADO FINAL ---
st.write("")
col_save, _ = st.columns([0.4, 0.6])
with col_save:
    st.markdown('<div class="btn-save">', unsafe_allow_html=True)
    if st.button("💾 GUARDAR CAMBIOS EN LA NUBE", use_container_width=True):
        guardar_datos_nube()
        st.success("✅ ¡Matriz guardada con éxito en tu base de datos!")
    st.markdown('</div>', unsafe_allow_html=True)

st.info("💡 Consejo: El Resumen Narrativo se ha cargado automáticamente de tus árboles. Puedes editarlo aquí si necesitas ajustar la redacción final.")
