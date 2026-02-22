import streamlit as st
import os
import pandas as pd
import graphviz
import textwrap
import html
from session_state import inicializar_session

# 1. Asegurar persistencia 
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
        text-align: left;
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
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE COLORES POR NIVEL ---
CONFIG_NIVELES = {
    "OBJETIVO GENERAL":       {"color": "#4338CA", "bg": "#EEF2FF"}, # Índigo
    "OBJETIVO ESPECÍFICO":    {"color": "#2563EB", "bg": "#EFF6FF"}, # Azul
    "ACTIVIDAD":              {"color": "#D97706", "bg": "#FFFBEB"}  # Ámbar
}

# --- EXTRACCIÓN DE DATOS REALES (MÉTODO DINÁMICO HOJA 11) ---
mapa = st.session_state.get("indicadores_mapa_objetivo", {})
datos_ind = st.session_state.get("datos_indicadores", {})
seleccion = st.session_state.get("seleccion_indicadores", {})
metas = st.session_state.get("meta_resultados_parciales", {})
riesgos_df = st.session_state.get("datos_riesgos", pd.DataFrame())

if isinstance(riesgos_df, pd.DataFrame) and not riesgos_df.empty:
    riesgos = riesgos_df.to_dict(orient="records")
else:
    riesgos = []

datos_reales = []

for kmap, k in mapa.items():
    partes = kmap.split("||")
    if len(partes) != 2:
        continue
        
    nivel_original = partes[0]
    objetivo_texto = partes[1]
    
    sel = seleccion.get(k, {})
    p_cols = ["P1", "P2", "P3", "P4", "P5"]
    is_selected = True if isinstance(sel, dict) and all(bool(sel.get(p, False)) for p in p_cols) else False
    
    if not is_selected:
        continue 
        
    ind_data = datos_ind.get(k, {})
    indicador_texto = str(ind_data.get("Indicador", "")).strip()
    
    meta_data = metas.get(k, {})
    meta_texto = str(meta_data.get("Meta", "")).strip()
    
    tipo_mml = "OBJETIVO ESPECÍFICO" 
    if "General" in nivel_original or "Fin" in nivel_original:
        tipo_mml = "OBJETIVO GENERAL"
    elif "Espec" in nivel_original or "Componente" in nivel_original or "Propósito" in nivel_original:
        tipo_mml = "OBJETIVO ESPECÍFICO"
    elif "Actividad" in nivel_original:
        tipo_mml = "ACTIVIDAD"
        
    supuesto = "Pendiente"
    for r in riesgos:
        if str(r.get("Objetivo", "")) == objetivo_texto:
            supuesto = str(r.get("Supuesto", "Pendiente"))
            break
            
    datos_reales.append({
        "tipo": tipo_mml,
        "objetivo": objetivo_texto,
        "indicador": indicador_texto,
        "meta": meta_texto,
        "supuesto": supuesto
    })

# --- ORDENAMIENTO JERÁRQUICO ---
orden_jerarquia = {
    "OBJETIVO GENERAL": 1,
    "OBJETIVO ESPECÍFICO": 2,
    "ACTIVIDAD": 3
}
datos_reales = sorted(datos_reales, key=lambda x: orden_jerarquia.get(x["tipo"], 99))

# --- FUNCIÓN DE EXPORTACIÓN ESTÉTICA EN PNG ---
def generar_png_estetico(datos):
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB', nodesep='0.3', ranksep='0.2', bgcolor='white', fontname='Arial')
    
    def wrap(t, w=25):
        # Saneamiento de caracteres especiales para etiquetas HTML de Graphviz
        t = str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        return "<BR/>".join(textwrap.wrap(t, width=w))

    for i, fila in enumerate(datos):
        conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#1E3A8A", "bg": "#f8fafc"})
        
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
                            <TD ALIGN="LEFT"><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>RESUMEN NARRATIVO</B></FONT></TD>
                            <TD ALIGN="CENTER"><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>INDICADOR</B></FONT></TD>
                            <TD ALIGN="CENTER"><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>META</B></FONT></TD>
                            <TD ALIGN="CENTER"><FONT COLOR="#1E3A8A" POINT-SIZE="9"><B>SUPUESTOS</B></FONT></TD>
                        </TR>
                        <TR>
                            <TD WIDTH="200" ALIGN="LEFT"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['objetivo'], 35)}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['indicador'], 20)}</FONT></TD>
                            <TD WIDTH="80" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['meta'], 12)}</FONT></TD>
                            <TD WIDTH="140" ALIGN="CENTER"><FONT COLOR="#334155" POINT-SIZE="10">{wrap(fila['supuesto'], 20)}</FONT></TD>
                        </TR>
                    </TABLE>
                </TD>
            </TR>
        </TABLE>>'''
        
        dot.node(f'card_{i}', label=label, shape='rect', style='filled', fillcolor='white', color='#e2e8f0', penwidth='2')
        
        if i > 0:
            dot.edge(f'card_{i-1}', f'card_{i}', style='invis')
            
    return dot.pipe(format='png')

# --- PANEL LATERAL PARA EXPORTACIÓN ---
with st.sidebar:
    if datos_reales:
        imagen_estetica = generar_png_estetico(datos_reales)
        st.download_button(
            label="🖼️ Descargar Matriz (PNG)",
            data=imagen_estetica,
            file_name="Matriz_Marco_Logico.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.warning("Completa los datos para habilitar la descarga.")

# --- ENCABEZADO CON IMAGEN Y AVANCE ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Revisión de la estructura operativa y coherencia del proyecto.</div>', unsafe_allow_html=True)
    st.progress(1.0)
    
with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- RENDERIZADO DE LA MATRIZ EN PANTALLA ---
if not datos_reales:
    st.warning("⚠️ No se encontraron indicadores validados. Para ver datos aquí, asegúrate de haber marcado las 5 casillas de validación (P1 a P5) y generado las metas para tus objetivos en la Hoja 11.")
else:
    st.markdown("""
        <div class="header-global">
            <div style="flex: 1.2;">NIVEL</div>
            <div style="flex: 2;">RESUMEN NARRATIVO</div>
            <div style="flex: 1.5;">INDICADOR</div>
            <div style="flex: 1;">META</div>
            <div style="flex: 1.5;">SUPUESTOS</div>
        </div>
    """, unsafe_allow_html=True)

    for fila in datos_reales:
        conf = CONFIG_NIVELES.get(fila['tipo'], {"color": "#64748b", "bg": "#f8fafc"})
        
        st.markdown(f"""
            <div class="card-mml" style="border-left: 6px solid {conf['color']}; background-color: {conf['bg']};">
                <div style="display: flex; flex-direction: row; gap: 15px; align-items: center;">
                    <div style="flex: 1.2;">
                        <div class="tipo-badge" style="background-color: {conf['color']};">{fila['tipo']}</div>
                    </div>
                    <div style="flex: 2;" class="col-content"><b>{fila['objetivo']}</b></div>
                    <div style="flex: 1.5; justify-content: center; text-align: center;" class="col-content">{fila['indicador']}</div>
                    <div style="flex: 1; justify-content: center; text-align: center;" class="col-content">{fila['meta']}</div>
                    <div style="flex: 1.5; justify-content: center; text-align: center;" class="col-content">{fila['supuesto']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
