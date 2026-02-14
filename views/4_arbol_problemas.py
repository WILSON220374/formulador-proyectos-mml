import streamlit as st
import graphviz
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO GLOBAL (Interfaz y Etiquetas de Fila) ---
st.markdown("""
    <style>
    /* Estética de Tarjetas: Fusión total con color */
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
    
    /* Etiquetas Laterales (Basadas en la imagen) */
    .etiqueta-fila {
        color: #000;
        padding: 15px 5px;
        border-radius: 5px;
        text-align: center;
        font-weight: 800;
        font-size: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100px; /* Alineado con la altura de la tarjeta */
        border: 2px solid #333;
        line-height: 1.1;
        text-transform: uppercase;
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
    "Efectos Indirectos": {"color": "#884EA0", "label": "EFECTO INDIRECTO", "bg_etiqueta": "#D2B4DE"},
    "Efectos Directos": {"color": "#2E86C1", "label": "EFECTO DIRECTO", "bg_etiqueta": "#AED6F1"},
    "Problema Principal": {"color": "#A93226", "label": "PROBLEMA CENTRAL", "bg_etiqueta": "#E6B0AA"},
    "Causas Directas": {"color": "#D4AC0D", "label": "CAUSA DIRECTA", "bg_etiqueta": "#F9E79F"},
    "Causas Indirectas": {"color": "#CA6F1E", "label": "CAUSA INDIRECTA", "bg_etiqueta": "#F5CBA7"}
}

# --- FUNCIONES DE APOYO ---
def render_etiqueta(tipo):
    conf = CONFIG_PROB[tipo]
    st.markdown(f'<div class="etiqueta-fila" style="background-color: {conf["bg_etiqueta"]};">{conf["label"]}</div>', unsafe_allow_html=True)

def render_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    st.markdown(f'<div style="background-color: {CONFIG_PROB[seccion]["color"]}; height: 15px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    nuevo = st.text_area("t", value=item['texto'], key=f"txt_{id_u}", label_visibility="collapsed")
    if st.button("🗑️", key=f"btn_{id_u}"):
        st.session_state['arbol_tarjetas'][seccion].pop(idx); guardar_datos_nube(); st.rerun()
    if nuevo != item['texto']: item['texto'] = nuevo; guardar_datos_nube()

# --- MOTOR DE DIBUJO ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_tarjetas', {})
    if not datos: return None
    dot = graphviz.Digraph(format='png')
    dot.attr(label='ÁRBOL DE PROBLEMAS', labelloc='t', fontsize='35', fontname='Arial Bold', fontcolor='#333333')
    dot.attr(dpi='300', rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')
    dot.attr('node', fontsize='20', fontcolor='white', fontname='Arial Bold', style='filled', color='none', margin='0.6,0.4', shape='box')
    
    import textwrap
    def limpiar(t, w=50): return "\n".join(textwrap.wrap(str(t).replace('"', "'"), width=w))
    
    pc = datos.get("Problema Principal", [])
    if pc:
        dot.node('PC', limpiar(pc[0]['texto'], 100), fillcolor=CONFIG_PROB["Problema Principal"]["color"], margin='0.8,0.4')

    for tipo, p_key, edge_dir in [("Efectos Directos", "PC", "forward"), ("Causas Directas", "PC", "back")]:
        items = datos.get(tipo, [])
        for i, it in enumerate(items):
            txt = it.get('texto') if isinstance(it, dict) else it
            dot.node(f"{tipo}{i}", limpiar(txt), fillcolor=CONFIG_PROB[tipo]["color"])
            if edge_dir == "forward": dot.edge('PC', f"{tipo}{i}")
            else: dot.edge(f"{tipo}{i}", 'PC')
            
            h_tipo = "Efectos Indirectos" if "Efecto" in tipo else "Causas Indirectas"
            for j, h in enumerate(datos.get(h_tipo, [])):
                if isinstance(h, dict) and h.get('padre') == txt:
                    dot.node(f"{h_tipo}{i}_{j}", limpiar(h.get('texto')), fillcolor=CONFIG_PROB[h_tipo]["color"])
                    if edge_dir == "forward": dot.edge(f"{tipo}{i}", f"{h_tipo}{i}_{j}")
                    else: dot.edge(f"{h_tipo}{i}_{j}", f"{tipo}{i}")
    return dot

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

    # --- LÓGICA DE FILAS CON ETIQUETAS ---
    def render_seccion_con_etiqueta(tipo_padre, tipo_hijo):
        padres = st.session_state['arbol_tarjetas'].get(tipo_padre, [])
        hijos = st.session_state['arbol_tarjetas'].get(tipo_hijo, [])
        if not padres: return

        # 1. Filas de Hijos (Indirectos)
        hijos_por_p = [[(idx, h) for idx, h in enumerate(hijos) if h.get('padre') == p['texto']] for p in padres]
        max_h = max([len(lista) for lista in hijos_por_p]) if hijos_por_p else 0
        
        ratios = [0.15] + [0.85/len(padres)] * len(padres)
        
        for h_idx in range(max_h - 1, -1, -1) if "Efecto" in tipo_padre else range(max_h):
            cols = st.columns(ratios)
            with cols[0]: 
                if h_idx == (max_h-1 if "Efecto" in tipo_padre else 0): render_etiqueta(tipo_hijo)
            for p_idx, col in enumerate(cols[1:]):
                with col:
                    if h_idx < len(hijos_por_p[p_idx]):
                        idx_real, h_data = hijos_por_p[p_idx][h_idx]
                        render_card(tipo_hijo, h_data, idx_real)

        # 2. Fila de Padres (Directos)
        cols_p = st.columns(ratios)
        with cols_p[0]: render_etiqueta(tipo_padre)
        for i, p_data in enumerate(padres):
            with cols_p[i+1]: render_card(tipo_padre, p_data, i)

    # RENDERIZADO FINAL DEL PANEL
    render_seccion_con_etiqueta("Efectos Directos", "Efectos Indirectos")
    
    st.markdown("---")
    # Fila Problema Central
    cols_pc = st.columns([0.15, 0.85])
    with cols_pc[0]: render_etiqueta("Problema Principal")
    with cols_pc[1]: 
        pc_l = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
        if pc_l: render_card("Problema Principal", pc_l[0], 0)
    
    st.markdown("---")
    render_seccion_con_etiqueta("Causas Directas", "Causas Indirectas")
