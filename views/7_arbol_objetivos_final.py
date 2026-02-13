import streamlit as st
import pandas as pd
import graphviz
import copy
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos persistentes
inicializar_session()

# --- ESTILO DE LA INTERFAZ WEB ---
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

st.info("Ajuste Automático: El árbol ahora se organiza solo para evitar superposiciones.")

# --- CONFIGURACIÓN DE COLORES (Consistente con tu diseño) ---
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"}
}

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

    # --- NUEVO MOTOR DE DIBUJO (GRAPHVIZ) ---
    def generar_arbol_graphviz():
        datos = st.session_state.get('arbol_objetivos_final', {})
        if not datos: return None

        # Crear el grafo
        dot = graphviz.Digraph(comment='Árbol de Objetivos', format='png')
        dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8', splines='ortho')
        dot.attr(fontname='Arial')

        # Función para limpiar texto y evitar errores en Graphviz
        def limpiar(t): 
            t = str(t).replace('"', "'")
            # Wrap de texto automático para las cajas
            import textwrap
            return "\n".join(textwrap.wrap(t, width=25))

        # 1. Nodo Objetivo General (El corazón)
        obj_gen = datos.get("Objetivo General", [])
        if obj_gen:
            label = limpiar(obj_gen[0].get('texto', ''))
            dot.node('OG', label, shape='box', style='filled', 
                     fillcolor=CONFIG_OBJ["Objetivo General"]["color"], fontname='Arial Bold')

        # 2. FINES (Hacia arriba)
        # Fines Directos -> OG
        for i, f_dir in enumerate(datos.get("Fines Directos", [])):
            id_f = f"FD_{i}"
            dot.node(id_f, limpiar(f_dir.get('texto', '')), shape='box', style='filled', 
                     fillcolor=CONFIG_OBJ["Fines Directos"]["color"])
            dot.edge(id_f, 'OG', dir='back') # Flecha hacia arriba
            
            # Fines Indirectos -> Fines Directos
            for j, f_ind in enumerate(datos.get("Fines Indirectos", [])):
                if f_ind.get('padre') == f_dir.get('texto'):
                    id_fi = f"FI_{i}_{j}"
                    dot.node(id_fi, limpiar(f_ind.get('texto', '')), shape='box', style='filled', 
                             fillcolor=CONFIG_OBJ["Fines Indirectos"]["color"])
                    dot.edge(id_fi, id_f, dir='back')
                    
                    # Fin Último -> Fin Indirecto
                    fin_u = datos.get("Fin Último", [])
                    if fin_u:
                        dot.node('FU', limpiar(fin_u[0].get('texto', '')), shape='box', style='filled', 
                                 fillcolor=CONFIG_OBJ["Fin Último"]["color"])
                        dot.edge('FU', id_fi, dir='back')

        # 3. MEDIOS (Hacia abajo)
        # OG -> Medios Directos
        for i, m_dir in enumerate(datos.get("Medios Directos", [])):
            id_m = f"MD_{i}"
            dot.node(id_m, limpiar(m_dir.get('texto', '')), shape='box', style='filled', 
                     fillcolor=CONFIG_OBJ["Medios Directos"]["color"])
            dot.edge('OG', id_m)
            
            # Medios Directos -> Medios Indirectos
            for j, m_ind in enumerate(datos.get("Medios Indirectos", [])):
                if m_ind.get('padre') == m_dir.get('texto'):
                    id_mi = f"MI_{i}_{j}"
                    dot.node(id_mi, limpiar(m_ind.get('texto', '')), shape='box', style='filled', 
                             fillcolor=CONFIG_OBJ["Medios Indirectos"]["color"])
                    dot.edge(id_m, id_mi)

        return dot

    # Botón de descarga
    grafo = generar_arbol_graphviz()
    if grafo:
        png_data = grafo.pipe(format='png')
        st.download_button("🖼️ Descargar Árbol PNG", data=png_data, 
                           file_name="arbol_objetivos_final.png", width="stretch")

# --- RENDERIZADO VISUAL ---
if st.session_state.get('arbol_objetivos_final'):
    st.subheader("📊 Visualización Estructural")
    st.graphviz_chart(generar_arbol_graphviz())

# --- RENDERIZADO DE EDICIÓN (Mantenemos tu lógica de tarjetas) ---
def calcular_altura_web(texto, min_h=100):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 30)
    return max(min_h, (lineas + 2) * 22)

def render_poda_card(seccion, item):
    id_id = item.get('id_unico', 'temp')
    texto_actual = item.get("texto", "")
    color = CONFIG_OBJ[seccion]["color"]
    st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    nuevo_texto = st.text_area(label=f"p_{id_id}", value=texto_actual, label_visibility="collapsed", height=calcular_altura_web(texto_actual), key=f"txt_{id_id}")
    if st.button("🗑️", key=f"btn_{id_id}"):
        st.session_state['arbol_objetivos_final'][seccion] = [x for x in st.session_state['arbol_objetivos_final'][seccion] if x.get('id_unico') != id_id]
        guardar_datos_nube(); st.rerun()
    if nuevo_texto != texto_actual:
        item["texto"] = nuevo_texto
        guardar_datos_nube()

# (Se omiten funciones mostrar_seccion y mostrar_rama por brevedad, se mantienen igual a tu código original)
