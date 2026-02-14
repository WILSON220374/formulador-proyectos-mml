import streamlit as st
import graphviz
import copy
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO DE LA INTERFAZ ---
st.markdown("""
    <style>
    div[data-testid="stTextArea"] textarea {
        background-color: #fcf8f8 !important;
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.2rem !important;
        margin-top: -10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🌳 4. Árbol de Problemas")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", width="stretch")

# --- CONFIGURACIÓN DE COLORES ---
CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#B3D9FF", "label": "EFECTOS INDIRECTOS"},
    "Efectos Directos": {"color": "#80BFFF", "label": "EFECTOS DIRECTOS"},
    "Problema Principal": {"color": "#FFB3BA", "label": "PROBLEMA CENTRAL"},
    "Causas Directas": {"color": "#FFFFBA", "label": "CAUSAS DIRECTAS"},
    "Causas Indirectas": {"color": "#FFDFBA", "label": "CAUSAS INDIRECTAS"}
}

# --- MOTOR DE DIBUJO (GRAPHVIZ) ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_tarjetas', {})
    if not datos: return None

    dot = graphviz.Digraph(format='png')
    dot.attr(label='\nÁRBOL DE PROBLEMAS\n ', labelloc='t', fontsize='22', fontname='Arial Bold', fontcolor='#1E3A8A')
    dot.attr(rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')

    def limpiar(t): 
        import textwrap
        return "\n".join(textwrap.wrap(str(t).replace('"', "'"), width=25))

    # 1. Problema Principal
    pc = datos.get("Problema Principal", [])
    if pc:
        txt = pc[0].get('texto', pc[0]) if isinstance(pc[0], dict) else pc[0]
        dot.node('PC', limpiar(txt), shape='box', style='filled', fillcolor=CONFIG_PROB["Problema Principal"]["color"], fontname='Arial Bold')

    # 2. EFECTOS
    ef_dir = datos.get("Efectos Directos", [])
    ef_ind = datos.get("Efectos Indirectos", [])
    for i, ed in enumerate(ef_dir):
        txt_ed = ed.get('texto', ed) if isinstance(ed, dict) else ed
        id_ed = f"ED{i}"
        dot.node(id_ed, limpiar(txt_ed), shape='box', style='filled', fillcolor=CONFIG_PROB["Efectos Directos"]["color"])
        dot.edge('PC', id_ed)
        for j, ei in enumerate(ef_ind):
            if isinstance(ei, dict) and ei.get('padre') == txt_ed:
                id_ei = f"EI{i}_{j}"
                dot.node(id_ei, limpiar(ei.get('texto')), shape='box', style='filled', fillcolor=CONFIG_PROB["Efectos Indirectos"]["color"])
                dot.edge(id_ed, id_ei)

    # 3. CAUSAS
    ca_dir = datos.get("Causas Directas", [])
    ca_ind = datos.get("Causas Indirectas", [])
    for i, cd in enumerate(ca_dir):
        txt_cd = cd.get('texto', cd) if isinstance(cd, dict) else cd
        id_cd = f"CD{i}"
        dot.node(id_cd, limpiar(txt_cd), shape='box', style='filled', fillcolor=CONFIG_PROB["Causas Directas"]["color"])
        dot.edge(id_cd, 'PC')
        for j, ci in enumerate(ca_ind):
            if isinstance(ci, dict) and ci.get('padre') == txt_cd:
                id_ci = f"CI{i}_{j}"
                dot.node(id_ci, limpiar(ci.get('texto')), shape='box', style='filled', fillcolor=CONFIG_PROB["Causas Indirectas"]["color"])
                dot.edge(id_ci, id_cd)

    return dot

# --- SIDEBAR ---
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
        st.download_button("🖼️ Descargar Árbol PNG", data=grafo.pipe(format='png'), file_name="arbol_problemas.png", width="stretch")

# --- PANEL DE EDICIÓN ---
def render_card(seccion, item, idx):
    if not isinstance(item, dict) or 'id_unico' not in item:
        txt = item.get('texto', item) if isinstance(item, dict) else item
        padre = item.get('padre') if isinstance(item, dict) else None
        item = {"texto": txt, "id_unico": str(uuid.uuid4())}
        if padre: item["padre"] = padre
        st.session_state['arbol_tarjetas'][seccion][idx] = item

    id_u = item['id_unico']
    st.markdown(f'<div style="background-color: {CONFIG_PROB[seccion]["color"]}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    nuevo = st.text_area("t", value=item['texto'], key=f"txt_{id_u}", label_visibility="collapsed")
    if st.button("🗑️", key=f"btn_{id_u}"):
        st.session_state['arbol_tarjetas'][seccion].pop(idx); guardar_datos_nube(); st.rerun()
    if nuevo != item['texto']: item['texto'] = nuevo; guardar_datos_nube()

if not any(st.session_state['arbol_tarjetas'].values()):
    st.warning("Agregue el Problema Principal en el panel lateral.")
else:
    st.subheader("📊 Visualización Estructural")
    st.graphviz_chart(generar_grafo_problemas())

    st.divider()
    st.subheader("📋 Panel de Edición")

    # 1. EFECTOS (Lógica de Espejo: Hijos arriba en su fila, Padres abajo en la suya)
    st.write(f"**{CONFIG_PROB['Efectos Directos']['label']} e INDIRECTOS**")
    ef_dir = st.session_state['arbol_tarjetas'].get("Efectos Directos", [])
    ef_ind = st.session_state['arbol_tarjetas'].get("Efectos Indirectos", [])
    if ef_dir:
        # FILA DE HIJOS (Arriba)
        cols_h = st.columns(len(ef_dir))
        for i, ed in enumerate(ef_dir):
            with cols_h[i]:
                txt_p = ed.get('texto') if isinstance(ed, dict) else ed
                for idx_h, h in enumerate(ef_ind):
                    if isinstance(h, dict) and h.get('padre') == txt_p:
                        render_card("Efectos Indirectos", h, idx_h)
        # FILA DE PADRES (Abajo - Alineados)
        cols_p = st.columns(len(ef_dir))
        for i, ed in enumerate(ef_dir):
            with cols_p[i]: render_card("Efectos Directos", ed, i)

    st.markdown("---")
    # 2. PROBLEMA CENTRAL
    st.write(f"**{CONFIG_PROB['Problema Principal']['label']}**")
    pc_list = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
    if pc_list: render_card("Problema Principal", pc_list[0], 0)

    st.markdown("---")
    # 3. CAUSAS (Lógica Normal: Padres arriba, Hijos abajo)
    st.write(f"**{CONFIG_PROB['Causas Directas']['label']} e INDIRECTAS**")
    ca_dir = st.session_state['arbol_tarjetas'].get("Causas Directas", [])
    ca_ind = st.session_state['arbol_tarjetas'].get("Causas Indirectas", [])
    if ca_dir:
        cols_cp = st.columns(len(ca_dir))
        for i, cd in enumerate(ca_dir):
            with cols_cp[i]: render_card("Causas Directas", cd, i)
        cols_ch = st.columns(len(ca_dir))
        for i, cd in enumerate(ca_dir):
            with cols_ch[i]:
                txt_pc = cd.get('texto') if isinstance(cd, dict) else cd
                for idx_hc, hc in enumerate(ca_ind):
                    if isinstance(hc, dict) and hc.get('padre') == txt_pc:
                        render_card("Causas Indirectas", hc, idx_hc)
