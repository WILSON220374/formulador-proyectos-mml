import streamlit as st
import graphviz
import os
import uuid
import textwrap
import copy
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- SANEAMIENTO Y MIGRACIÓN DE DATOS ---
if 'arbol_objetivos_final' not in st.session_state:
    st.session_state['arbol_objetivos_final'] = {}

if 'referencia_manual' not in st.session_state['arbol_objetivos_final']:
    st.session_state['arbol_objetivos_final']['referencia_manual'] = {
        "nombre": "", "objetivo": "", "especificos": [], "actividades": []
    }

ref_data = st.session_state['arbol_objetivos_final']['referencia_manual']

# --- FUNCIONES DE GESTIÓN Y SINCRONIZACIÓN (REPARADAS) ---
def sincronizar_objetivos_desde_poda():
    """Actualiza la tabla superior con los datos vigentes del árbol podado."""
    datos_arbol = st.session_state['arbol_objetivos_final']
    ref = st.session_state['arbol_objetivos_final']['referencia_manual']
    
    # 1. Objetivo General
    og = datos_arbol.get("Objetivo General", [])
    if og: ref["objetivo"] = og[0].get("texto", "")
    
    # 2. Objetivos Específicos y Actividades
    ref["especificos"] = [c.get("texto") for c in datos_arbol.get("Medios Directos", []) if c.get("texto")]
    ref["actividades"] = [c.get("texto") for c in datos_arbol.get("Medios Indirectos", []) if c.get("texto")]
    
    guardar_datos_nube()

def eliminar_tarjeta_poda(seccion, idx):
    """Elimina una tarjeta y sus descendientes (Eliminación en Cascada)."""
    datos = st.session_state['arbol_objetivos_final']
    item_a_borrar = datos[seccion].pop(idx)
    texto_padre = item_a_borrar.get("texto")

    # Si borramos un Objetivo Específico, borramos sus Actividades vinculadas
    if seccion == "Medios Directos":
        if "Medios Indirectos" in datos:
            datos["Medios Indirectos"] = [h for h in datos["Medios Indirectos"] if h.get("padre") != texto_padre]
    
    # Si borramos un Fin Directo, borramos sus Fines Indirectos vinculados
    elif seccion == "Fines Directos":
        if "Fines Indirectos" in datos:
            datos["Fines Indirectos"] = [h for h in datos["Fines Indirectos"] if h.get("padre") != texto_padre]

    guardar_datos_nube()
    # Sincronización inmediata para evitar discrepancias
    sincronizar_objetivos_desde_poda()

def agregar_item_lista(clave_lista, clave_temporal):
    nuevo_texto = st.session_state.get(clave_temporal, "").strip()
    if nuevo_texto:
        items = [l.strip().lstrip('*-•').strip() for l in nuevo_texto.split('\n') if l.strip()]
        st.session_state['arbol_objetivos_final']['referencia_manual'][clave_lista].extend(items)
        st.session_state[clave_temporal] = ""
        guardar_datos_nube()

def eliminar_item_lista(clave_lista, indice):
    st.session_state['arbol_objetivos_final']['referencia_manual'][clave_lista].pop(indice)
    guardar_datos_nube()

def actualizar_campo_simple(clave):
    st.session_state['arbol_objetivos_final']['referencia_manual'][clave] = st.session_state[f"temp_{clave}"]
    guardar_datos_nube()

