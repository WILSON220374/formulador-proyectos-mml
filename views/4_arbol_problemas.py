import streamlit as st
import graphviz
import os
import uuid
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- CAPA 1: LIMPIEZA PROFUNDA (ELIMINA "NONE" DE LA NUBE) ---
if 'arbol_tarjetas' in st.session_state:
    datos_corruptos = False
    for seccion in st.session_state['arbol_tarjetas']:
        lista_original = st.session_state['arbol_tarjetas'][seccion]
        if isinstance(lista_original, list):
            # Filtro estricto: Solo fichas con texto real, sin "None" y con longitud mínima
            lista_limpia = [
                it for it in lista_original if isinstance(it, dict) and 
                it.get('texto') and 
                str(it.get('texto')).strip().upper() != "NONE" and
                len(str(it.get('texto')).strip()) > 2
            ]
            if len(lista_limpia) != len(lista_original):
                st.session_state['arbol_tarjetas'][seccion] = lista_limpia
                datos_corruptos = True
    
    # Si detectamos basura, forzamos el guardado en Supabase para limpiar la nube
    if datos_corruptos:
        guardar_datos_nube()
        st.rerun()

# --- CAPA 2: DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 10rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;           
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 13px !important;
    }

    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ef4444 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 10px 10px 0 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🌳 4. Árbol de Problemas</div>', unsafe_allow_html=True)
    st.markdown('Construcción lógica con sistema de autolimpieza de datos.', unsafe_allow_html=True)
    pc_data = st.session_state.get('arbol_tarjetas', {}).get("Problema Principal", [])
    hay_datos = len(pc_data) > 0

with col_img:
    if os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- CAPA 3: MOTOR DE DIBUJO CON GUÍA LATERAL (ESTILO PROFESIONAL) ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_tarjetas', {})
    pc = [it for it in datos.get("Problema Principal", []) if it.get('texto')]
    if not pc: return None

    dot = graphviz.Digraph(format='png')
    dot.attr(label='\nÁRBOL DE PROBLEMAS\n ', labelloc='t', fontsize='28', fontname='Arial Bold', fontcolor='#1E3A8A')
    dot.attr(size='16,12!', ratio='fill', center='true', dpi='300') 
    dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')
    
    def limpiar(t): return "\n".join(textwrap.wrap(str(t).upper(), width=25))
    COLORS = {"PC": "#A93226", "ED": "#2E86C1", "EI": "#884EA0", "CD": "#D4AC0D", "CI": "#CA6F1E"}

    # Guía Lateral Izquierda
    etiquetas = {"L_EI": "EFECTO\nINDIRECTO", "L_ED": "EFECTO\nDIRECTO", "L_PC": "PROBLEMA\nCENTRAL", "L_CD": "CAUSA\nDIRECTA", "L_CI": "CAUSA\nINDIRECTA"}
    for id_e, txt in etiquetas.items():
        dot.node(id_e, txt, shape='plaintext', fontcolor='#94a3b8', fontsize='10', fontname='Arial Bold')
    dot.edge("L_CI", "L_CD", style='invis'); dot.edge("L_CD", "L_PC", style='invis'); dot.edge("L_PC", "L_ED", style='invis'); dot.edge("L_ED", "L_EI", style='invis')

    # Problema Central
    with dot.subgraph() as s:
        s.attr(rank='same'); s.node('L_PC')
        s.node('PC', limpiar(pc[0]['texto']), fillcolor=COLORS["PC"], fontcolor='white', color='none', width='4.5')

    # Ramas de Causas y Efectos
    for tipo, id_p, l_node, edge_dir, col in [("Efectos Directos", "ED", "L_ED", "forward", COLORS["ED"]), ("Causas Directas", "CD", "L_CD", "back", COLORS["CD"])]:
        items = [it for it in datos.get(tipo, []) if it.get('texto')]
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node(l_node)
            for i, it in enumerate(items):
                node_id = f"{id_p}{i}"
                s.node(node_id, limpiar(it['texto']), fillcolor=col, fontcolor='white' if col != COLORS["CD"] else 'black', color='none')
                dot.edge('PC', node_id) if edge_dir == "forward" else dot.edge(node_id, 'PC')
                
                # Indirectas (Hijos)
                h_tipo = "Efectos Indirectos" if "Efecto" in tipo else "Causas Indirectas"
                h_col = COLORS["EI"] if "Efecto" in tipo else COLORS["CI"]
                h_l_node = "L_EI" if "Efecto" in tipo else "L_CI"
                hijos = [h for h in datos.get(h_tipo, []) if h.get('padre') == it['texto'] and h.get('texto')]
                with dot.subgraph() as sh:
                    sh.attr(rank='same'); sh.node(h_l_node)
                    for j, h in enumerate(hijos):
                        h_id = f"{id_p}I{i}_{j}"
                        sh.node(h_id, limpiar(h['texto']), fillcolor=h_col, fontcolor='white', color='none', fontsize='9')
                        dot.edge(node_id, h_id) if edge_dir == "forward" else dot.edge(h_id, node_id)
    return dot

