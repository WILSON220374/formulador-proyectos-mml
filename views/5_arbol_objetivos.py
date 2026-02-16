import streamlit as st
import graphviz
import os
import uuid
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTRATEGIA: SANEAMIENTO DE DATOS ---
if 'arbol_objetivos' in st.session_state:
    for seccion in st.session_state['arbol_objetivos']:
        lista = st.session_state['arbol_objetivos'][seccion]
        if isinstance(lista, list):
            st.session_state['arbol_objetivos'][seccion] = [
                it for it in lista if isinstance(it, dict) and it.get('texto')
            ]

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 10rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;           
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #000 !important;
        min-height: 100px !important;
    }

    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ef4444 !important;
        font-size: 1.2rem !important;
        margin-top: -15px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🎯 5. Árbol de Objetivos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Transformación de problemas en estados positivos.</div>', unsafe_allow_html=True)
    
    hay_datos = any(st.session_state.get('arbol_objetivos', {}).values())
    st.progress(1.0 if hay_datos else 0.0)

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

CONFIG_OBJ = {
    "Fines Indirectos": {"color": "#154360", "label": "FINES\nINDIRECTOS"},
    "Fines Directos":   {"color": "#1F618D", "label": "FINES\nDIRECTOS"},
    "Objetivo General": {"color": "#C0392B", "label": "OBJETIVO\nGENERAL"},
    "Medios Directos":  {"color": "#F1C40F", "label": "OBJETIVOS\nESPECÍFICOS"},
    "Medios Indirectos":{"color": "#D35400", "label": "ACTIVIDADES"}
}

# --- MOTOR DE DIBUJO ---
def generar_grafo_objetivos():
    datos = st.session_state.get('arbol_objetivos', {})
    if not any(datos.values()): return None
    
    dot = graphviz.Digraph(format='png')
    dot.attr(label='\nÁRBOL DE OBJETIVOS\n ', labelloc='t', fontsize='28', fontname='Arial Bold', fontcolor='#1E3A8A')
    dot.attr(size='16,12!', ratio='fill', center='true', dpi='300') 
    dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')
    
    def limpiar(t): return "\n".join(textwrap.wrap(str(t).upper(), width=25))

    for tipo in CONFIG_OBJ:
        conf = CONFIG_OBJ[tipo]
        dot.node(f"L_{tipo[:2]}", conf['label'], shape='plaintext', fontcolor=conf['color'], fontsize='12', fontname='Arial Bold', style='none')

    obj_gen = [it for it in datos.get("Objetivo General", []) if it.get('texto')]
    if obj_gen:
        dot.node("OG", limpiar(obj_gen[0]['texto']), fillcolor=CONFIG_OBJ["Objetivo General"]["color"], fontcolor='white', color='none', width='4.5')

    for tipo, p_id, h_tipo in [("Fines Directos", "OG", "Fines Indirectos"), ("Medios Directos", "OG", "Medios Indirectos")]:
        items = [it for it in datos.get(tipo, []) if it.get('texto')]
        for i, item in enumerate(items):
            node_id = f"{tipo[:2]}{i}"
            dot.node(node_id, limpiar(item['texto']), fillcolor=CONFIG_OBJ[tipo]["color"], fontcolor='white' if "Fin" in tipo else 'black', color='none')
            if "Fin" in tipo: dot.edge("OG", node_id)
            else: dot.edge(node_id, "OG")
            
            hijos = [h for h in datos.get(h_tipo, []) if h.get('padre') == item.get('texto')]
            for j, h in enumerate(hijos):
                h_id = f"{h_tipo[:2]}{i}_{j}"
                dot.node(h_id, limpiar(h['texto']), fillcolor=CONFIG_OBJ[h_tipo]["color"], fontcolor='white', color='none', fontsize='10')
                if "Fin" in tipo: dot.edge(node_id, h_id)
                else: dot.edge(h_id, node_id)
    return dot