# --- DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 10rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    .list-item {
        background-color: #f8fafc; border: 1px solid #e2e8f0;
        padding: 8px 12px; border-radius: 8px; margin-bottom: 5px;
        display: flex; justify-content: space-between; align-items: center;
        font-size: 14px; color: #334155;
    }
    .poda-card {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 0 0 10px 10px;
        padding: 15px; text-align: center; font-size: 14px; font-weight: 700;
        color: #1e293b; min-height: 80px; display: flex; align-items: center; justify-content: center; margin-bottom: 5px;
    }
    .main .stButton button { border: none !important; background: transparent !important; color: #ef4444 !important; font-size: 1.1rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON BARRA DE PROGRESO ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🎯 7. Árbol de Objetivos Final</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Estructuración definitiva de la Alternativa Técnica.</div>', unsafe_allow_html=True)
    
    puntos = 0
    if ref_data.get('objetivo', '').strip(): puntos += 1
    if ref_data.get('especificos'): puntos += 1
    if ref_data.get('actividades'): puntos += 1
    st.progress(puntos / 3)

with col_img:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- MOTOR DE DIBUJO ---
CONFIG_OBJ = {
    "Fin Último":        {"color": "#0E6251", "label": "FIN\\nÚLTIMO"},
    "Fines Indirectos":  {"color": "#154360", "label": "FINES\\nINDIRECTOS"},
    "Fines Directos":    {"color": "#1F618D", "label": "FINES\\nDIRECTOS"},
    "Objetivo General":  {"color": "#C0392B", "label": "OBJETIVO\\nGENERAL"},
    "Medios Directos":   {"color": "#F1C40F", "label": "OBJETIVOS\\nESPECÍFICOS"},
    "Medios Indirectos": {"color": "#D35400", "label": "ACTIVIDADES"}
}

def generar_grafo_final():
    datos = st.session_state.get('arbol_objetivos_final', {})
    claves_graficas = [k for k in datos.keys() if k != 'referencia_manual']
    if not any(datos.get(k) for k in claves_graficas): return None
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')
    def limpiar(t): return "\\n".join(textwrap.wrap(str(t).upper(), width=25))
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

def render_poda_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color_barra = CONFIG_OBJ.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 10px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="poda-card">{str(item.get("texto", "")).upper()}</div>', unsafe_allow_html=True)
    # Nombre de función corregido aquí:
    st.button("🗑️", key=f"poda_obj_{id_u}", on_click=eliminar_tarjeta_poda, args=(seccion, idx))

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    def importar_p5():
        ref_bk = copy.deepcopy(st.session_state['arbol_objetivos_final'].get('referencia_manual', {}))
        nuevo = copy.deepcopy(st.session_state.get('arbol_objetivos', {}))
        nuevo['referencia_manual'] = ref_bk
        st.session_state['arbol_objetivos_final'] = nuevo
        guardar_datos_nube()
    st.button("♻️ Importar Paso 5", use_container_width=True, type="primary", on_click=importar_p5)
    st.divider()
    grafo = generar_grafo_final()
    if grafo: st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_final.png", use_container_width=True)

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🌳 Visualización", "✂️ Poda y Ajuste"])

with tab1:
    g_f = generar_grafo_final()
    if g_f: st.image(g_f.pipe(format='png'), use_container_width=True)

with tab2:
    col_title, col_sync = st.columns([0.6, 0.4], vertical_alignment="center")
    with col_title:
        st.markdown("### 📌 Alternativa Seleccionada")
    with col_sync:
        st.button("🔄 Sincronizar con Árbol", key="sync_obj_top", type="primary", use_container_width=True, on_click=sincronizar_objetivos_desde_poda)

    st.markdown("**Objetivo General**")
    st.text_area("OG", value=ref_data['objetivo'], key="temp_objetivo", label_visibility="collapsed", height=100, on_change=actualizar_campo_simple, args=("objetivo",))
    
    st.divider()

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("**Objetivos Específicos (Componentes)**")
        # Ciclo de visualización pura sincronizada con el árbol
        if ref_data['especificos']:
            for item in ref_data['especificos']:
                st.markdown(f"<div class='list-item'>• {item}</div>", unsafe_allow_html=True)
        else:
            st.info("Sincronice con el árbol para ver los componentes.")
        
        ei1, ei2 = st.columns([0.8, 0.2])
        with ei1: st.text_area("Nuevo Esp", label_visibility="collapsed", key="new_esp", placeholder="Componente...", height=68)
        with ei2: st.button("➕", key="add_esp", on_click=agregar_item_lista, args=('especificos', 'new_esp'))

    with col_der:
        st.markdown("**Actividades Clave**")
        # Ciclo de visualización pura sincronizada con el árbol
        if ref_data['actividades']:
            for item in ref_data['actividades']:
                st.markdown(f"<div class='list-item'>➡️ {item}</div>", unsafe_allow_html=True)
        else:
            st.info("Sincronice con el árbol para ver las actividades.")
        
        ai1, ai2 = st.columns([0.8, 0.2])
        with ai1: st.text_area("Nueva Act", label_visibility="collapsed", key="new_act", placeholder="Actividad...", height=68)
        with ai2: st.button("➕", key="add_act", on_click=agregar_item_lista, args=('actividades', 'new_act'))

    st.divider()
    st.subheader("📋 Panel de Poda")
    
    def mostrar_seccion_poda(tipo_padre, tipo_hijo):
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

    mostrar_seccion_poda("Fines Directos", "Fines Indirectos")
    st.markdown("---")
    og_f = st.session_state['arbol_objetivos_final'].get("Objetivo General", [])
    if og_f: render_poda_card("Objetivo General", og_f[0], 0)
    st.markdown("---")
    mostrar_seccion_poda("Medios Directos", "Medios Indirectos")
