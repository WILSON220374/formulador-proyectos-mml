import streamlit as st
import graphviz
import os
import uuid
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTRATEGIA: SANEAMIENTO DE DATOS (Arreglo para Grupo 2) ---
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
    st.markdown('<div class="subtitulo-gris">Transformación de problemas en estados positivos y medios para alcanzarlos.</div>', unsafe_allow_html=True)
    
    hay_datos = any(st.session_state.get('arbol_objetivos', {}).values())
    progreso = 1.0 if hay_datos else 0.0
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- CONFIGURACIÓN DE COLORES ---
CONFIG_OBJ = {
    "Fines Indirectos": {"color": "#154360", "font_color": "white", "label": "FINES\nINDIRECTOS"},
    "Fines Directos":   {"color": "#1F618D", "font_color": "white", "label": "FINES\nDIRECTOS"},
    "Objetivo General": {"color": "#C0392B", "font_color": "white", "label": "OBJETIVO\nGENERAL"},
    "Medios Directos":  {"color": "#F1C40F", "font_color": "black", "label": "OBJETIVOS\nESPECÍFICOS"},
    "Medios Indirectos":{"color": "#D35400", "font_color": "white", "label": "ACTIVIDADES"}
}

# --- MOTOR DE DIBUJO PROFESIONAL ---
def generar_grafo_objetivos():
    datos = st.session_state.get('arbol_objetivos', {})
    if not any(datos.values()): return None
    
    dot = graphviz.Digraph(format='png')
    dot.attr(label='\nÁRBOL DE OBJETIVOS\n ', labelloc='t', fontsize='28', fontname='Arial Bold', fontcolor='#1E3A8A')
    dot.attr(size='16,12!', ratio='fill', center='true', dpi='300') 
    dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')
    
    def limpiar(t): return "\n".join(textwrap.wrap(str(t).upper(), width=25))

    etiquetas = {"L_FI": "Fines Indirectos", "L_FD": "Fines Directos", "L_OG": "Objetivo General", "L_MD": "Medios Directos", "L_MI": "Medios Indirectos"}
    for id_e, tipo in etiquetas.items():
        conf = CONFIG_OBJ[tipo]
        dot.node(id_e, conf['label'], shape='plaintext', fontcolor=conf['color'], fontsize='12', fontname='Arial Bold', style='none')

    dot.edge("L_MI", "L_MD", style='invis')
    dot.edge("L_MD", "L_OG", style='invis')
    dot.edge("L_OG", "L_FD", style='invis')
    dot.edge("L_FD", "L_FI", style='invis')

    # 1. Objetivo General
    obj_gen = [it for it in datos.get("Objetivo General", []) if it.get('texto')]
    if obj_gen:
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node('L_OG', shape='plaintext', style='none')
            s.node("OG", limpiar(obj_gen[0]['texto']), fillcolor=CONFIG_OBJ["Objetivo General"]["color"], fontcolor='white', color='none', width='4.5')

    # 2. Fines Directos
    f_dir = [it for it in datos.get("Fines Directos", []) if it.get('texto')]
    with dot.subgraph() as s:
        s.attr(rank='same'); s.node('L_FD', shape='plaintext', style='none')
        for i, item in enumerate(f_dir):
            node_id = f"FD{i}"
            s.node(node_id, limpiar(item['texto']), fillcolor=CONFIG_OBJ["Fines Directos"]["color"], fontcolor='white', color='none')
            if obj_gen: dot.edge("OG", node_id)

    # 3. Fines Indirectos
    f_ind = [it for it in datos.get("Fines Indirectos", []) if it.get('texto')]
    with dot.subgraph() as s:
        s.attr(rank='same'); s.node('L_FI', shape='plaintext', style='none')
        for i, item in enumerate(f_ind):
            node_id = f"FI{i}"
            s.node(node_id, limpiar(item['texto']), fillcolor=CONFIG_OBJ["Fines Indirectos"]["color"], fontcolor='white', color='none', fontsize='10')
            for j, p_data in enumerate(f_dir):
                if item.get('padre') == p_data.get('texto'):
                    dot.edge(f"FD{j}", node_id)

    # 4. Medios Directos
    m_dir = [it for it in datos.get("Medios Directos", []) if it.get('texto')]
    with dot.subgraph() as s:
        s.attr(rank='same'); s.node('L_MD', shape='plaintext', style='none')
        for i, item in enumerate(m_dir):
            node_id = f"MD{i}"
            s.node(node_id, limpiar(item['texto']), fillcolor=CONFIG_OBJ["Medios Directos"]["color"], fontcolor='black', color='none')
            if obj_gen: dot.edge(node_id, "OG")

    # 5. Medios Indirectos
    m_ind = [it for it in datos.get("Medios Indirectos", []) if it.get('texto')]
    with dot.subgraph() as s:
        s.attr(rank='same'); s.node('L_MI', shape='plaintext', style='none')
        for i, item in enumerate(m_ind):
            node_id = f"MI{i}"
            s.node(node_id, limpiar(item['texto']), fillcolor=CONFIG_OBJ["Medios Indirectos"]["color"], fontcolor='white', color='none', fontsize='10')
            for j, p_data in enumerate(m_dir):
                if item.get('padre') == p_data.get('texto'):
                    dot.edge(node_id, f"MD{j}")
                
    return dot