# --- RENDERIZADO DE TARJETA ---
def render_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color = {"Efectos Indirectos": "#884EA0", "Efectos Directos": "#2E86C1", "Problema Principal": "#A93226", "Causas Directas": "#D4AC0D", "Causas Indirectas": "#CA6F1E"}.get(seccion, "#ccc")
    st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    
    texto_actual = item.get('texto', '')
    nuevo = st.text_area("t", value=texto_actual, key=f"txt_{id_u}", label_visibility="collapsed")
    
    if st.button("🗑️", key=f"btn_{id_u}"):
        st.session_state['arbol_tarjetas'][seccion].pop(idx)
        guardar_datos_nube(); st.rerun()
    if nuevo != texto_actual and len(nuevo.strip()) > 2: 
        st.session_state['arbol_tarjetas'][seccion][idx]['texto'] = nuevo.strip().upper()
        guardar_datos_nube()

# --- SIDEBAR: GESTIÓN Y BORRADO SEGURO ---
with st.sidebar:
    st.header("➕ Agregar Ficha")
    tipo_sel = st.selectbox("Nivel:", ["Efectos Indirectos", "Efectos Directos", "Problema Principal", "Causas Directas", "Causas Indirectas"], index=2)
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción:")
        padre_asociado = None
        if "Indirect" in tipo_sel:
            p_key = "Efectos Directos" if "Efecto" in tipo_sel else "Causas Directas"
            opciones = [it['texto'] for it in st.session_state.get('arbol_tarjetas', {}).get(p_key, []) if isinstance(it, dict)]
            if opciones: padre_asociado = st.selectbox("Vincular a:", opciones)
        
        if st.form_submit_button("Generar Ficha") and texto_input.strip():
            nueva = {"texto": texto_input.strip().upper(), "id_unico": str(uuid.uuid4())}
            if padre_asociado: nueva["padre"] = padre_asociado
            if tipo_sel == "Problema Principal": st.session_state['arbol_tarjetas'][tipo_sel] = [nueva]
            else: st.session_state['arbol_tarjetas'][tipo_sel].append(nueva)
            guardar_datos_nube(); st.rerun()

    st.divider()
    grafo = generar_grafo_problemas()
    if grafo: st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_problemas.png", use_container_width=True)

    # --- BOTÓN DE BORRADO SEGURO (ELIMINA LOS "NONE" DE RAÍZ) ---
    with st.expander("⚠️ Zona de Peligro"):
        st.write("Eliminar permanentemente todos los datos del árbol en la nube.")
        confirmar = st.checkbox("Confirmo el reseteo total")
        if st.button("🔥 BORRAR TODO", disabled=not confirmar, use_container_width=True):
            st.session_state['arbol_tarjetas'] = {"Efectos Indirectos": [], "Efectos Directos": [], "Problema Principal": [], "Causas Directas": [], "Causas Indirectas": []}
            guardar_datos_nube()
            st.rerun()

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🌳 Visualización", "📝 Constructor"])

with tab1:
    if not hay_datos:
        st.info("🎯 Defina el Problema Principal para visualizar el árbol.")
    else:
        g = generar_grafo_problemas()
        if g: st.image(g.pipe(format='png'), use_container_width=True)

with tab2:
    if not hay_datos:
        st.info("💡 Use el menú lateral para construir su árbol.")
    else:
        st.subheader("📋 Panel de Edición Lógica")
        def mostrar_seccion(p, h):
            padres = [it for it in st.session_state['arbol_tarjetas'].get(p, []) if it.get('texto')]
            if padres:
                st.write(f"**{p}**")
                cols = st.columns(len(padres))
                for i, it in enumerate(padres):
                    with cols[i]:
                        render_card(p, it, i)
                        hijos = [hj for hj in st.session_state['arbol_tarjetas'].get(h, []) if hj.get('padre') == it.get('texto')]
                        for hj in hijos:
                            idx_r = st.session_state['arbol_tarjetas'][h].index(hj)
                            render_card(h, hj, idx_r)

        mostrar_seccion("Efectos Directos", "Efectos Indirectos")
        st.divider()
        st.write("**Problema Principal**")
        render_card("Problema Principal", pc_data[0], 0)
        st.divider()
        mostrar_seccion("Causas Directas", "Causas Indirectas")
