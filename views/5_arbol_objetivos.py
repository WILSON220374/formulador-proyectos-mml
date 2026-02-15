import streamlit as st
import graphviz
import os
import uuid
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia
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
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- CONFIGURACIÓN DE COLORES ---
CONFIG_OBJ = {
    "Fines Indirectos": {"color": "#154360", "font_color": "white", "label": "FINES\nINDIRECTOS"},
    "Fines Directos":   {"color": "#1F618D", "font_color": "white", "label": "FINES\nDIRECTOS"},
    "Objetivo General": {"color": "#C0392B", "font_color": "white", "label": "OBJETIVO\nGENERAL"},
    "Medios Directos":  {"color": "#F1C40F", "font_color": "black", "label": "OBJETIVOS\nESPECÍFICOS"},
    "Medios Indirectos":{"color": "#D35400", "font_color": "white", "label": "ACTIVIDADES"}
}

# --- PILOTO AUTOMÁTICO DE LIMPIEZA ---
if hay_datos:
    datos = st.session_state['arbol_objetivos']
    cambios_realizados = False
    
    padres_validos_fi = [p['texto'] for p in datos.get("Fines Directos", [])]
    fines_indirectos_limpios = [h for h in datos.get("Fines Indirectos", []) if h.get('padre') in padres_validos_fi]
    if len(datos.get("Fines Indirectos", [])) != len(fines_indirectos_limpios):
        datos["Fines Indirectos"] = fines_indirectos_limpios
        cambios_realizados = True

    padres_validos_mi = [p['texto'] for p in datos.get("Medios Directos", [])]
    medios_indirectos_limpios = [h for h in datos.get("Medios Indirectos", []) if h.get('padre') in padres_validos_mi]
    if len(datos.get("Medios Indirectos", [])) != len(medios_indirectos_limpios):
        datos["Medios Indirectos"] = medios_indirectos_limpios
        cambios_realizados = True
        
    if cambios_realizados:
        st.session_state['arbol_objetivos'] = datos
        guardar_datos_nube()
        st.rerun()

# --- MOTOR DE DIBUJO ---
def generar_grafo_objetivos():
    datos = st.session_state.get('arbol_objetivos', {})
    if not any(datos.values()): return None
    
    dot = graphviz.Digraph(format='png')
    
    # Configuración IDÉNTICA a Problemas
    dot.attr(label='ÁRBOL DE OBJETIVOS', labelloc='t', fontsize='35', fontname='Arial Bold', fontcolor='#333333')
    dot.attr(dpi='300', rankdir='BT', nodesep='0.5', ranksep='0.8', splines='ortho')
    dot.attr('node', fontsize='20', fontname='Arial Bold', style='filled', color='none', margin='0.6,0.4', shape='box')
    
    def limpiar(t, w=50): return "\n".join(textwrap.wrap(str(t).upper(), width=w))

    # ETIQUETAS LATERALES (Sin Fin Último)
    etiquetas = ["L_FI", "L_FD", "L_OG", "L_MD", "L_MI"]
    tipos = ["Fines Indirectos", "Fines Directos", "Objetivo General", "Medios Directos", "Medios Indirectos"]
    
    for id_e, tipo in zip(etiquetas, tipos):
        conf = CONFIG_OBJ[tipo]
        dot.node(id_e, conf['label'], shape='plaintext', fontcolor=conf['color'], fontsize='18', fontname='Arial Bold', style='')

    for i in range(len(etiquetas)-1):
        dot.edge(etiquetas[i+1], etiquetas[i], style='invis')

    # --- NODOS ---

    # 1. Fines Indirectos (Ahora son la cima)
    if datos.get("Fines Indirectos"):
        c = CONFIG_OBJ["Fines Indirectos"]
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node('L_FI')
            for i, item in enumerate(datos["Fines Indirectos"]):
                # Eliminadas todas las referencias a "FU"
                s.node(f"FI{i}", limpiar(item['texto']), fillcolor=c["color"], fontcolor=c["font_color"])

    # 2. Fines Directos
    if datos.get("Fines Directos"):
        c = CONFIG_OBJ["Fines Directos"]
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node('L_FD')
            for i, item in enumerate(datos["Fines Directos"]):
                node_id = f"FD{i}"
                s.node(node_id, limpiar(item['texto']), fillcolor=c["color"], fontcolor=c["font_color"])
                # Conexiones hacia arriba (Fines Indirectos)
                hijos = [h for idx, h in enumerate(datos.get("Fines Indirectos", [])) if h.get('padre') == item['texto']]
                for h in hijos:
                    idx_real = datos["Fines Indirectos"].index(h)
                    dot.edge(node_id, f"FI{idx_real}", weight="5")

    # 3. Objetivo General (Centro Único)
    if datos.get("Objetivo General"):
        c = CONFIG_OBJ["Objetivo General"]
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node('L_OG')
            # Nodo central robusto
            s.node("OG", limpiar(datos["Objetivo General"][0]['texto'], w=80), 
                   fillcolor=c["color"], fontcolor=c["font_color"], margin='0.8,0.4')
            
        for i, item in enumerate(datos.get("Fines Directos", [])): 
            # Eliminada la conexión invisible a FU, ahora es directo hacia arriba
            dot.edge("OG", f"FD{i}", weight="5")

    # 4. Medios Directos
    if datos.get("Medios Directos"):
        c = CONFIG_OBJ["Medios Directos"]
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node('L_MD')
            for i, item in enumerate(datos["Medios Directos"]):
                node_id = f"MD{i}"
                s.node(node_id, limpiar(item['texto']), fillcolor=c["color"], fontcolor=c["font_color"])
                if datos.get("Objetivo General"): dot.edge(node_id, "OG", weight="5")

    # 5. Medios Indirectos
    if datos.get("Medios Indirectos"):
        c = CONFIG_OBJ["Medios Indirectos"]
        with dot.subgraph() as s:
            s.attr(rank='same'); s.node('L_MI')
            for i, item in enumerate(datos["Medios Indirectos"]):
                node_id = f"MI{i}"
                s.node(node_id, limpiar(item['texto']), fillcolor=c["color"], fontcolor=c["font_color"])
                for p_idx, padre in enumerate(datos.get("Medios Directos", [])):
                    if item.get('padre') == padre['texto']:
                        dot.edge(node_id, f"MD{p_idx}", weight="5")
                
    return dot

