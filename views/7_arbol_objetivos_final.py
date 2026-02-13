import streamlit as st
import pandas as pd
import graphviz
import copy
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos persistentes e inicialización
inicializar_session()

# --- ESTILO DE LA INTERFAZ (Tarjetas y Papeleras) ---
st.markdown("""
    <style>
    div[data-testid="stTextArea"] textarea {
        background-color: #f8f9fb !important;
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding-top: 15px !important;
    }
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.2rem !important;
        margin-top: -15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🎯 7. Árbol de Objetivos Final")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", width="stretch")

st.info("💡 **Modo Edición:** Elimine las fichas que no formarán parte de la propuesta definitiva. La vista previa se actualizará al instante.")

# --- CONFIGURACIÓN DE COLORES ---
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"}
}

# --- LÓGICA DE DIBUJO PROFESIONAL (GRAPHVIZ) ---
def generar_arbol_graphviz():
    datos = st.session_state.get('arbol_objetivos_final', {})
    if not datos: return None

    dot = graphviz.Digraph(comment='Árbol de Objetivos', format='png')
    dot.attr(label='\nÁRBOL DE OBJETIVOS FINAL\n ', labelloc='t', 
             fontsize='22', fontname='Arial Bold', fontcolor='#1E3A8A')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8', splines='ortho')

    def limpiar(t): 
        import textwrap
        t = str(t).replace('"', "'")
        return "\n".join(textwrap.wrap(t, width=25))

    # 1. Nodo Objetivo General (OG)
    obj_gen = datos.get("Objetivo General", [])
    if obj_gen:
        dot.node('OG', limpiar(obj_gen[0].get('texto', '')), shape='box', style='filled', 
                 fillcolor=CONFIG_OBJ["Objetivo General"]["color"], fontname='Arial Bold')

    # 2. FINES (Hacia arriba)
    f_directos = datos.get("Fines Directos", [])
    f_indirectos = datos.get("Fines Indirectos", [])
    textos_f_dir = [f.get('texto') for f in f_directos]
    textos_f_ind = [f.get('texto') for f in f_indirectos]

    for i, f_dir in enumerate(f_directos):
        id_f = f"FD_{i}"
        dot.node(id_f, limpiar(f_dir.get('texto', '')), shape='box', style='filled', fillcolor=CONFIG_OBJ["Fines Directos"]["color"])
        dot.edge(id_f, 'OG', dir='back')
        
        # Hijos: Fines Indirectos
        for j, f_ind in enumerate(f_indirectos):
            if f_ind.get('padre') == f_dir.get('texto'):
                id_fi = f"FI_{i}_{j}"
                dot.node(id_fi, limpiar(f_ind.get('texto', '')), shape='box', style='filled', fillcolor=CONFIG_OBJ["Fines Indirectos"]["color"])
                dot.edge(id_fi, id_f, dir='back')
                
                # Nieto: Fin Último (Solo si el padre indirecto existe)
                for k, fu in enumerate(datos.get("Fin Último", [])):
                    dot.node('FU', limpiar(fu.get('texto', '')), shape='box', style='filled', fillcolor=CONFIG_OBJ["Fin Último"]["color"])
                    dot.edge('FU', id_fi, dir='back')

    # 3. MEDIOS (Hacia abajo)
    m_directos = datos.get("Medios Directos", [])
    m_indirectos = datos.get("Medios Indirectos", [])
    textos_m_dir = [m.get('texto') for m in m_directos]

    for i, m_dir in enumerate(m_directos):
        id_m = f"MD_{i}"
        dot.node(id_m, limpiar(m_dir.get('texto', '')), shape='box', style='filled', fillcolor=CONFIG_OBJ["Medios Directos"]["color"])
        dot.edge('OG', id_m)
        
        # Hijos: Actividades (Medios Indirectos)
        for j, m_ind in enumerate(m_indirectos):
            if m_ind.get('padre') == m_dir.get('texto'):
                id_mi = f"MI_{i}_{j}"
                dot.node(id_mi, limpiar(m_ind.get('texto', '')), shape='box', style='filled', fillcolor=CONFIG_OBJ["Medios Indirectos"]["color"])
                dot.edge(id_m, id_mi)

    return dot

# --- SIDEBAR: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("♻️ Importar desde Paso 5", use_container_width=True):
        datos_original = copy.deepcopy(st.session_state.get('arbol_objetivos', {}))
        datos_con_id = {}
        for seccion, lista in datos_original.items():
            procesados = []
            for item in lista:
                new_item = item if isinstance(item, dict) else {'texto': item}
                new_item['id_unico'] = str(uuid.uuid4())
                procesados.append(new_item)
            datos_con_id[seccion] = procesados
        st.session_state['arbol_objetivos_final'] = datos_con_id
        guardar_datos_nube(); st.rerun()

    st.divider()
    grafo = generar_arbol_graphviz()
    if grafo:
        st.download_button("🖼️ Descargar Árbol PNG", data=grafo.pipe(format='png'), 
                           file_name="arbol_objetivos_final.png", width="stretch")

# --- ÁREA DE TRABAJO PRINCIPAL ---
arbol_f = st.session_state.get('arbol_objetivos_final', {})

if not arbol_f:
    st.warning("El árbol está vacío. Por favor, use el botón 'Importar desde Paso 5' en la barra lateral.")
else:
    # A. VISTA PREVIA (Siempre al principio)
    st.subheader("📊 Vista Previa del Árbol Definitivo")
    with st.container(border=True):
        st.graphviz_chart(generar_arbol_graphviz())
    
    st.divider()
    
    # B. ZONA DE PODA (Edición de fichas)
    def render_poda_card(seccion, item):
        id_u = item.get('id_unico', 'temp')
        texto_actual = item.get("texto", "")
        color = CONFIG_OBJ[seccion]["color"]
        
        st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
        nuevo_texto = st.text_area(label=f"p_{id_u}", value=texto_actual, label_visibility="collapsed", key=f"txt_{id_u}")
        
        if st.button("🗑️", key=f"btn_{id_u}"):
            st.session_state['arbol_objetivos_final'][seccion] = [x for x in st.session_state['arbol_objetivos_final'][seccion] if x.get('id_unico') != id_u]
            guardar_datos_nube(); st.rerun()
        
        if nuevo_texto != texto_actual:
            item["texto"] = nuevo_texto
            guardar_datos_nube()

    # Función para mostrar jerarquías en la web
    def mostrar_seccion_simple(key):
        col_l, col_c = st.columns([1, 4])
        col_l.markdown(f"**{CONFIG_OBJ[key]['label']}**")
        with col_c:
            for it in arbol_f.get(key, []): render_poda_card(key, it)

    def mostrar_rama_jerarquica(padre_key, hijo_key, inversion=False):
        padres = arbol_f.get(padre_key, [])
        hijos = arbol_f.get(hijo_key, [])
        orden = [(hijo_key, True), (padre_key, False)] if inversion else [(padre_key, False), (hijo_key, True)]
        
        for seccion, es_hijo in orden:
            c1, c2 = st.columns([1, 4])
            c1.markdown(f"**{CONFIG_OBJ[seccion]['label']}**")
            with c2:
                if padres:
                    cols = st.columns(len(padres))
                    for i, p_data in enumerate(padres):
                        with cols[i]:
                            if es_hijo:
                                h_rel = [h for h in hijos if h.get("padre") == p_data.get("texto")]
                                for h_it in h_rel: render_poda_card(seccion, h_it)
                            else:
                                render_poda_card(seccion, p_data)

    # Renderizado jerárquico de las tarjetas
    mostrar_seccion_simple("Fin Último")
    st.markdown("---")
    mostrar_rama_jerarquica("Fines Directos", "Fines Indirectos", inversion=True)
    st.markdown("---")
    mostrar_seccion_simple("Objetivo General")
    st.markdown("---")
    mostrar_rama_jerarquica("Medios Directos", "Medios Indirectos", inversion=False)
