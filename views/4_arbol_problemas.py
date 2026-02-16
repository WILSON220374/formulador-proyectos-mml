#import streamlit as st
import graphviz
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTILO GLOBAL ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

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

    [data-testid="stImage"] img { border-radius: 12px; pointer-events: none; }
    button[title="View fullscreen"] { display: none !important; }
    
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.3rem !important;
        margin-top: -15px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_l = st.columns([0.8, 0.2], vertical_alignment="center")
with col_t:
    st.markdown('<p class="titulo-seccion">🌳 4. Árbol de Problemas</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo-gris">Identifique las causas y efectos del problema central.</p>', unsafe_allow_html=True)
with col_l:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- CONFIGURACIÓN DE SECCIONES ---
CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#FEE2E2", "borde": "#EF4444", "label": "🔴 Efecto Indirecto"},
    "Efectos Directos": {"color": "#FEF2F2", "borde": "#F87171", "label": "🏮 Efecto Directo"},
    "Problema Principal": {"color": "#EFF6FF", "borde": "#3B82F6", "label": "💎 Problema Central"},
    "Causas Directas": {"color": "#F0FDF4", "borde": "#4ADE80", "label": "🌳 Causa Directa"},
    "Causas Indirectas": {"color": "#F6FEF9", "borde": "#86EFAC", "label": "🌿 Causa Indirecta"}
}

# Inicializar si no existe
if 'arbol_tarjetas' not in st.session_state:
    st.session_state['arbol_tarjetas'] = {k: [] for k in CONFIG_PROB.keys()}

# --- FUNCIONES DE APOYO ---
def render_card(tipo, data, index):
    # SANEAMIENTO: Si data no es un diccionario válido, no renderizar nada
    if not isinstance(data, dict) or 'texto' not in data:
        return

    conf = CONFIG_PROB[tipo]
    with st.container():
        st.markdown(f"""
            <div style="background-color: {conf['borde']}; color: white; padding: 5px; 
            border-radius: 10px 10px 0 0; text-align: center; font-size: 11px; font-weight: bold; margin-bottom: -5px;">
                {conf['label']}
            </div>
        """, unsafe_allow_html=True)
        
        # El área de texto muestra el contenido
        nuevo_texto = st.text_area(
            f"T_{tipo}_{index}", 
            value=data['texto'], 
            key=f"input_{tipo}_{index}", 
            label_visibility="collapsed"
        )
        
        # Botón para eliminar
        if st.button("🗑️", key=f"del_{tipo}_{index}"):
            st.session_state['arbol_tarjetas'][tipo].pop(index)
            guardar_datos_nube()
            st.rerun()
            
        # Guardado automático si cambia el texto
        if nuevo_texto != data['texto']:
            st.session_state['arbol_tarjetas'][tipo][index]['texto'] = nuevo_texto
            guardar_datos_nube()

def generar_grafo_problemas():
    dot = graphviz.Digraph(comment='Arbol de Problemas')
    dot.attr(rankdir='BT', nodesep='0.5', ranksep='0.6')
    
    # Estilo base de nodos
    dot.attr('node', shape='box', style='filled, rounded', fontname='Arial Bold', fontsize='11')
    
    # 1. Problema Central (el ancla)
    pc_lista = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
    if not pc_lista: return None
    
    # SANEAMIENTO: Tomar solo el primer elemento válido
    pc_data = pc_lista[0] if isinstance(pc_lista[0], dict) else {"texto": "Problema no definido"}
    pc_txt = pc_data.get('texto', '...')
    dot.node('PC', pc_txt, fillcolor='#DBEAFE', color='#3B82F6', penwidth='3')

    # 2. Causas y Efectos
    for seccion, prefijo in [("Causas Directas", "CD"), ("Efectos Directos", "ED")]:
        items = st.session_state['arbol_tarjetas'].get(seccion, [])
        for i, item in enumerate(items):
            if not isinstance(item, dict): continue
            node_id = f"{prefijo}_{i}"
            dot.node(node_id, item['texto'], fillcolor='#F0FDF4' if 'Causa' in seccion else '#FEF2F2')
            
            # Relación con PC
            if "Causa" in seccion: dot.edge(node_id, 'PC')
            else: dot.edge('PC', node_id)
            
            # 3. Sub-niveles (Indirectos)
            sub_sec = seccion.replace("Directas", "Indirectas")
            subs = st.session_state['arbol_tarjetas'].get(sub_sec, [])
            for j, sub in enumerate(subs):
                if isinstance(sub, dict) and sub.get('padre') == item['texto']:
                    sub_id = f"{prefijo}I_{j}"
                    dot.node(sub_id, sub['texto'], fillcolor='#F6FEF9' if 'Causa' in seccion else '#FFF1F2', fontsize='10')
                    if "Causa" in seccion: dot.edge(sub_id, node_id)
                    else: dot.edge(node_id, sub_id)
    
    return dot

