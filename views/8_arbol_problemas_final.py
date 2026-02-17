import streamlit as st
import graphviz
import os
import uuid
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia
inicializar_session()

# --- SANEAMIENTO Y MIGRACIÓN DE DATOS ---
if 'arbol_problemas_final' not in st.session_state:
    st.session_state['arbol_problemas_final'] = {}

# Nueva estructura para la Matriz de Marco Lógico (Referencia estructurada)
if 'referencia_manual_prob' not in st.session_state['arbol_problemas_final']:
    st.session_state['arbol_problemas_final']['referencia_manual_prob'] = {
        "problema_central": "", "causas_directas": [], "causas_indirectas": []
    }

ref_prob = st.session_state['arbol_problemas_final']['referencia_manual_prob']

# Conversión automática: Si hay texto viejo en el estado, lo migramos a la lista nueva
for clave in ['causas_directas', 'causas_indirectas']:
    if isinstance(ref_prob.get(clave), str):
        texto_viejo = ref_prob[clave]
        if texto_viejo.strip():
            items = [l.strip().lstrip('*-•').strip() for l in texto_viejo.split('\n') if l.strip()]
            ref_prob[clave] = items
        else:
            ref_prob[clave] = []

# --- DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 10rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    /* Estilo para las tarjetas de problemas (Rojizo) */
    .list-item-prob {
        background-color: #fef2f2;
        border: 1px solid #fee2e2;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        color: #991b1b;
    }

    .poda-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 0 0 10px 10px;
        padding: 15px;
        text-align: center;
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 5px;
    }

    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ef4444 !important;
        font-size: 1.1rem !important;
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

# --- FUNCIONES DE GESTIÓN (CALLBACKS) ---
def agregar_item_prob(clave_lista, clave_temporal):
    nuevo_texto = st.session_state.get(clave_temporal, "").strip()
    if nuevo_texto:
        items = [l.strip().lstrip('*-•').strip() for l in nuevo_texto.split('\n') if l.strip()]
        st.session_state['arbol_problemas_final']['referencia_manual_prob'][clave_lista].extend(items)
        st.session_state[clave_temporal] = ""
        guardar_datos_nube()

def eliminar_item_prob(clave_lista, indice):
    st.session_state['arbol_problemas_final']['referencia_manual_prob'][clave_lista].pop(indice)
    guardar_datos_nube()

def actualizar_prob_central():
    st.session_state['arbol_problemas_final']['referencia_manual_prob']['problema_central'] = st.session_state.temp_prob_central
    guardar_datos_nube()

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🌳 8. Árbol de Problemas Final</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Ajuste definitivo del diagnóstico basado en la estrategia.</div>', unsafe_allow_html=True)
    
    datos_prob = st.session_state.get('arbol_problemas_final', {})
    hay_datos = any(datos_prob[k] for k in datos_prob.keys() if k != 'referencia_manual_prob')
    st.progress(1.0 if hay_datos else 0.0)

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#B3D9FF", "label": "EFECTOS\nINDIRECTOS"},
    "Efectos Directos":   {"color": "#80BFFF", "label": "EFECTOS\nDIRECTOS"},
    "Problema Principal": {"color": "#FFB3BA", "label": "PROBLEMA\nCENTRAL"},
    "Causas Directas":    {"color": "#FFFFBA", "label": "CAUSAS\nDIRECTAS"},
    "Causas Indirectas":  {"color": "#FFDFBA", "label": "CAUSAS\nINDIRECTAS"}
}

