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

# --- ENCABEZADO CON LOGO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🌳 4. Árbol de Problemas")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", width="stretch")

# --- CONFIGURACIÓN DE COLORES Y ESTRUCTURA ---
CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#B3D9FF", "label": "EFECTOS INDIRECTOS"},
    "Efectos Directos": {"color": "#80BFFF", "label": "EFECTOS DIRECTOS"},
    "Problema Principal": {"color": "#FFB3BA", "label": "PROBLEMA CENTRAL"},
    "Causas Directas": {"color": "#FFFFBA", "label": "CAUSAS DIRECTAS"},
    "Causas Indirectas": {"color": "#FFDFBA", "label": "CAUSAS INDIRECTAS"}
}

# --- MOTOR DE DIBUJO PROFESIONAL (GRAPHVIZ) ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_tarjetas', {})
    if not datos: return None

    # Modo BT para que las causas queden abajo y los efectos arriba
    dot = graphviz.Digraph(format='png')
    dot.attr(label='\nÁRBOL DE PROBLEMAS\n ', labelloc='t', 
             fontsize='22', fontname='Arial Bold', fontcolor='#1E3A8A')
    
    dot.attr(rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')

    def limpiar(t): 
        import textwrap
        t = str(t).replace('"', "'")
        return "\n".join(textwrap.wrap(t, width=25))

    def get_txt(it):
        return it.get('texto', it) if isinstance(it, dict) else it

    # 1. Problema Principal
    p_principal = datos.get("Problema Principal", [])
    if p_principal:
        txt_pc = get_txt(p_principal[0])
        dot.node('PC', limpiar(txt_pc), shape='box', style='filled', 
                 fillcolor=CONFIG_PROB["Problema Principal"]["color"], fontname='Arial Bold')

    # 2. EFECTOS (Hacia arriba)
    ef_dir = datos.get("Efectos Directos", [])
    ef_ind = datos.get("Efectos Indirectos", [])
    for i, ed in enumerate(ef_dir):
        txt_ed = get_txt(ed)
        id_ed = f"ED{i}"
        dot.node(id_ed, limpiar(txt_ed), shape='box', style='filled', fillcolor=CONFIG_PROB["Efectos Directos"]["color"])
        dot.edge('PC', id_ed)
        for j, ei in enumerate(ef_ind):
            if isinstance(ei, dict) and ei.get('padre') == txt_ed:
                id_ei = f"EI{i}{j}"
                dot.node(id_ei, limpiar(ei.get('texto')), shape='box', style='filled', fillcolor=CONFIG_PROB["Efectos Indirectos"]["color"])
                dot.edge(id_ed, id_ei)

    # 3. CAUSAS (Hacia abajo)
    ca_dir = datos.get("Causas Directas", [])
    ca_ind = datos.get("Causas Indirectas", [])
    for i, cd in enumerate(ca_dir):
        txt_cd = get_txt(cd)
        id_cd = f"CD{i}"
        dot.node(id_cd, limpiar(txt_cd), shape='box', style='filled', fillcolor=CONFIG_PROB["Causas Directas"]["color"])
        dot.edge(id_cd, 'PC')
        for j, ci in enumerate(ca_ind):
            if isinstance(ci, dict) and ci.get('padre') == txt_cd:
                id_ci = f"CI{i}{j}"
                dot.node(id_ci, limpiar(ci.get('texto')), shape='box', style='filled', fillcolor=CONFIG_PROB["Causas Indirectas"]["color"])
                dot.edge(id_ci, id_cd)

    return dot

# --- SIDEBAR: GESTIÓN DE FICHAS ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Seleccione Sección:", list(CONFIG_PROB.keys()))
    
    with st.form("crear_ficha_nube", clear_on_submit=True):
        texto_input = st.text_area("Descripción (Máx 180 caracteres):", max_chars=180)
        padre_asociado = None
        
        if "Indirectas" in tipo_sel or "Indirectos" in tipo_sel:
            padre_key = "Efectos Directos" if "Efectos" in tipo_sel else "Causas Directas"
            items_p = st.session_state['arbol_tarjetas'].get(padre_key, [])
            opciones_p = [it.get('texto', it) if isinstance(it, dict) else it for it in items_p]
            if opciones_p:
                padre_asociado = st.selectbox(f"Vincular a {CONFIG_PROB[padre_key]['label']}:", opciones_p)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            nueva_ficha = {"texto": texto_input, "id_unico": str(uuid.uuid4())}
            if padre_asociado: nueva_ficha["padre"] = padre_asociado
            
            if tipo_sel == "Problema Principal":
                st.session_state['arbol_tarjetas'][tipo_sel] = [nueva_ficha]
            else:
                st.session_state['arbol_tarjetas'][tipo_sel].append(nueva_ficha)
            
            guardar_datos_nube(); st.rerun()

    st.divider()
    grafo = generar_grafo_problemas()
    if grafo:
        st.download_button("🖼️ Descargar Árbol PNG", data=grafo.pipe(format='png'), 
                           file_name="arbol_problemas.png", width="stretch")

# --- ÁREA PRINCIPAL ---
if not any(st.session_state['arbol_tarjetas'].values()):
    st.warning("Comience agregando el Problema Principal en el panel lateral.")
else:
    st.subheader("📊 Visualización Estructural")
    with st.container(border=True):
        st.graphviz_chart(generar_grafo_problemas())

    st.divider()

    # --- FUNCIÓN RENDERIZADO DE TARJETA ---
    def render_card(seccion, item, idx):
        if not isinstance(item, dict) or 'id_unico' not in item:
            texto = item.get('texto', item) if isinstance(item, dict) else item
            padre = item.get('padre') if isinstance(item, dict) else None
            item = {"texto": texto, "id_unico": str(uuid.uuid4())}
            if padre: item["padre"] = padre
            st.session_state['arbol_tarjetas'][seccion][idx] = item

        id_u = item['id_unico']
        color = CONFIG_PROB[seccion]["color"]
        
        st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
        nuevo_txt = st.text_area("t", value=item['texto'], key=f"txt_{id_u}", label_visibility="collapsed")
        
        if st.button("🗑️", key=f"btn_{id_u}"):
            st.session_state['arbol_tarjetas'][seccion].pop(idx)
            guardar_datos_nube(); st.rerun()
        
        if nuevo_txt != item['texto']:
            item['texto'] = nuevo_txt
            guardar_datos_nube()

    # --- PANEL DE EDICIÓN CON ALINEACIÓN HORIZONTAL ---
    st.subheader("📋 Panel de Edición")

    # 1. SECCIÓN DE EFECTOS (Stacking Vertical por rama, pero Padres alineados)
    st.write(f"**{CONFIG_PROB['Efectos Directos']['label']} e INDIRECTOS**")
    ef_directos = st.session_state['arbol_tarjetas'].get("Efectos Directos", [])
    if ef_directos:
        # Fila de hijos para mantener alineación superior
        cols_h_ef = st.columns(len(ef_directos))
        ef_indirectos = st.session_state['arbol_tarjetas'].get("Efectos Indirectos", [])
        for i, ed in enumerate(ef_directos):
            with cols_h_ef[i]:
                txt_p = ed.get('texto') if isinstance(ed, dict) else ed
                for idx_h, h in enumerate(ef_indirectos):
                    if isinstance(h, dict) and h.get('padre') == txt_p:
                        render_card("Efectos Indirectos", h, idx_h)
        
        # Fila de padres para garantizar línea horizontal única
        cols_p_ef = st.columns(len(ef_directos))
        for i, ed in enumerate(ef_directos):
            with cols_p_ef[i]:
                render_card("Efectos Directos", ed, i)
    else: st.caption("No hay efectos definidos.")

    st.markdown("---")

    # 2. PROBLEMA CENTRAL
    st.write(f"**{CONFIG_PROB['Problema Principal']['label']}**")
    p_central_list = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
    if p_central_list:
        render_card("Problema Principal", p_central_list[0], 0)

    st.markdown("---")

    # 3. SECCIÓN DE CAUSAS (Padres alineados arriba, hijos alineados abajo)
    st.write(f"**{CONFIG_PROB['Causas Directas']['label']} e INDIRECTAS**")
    ca_directas = st.session_state['arbol_tarjetas'].get("Causas Directas", [])
    if ca_directas:
        # Fila de padres (Causas Directas) - ALINEADOS HORIZONTALMENTE
        cols_p_ca = st.columns(len(ca_directas))
        for i, cd in enumerate(ca_directas):
            with cols_p_ca[i]:
                render_card("Causas Directas", cd, i)
        
        # Fila de hijos (Causas Indirectas) - APARECEN DEBAJO
        cols_h_ca = st.columns(len(ca_directas))
        ca_indirectas = st.session_state['arbol_tarjetas'].get("Causas Indirectas", [])
        for i, cd in enumerate(ca_directas):
            with cols_h_ca[i]:
                txt_pc = cd.get('texto') if isinstance(cd, dict) else cd
                for idx_hc, hc in enumerate(ca_indirectas):
                    if isinstance(hc, dict) and hc.get('padre') == txt_pc:
                        render_card("Causas Indirectas", hc, idx_hc)
    else: st.caption("No hay causas definidas.")