# --- SIDEBAR: GESTIÓN ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Sección:", list(CONFIG_PROB.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción:")
        padre_asociado = None
        
        if "Indirect" in tipo_sel:
            p_key = "Efectos Directos" if "Efecto" in tipo_sel else "Causas Directas"
            
            # AJUSTE DE SEGURIDAD: Filtramos para ignorar elementos corruptos (TypeError Fix)
            lista_raw = st.session_state.get('arbol_tarjetas', {}).get(p_key, [])
            opciones = [it['texto'] for it in lista_raw if isinstance(it, dict) and 'texto' in it]
            
            if opciones: 
                padre_asociado = st.selectbox("Vincular a:", opciones)
            else:
                st.warning(f"⚠️ Primero cree {p_key}.")
        
        generar = st.form_submit_button("Generar")
        if generar and texto_input:
            nueva = {"texto": texto_input, "id_unico": str(uuid.uuid4())}
            if padre_asociado: nueva["padre"] = padre_asociado
            
            if tipo_sel == "Problema Principal": st.session_state['arbol_tarjetas'][tipo_sel] = [nueva]
            else: st.session_state['arbol_tarjetas'][tipo_sel].append(nueva)
            
            guardar_datos_nube()
            st.rerun()

    st.divider()
    grafo = generar_grafo_problemas()
    if grafo: 
        st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_problemas.png", use_container_width=True)

# --- PANEL VISUAL DEL ÁRBOL ---
# Saneamiento de las listas antes de renderizar
for k in st.session_state['arbol_tarjetas']:
    if isinstance(st.session_state['arbol_tarjetas'][k], list):
        st.session_state['arbol_tarjetas'][k] = [it for it in st.session_state['arbol_tarjetas'][k] if isinstance(it, dict) and 'texto' in it]

def render_seccion_jerarquica(tipo_padre, tipo_hijo, inversion=False):
    padres = st.session_state['arbol_tarjetas'].get(tipo_padre, [])
    hijos = st.session_state['arbol_tarjetas'].get(tipo_hijo, [])
    
    if padres:
        hijos_por_p = []
        for p in padres:
            h_rel = [(idx, h) for idx, h in enumerate(hijos) if h.get('padre') == p['texto']]
            hijos_por_p.append(h_rel)
        
        max_h = max([len(h) for h in hijos_por_p]) if hijos_por_p else 0
        
        if inversion: # Efectos: Hijos arriba
            for h_idx in range(max_h - 1, -1, -1):
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
        else: # Causas: Hijos abajo
            cols_p = st.columns(len(padres))
            for i, p_data in enumerate(padres):
                with cols_p[i]: render_card(tipo_padre, p_data, i)
            for h_idx in range(max_h):
                cols = st.columns(len(padres))
                for p_idx, col in enumerate(cols):
                    with col:
                        if h_idx < len(hijos_por_p[p_idx]):
                            idx_real, h_data = hijos_por_p[p_idx][h_idx]
                            render_card(tipo_hijo, h_data, idx_real)
                        else: st.empty()

render_seccion_jerarquica("Efectos Directos", "Efectos Indirectos", inversion=True)
st.markdown("---")
pc_l = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
if pc_l:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: render_card("Problema Principal", pc_l[0], 0)
else:
    st.info("💡 Use el menú lateral para definir el Problema Principal.")
st.markdown("---")
render_seccion_jerarquica("Causas Directas", "Causas Indirectas")
