import streamlit as st
import os
from session_state import inicializar_session

# 1. Asegurar persistencia (sin conectar datos externos aún)
inicializar_session()

# --- DISEÑO DE ALTO IMPACTO (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Estilo base de las tarjetas */
    .card-mml {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Contenido de los datos alineado verticalmente */
    .col-content {
        font-size: 0.95rem;
        color: #334155;
        text-align: left; /* Alineado a la izquierda para mejor lectura narrativa */
        line-height: 1.4;
        display: flex;
        align-items: center;
    }

    /* Encabezado global de la tabla */
    .header-global {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 0.85rem;
        text-transform: uppercase;
        text-align: center;
        border-bottom: 2px solid #1E3A8A;
        padding-bottom: 10px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: row;
        gap: 15px;
    }

    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    
    /* Etiquetas de nivel (Badges) */
    .tipo-badge {
        color: white;
        padding: 8px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        text-align: center;
        display: inline-block;
        width: 100%; /* Para que el óvalo ocupe el ancho de su columna */
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON IMAGEN Y AVANCE ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Revisión de la estructura operativa y coherencia del proyecto.</div>', unsafe_allow_html=True)
    st.progress(0.60)
    
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- CONFIGURACIÓN DE COLORES POR NIVEL ---
CONFIG_NIVELES = {
    "OBJETIVO GENERAL":       {"color": "#4338CA", "bg": "#EEF2FF"}, # Índigo
    "OBJETIVO ESPECÍFICO":    {"color": "#2563EB", "bg": "#EFF6FF"}, # Azul
    "COMPONENTE / PRODUCTO":  {"color": "#059669", "bg": "#ECFDF5"}, # Verde
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}  # Ámbar
}

# --- DATOS DE PRUEBA (SOLO PARA REVISIÓN DE DISEÑO) ---
datos_ejemplo = [
    {
        "tipo": "OBJETIVO GENERAL", 
        "objetivo": "AQUÍ APARECERÁ EL OBJETIVO GENERAL", 
        "indicador": "INDICADOR DE FIN", 
        "meta": "META", 
        "supuesto": "SUPUESTO DE CONTEXTO"
    },
    {
        "tipo": "OBJETIVO ESPECÍFICO", 
        "objetivo": "AQUÍ APARECERÁ EL OBJETIVO ESPECÍFICO DE LA HOJA 7", 
        "indicador": "INDICADOR AUTOMÁTICO DE LA HOJA 11", 
        "meta": "META DILIGENCIADA", 
        "supuesto": "SUPUESTO DE LA HOJA 12"
    },
    {
        "tipo": "COMPONENTE / PRODUCTO", 
        "objetivo": "AQUÍ APARECERÁN LOS PRODUCTOS", 
        "indicador": "INDICADOR DE PRODUCTO", 
        "meta": "CANTIDAD", 
        "supuesto": "CONDICIÓN EXTERNA"
    },
    {
        "tipo": "ACTIVIDAD", 
        "objetivo": "AQUÍ APARECERÁN LAS ACCIONES", 
        "indicador": "PRESUPUESTO ASIGNADO", 
        "meta": "MEDIDA", 
        "supuesto": "RECURSOS DISPONIBLES"
    }
]

# --- ENCABEZADO GLOBAL DE LA TABLA ---
st.markdown("""
    <div class="header-global">
        <div style="flex: 1.2;">NIVEL</div>
        <div style="flex: 2;">RESUMEN NARRATIVO</div>
        <div style="flex: 1.5;">INDICADOR</div>
        <div style="flex: 1;">META</div>
        <div style="flex: 1.5;">SUPUESTOS</div>
    </div>
""", unsafe_allow_html=True)

# --- RENDERIZADO DE LA MATRIZ (FILAS) ---
for fila in datos_ejemplo:
    conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#64748b", "bg": "#f8fafc"})
    
    st.markdown(f"""
        <div class="card-mml" style="border-left: 6px solid {conf['color']}; background-color: {conf['bg']};">
            <div style="display: flex; flex-direction: row; gap: 15px; align-items: center;">
                <div style="flex: 1.2;">
                    <div class="tipo-badge" style="background-color: {conf['color']};">{fila['tipo']}</div>
                </div>
                <div style="flex: 2;" class="col-content"><b>{fila['objetivo']}</b></div>
                <div style="flex: 1.5;" class="col-content">{fila['indicador']}</div>
                <div style="flex: 1;" class="col-content text-center">{fila['meta']}</div>
                <div style="flex: 1.5;" class="col-content">{fila['supuesto']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()
st.info("ℹ️ Esta es la vista previa del diseño con el formato de tabla matricial horizontal.")