# --- RENDERIZADO DE TARJETA CON ACTUALIZACIÓN EN CASCADA ---
def render_card_obj(seccion, item, idx, seccion_hijos=None):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color_barra = CONFIG_OBJ.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 12px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    
    texto_viejo = item.get('texto', '')
    nuevo_texto = st.text_area("t", value=texto_viejo, key=f"obj_txt_{id_u}", label_visibility="collapsed")
    
    if st.button("🗑️", key=f"obj_btn_{id_u}"):
        st.session_state['arbol_objetivos'][seccion].pop(idx); guardar_datos_nube(); st.rerun()
    
    if nuevo_texto and nuevo_texto.upper() != texto_viejo.upper():
        nuevo_fmt = nuevo_texto.upper().strip()
        # AJUSTE 1: Actualizar el campo 'padre' de todos los hijos vinculados
        if seccion_hijos:
            for h in st.session_state['arbol_objetivos'].get(seccion_hijos, []):
                if h.get('padre') == texto_viejo:
                    h['padre'] = nuevo_fmt
        
        st.session_state['arbol_objetivos'][seccion][idx]['texto'] = nuevo_fmt
        guardar_datos_nube()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True, type="primary"):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {"Efectos Indirectos": "Fines Indirectos", "Efectos Directos": "Fines Directos", "Problema Principal": "Objetivo General", "Causas Directas": "Medios Directos", "Causas Indirectas": "Medios Indirectos"}
        for k in CONFIG_OBJ: st.session_state['arbol_objetivos'][k] = []
        for p_sec, o_sec in mapeo.items():
            for it in problemas.get(p_sec, []):
                if isinstance(it, dict):
                    nueva = {"texto": it.get('texto', '').upper(), "id_unico": str(uuid.uuid4()), "padre": it.get('padre', "").upper()}
                    st.session_state['arbol_objetivos'][o_sec].append(nueva)
        guardar_datos_nube(); st.rerun()

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🌳 Visualización", "📝 Edición"])

with tab1:
    grafo_f = generar_grafo_objetivos()
    if grafo_f: st.image(grafo_f.pipe(format='png'), use_container_width=True)

with tab2:
    if hay_datos:
        def mostrar_seccion_jerarquica(tipo_padre, tipo_hijo):
            # AJUSTE 2: Obtener padres con sus índices originales de la base de datos
            padres_data = st.session_state['arbol_objetivos'].get(tipo_padre, [])
            padres_con_idx = [(idx, p) for idx, p in enumerate(padres_data) if isinstance(p, dict) and p.get('texto')]
            if not padres_con_idx: return
            
            st.write(f"**{tipo_padre}**")
            hijos_full = st.session_state['arbol_objetivos'].get(tipo_hijo, [])
            hijos_por_p = [[(idx_h, h) for idx_h, h in enumerate(hijos_full) if h.get('padre') == p_data.get('texto')] for _, p_data in padres_con_idx]
            max_h = max([len(lista) for lista in hijos_por_p]) if hijos_por_p else 0

            # Dibujo por filas (Efectos hacia arriba, Medios hacia abajo)
            if "Fin" in tipo_padre:
                for h_idx in range(max_h - 1, -1, -1):
                    cols = st.columns(len(padres_con_idx))
                    for p_col_idx, col in enumerate(cols):
                        with col:
                            if h_idx < len(hijos_por_p[p_col_idx]):
                                idx_h_real, h_data = hijos_por_p[p_col_idx][h_idx]
                                render_card_obj(tipo_hijo, h_data, idx_h_real)
                            else: st.empty()
                cols_p = st.columns(len(padres_con_idx))
                for i, (idx_original, p_data) in enumerate(padres_con_idx):
                    with cols_p[i]: render_card_obj(tipo_padre, p_data, idx_original, tipo_hijo)
            else:
                cols_p = st.columns(len(padres_con_idx))
                for i, (idx_original, p_data) in enumerate(padres_con_idx):
                    with cols_p[i]: render_card_obj(tipo_padre, p_data, idx_original, tipo_hijo)
                for h_idx in range(max_h):
                    cols = st.columns(len(padres_con_idx))
                    for p_col_idx, col in enumerate(cols):
                        with col:
                            if h_idx < len(hijos_por_p[p_col_idx]):
                                idx_h_real, h_data = hijos_por_p[p_col_idx][h_idx]
                                render_card_obj(tipo_hijo, h_data, idx_h_real)
                            else: st.empty()

        mostrar_seccion_jerarquica("Fines Directos", "Fines Indirectos")
        st.markdown("---")
        pc_og = st.session_state['arbol_objetivos'].get("Objetivo General", [])
        if pc_og: render_card_obj("Objetivo General", pc_og[0], 0)
        st.markdown("---")
        mostrar_seccion_jerarquica("Medios Directos", "Medios Indirectos")
