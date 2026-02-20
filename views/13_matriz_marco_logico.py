import streamlit as st
import os
import graphviz
import textwrap
from session_state import inicializar_session

# 1. Asegurar persistencia
inicializar_session()

# --- DISEÑO DE PANTALLA (CSS) ---
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

# --- CONFIGURACIÓN DE NIVELES ---
CONFIG_NIVELES = {
    "PROPÓSITO / ESPECÍFICO": {"color": "#2563EB", "bg": "#EFF6FF"},
    "COMPONENTE / PRODUCTO":  {"color": "#059669", "bg": "#ECFDF5"},
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}
}

# --- DATOS DE PRUEBA ---
datos_ejemplo = [
    {"tipo": "PROPÓSITO / ESPECÍFICO", "objetivo": "Objetivo Específico de prueba para validación", "indicador": "Indicador de Propósito", "meta": "100%", "supuesto": "Participación comunitaria"},
    {"tipo": "COMPONENTE / PRODUCTO", "objetivo": "Producto o Medios Directos generados", "indicador": "Indicador de Producto", "meta": "500 unidades", "supuesto": "Proveedores a tiempo"},
    {"tipo": "ACTIVIDAD", "objetivo": "Acciones y Medios Indirectos ejecutados", "indicador": "Presupuesto", "meta": "$100.000.000", "supuesto": "Recursos disponibles"}
]

# --- FUNCIÓN DE EXPORTACIÓN ESTÉTICA ---
def generar_png_estetico(datos):
    """Genera una imagen que imita visualmente las tarjetas de la interfaz."""
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB', nodesep='0.3', ranksep='0.2', bgcolor='white', fontname='Arial')
    
    for i, fila in enumerate(datos):
        conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#1E3A8A", "bg": "#f8fafc"})
        
        # Función para ajustar texto en la imagen
        def wrap(t, w=25): return "<BR/>".join(textwrap.wrap(str(t), width=w))

        # El diseño usa una tabla maestra para el borde izquierdo y otra para el contenido
        label = f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
            <TR>
                <TD WIDTH="10" BGCOLOR="{conf['color']}"></TD>
                <TD BGCOLOR="{conf['bg']}">
                    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="10" CELLPADDING="5">
                        <TR>
                            <TD COLSPAN="4" ALIGN="LEFT">
                                <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5">
                                    <TR><TD BGCOLOR="{conf['color']}" PORT="header"><FONT COLOR="white" POINT-SIZE="10"><B>  {fila['tipo']}  </B></FONT></TD></TR>
                                </TABLE>
                            </TD>
                        </TR>
                        <TR>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>🎯 OBJETIVO</B></FONT></TD>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>📊 INDICADOR</B></FONT></TD>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>🏁 META</B></FONT></TD>
                            <TD><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>🛡️ SUPUESTOS</B></FONT></TD>
                        </TR>
                        <TR>
                            <TD WIDTH="180" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['objetivo'])}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['indicador'], 20)}</FONT></TD>
                            <TD WIDTH="80" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['meta'], 12)}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['supuesto'], 20)}</FONT></TD>
                        </TR>
                    </TABLE>
                </TD>
            </TR>
        </TABLE>>'''
        
        # Creamos el nodo con estilo de tarjeta
        dot.node(f'card_{i}', label=label, shape='rect', style='filled', fillcolor='white', color='#e2e8f0', penwidth='2')
        
        if i > 0:
            dot.edge(f'card_{i-1}', f'card_{i}', style='invis')
            
    return dot.pipe(format='png')

# --- PANEL LATERAL ---
with st.sidebar:
    # Botón de descarga con el nuevo diseño
    imagen_estetica = generar_png_estetico(datos_ejemplo)
    st.download_button(
        label="🖼️ Descargar Matriz (PNG)",
        data=imagen_estetica,
        file_name="MML_Visual.png",
        mime="image/png",
        use_container_width=True
    )

# --- CUERPO DE LA PÁGINA ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Validación.</div>', unsafe_allow_html=True)
    st.progress(0.60)
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- RENDERIZADO EN PANTALLA ---
for fila in datos_ejemplo:
    conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#64748b", "bg": "#f8fafc"})
    st.markdown(f"""
        <div class="card-mml" style="border-left: 10px solid {conf['color']}; background-color: {conf['bg']};">
            <div class="tipo-badge" style="background-color: {conf['color']};">
                {fila['tipo']}
            </div>
            <div style="display: flex; flex-direction: row; gap: 15px;">
                <div style="flex: 2;"><div class="col-title" style="color: {conf['color']};">🎯 Objetivo</div><div class="col-content">{fila['objetivo']}</div></div>
                <div style="flex: 1.5;"><div class="col-title" style="color: {conf['color']};">📊 Indicador</div><div class="col-content">{fila['indicador']}</div></div>
                <div style="flex: 1;"><div class="col-title" style="color: {conf['color']};">🏁 Meta</div><div class="col-content">{fila['meta']}</div></div>
                <div style="flex: 1.5;"><div class="col-title" style="color: {conf['color']};">🛡️ Supuestos</div><div class="col-content">{fila['supuesto']}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()