# --- RENDERIZADO DE TARJETA ---
def render_card_obj(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    
    # Barra de color
    color_barra = CONFIG_OBJ.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 12px; border-radius: 10px 10px 0 0; margin-bottom: 0px;"></div>', unsafe_allow_html=True)
    
    texto_viejo = item['texto']
    nuevo_texto = st.text_area("t", value=texto_viejo, key=f"obj_txt_{id_u}", label_visibility="collapsed")
    
    if st.button("🗑️", key=f"obj_btn_{id_u}"):
        st.session_state['arbol_objetivos'][seccion].pop(idx)
        guardar_datos_nube()
        st.rerun()
    
    if nuevo_texto != texto_viejo:
        item['texto'] = nuevo_texto.upper()
        relaciones = {"Fines Directos": "Fines Indirectos", "Medios Directos": "Medios Indirectos"}
        if seccion in relaciones:
            seccion_hija = relaciones[seccion]
            for hijo in st.session_state['arbol_objetivos'][seccion_hija]:
                if isinstance(hijo, dict) and hijo.get("padre") == texto_viejo:
                    hijo["padre"] = nuevo_texto.upper()
        guardar_datos_nube()
        st.rerun()

# --- SIDEBAR ---
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
        # IMPORTANTE: Mantenemos el Fin Último en memoria por si acaso, pero no lo dibujamos
        if not st.session_state['arbol_objetivos'].get("Fin Último"):
             st.session_state['arbol_objetivos']["Fin Último"] = [{"texto": "MEJORAR LA CALIDAD DE VIDA", "id_unico": str(uuid.uuid4())}]

        for p_sec, o_sec in mapeo.items():
            for item in problemas.get(p_sec, []):
                nueva = {
                    "texto": item['texto'].upper(), 
                    "id_unico": str(uuid.uuid4()),
                    "padre": item.get('padre', "").upper()
                }
                st.session_state['arbol_objetivos'][o_sec].append(nueva)
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

        # Fines: Hijos Arriba
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
        
        # Medios: Hijos Abajo
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

    # RENDERIZADO DEL PANEL
    # Ocultamos la tarjeta de Fin Último del panel de edición también para ser consistentes
    
    render_seccion_jerarquica("Fines Directos", "Fines Indirectos")
    st.markdown("---")
    pc_og = st.session_state['arbol_objetivos'].get("Objetivo General", [])
    if pc_og: 
        st.write("**Objetivo General**")
        render_card_obj("Objetivo General", pc_og[0], 0)
    st.markdown("---")
    render_seccion_jerarquica("Medios Directos", "Medios Indirectos")
