import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicializar memoria y configuración
inicializar_session()

# --- ESTILOS CSS (Igualando el diseño de Equipo) ---
st.markdown("""
    <style>
    .titulo-seccion {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #4F8BFF;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    .subtitulo-gris {
        font-size: 16px !important;
        color: #666;
        margin-bottom: 10px;
    }
    /* Estilo para las cajas de texto */
    .stTextArea textarea {
        background-color: #fcfdfe;
        border: 1px solid #e0e7ff;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #4F8BFF;
        box-shadow: 0 0 0 2px rgba(79, 139, 255, 0.1);
    }
    /* Hack para imagen estática y sin fullscreen */
    [data-testid="stImage"] img {
        pointer-events: none;
        user-select: none;
        border-radius: 10px;
    }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    
    /* Contenedores con borde suave */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        border: 1px solid #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA INTEGRADA (Mejor distribución) ---
# Usamos [4, 1] para que el logo tenga su espacio pero no se aleje tanto
col_titulo, col_logo = st.columns([4, 1], gap="medium", vertical_alignment="center")

with col_titulo:
    st.markdown('<div class="titulo-seccion">🎯 1. Diagnóstico del Problema</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Defina la situación negativa central y sus evidencias.</div>', unsafe_allow_html=True)
    
    # --- CÁLCULO DE PROGRESO INTEGRADO AL TÍTULO ---
    datos = st.session_state['datos_problema']
    # Aseguramos que los campos existan antes de calcular
    c_p = datos.get('problema_central', '')
    c_s = datos.get('sintomas', '')
    c_c = datos.get('causas_inmediatas', '')
    c_a = datos.get('factores_agravantes', '')
    
    campos = [c_p, c_s, c_c, c_a]
    completos = sum(1 for c in campos if c and len(str(c).strip()) > 10)
    progreso = completos / 4
    
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_logo:
    # Verificamos ambas opciones de nombre por seguridad
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- FUNCIÓN DE AUTO-AJUSTE DE ALTURA (MANTENIDA) ---
def calcular_altura(texto, min_h=150):
    if not texto: return min_h
    # Ajuste ligero al cálculo para que no sea tan alto tan rápido
    lineas = str(texto).count('\n') + (len(str(texto)) // 90)
    return max(min_h, (lineas + 1) * 24)

# --- SECCIÓN 1: EL PROBLEMA CENTRAL ---
with st.container(border=True):
    st.markdown("### 🚨 El Problema Central")
    st.caption("Describa claramente la situación negativa (No la falta de una solución).")
    
    val_problema = datos.get('problema_central', '')
    h_p = calcular_altura(val_problema)
    
    p_central = st.text_area(
        "Descripción", value=val_problema, height=h_p,
        key="txt_p_central", label_visibility="collapsed",
        placeholder="Ej: Aumento de la accidentalidad en la vía Sogamoso..."
    )

st.write("") # Espaciador

# --- SECCIÓN 2: ANÁLISIS (2 COLUMNAS) ---
c1, c2 = st.columns(2, gap="large")

with c1:
    with st.container(border=True):
        st.markdown("### 📉 Síntomas (Efectos)")
        st.caption("¿Qué evidencia demuestra que el problema existe?")
        
        val_sintomas = datos.get('sintomas', '')
        h_s = calcular_altura(val_sintomas)
        
        sintomas = st.text_area(
            "S", value=val_sintomas, height=h_s, 
            key="txt_sintomas", label_visibility="collapsed",
            placeholder="Ej: Quejas constantes, deterioro físico visible..."
        )

    # Colocamos Factores Agravantes aquí abajo para equilibrar si prefieres
    # O mantenemos tu estructura original de 2 columnas + 1 abajo.
    # Vamos a mantener tu estructura original (Causas a la derecha)

with c2:
    with st.container(border=True):
        st.markdown("### 🛠️ Causas Inmediatas")
        st.caption("¿Por qué está ocurriendo esto ahora?")
        
        val_causas = datos.get('causas_inmediatas', '')
        h_c = calcular_altura(val_causas)
        
        causas = st.text_area(
            "C", value=val_causas, height=h_c, 
            key="txt_causas", label_visibility="collapsed",
            placeholder="Ej: Falta de mantenimiento, diseño inadecuado..."
        )

st.write("") 

# --- SECCIÓN 3: FACTORES AGRAVANTES ---
with st.container(border=True):
    st.markdown("### ⚠️ Factores Agravantes")
    st.caption("Elementos externos o contextos que empeoran la situación.")
    
    val_agravantes = datos.get('factores_agravantes', '')
    h_a = calcular_altura(val_agravantes)
    
    agravantes = st.text_area(
        "A", value=val_agravantes, height=h_a, 
        key="txt_agravantes", label_visibility="collapsed",
        placeholder="Ej: Temporada de lluvias, recortes presupuestales..."
    )

# --- LÓGICA DE GUARDADO AUTOMÁTICO (MANTENIDA) ---
# Comparamos los valores actuales con los de sesión para detectar cambios
if (p_central != datos.get('problema_central') or 
    sintomas != datos.get('sintomas') or 
    causas != datos.get('causas_inmediatas') or 
    agravantes != datos.get('factores_agravantes')):
    
    st.session_state['datos_problema'] = {
        "problema_central": p_central, 
        "sintomas": sintomas,
        "causas_inmediatas": causas, 
        "factores_agravantes": agravantes
    }
    guardar_datos_nube()
    st.rerun()