# --- MOTOR DE DIBUJO ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_problemas_final', {})
    claves_graficas = [k for k in datos.keys() if k not in ['referencia_manual', 'referencia_manual_prob']]
    if not any(datos.get(k) for k in claves_graficas): return None
    
    dot = graphviz.Digraph(format='png')
    dot.attr(label='\nÁRBOL DE PROBLEMAS FINAL\n ', labelloc='t', fontsize='28', fontname='Arial Bold', fontcolor='#1E3A8A')
    dot.attr(size='16,12!', ratio='fill', center='true', dpi='300') 
    dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')
    
    def limpiar(t): return "\n".join(textwrap.wrap(str(t).upper(), width=25))

    niv_list = ["CI", "CD", "PP", "ED", "EI"]
    MAPA_LLAVES = {"CI": "Causas Indirectas", "CD": "Causas Directas", "PP": "Problema Principal", "ED": "Efectos Directos", "EI": "Efectos Indirectos"}
    
    for niv in niv_list:
        conf = CONFIG_PROB[MAPA_LLAVES[niv]]
        dot.node(f"L_{niv}", conf['label'], shape='plaintext', fontcolor='#475569', fontsize='11', fontname='Arial Bold', style='none')
    for i in range(len(niv_list)-1):
        dot.edge(f"L_{niv_list[i]}", f"L_{niv_list[i+1]}", style='invis')

    prob_pp = [it for it in datos.get("Problema Principal", []) if it.get('texto')]
    if prob_pp: dot.node("PP", limpiar(prob_pp[0]['texto']), fillcolor=CONFIG_PROB["Problema Principal"]["color"], fontcolor='black', color='none', width='4.5')

    for tipo, p_id, h_tipo in [("Efectos Directos", "PP", "Efectos Indirectos")]:
        items = [it for it in datos.get(tipo, []) if it.get('texto')]
        for i, item in enumerate(items):
            n_id = f"ED{i}"
            dot.node(n_id, limpiar(item['texto']), fillcolor=CONFIG_PROB[tipo]["color"], fontcolor='black', color='none')
            dot.edge("PP", n_id)
            hijos = [h for h in datos.get(h_tipo, []) if h.get('padre') == item.get('texto')]
            for j, h in enumerate(hijos):
                h_id = f"EI{i}_{j}"
                dot.node(h_id, limpiar(h['texto']), fillcolor=CONFIG_PROB[h_tipo]["color"], fontcolor='black', color='none', fontsize='10')
                dot.edge(n_id, h_id)

    for tipo, p_id, h_tipo in [("Causas Directas", "PP", "Causas Indirectas")]:
        items = [it for it in datos.get(tipo, []) if it.get('texto')]
        for i, item in enumerate(items):
            n_id = f"CD{i}"
            dot.node(n_id, limpiar(item['texto']), fillcolor=CONFIG_PROB[tipo]["color"], fontcolor='black', color='none')
            dot.edge(n_id, "PP")
            hijos = [h for h in datos.get(h_tipo, []) if h.get('padre') == item.get('texto')]
            for j, h in enumerate(hijos):
                h_id = f"CI{i}_{j}"
                dot.node(h_id, limpiar(h['texto']), fillcolor=CONFIG_PROB[h_tipo]["color"], fontcolor='black', color='none', fontsize='10')
                dot.edge(h_id, n_id)
    return dot

# --- RENDERIZADO DE TARJETA MODO PODA ---
def render_poda_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color_barra = CONFIG_PROB.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 10px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="poda-card">{str(item.get("texto", "")).upper()}</div>', unsafe_allow_html=True)
    st.button("🗑️", key=f"poda_prob_{id_u}", on_click=lambda: (st.session_state['arbol_problemas_final'][seccion].pop(idx), guardar_datos_nube()))

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    def importar_p4():
        origen = st.session_state.get('arbol_tarjetas', {})
        st.session_state['arbol_problemas_final'] = copy.deepcopy(origen)
        guardar_datos_nube()
    st.button("♻️ Importar desde Paso 4", use_container_width=True, type="primary", on_click=importar_p4)
    st.divider()
    grafo = generar_grafo_problemas()
    if grafo: st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_problemas_final.png", use_container_width=True)

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🌳 Visualización", "✂️ Poda y Ajuste"])

with tab1:
    g_f = generar_grafo_problemas()
    if g_f: st.image(g_f.pipe(format='png'), use_container_width=True)

