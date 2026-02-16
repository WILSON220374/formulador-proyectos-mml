import streamlit as st
import graphviz
import os
import uuid
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 10rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    .resumen-estrategico {
        background-color: #f0f7ff;
        border-left: 5px solid #1E3A8A;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
        font-size: 1.2rem !important;
        margin-top: -10px !important;
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
    st.markdown('<div class="titulo-seccion">🎯 7. Árbol de Objetivos Final</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Poda definitiva sincronizada con la alternativa seleccionada.</div>', unsafe_allow_html=True)
    
    datos_final = st.session_state.get('arbol_objetivos_final', {})
    hay_datos = any(datos_final.values()) if datos_final else False
    st.progress(1.0 if hay_datos else 0.0)

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

CONFIG_OBJ = {
    "Fin Último":        {"color": "#0E6251", "label": "FIN\nÚLTIMO"},
    "Fines Indirectos":  {"color": "#154360", "label": "FINES\nINDIRECTOS"},
    "Fines Directos":    {"color": "#1F618D", "label": "FINES\nDIRECTOS"},
    "Objetivo General":  {"color": "#C0392B", "label": "OBJETIVO\nGENERAL"},
    "Medios Directos":   {"color": "#F1C40F", "label": "OBJETIVOS\nESPECÍFICOS"},
    "Medios Indirectos": {"color": "#D35400", "label": "ACTIVIDADES"}
}

# --- RASTREO DE DATOS DESDE ALTERNATIVAS CONSOLIDADAS ---
# 1. Buscamos el nombre de la alternativa ganadora
nombre_ganadora = st.session_state.get('seleccion_final', "")

# 2. Buscamos en la lista de alternativas consolidadas (donde están los textos largos)
lista_consolidadas = st.session_state.get('alternativas_consolidadas', [])
datos_alternativa = {}

for alt in lista_consolidadas:
    # Verificamos si el nombre coincide con la seleccionada
    if alt.get('titulo', '') in nombre_ganadora or nombre_ganadora in alt.get('titulo', ''):
        datos_alternativa = alt
        break

# Extraemos la información para mostrarla en el Panel de Referencia
obj_ref = datos_alternativa.get('titulo', 'PENDIENTE DE SELECCIÓN').upper()
res_ref = datos_alternativa.get('resumen', 'No se encontró resumen.')
act_ref = datos_alternativa.get('actividades', 'No se encontraron actividades vinculadas.')

# --- MOTOR DE DIBUJO ---
def generar_grafo_final():
    datos = st.session_state.get('arbol_objetivos_final', {})
    if not any(datos.values()): return None
    
    dot = graphviz.Digraph(format='png')
    dot.attr(label='\nÁRBOL DE OBJETIVOS FINAL\n ', labelloc='t', fontsize='28', fontname='Arial Bold', fontcolor='#1E3A8A')
    dot.attr(size='16,12!', ratio='fill', center='true', dpi='300') 
    dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')
    
    def limpiar(t): return "\n".join(textwrap.wrap(str(t).upper(), width=25))

    MAPA_LLAVES = {"MI": "Medios Indirectos", "MD": "Medios Directos", "OG": "Objetivo General", "FD": "Fines Directos", "FI": "Fines Indirectos", "FU": "Fin Último"}
    niv_list = ["MI", "MD", "OG", "FD", "FI", "FU"]
    
    for niv in niv_list:
        conf = CONFIG_OBJ[MAPA_LLAVES[niv]]
        dot.node(f"L_{niv}", conf['label'], shape='plaintext', fontcolor=conf['color'], fontsize='11', fontname='Arial Bold', style='none')
    for i in range(len(niv_list)-1):
        dot.edge(f"L_{niv_list[i]}", f"L_{niv_list[i+1]}", style='invis')

    obj_gen = [it for it in datos.get("Objetivo General", []) if it.get('texto')]
    with dot.subgraph() as s:
        s.attr(rank='same'); s.node("L_OG")
        if obj_gen: s.node("OG", limpiar(obj_gen[0]['texto']), fillcolor=CONFIG_OBJ["Objetivo General"]["color"], fontcolor='white', color='none', width='4.5')

    for tipo, p_key, h_tipo in [("Fines Directos", "FD", "Fines Indirectos"), ("Medios Directos", "MD", "Medios Indirectos")]:
        items = [it for it in datos.get(tipo, []) if it.get('texto')]
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node(f"L_{p_key}")
            for i, it in enumerate(items):
                n_id = f"{p_key}{i}"
                s.node(n_id, limpiar(it['texto']), fillcolor=CONFIG_OBJ[tipo]["color"], fontcolor='white' if "Fin" in tipo else 'black', color='none')
                if "Fin" in tipo: dot.edge("OG", n_id)
                else: dot.edge(n_id, "OG")
                
                h_items = [h for h in datos.get(h_tipo, []) if h.get('padre') == it.get('texto')]
                for j, h in enumerate(h_items):
                    h_id = f"{h_tipo[:2]}{i}_{j}"
                    dot.node(h_id, limpiar(h['texto']), fillcolor=CONFIG_OBJ[h_tipo]["color"], fontcolor='white', color='none', fontsize='10')
                    if "Fin" in tipo: dot.edge(n_id, h_id)
                    else: dot.edge(h_id, n_id)
                
    return dot

# --- RENDERIZADO DE TARJETA ---
def render_poda_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color_barra = CONFIG_OBJ.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 10px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="poda-card">{str(item.get("texto", "")).upper()}</div>', unsafe_allow_html=True)
    if st.button("🗑️", key=f"poda_btn_{id_u}"):
        st.session_state['arbol_objetivos_final'][seccion].pop(idx); guardar_datos_nube(); st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar Paso 5", use_container_width=True, type="primary"):
        st.session_state['arbol_objetivos_final'] = copy.deepcopy(st.session_state.get('arbol_objetivos', {}))
        guardar_datos_nube(); st.rerun()
    st.divider()
    grafo = generar_grafo_final()
    if grafo: st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_final.png", use_container_width=True)

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🌳 Visualización", "✂️ Poda y Ajuste"])

with tab1:
    g_f = generar_grafo_final()
    if g_f: st.image(g_f.pipe(format='png'), use_container_width=True)

with tab2:
    if hay_datos:
        # PANEL DE REFERENCIA CON RASTREO AUTOMÁTICO
        st.subheader("📌 Referencia: Estrategia Seleccionada")
        st.markdown(f"""
        <div class="resumen-estrategico">
            <h4 style="margin-top:0; color:#1E3A8A;">🎯 OBJETIVO GENERAL:</h4>
            <p><b>{obj_ref}</b></p>
            <hr style="border: 0; border-top: 1px solid #d1d5db; margin: 15px 0;">
            <p style="margin-bottom: 5px;"><b>Resumen de la Alternativa:</b></p>
            <p style="color: #4b5563;">{res_ref}</p>
            <p style="margin-top: 10px; margin-bottom: 5px;"><b>Actividades Clave Definidas:</b></p>
            <p style="color: #4b5563;">{act_ref}</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📋 Panel de Poda")
        def mostrar_seccion_final(tipo_padre, tipo_hijo):
            padres = [(idx, p) for idx, p in enumerate(st.session_state['arbol_objetivos_final'].get(tipo_padre, [])) if p.get('texto')]
            if not padres: return
            st.write(f"**{tipo_padre}**")
            hijos = st.session_state['arbol_objetivos_final'].get(tipo_hijo, [])
            h_por_p = [[(idx_h, h) for idx_h, h in enumerate(hijos) if h.get('padre') == p_d.get('texto')] for _, p_d in padres]
            max_h = max([len(l) for l in h_por_p]) if h_por_p else 0

            if "Fin" in tipo_padre:
                for h_idx in range(max_h - 1, -1, -1):
                    cols = st.columns(len(padres))
                    for p_col, col in enumerate(cols):
                        with col:
                            if h_idx < len(h_por_p[p_col]): render_poda_card(tipo_hijo, h_por_p[p_col][h_idx][1], h_por_p[p_col][h_idx][0])
                            else: st.empty()
                cols_p = st.columns(len(padres))
                for i, (idx_o, p_d) in enumerate(padres):
                    with cols_p[i]: render_poda_card(tipo_padre, p_d, idx_o)
            else:
                cols_p = st.columns(len(padres))
                for i, (idx_o, p_d) in enumerate(padres):
                    with cols_p[i]: render_poda_card(tipo_padre, p_d, idx_o)
                for h_idx in range(max_h):
                    cols = st.columns(len(padres))
                    for p_col, col in enumerate(cols):
                        with col:
                            if h_idx < len(h_por_p[p_col]): render_poda_card(tipo_hijo, h_por_p[p_col][h_idx][1], h_por_p[p_col][h_idx][0])
                            else: st.empty()

        mostrar_seccion_final("Fines Directos", "Fines Indirectos")
        st.markdown("---")
        og_f = st.session_state['arbol_objetivos_final'].get("Objetivo General", [])
        if og_f: render_poda_card("Objetivo General", og_f[0], 0)
        st.markdown("---")
        mostrar_seccion_final("Medios Directos", "Medios Indirectos")
