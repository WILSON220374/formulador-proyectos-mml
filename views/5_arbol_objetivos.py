import streamlit as st
import graphviz
import os
import uuid
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia y Memoria
inicializar_session()

# --- ESTILO GLOBAL (Interfaz Limpia y Tarjetas) ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    /* Estética de Tarjetas: Fusión total con color */
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        border: none !important;           
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #000 !important;
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
        position: relative;
        z-index: 2;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ESTÁNDAR ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🎯 5. Árbol de Objetivos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Transformación de problemas en estados positivos y medios para alcanzarlos.</div>', unsafe_allow_html=True)
    
    hay_datos = any(st.session_state.get('arbol_objetivos', {}).values())
    progreso = 1.0 if hay_datos else 0.0
    st.progress(progreso, text=f"Nivel de Completitud: {int(progreso * 100)}%")

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- CONFIGURACIÓN DE COLORES Y NIVELES ---
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FIN INDIRECTO"},
    "Fines Directos": {"color": "#80BFFF", "label": "FIN DIRECTO"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "MEDIO DIRECTO"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "MEDIO INDIRECTO"}
}

# --- MOTOR DE DIBUJO (GRAPHVIZ) ---
def generar_grafo_objetivos():
    datos = st.session_state.get('arbol_objetivos', {})
    if not any(datos.values()): return None
    
    dot = graphviz.Digraph(format='png')
    dot.attr(label='ÁRBOL DE OBJETIVOS', labelloc='t', fontsize='35', fontname='Arial Bold', fontcolor='#333333')
    dot.attr(dpi='300', rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')
    dot.attr('node', fontsize='18', fontcolor='#31333F', fontname='Arial Bold', style='filled', color='none', margin='0.6,0.4', shape='box')
    
    def limpiar(t, w=45): return "\n".join(textwrap.wrap(str(t).upper(), width=w))

    # Nodos Centrales
    if datos.get("Fin Último"):
        dot.node("FU", limpiar(datos["Fin Último"][0]['texto']), fillcolor=CONFIG_OBJ["Fin Último"]["color"])
    if datos.get("Objetivo General"):
        dot.node("OG", limpiar(datos["Objetivo General"][0]['texto']), fillcolor=CONFIG_OBJ["Objetivo General"]["color"])
        if datos.get("Fin Último"): dot.edge("OG", "FU", style="invis")

    # Ramas: Fines y Medios
    for p_sec, h_sec, p_id_base, h_id_base, edge_dir in [
        ("Fines Directos", "Fines Indirectos", "FD", "FI", "forward"),
        ("Medios Directos", "Medios Indirectos", "MD", "MI", "back")
    ]:
        padres = datos.get(p_sec, [])
        for i, p in enumerate(padres):
            p_node = f"{p_id_base}{i}"
            dot.node(p_node, limpiar(p['texto']), fillcolor=CONFIG_OBJ[p_sec]["color"])
            if datos.get("Objetivo General"):
                if edge_dir == "forward": dot.edge("OG", p_node)
                else: dot.edge(p_node, "OG")
            
            hijos = [h for h in datos.get(h_sec, []) if h.get('padre') == p['texto']]
            for j, h in enumerate(hijos):
                h_node = f"{h_id_base}{i}_{j}"
                dot.node(h_node, limpiar(h['texto']), fillcolor=CONFIG_OBJ[h_sec]["color"])
                if edge_dir == "forward": dot.edge(p_node, h_node)
                else: dot.edge(h_node, p_node)
                
    return dot

# --- RENDERIZADO DE TARJETA ---
def render_card_obj(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    st.markdown(f'<div style="background-color: {CONFIG_OBJ[seccion]["color"]}; height: 10px; border-radius: 10px 10px 0 0; margin-bottom: 0px;"></div>', unsafe_allow_html=True)
    nuevo = st.text_area("t", value=item['texto'], key=f"obj_txt_{id_u}", label_visibility="collapsed")
    if st.button("🗑️", key=f"obj_btn_{id_u}"):
        st.session_state['arbol_objetivos'][seccion].pop(idx); guardar_datos_nube(); st.rerun()
    if nuevo != item['texto']: item['texto'] = nuevo; guardar_datos_nube()

# --- SIDEBAR: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True, type="primary"):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {
            "Efectos Indirectos": "Fines Indirectos", 
            "Efectos Directos": "Fines Directos", 
            "Problema Principal": "Objetivo General", 
            "Causas Directas": "Medios Directos", 
            "Causas Indirectas": "Medios Indirectos"
        }
        for k in CONFIG_OBJ: st.session_state['arbol_objetivos'][k] = []
        
        for p_sec, o_sec in mapeo.items():
            for item in problemas.get(p_sec, []):
                nueva = {
                    "texto": item['texto'].upper(), 
                    "id_unico": str(uuid.uuid4()),
                    "padre": item.get('padre', "").upper()
                }
                st.session_state['arbol_objetivos'][o_sec].append(nueva)
        
        if not st.session_state['arbol_objetivos']["Fin Último"]:
            st.session_state['arbol_objetivos']["Fin Último"] = [{"texto": "MEJORAR LA CALIDAD DE VIDA", "id_unico": str(uuid.uuid4())}]
        
        guardar_datos_nube(); st.rerun()

    st.divider()
    grafo = generar_grafo_objetivos()
    if grafo: st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_objetivos.png", use_container_width=True)

# --- PANEL PRINCIPAL ---
if not hay_datos:
    st.info("Utilice el botón en la barra lateral para importar los datos desde el Árbol de Problemas.")
else:
    grafo = generar_grafo_objetivos()
    if grafo: st.image(grafo.pipe(format='png'), use_container_width=True)
    
    st.divider()
    st.subheader("📋 Panel de Edición")

    def render_seccion_jerarquica(tipo_padre, tipo_hijo):
        padres = st.session_state['arbol_objetivos'].get(tipo_padre, [])
        hijos = st.session_state['arbol_objetivos'].get(tipo_hijo, [])
        if not padres: return
        
        st.write(f"**{tipo_padre} e {tipo_hijo}**")
        hijos_por_p = [[(idx, h) for idx, h in enumerate(hijos) if h.get('padre') == p['texto']] for p in padres]
        max_h = max([len(lista) for lista in hijos_por_p]) if hijos_por_p else 0

        # FINES: Indirectos (hijos) arriba, Directos (padres) abajo
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
        
        # MEDIOS: Directos (padres) arriba, Indirectos (hijos) abajo
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

    # 1. Fines
    pc_fu = st.session_state['arbol_objetivos'].get("Fin Último", [])
    if pc_fu: 
        st.write("**Fin Último**")
        render_card_obj("Fin Último", pc_fu[0], 0)
    render_seccion_jerarquica("Fines Directos", "Fines Indirectos")
    
    st.markdown("---")
    # 2. Objetivo General
    pc_og = st.session_state['arbol_objetivos'].get("Objetivo General", [])
    if pc_og: 
        st.write("**Objetivo General**")
        render_card_obj("Objetivo General", pc_og[0], 0)
    
    st.markdown("---")
    # 3. Medios
    render_seccion_jerarquica("Medios Directos", "Medios Indirectos")