with tab2:
    if hay_datos:
        # --- NUEVA SECCIÓN: PROBLEMAS A RESOLVER ---
        st.subheader("📌 Problemas a resolver")
        st.info("Estructure aquí el diagnóstico definitivo. Estos problemas se vincularán con la Matriz de Marco Lógico.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Problema Central**")
            st.text_area("Problema Central", value=ref_prob['problema_central'], key="temp_prob_central", 
                         label_visibility="collapsed", height=150, on_change=actualizar_prob_central)
        
        with col2:
            # 1. CAUSAS DIRECTAS
            st.markdown("**Causas Directas**")
            for i, item in enumerate(ref_prob['causas_directas']):
                c1, c2 = st.columns([0.9, 0.1])
                with c1: st.markdown(f"<div class='list-item-prob'>• {item}</div>", unsafe_allow_html=True)
                with c2: st.button("🗑️", key=f"del_cd_{i}", on_click=eliminar_item_prob, args=('causas_directas', i))
            
            # Input agregar CD
            ci1, ci2 = st.columns([0.85, 0.15])
            with ci1: st.text_area("Nueva CD", label_visibility="collapsed", key="new_cd", placeholder="Agregar causa directa...", height=68)
            with ci2: st.button("➕", key="btn_add_cd", on_click=agregar_item_prob, args=('causas_directas', 'new_cd'))

            st.divider()

            # 2. CAUSAS INDIRECTAS
            st.markdown("**Causas Indirectas**")
            for i, item in enumerate(ref_prob['causas_indirectas']):
                c1, c2 = st.columns([0.9, 0.1])
                with c1: st.markdown(f"<div class='list-item-prob'>• {item}</div>", unsafe_allow_html=True)
                with c2: st.button("🗑️", key=f"del_ci_{i}", on_click=eliminar_item_prob, args=('causas_indirectas', i))
            
            # Input agregar CI
            cii1, cii2 = st.columns([0.85, 0.15])
            with cii1: st.text_area("Nueva CI", label_visibility="collapsed", key="new_ci", placeholder="Agregar causa indirecta...", height=68)
            with cii2: st.button("➕", key="btn_add_ci", on_click=agregar_item_prob, args=('causas_indirectas', 'new_ci'))

        st.divider()

        # --- PANEL DE PODA ---
        st.subheader("📋 Panel de Poda")
        st.info("Solo lectura: Use la papelera para descartar lo que no sea parte del diagnóstico definitivo.")
        
        def mostrar_seccion_problemas(tipo_padre, tipo_hijo):
            datos_sec = st.session_state['arbol_problemas_final'].get(tipo_padre, [])
            padres_con_idx = [(idx, p) for idx, p in enumerate(datos_sec) if p.get('texto')]
            if not padres_con_idx: return
            st.write(f"**{tipo_padre}**")
            hijos = st.session_state['arbol_problemas_final'].get(tipo_hijo, [])
            h_por_p = [[(idx_h, h) for idx_h, h in enumerate(hijos) if h.get('padre') == p_d.get('texto')] for _, p_d in padres_con_idx]
            max_h = max([len(l) for l in h_por_p]) if h_por_p else 0
            if "Efectos" in tipo_padre:
                for h_idx in range(max_h - 1, -1, -1):
                    cols = st.columns(len(padres_con_idx))
                    for p_col, col in enumerate(cols):
                        with col:
                            if h_idx < len(h_por_p[p_col]): render_poda_card(tipo_hijo, h_por_p[p_col][h_idx][1], h_por_p[p_col][h_idx][0])
                            else: st.empty()
                cols_p = st.columns(len(padres_con_idx))
                for i, (idx_o, p_d) in enumerate(padres_con_idx):
                    with cols_p[i]: render_poda_card(tipo_padre, p_d, idx_o)
            else:
                cols_p = st.columns(len(padres_con_idx))
                for i, (idx_o, p_d) in enumerate(padres_con_idx):
                    with cols_p[i]: render_poda_card(tipo_padre, p_d, idx_o)
                for h_idx in range(max_h):
                    cols = st.columns(len(padres_con_idx))
                    for p_col, col in enumerate(cols):
                        with col:
                            if h_idx < len(h_por_p[p_col]): render_poda_card(tipo_hijo, h_por_p[p_col][h_idx][1], h_por_p[p_col][h_idx][0])
                            else: st.empty()

        mostrar_seccion_problemas("Efectos Directos", "Efectos Indirectos")
        st.markdown("---")
        pp_f = st.session_state['arbol_problemas_final'].get("Problema Principal", [])
        if pp_f: render_poda_card("Problema Principal", pp_f[0], 0)
        st.markdown("---")
        mostrar_seccion_problemas("Causas Directas", "Causas Indirectas")
