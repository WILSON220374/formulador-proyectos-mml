import streamlit as st
import graphviz
import os
import uuid
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- BLOQUE DE MIGRACIÓN DE DATOS (AUTO-REPARACIÓN) ---
if 'arbol_objetivos_final' not in st.session_state:
    st.session_state['arbol_objetivos_final'] = {}

if 'referencia_manual' not in st.session_state['arbol_objetivos_final']:
    st.session_state['arbol_objetivos_final']['referencia_manual'] = {
        "nombre": "", "objetivo": "", "especificos": [], "actividades": []
    }

ref_data = st.session_state['arbol_objetivos_final']['referencia_manual']

# Conversión de seguridad: Texto a Lista
for clave in ['especificos', 'actividades']:
    if isinstance(ref_data.get(clave), str):
        texto_viejo = ref_data[clave]
        if texto_viejo.strip():
            items = [linea.strip().lstrip('*-•').strip() for linea in texto_viejo.split('\n') if linea.strip()]
            ref_data[clave] = items
        else:
            ref_data[clave] = []

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 10rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    .list-item {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        color: #334155;
    }
    
    .list-header {
        font-weight: 700;
        color: #1E3A8A;
        margin-top: 10px;
        margin-bottom: 5px;
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
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE GESTIÓN (CALLBACKS SEGUROS) ---
# Al usar estas funciones en 'on_click', evitamos el error de StreamlitAPIException
def agregar_item(clave_lista, clave_temporal):
    nuevo_texto = st.session_state.get(clave_temporal, "").strip()
    if nuevo_texto:
        nuevos_items = [l.strip().lstrip('*-•').strip() for l in nuevo_texto.split('\n') if l.strip()]
        st.session_state['arbol_objetivos_final']['referencia_manual'][clave_lista].extend(nuevos_items)
        st.session_state[clave_temporal] = "" # Limpiar input es seguro aquí porque ocurre ANTES del renderizado
        guardar_datos_nube()

def eliminar_item(clave_lista, indice):
    st.session_state['arbol_objetivos_final']['referencia_manual'][clave_lista].pop(indice)
    guardar_datos_nube()

def actualizar_campo_simple(clave):
    st.session_state['arbol_objetivos_final']['referencia_manual'][clave] = st.session_state[f"temp_{clave}"]
    guardar_datos_nube()

# --- FUNCIÓN INTELIGENTE: CALCULAR ALTURA DINÁMICA ---
def calc_altura(texto):
    if not texto: return 100
    lineas = str(texto).count('\n') + (len(str(texto)) // 50) + 1
    return max(100, lineas * 25)

# --- ENCABEZADO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🎯 7. Árbol de Objetivos Final</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Diligenciamiento manual y poda definitiva de componentes.</div>', unsafe_allow_html=True)
    
    datos_final = st.session_state.get('arbol_objetivos_final', {})
    claves_reales = [k for k in datos_final.keys() if k != 'referencia_manual']
    hay_datos = any(datos_final[k] for k in claves_reales) if claves_reales else False
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

# --- MOTOR DE DIBUJO ---
def generar_grafo_final():
    datos = st.session_state.get('arbol_objetivos_final', {})
    claves_graficas = [k for k in datos.keys() if k != 'referencia_manual']
    if not any(datos.get(k) for k in claves_graficas): return None
    
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
    if obj_gen: dot.node("OG", limpiar(obj_gen[0]['texto']), fillcolor=CONFIG_OBJ["Objetivo General"]["color"], fontcolor='white', color='none', width='4.5')

    for tipo, p_id, h_tipo in [("Fines Directos", "OG", "Fines Indirectos"), ("Medios Directos", "OG", "Medios Indirectos")]:
        items = [it for it in datos.get(tipo, []) if it.get('texto')]
        for i, item in enumerate(items):
            n_id = f"{tipo[:2]}{i}"
            dot.node(n_id, limpiar(item['texto']), fillcolor=CONFIG_OBJ[tipo]["color"], fontcolor='white' if "Fin" in tipo else 'black', color='none')
            if "Fin" in tipo: dot.edge("OG", n_id)
            else: dot.edge(n_id, "OG")
            hijos = [h for h in datos.get(h_tipo, []) if h.get('padre') == item.get('texto')]
            for j, h in enumerate(hijos):
                h_id = f"{h_tipo[:2]}{i}_{j}"
                dot.node(h_id, limpiar(h['texto']), fillcolor=CONFIG_OBJ[h_tipo]["color"], fontcolor='white', color='none', fontsize='10')
                if "Fin" in tipo: dot.edge(n_id, h_id)
                else: dot.edge(h_id, n_id)
    return dot

# --- RENDERIZADO DE TARJETA MODO PODA ---
def render_poda_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color_barra = CONFIG_OBJ.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 10px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="poda-card">{str(item.get("texto", "")).upper()}</div>', unsafe_allow_html=True)
    # Callback para poda
    st.button("🗑️", key=f"poda_btn_{id_u}", on_click=lambda: (st.session_state['arbol_objetivos_final'][seccion].pop(idx), guardar_datos_nube()))

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    def importar_paso_5():
        ref_bk = copy.deepcopy(st.session_state['arbol_objetivos_final'].get('referencia_manual', {}))
        nuevo = copy.deepcopy(st.session_state.get('arbol_objetivos', {}))
        nuevo['referencia_manual'] = ref_bk
        st.session_state['arbol_objetivos_final'] = nuevo
        guardar_datos_nube()
        
    st.button("♻️ Importar Paso 5", use_container_width=True, type="primary", on_click=importar_paso_5)
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
        st.subheader("📌 Alternativa Seleccionada")
        st.info("La estructuración en listas facilita la creación automática de la Matriz de Marco Lógico.")

        # --- SECCIÓN SUPERIOR: TEXTOS SIMPLES ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.markdown("**Nombre de la Alternativa**")
            st.text_input("Nombre", value=ref_data['nombre'], label_visibility="collapsed", key="temp_nombre", on_change=actualizar_campo_simple, args=("nombre",))
            
            st.markdown("**Objetivo General**")
            st.text_area("Obj. General", value=ref_data['objetivo'], label_visibility="collapsed", key="temp_objetivo", 
                         height=calc_altura(ref_data['objetivo']), on_change=actualizar_campo_simple, args=("objetivo",))

        # --- SECCIÓN INFERIOR: LISTAS DINÁMICAS (Corregido) ---
        with col_der:
            # 1. OBJETIVOS ESPECÍFICOS
            st.markdown("<div class='list-header'>Objetivos Específicos (Componentes)</div>", unsafe_allow_html=True)
            if not ref_data['especificos']:
                st.caption("No hay objetivos específicos aún.")
            else:
                for i, item in enumerate(ref_data['especificos']):
                    c1, c2 = st.columns([0.9, 0.1])
                    with c1: st.markdown(f"<div class='list-item'>• {item}</div>", unsafe_allow_html=True)
                    with c2: 
                        # Callback directo en el botón
                        st.button("🗑️", key=f"del_esp_{i}", on_click=eliminar_item, args=('especificos', i))
            
            # Input para agregar nuevo
            c_in, c_btn = st.columns([0.85, 0.15])
            with c_in: 
                st.text_area("Nuevo Obj", label_visibility="collapsed", key="new_esp", placeholder="Escriba aquí...", height=68)
            with c_btn: 
                # Callback directo en el botón
                st.button("➕", key="btn_add_esp", on_click=agregar_item, args=('especificos', 'new_esp'))

            st.divider()

            # 2. ACTIVIDADES CLAVE
            st.markdown("<div class='list-header'>Actividades Clave</div>", unsafe_allow_html=True)
            if not ref_data['actividades']:
                st.caption("No hay actividades registradas.")
            else:
                for i, item in enumerate(ref_data['actividades']):
                    c1, c2 = st.columns([0.9, 0.1])
                    with c1: st.markdown(f"<div class='list-item'>➡️ {item}</div>", unsafe_allow_html=True)
                    with c2: 
                        # Callback directo en el botón
                        st.button("🗑️", key=f"del_act_{i}", on_click=eliminar_item, args=('actividades', i))
            
            # Input para agregar nueva
            c_in_a, c_btn_a = st.columns([0.85, 0.15])
            with c_in_a: 
                st.text_area("Nueva Act", label_visibility="collapsed", key="new_act", placeholder="Escriba aquí...", height=68)
            with c_btn_a: 
                # Callback directo en el botón
                st.button("➕", key="btn_add_act", on_click=agregar_item, args=('actividades', 'new_act'))

        st.divider()

        # --- PANEL DE PODA ---
        st.subheader("📋 Panel de Poda")
        st.info("Solo lectura: Use la papelera para descartar lo que no aporte a la alternativa de arriba.")

        def mostrar_seccion_final(tipo_padre, tipo_hijo):
            datos_sec = st.session_state['arbol_objetivos_final'].get(tipo_padre, [])
            padres_con_idx = [(idx, p) for idx, p in enumerate(datos_sec) if p.get('texto')]
            if not padres_con_idx: return
            st.write(f"**{tipo_padre}**")
            hijos = st.session_state['arbol_objetivos_final'].get(tipo_hijo, [])
            h_por_p = [[(idx_h, h) for idx_h, h in enumerate(hijos) if h.get('padre') == p_d.get('texto')] for _, p_d in padres_con_idx]
            max_h = max([len(l) for l in h_por_p]) if h_por_p else 0
            if "Fin" in tipo_padre:
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

        mostrar_seccion_final("Fines Directos", "Fines Indirectos")
        st.markdown("---")
        og_f = st.session_state['arbol_objetivos_final'].get("Objetivo General", [])
        if og_f: render_poda_card("Objetivo General", og_f[0], 0)
        st.markdown("---")
        mostrar_seccion_final("Medios Directos", "Medios Indirectos")
