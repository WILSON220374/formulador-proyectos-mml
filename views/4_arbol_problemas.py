import streamlit as st
import graphviz
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO GLOBAL (Fusión de Tarjetas y Estructura Rígida) ---
st.markdown("""
    <style>
    /* Estética de Tarjetas: Fusión total con color (Aprobada) */
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        border: none !important;           
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #000 !important;
        box-shadow: none !important;
        min-height: 100px !important;
    }
    
    /* Ajuste del botón eliminar */
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.3rem !important;
        margin-top: -15px !important;
        position: relative;
        z-index: 2;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🌳 4. Árbol de Problemas")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- CONFIGURACIÓN DE COLORES SÓLIDOS (APROBADA) ---
CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#884EA0", "label": "EFECTOS INDIRECTOS"},
    "Efectos Directos": {"color": "#2E86C1", "label": "EFECTOS DIRECTOS"},
    "Problema Principal": {"color": "#A93226", "label": "PROBLEMA CENTRAL"},
    "Causas Directas": {"color": "#D4AC0D", "label": "CAUSAS DIRECTAS"},
    "Causas Indirectas": {"color": "#CA6F1E", "label": "CAUSAS INDIRECTAS"}
}

# --- MOTOR DE DIBUJO (AJUSTADO: FUENTE 18 Y LETRA BLANCA TOTAL) ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_tarjetas', {})
    if not datos: return None
    dot = graphviz.Digraph(format='png')
    
    # Configuración global de nodos: Letra Blanca y Tamaño 18
    dot.attr('node', fontsize='18', fontcolor='white', fontname='Arial Bold')
    dot.attr(rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')
    
    import textwrap
    def limpiar_estandar(t): 
        return "\n".join(textwrap.wrap(str(t).replace('"', "'"), width=100))
    
    # 1. PROBLEMA CENTRAL (Ancho 200, Letra Blanca)
    pc = datos.get("Problema Principal", [])
    if pc:
        txt_pc = pc[0]['texto'] if isinstance(pc[0], dict) else pc[0]
        txt_ancho = "\n".join(textwrap.wrap(str(txt_pc).replace('"', "'"), width=200))
        dot.node('PC', txt_ancho, shape='box', style='filled', 
                 fillcolor=CONFIG_PROB["Problema Principal"]["color"], 
                 margin='0.3,0.1')

    # 2. EFECTOS (Letra Blanca)
    ef_dir = datos.get("Efectos Directos", [])
    ef_ind = datos.get("Efectos Indirectos", [])
    for i, ed in enumerate(ef_dir):
        txt_ed = ed.get('texto', ed) if isinstance(ed, dict) else ed
        dot.node(f"ED{i}", limpiar_estandar(txt_ed), shape='box', style='filled', 
                 fillcolor=CONFIG_PROB["Efectos Directos"]["color"])
        dot.edge('PC', f"ED{i}")
        for j, ei in enumerate(ef_ind):
            if isinstance(ei, dict) and ei.get('padre') == txt_ed:
                dot.node(f"EI{i}_{j}", limpiar_estandar(ei.get('texto')), shape='box', style='filled', 
                         fillcolor=CONFIG_PROB["Efectos Indirectos"]["color"])
                dot.edge(f"ED{i}", f"EI{i}_{j}")

    # 3. CAUSAS (Ahora también con Letra Blanca)
    ca_dir = datos.get("Causas Directas", [])
    ca_ind = datos.get("Causas Indirectas", [])
    for i, cd in enumerate(ca_dir):
        txt_cd = cd.get('texto', cd) if isinstance(cd, dict) else cd
        dot.node(f"CD{i}", limpiar_estandar(txt_cd), shape='box', style='filled', 
                 fillcolor=CONFIG_PROB["Causas Directas"]["color"])
        dot.edge(f"CD{i}", 'PC')
        for j, ci in enumerate(ca_ind):
            if isinstance(ci, dict) and ci.get('padre') == txt_cd:
                dot.node(f"CI{i}_{j}", limpiar_estandar(ci.get('texto')), shape='box', style='filled', 
                         fillcolor=CONFIG_PROB["Causas Indirectas"]["color"])
                dot.edge(f"CI{i}_{j}", f"CD{i}")
    return dot

# --- RENDERIZADO DE TARJETA ---
def render_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    st.markdown(f'<div style="background-color: {CONFIG_PROB[seccion]["color"]}; height: 15px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    nuevo = st.text_area("t", value=item['texto'], key=f"txt_{id_u}", label_visibility="collapsed")
    if st.button("🗑️", key=f"btn_{id_u}"):
        st.session_state['arbol_tarjetas'][seccion].pop(idx); guardar_datos_nube(); st.rerun()
    if nuevo != item['texto']: item['texto'] = nuevo; guardar_datos_nube()

# --- SIDEBAR (GESTIÓN Y EXPORTACIÓN) ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG_PROB.keys()))
    with st.form("crear_ficha_nube", clear_on_submit=True):
        texto_input = st.text_area("Descripción:", max_chars=180)
        padre_asociado = None
        if "Indirectas" in tipo_sel or "Indirectos" in tipo_sel:
            p_key = "Efectos Directos" if "Efectos" in tipo_sel else "Causas Directas"
            items_p = st.session_state['arbol_tarjetas'].get(p_key, [])
            opciones_p = [it.get('texto', it) if isinstance(it, dict) else it for it in items_p]
            if opciones_p: padre_asociado = st.selectbox(f"Vincular a:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            nueva = {"texto": texto_input, "id_unico": str(uuid.uuid4())}
            if padre_asociado: nueva["padre"] = padre_asociado
            if tipo_sel == "Problema Principal": st.session_state['arbol_tarjetas'][tipo_sel] = [nueva]
            else: st.session_state['arbol_tarjetas'][tipo_sel].append(nueva)
            guardar_datos_nube(); st.rerun()
    
    st.divider()
    grafo = generar_grafo_problemas()
    if grafo:
        st.download_button("🖼️ Descargar Árbol PNG", data=grafo.pipe(format='png'), file_name="arbol_problemas.png", use_container_width=True)

# --- PANEL PRINCIPAL ---
if not any(st.session_state['arbol_tarjetas'].values()):
    st.warning("Agregue el Problema Principal en el panel lateral.")
else:
    st.graphviz_chart(generar_grafo_problemas())
    st.divider()
    st.subheader("📋 Panel de Edición")

    # 1. SECCIÓN EFECTOS (TABLA RÍGIDA)
    st.write(f"**{CONFIG_PROB['Efectos Directos']['label']} e INDIRECTOS**")
    ef_dir = st.session_state['arbol_tarjetas'].get("Efectos Directos", [])
    ef_ind = st.session_state['arbol_tarjetas'].get("Efectos Indirectos", [])
    
    if ef_dir:
        max_hijos = 0
        hijos_por_padre = []
        for ed in ef_dir:
            txt_p = ed.get('texto') if isinstance(ed, dict) else ed
            h_padre = [(idx, h) for idx, h in enumerate(ef_ind) if isinstance(h, dict) and h.get('padre') == txt_p]
            hijos_por_padre.append(h_padre)
            max_hijos = max(max_hijos, len(h_padre))

        for h_idx in range(max_hijos - 1, -1, -1):
            cols_h = st.columns(len(ef_dir))
            for p_idx, col in enumerate(cols_h):
                with col:
                    if h_idx < len(hijos_por_padre[p_idx]):
                        idx_real, hijo_data = hijos_por_padre[p_idx][h_idx]
                        render_card("Efectos Indirectos", hijo_data, idx_real)
                    else:
                        st.empty()

        cols_p = st.columns(len(ef_dir))
        for i, ed in enumerate(ef_dir):
            with cols_p[i]:
                render_card("Efectos Directos", ed, i)

    st.markdown("---")
    # 2. PROBLEMA CENTRAL
    st.write(f"**{CONFIG_PROB['Problema Principal']['label']}**")
    pc_list = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
    if pc_list: render_card("Problema Principal", pc_list[0], 0)

    st.markdown("---")
    # 3. SECCIÓN CAUSAS
    st.write(f"**{CONFIG_PROB['Causas Directas']['label']} e INDIRECTAS**")
    ca_dir = st.session_state['arbol_tarjetas'].get("Causas Directas", [])
    ca_ind = st.session_state['arbol_tarjetas'].get("Causas Indirectas", [])
    
    if ca_dir:
        cols_ca = st.columns(len(ca_dir))
        for i, cd in enumerate(ca_dir):
            with cols_ca[i]:
                render_card("Causas Directas", cd, i)
                txt_pc = cd.get('texto') if isinstance(cd, dict) else cd
                for idx_hc, hc in enumerate(ca_ind):
                    if isinstance(hc, dict) and hc.get('padre') == txt_pc:
                        render_card("Causas Indirectas", hc, idx_hc)
