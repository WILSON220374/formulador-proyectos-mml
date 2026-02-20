import streamlit as st
import os
import graphviz
from session_state import inicializar_session

# 1. Asegurar persistencia
inicializar_session()

# --- DISEÑO DE ALTO IMPACTO (CSS CUSTOM) ---
st.markdown("""
    <style>
    .card-mml {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
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
    .col-content {
        font-size: 0.95rem;
        color: #334155;
        text-align: center;
        line-height: 1.5;
        padding: 5px;
    }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
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

# --- CONFIGURACIÓN DE NIVELES Y COLORES ---
CONFIG_NIVELES = {
    "PROPÓSITO / ESPECÍFICO": {"color": "#2563EB", "bg": "#EFF6FF"},
    "COMPONENTE / PRODUCTO":  {"color": "#059669", "bg": "#ECFDF5"},
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}
}

# --- DATOS DE PRUEBA (SOLO PARA DISEÑO) ---
datos_ejemplo = [
    {"tipo": "PROPÓSITO / ESPECÍFICO", "objetivo": "Objetivo Específico de prueba", "indicador": "Indicador de Propósito", "meta": "100%", "supuesto": "Participación comunitaria"},
    {"tipo": "COMPONENTE / PRODUCTO", "objetivo": "Producto o Medios Directos", "indicador": "Indicador de Producto", "meta": "500 unidades", "supuesto": "Proveedores a tiempo"},
    {"tipo": "ACTIVIDAD", "objetivo": "Acciones y Medios Indirectos", "indicador": "Presupuesto", "meta": "$100.000.000", "supuesto": "Recursos disponibles"}
]

# --- FUNCIÓN PARA GENERAR EL PNG ---
def generar_png_mml(datos):
    """Crea una versión de imagen de la matriz usando Graphviz."""
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB', nodesep='0.1', ranksep='0.1')
    
    # Estilo de tabla HTML dentro de Graphviz
    for i, fila in enumerate(datos):
        conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#1E3A8A"})
        # Creamos una etiqueta HTML para el nodo
        label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="10" BGCOLOR="white">
            <TR><TD COLSPAN="4" BGCOLOR="{conf['color']}"><FONT COLOR="white"><B>{fila['tipo']}</B></FONT></TD></TR>
            <TR>
                <TD BGCOLOR="#f1f5f9"><B>OBJETIVO</B></TD>
                <TD BGCOLOR="#f1f5f9"><B>INDICADOR</B></TD>
                <TD BGCOLOR="#f1f5f9"><B>META</B></TD>
                <TD BGCOLOR="#f1f5f9"><B>SUPUESTOS</B></TD>
            </TR>
            <TR>
                <TD WIDTH="200">{fila['objetivo']}</TD>
                <TD WIDTH="150">{fila['indicador']}</TD>
                <TD WIDTH="100">{fila['meta']}</TD>
                <TD WIDTH="150">{fila['supuesto']}</TD>
            </TR>
        </TABLE>>'''
        dot.node(f'node{i}', label=label, shape='plaintext')
    
    return dot.pipe(format='png')

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Exportación")
    st.write("Descarga la matriz en formato de imagen para tus informes.")
    
    # Botón de descarga
    imagen_png = generar_png_mml(datos_ejemplo)
    st.download_button(
        label="🖼️ Descargar Matriz como PNG",
        data=imagen_png,
        file_name="matriz_marco_logico.png",
        mime="image/png",
        use_container_width=True
    )
    st.divider()

# --- ENCABEZADO PRINCIPAL ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Estructura validada del proyecto.</div>', unsafe_allow_html=True)
    st.progress(0.60)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- RENDERIZADO DE LAS TARJETAS (VISTA PREVIA) ---
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
