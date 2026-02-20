import streamlit as st
import os
from session_state import inicializar_session

# 1. Asegurar persistencia
inicializar_session()

# --- DISEÑO DE ALTO IMPACTO (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Estilo base de las tarjetas */
    .card-mml {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Títulos de columnas */
    .col-title {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 0.85rem;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 8px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 5px;
    }
    
    /* Contenido de los datos */
    .col-content {
        font-size: 0.95rem;
        color: #334155;
        text-align: center;
        line-height: 1.5;
        padding: 5px;
    }

    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Estilo base de los badges */
    .tipo-badge {
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON IMAGEN ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Validación de la coherencia operativa por niveles.</div>', unsafe_allow_html=True)
    
    # Barra de avance
    st.progress(0.60)
    st.caption("Progreso de validación: 60%")

with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- MAPEO DE COLORES POR NIVEL ---
# Definimos colores únicos para identificar cada nivel rápidamente
CONFIG_NIVELES = {
    "PROPÓSITO / ESPECÍFICO": {"color": "#2563EB", "bg": "#EFF6FF"}, # Azul vibrante
    "COMPONENTE / PRODUCTO":  {"color": "#059669", "bg": "#ECFDF5"}, # Esmeralda
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}  # Ámbar
}

# --- DATOS DE EJEMPLO (SIN LA FILA DE FIN) ---
datos_ejemplo = [
    {"tipo": "PROPÓSITO / ESPECÍFICO", "objetivo": "Resultado directo que se espera lograr con el proyecto", "indicador": "Indicador de Propósito", "meta": "100%", "supuesto": "La comunidad participa activamente"},
    {"tipo": "COMPONENTE / PRODUCTO", "objetivo": "Bienes o servicios producidos por el proyecto", "indicador": "Número de servicios entregados", "meta": "500 unidades", "supuesto": "Proveedores cumplen tiempos"},
    {"tipo": "ACTIVIDAD", "objetivo": "Acciones necesarias para generar los productos", "indicador": "Presupuesto ejecutado", "meta": "$100.000.000", "supuesto": "Recursos disponibles oportunamente"}
]

# --- RENDERIZADO DE BLOQUES DINÁMICOS ---
for fila in datos_ejemplo:
    conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#64748b", "bg": "#f8fafc"})
    
    st.markdown(f"""
        <div class="card-mml" style="border-left: 10px solid {conf['color']}; background-color: {conf['bg']};">
            <div class="tipo-badge" style="background-color: {conf['color']};">
                {fila['tipo']}
            </div>
            <div style="display: flex; flex-direction: row; gap: 15px;">
                <div style="flex: 2;">
                    <div class="col-title" style="color: {conf['color']}; border-bottom-color: {conf['color']}33;">🎯 Objetivo</div>
                    <div class="col-content">{fila['objetivo']}</div>
                </div>
                <div style="flex: 1.5;">
                    <div class="col-title" style="color: {conf['color']}; border-bottom-color: {conf['color']}33;">📊 Indicador</div>
                    <div class="col-content">{fila['indicador']}</div>
                </div>
                <div style="flex: 1;">
                    <div class="col-title" style="color: {conf['color']}; border-bottom-color: {conf['color']}33;">🏁 Meta</div>
                    <div class="col-content">{fila['meta']}</div>
                </div>
                <div style="flex: 1.5;">
                    <div class="col-title" style="color: {conf['color']}; border-bottom-color: {conf['color']}33;">🛡️ Supuestos</div>
                    <div class="col-content">{fila['supuesto']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()
