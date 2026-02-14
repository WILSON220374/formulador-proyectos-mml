import streamlit as st
import graphviz
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO GLOBAL (Interfaz Limpia) ---
st.markdown("""
    <style>
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

CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#884EA0", "label": "EFECTO\nINDIRECTO"},
    "Efectos Directos": {"color": "#2E86C1", "label": "EFECTO\nDIRECTO"},
    "Problema Principal": {"color": "#A93226", "label": "PROBLEMA\nCENTRAL"},
    "Causas Directas": {"color": "#D4AC0D", "label": "CAUSA\nDIRECTA"},
    "Causas Indirectas": {"color": "#CA6F1E", "label": "CAUSA\nINDIRECTA"}
}

# --- MOTOR DE DIBUJO (ETIQUETAS COMO TEXTO PLANO) ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_tarjetas', {})
    if not datos: return None
    dot = graphviz.Digraph(format='png')
    
    dot.attr(label='ÁRBOL DE PROBLEMAS', labelloc='t', fontsize='35', fontname='Arial Bold', fontcolor='#333333')
    dot.attr(dpi='300', rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')
    
    # Nodos de Contenido (Tarjetas con color)
    dot.attr('node', fontsize='20', fontcolor='white', fontname='Arial Bold', style='filled', color='none', margin='0.6,0.4', shape='box')
    
    import textwrap
    def limpiar(t, w=50): return "\n".join(textwrap.wrap(str(t).replace('"', "'"), width=w))

    # --- CREACIÓN DE ETIQUETAS LATERALES (SOLO TEXTO) ---
    def crear_nodo_etiqueta(id_et, tipo):
        conf = CONFIG_PROB[tipo]
        # shape='plaintext' elimina el recuadro completamente
        dot.node(id_et, conf['label'], shape='plaintext', fontcolor=conf['color'], fontsize='18', fontname='Arial Bold')

    # Definir nodos de etiquetas
    etiquetas = ["L_EI", "L_ED", "L_PC", "L_CD", "L_CI"]
    tipos = ["Efectos Indirectos", "Efectos Directos", "Problema Principal", "Causas Directas", "Causas Indirectas"]
    for id_e, tipo in zip(etiquetas, tipos):
        crear_nodo_etiqueta(id_e, tipo)
    
    # Vincular etiquetas verticalmente (invisible)
    for i in range(len(etiquetas)-1):
        dot.edge(etiquetas[i+1], etiquetas[i], style='invis')

    # --- RENDERIZADO DE CONTENIDO POR NIVELES ---
    pc = datos.get("Problema Principal", [])
    if pc:
        dot.node('PC', limpiar(pc[0]['texto'], 100), fillcolor=CONFIG_PROB["Problema Principal"]["color"], margin='0.8,0.4')
        with dot.subgraph() as s:
            s.attr(rank='same')
            s.node('L_PC')
            s.node('PC')

    for tipo, id_et, p_key, edge_dir in [
        ("Efectos Directos", "L_ED", "PC", "forward"), 
        ("Causas Directas", "L_CD", "PC", "back")
    ]:
        items = datos.get(tipo, [])
        h_tipo = "Efectos Indirectos" if "Efecto" in tipo else "Causas Indirectas"
        id_et_h = "L_EI" if "Efecto" in tipo else "L_CI"
        
        with dot.subgraph() as s_p:
            s_p.attr(rank='same')
            s_p.node(id_et)
            for i, it in enumerate(items):
                txt = it.get('texto') if isinstance(it, dict) else it
                node_id = f"{tipo}{i}"
                s_p.node(node_id, limpiar(txt), fillcolor=CONFIG_PROB[tipo]["color"])
                if edge_dir == "forward": dot.edge('PC', node_id)
                else: dot.edge(node_id, 'PC')

        with dot.subgraph() as s_h:
            s_h.attr(rank='same')
            s_h.node(id_et_h)
            for i, it in enumerate(items):
                txt_p = it.get('texto') if isinstance(it, dict) else it
                for j, h in enumerate(datos.get(h_tipo, [])):
                    if isinstance(h, dict) and h.get('padre') == txt_p:
                        h_id = f"{h_tipo}{i}_{j}"
                        s_h.node(h_id, limpiar(h.get('texto')), fillcolor=CONFIG_PROB[h_tipo]["color"])
                        if edge_dir == "forward": dot.edge(f"{tipo}{i}", h_id)
                        else: dot.edge(h_id, f"{tipo}{i}")
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

# --- SIDEBAR ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Sección:", list(CONFIG_PROB.keys()))
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción:")
        padre_asociado = None
        if "Indirect" in tipo_sel:
            p_key = "Efectos Directos" if "Efecto" in tipo_sel else "Causas Directas"
            opciones = [it['texto'] for it in st.session_state['arbol_tarjetas'].get(p_key, [])]
            if opciones: padre_asociado = st.selectbox("Vincular a:", opciones)
        if st.form_submit_button("Generar") and texto_input:
            nueva = {"texto": texto_input, "id_unico": str(uuid.uuid4())}
            if padre_asociado: nueva["padre"] = padre_asociado
            if tipo_sel == "Problema Principal": st.session_state['arbol_tarjetas'][tipo_sel] = [nueva]
            else: st.session_state['arbol_tarjetas'][tipo_sel].append(nueva)
            guardar_datos_nube(); st.rerun()
    st.divider()
    grafo = generar_grafo_problemas()
    if grafo: st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol.png", use_container_width=True)

# --- PANEL PRINCIPAL ---
if not any(st.session_state['arbol_tarjetas'].values()):
    st.warning("Inicie con el Problema Principal.")
else:
    grafo_f = generar_grafo_problemas()
    if grafo_f: st.image(grafo_f.pipe(format='png'), use_container_width=True)
    st.divider()
    st.subheader("📋 Panel de Edición")

    def render_seccion_simple(tipo_padre, tipo_hijo):
        padres = st.session_state['arbol_tarjetas'].get(tipo_padre, [])
        hijos = st.session_state['arbol_tarjetas'].get(tipo_hijo, [])
        if not padres: return
        
        st.write(f"**{tipo_padre} e {tipo_hijo}**")
        hijos_por_p = [[(idx, h) for idx, h in enumerate(hijos) if h.get('padre') == p['texto']] for p in padres]
        max_h = max([len(lista) for lista in hijos_por_p]) if hijos_por_p else 0

        for h_idx in range(max_h - 1, -1, -1) if "Efecto" in tipo_padre else range(max_h):
            cols = st.columns(len(padres))
            for p_idx, col in enumerate(cols):
                with col:
                    if h_idx < len(hijos_por_p[p_idx]):
                        idx_real, h_data = hijos_por_p[p_idx][h_idx]
                        render_card(tipo_hijo, h_data, idx_real)
                    else: st.empty()

        cols_p = st.columns(len(padres))
        for i, p_data in enumerate(padres):
            with cols_p[i]: render_card(tipo_padre, p_data, i)

    render_seccion_simple("Efectos Directos", "Efectos Indirectos")
    st.markdown("---")
    st.write("**Problema Principal**")
    pc_l = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
    if pc_l: render_card("Problema Principal", pc_l[0], 0)
    st.markdown("---")
    render_seccion_simple("Causas Directas", "Causas Indirectas")