# --- RENDERIZADO DE TARJETA ---
def render_card_obj(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color_barra = CONFIG_OBJ.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 12px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    
    texto_viejo = item.get('texto', '')
    nuevo_texto = st.text_area("t", value=texto_viejo, key=f"obj_txt_{id_u}", label_visibility="collapsed")
    
    if st.button("🗑️", key=f"obj_btn_{id_u}"):
        st.session_state['arbol_objetivos'][seccion].pop(idx); guardar_datos_nube(); st.rerun()
    
    if nuevo_texto != texto_viejo:
        st.session_state['arbol_objetivos'][seccion][idx]['texto'] = nuevo_texto.upper()
        guardar_datos_nube()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True, type="primary"):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {"Efectos Indirectos": "Fines Indirectos", "Efectos Directos": "Fines Directos", "Problema Principal": "Objetivo General", "Causas Directas": "Medios Directos", "Causas Indirectas": "Medios Indirectos"}
        for k in CONFIG_OBJ: st.session_state['arbol_objetivos'][k] = []
        for p_sec, o_sec in mapeo.items():
            for item in problemas.get(p_sec, []):
                if isinstance(item, dict):
                    nueva = {"texto": item.get('texto', '').upper(), "id_unico": str(uuid.uuid4()), "padre": item.get('padre', "").upper()}
                    st.session_state['arbol_objetivos'][o_sec].append(nueva)
        guardar_datos_nube(); st.rerun()
    
    st.divider()
    grafo = generar_grafo_objetivos()
    if grafo: 
        st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_objetivos.png", use_container_width=True)

    st.divider()
    with st.expander("⚠️ BORRADO TOTAL"):
        st.write("Esto reseteará el Árbol de Objetivos.")
        confirmar = st.checkbox("Confirmo el reseteo")
        if st.button("🔥 BORRAR TODO", disabled=not confirmar, use_container_width=True):
            for k in CONFIG_OBJ: st.session_state['arbol_objetivos'][k] = []
            guardar_datos_nube(); st.rerun()

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🌳 Visualización del Árbol", "📝 Constructor y Edición"])

with tab1:
    if not hay_datos:
        st.info("Utilice el botón en la barra lateral para importar los datos del Árbol de Problemas.")
    else:
        grafo_f = generar_grafo_objetivos()
        if grafo_f: st.image(grafo_f.pipe(format='png'), use_container_width=True)

with tab2:
    if not hay_datos:
        st.info("💡 Importe sus datos para comenzar la edición.")
    else:
        st.subheader("📋 Panel de Edición de Objetivos")

        def mostrar_seccion_jerarquica(tipo_padre, tipo_hijo):
            padres = [p for p in st.session_state['arbol_objetivos'].get(tipo_padre, []) if isinstance(p, dict)]
            hijos = st.session_state['arbol_objetivos'].get(tipo_hijo, [])
            if not padres: return
            
            st.write(f"**{tipo_padre} e {tipo_hijo}**")
            hijos_por_p = [[(idx, h) for idx, h in enumerate(hijos) if h.get('padre') == p.get('texto')] for p in padres]
            max_h = max([len(lista) for lista in hijos_por_p]) if hijos_por_p else 0

            # FILAS PARA FINES (Crecen hacia arriba)
            if "Fin" in tipo_padre:
                for h_idx in range(max_h - 1, -1, -1):
                    cols = st.columns(len(padres))
                    for p_idx, col in enumerate(cols):
                        with col:
                            if h_idx < len(hijos_por_p[p_idx]):
                                idx_real, h_data = hijos_por_p[p_idx][h_idx]
                                render_card_obj(tipo_hijo, h_data, idx_real)
                            else: st.empty()
                cols_p = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    with cols_p[i]: render_card_obj(tipo_padre, p_data, i)
            
            # FILAS PARA MEDIOS (Crecen hacia abajo)
            else:
                cols_p = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    with cols_p[i]: render_card_obj(tipo_padre, p_data, i)
                for h_idx in range(max_h):
                    cols = st.columns(len(padres))
                    for p_idx, col in enumerate(cols):
                        with col:
                            if h_idx < len(hijos_por_p[p_idx]):
                                idx_real, h_data = hijos_por_p[p_idx][h_idx]
                                render_card_obj(tipo_hijo, h_data, idx_real)
                            else: st.empty()

        mostrar_seccion_jerarquica("Fines Directos", "Fines Indirectos")
        st.markdown("---")
        pc_og = [it for it in st.session_state['arbol_objetivos'].get("Objetivo General", []) if isinstance(it, dict)]
        if pc_og: 
            st.write("**Objetivo General**")
            render_card_obj("Objetivo General", pc_og[0], 0)
        st.markdown("---")
        mostrar_seccion_jerarquica("Medios Directos", "Medios Indirectos")
