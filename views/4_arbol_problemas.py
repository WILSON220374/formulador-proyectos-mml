import streamlit as st
import graphviz
import os
import uuid
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- ESTRATEGIA 1: LIMPIEZA SILENCIOSA ---
if 'arbol_tarjetas' in st.session_state:
    for seccion in st.session_state['arbol_tarjetas']:
        lista = st.session_state['arbol_tarjetas'][seccion]
        if isinstance(lista, list):
            # Filtramos para que solo queden fichas reales con contenido
            st.session_state['arbol_tarjetas'][seccion] = [
                it for it in lista if isinstance(it, dict) and it.get('texto') and len(str(it.get('texto')).strip()) > 1
            ]

# --- ESTRATEGIA 2: DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    /* Añadimos un margen inferior para que el contenido no choque con el borde */
    .block-container { padding-bottom: 10rem !important; }
    
    /* Estilo de los títulos */
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }

    /* Estilo de las tarjetas de edición dentro de la pestaña Constructor */
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;           
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 14px !important;
        color: #1e293b !important;
        min-height: 100px !important;
    }

    /* Botón de eliminar (papelera) */
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ef4444 !important;
        font-size: 1.2rem !important;
        margin-top: -15px !important;
    }
    
    /* Ajuste de pestañas */
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
    st.markdown('<div class="titulo-seccion">🌳 4. Árbol de Problemas</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Separe la construcción lógica de la visualización final del proyecto.</div>', unsafe_allow_html=True)
    
    pc_data = st.session_state.get('arbol_tarjetas', {}).get("Problema Principal", [])
    hay_datos = len(pc_data) > 0
    st.progress(1.0 if hay_datos else 0.0, text="Progreso del Diagnóstico" if hay_datos else "Esperando Problema Central")

with col_img:
    if os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- ESTRATEGIA 3: MARCO DE TAMAÑO CONTROLADO ---
def generar_grafo_problemas():
    datos = st.session_state.get('arbol_tarjetas', {})
    pc = datos.get("Problema Principal", [])
    if not pc: return None

    # El atributo 'size' con '!' fuerza al dibujo a quedarse en un marco fijo
    dot = graphviz.Digraph(format='png')
    dot.attr(size='10,8!', ratio='fill', center='true') 
    dot.attr(rankdir='BT', nodesep='0.5', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='12', fontname='Arial Bold', style='filled', shape='box', margin='0.3,0.2')
    
    def limpiar(t): return "\n".join(textwrap.wrap(str(t).upper(), width=25))

    COLORS = {"PC": "#A93226", "ED": "#2E86C1", "EI": "#884EA0", "CD": "#D4AC0D", "CI": "#CA6F1E"}

    # Nodo Central
    dot.node('PC', limpiar(pc[0]['texto']), fillcolor=COLORS["PC"], fontcolor='white', color='none')

    # Ramas: Efectos y Causas
    for tipo, id_p, p_key, edge_dir, col in [
        ("Efectos Directos", "ED", "PC", "forward", COLORS["ED"]),
        ("Causas Directas", "CD", "PC", "back", COLORS["CD"])
    ]:
        items = datos.get(tipo, [])
        for i, it in enumerate(items):
            node_id = f"{id_p}{i}"
            dot.node(node_id, limpiar(it['texto']), fillcolor=col, fontcolor='white', color='none')
            dot.edge('PC', node_id) if edge_dir == "forward" else dot.edge(node_id, 'PC')
            
            # Sub-ramas (Indirectas)
            h_tipo = "Efectos Indirectos" if "Efecto" in tipo else "Causas Indirectas"
            h_col = COLORS["EI"] if "Efecto" in tipo else COLORS["CI"]
            for j, h in enumerate(datos.get(h_tipo, [])):
                if h.get('padre') == it['texto']:
                    h_id = f"{id_p}I{i}_{j}"
                    dot.node(h_id, limpiar(h['texto']), fillcolor=h_col, fontcolor='white', color='none', fontsize='10')
                    dot.edge(node_id, h_id) if edge_dir == "forward" else dot.edge(h_id, node_id)
    return dot

# --- RENDERIZADO DE TARJETA ---
def render_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color = {"Efectos Indirectos": "#884EA0", "Efectos Directos": "#2E86C1", "Problema Principal": "#A93226", "Causas Directas": "#D4AC0D", "Causas Indirectas": "#CA6F1E"}.get(seccion, "#ccc")
    st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    
    nuevo = st.text_area("t", value=item.get('texto', ''), key=f"txt_{id_u}", label_visibility="collapsed")
    if st.button("🗑️", key=f"btn_{id_u}"):
        st.session_state['arbol_tarjetas'][seccion].pop(idx); guardar_datos_nube(); st.rerun()
    if nuevo != item.get('texto', ''): 
        st.session_state['arbol_tarjetas'][seccion][idx]['texto'] = nuevo
        guardar_datos_nube()

# --- SIDEBAR: GESTIÓN DE DATOS ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Nivel a agregar:", ["Efectos Indirectos", "Efectos Directos", "Problema Principal", "Causas Directas", "Causas Indirectas"], index=2)
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción de la ficha:")
        padre_asociado = None
        if "Indirect" in tipo_sel:
            p_key = "Efectos Directos" if "Efecto" in tipo_sel else "Causas Directas"
            opciones = [it['texto'] for it in st.session_state.get('arbol_tarjetas', {}).get(p_key, []) if isinstance(it, dict)]
            if opciones: padre_asociado = st.selectbox("Vincular a ficha superior:", opciones)
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            nueva = {"texto": texto_input, "id_unico": str(uuid.uuid4())}
            if padre_asociado: nueva["padre"] = padre_asociado
            if tipo_sel == "Problema Principal": st.session_state['arbol_tarjetas'][tipo_sel] = [nueva]
            else: st.session_state['arbol_tarjetas'][tipo_sel].append(nueva)
            guardar_datos_nube(); st.rerun()
    st.divider()
    grafo = generar_grafo_problemas()
    if grafo: st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_problemas.png", use_container_width=True)

# --- PANEL PRINCIPAL: SISTEMA DE PESTAÑAS ---
tab1, tab2 = st.tabs(["🌳 Visualización del Árbol", "📝 Constructor y Edición"])

with tab1:
    if not hay_datos:
        st.markdown("""
            <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; padding: 40px; border-radius: 20px; text-align: center; margin-top: 20px;">
                <h2 style="color: #64748b;">🎯 ¡Bienvenido a JCFlow!</h2>
                <p style="color: #94a3b8; font-size: 18px;">Su árbol aparecerá aquí una vez que defina el <b>Problema Principal</b> desde el menú lateral.</p>
                <div style="font-size: 50px;">🏗️</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        grafo_f = generar_grafo_problemas()
        if grafo_f:
            st.image(grafo_f.pipe(format='png'), use_container_width=True)

with tab2:
    if not hay_datos:
        st.info("💡 Utilice el menú lateral para agregar el Problema Principal y comenzar a construir su árbol.")
    else:
        st.subheader("📋 Panel de Edición de Fichas")
        
        def mostrar_seccion_dinamica(tipo_padre, tipo_hijo):
            padres = st.session_state.get('arbol_tarjetas', {}).get(tipo_padre, [])
            if not padres: return
            
            st.write(f"**{tipo_padre}**")
            cols = st.columns(len(padres))
            for i, p in enumerate(padres):
                with cols[i]:
                    render_card(tipo_padre, p, i)
                    # Mostrar hijos asociados justo debajo
                    hijos = [h for h in st.session_state.get('arbol_tarjetas', {}).get(tipo_hijo, []) if h.get('padre') == p.get('texto')]
                    for j, h in enumerate(hijos):
                        idx_real = st.session_state['arbol_tarjetas'][tipo_hijo].index(h)
                        render_card(tipo_hijo, h, idx_real)

        mostrar_seccion_dinamica("Efectos Directos", "Efectos Indirectos")
        st.markdown("---")
        st.write("**Problema Principal**")
        render_card("Problema Principal", pc_data[0], 0)
        st.markdown("---")
        mostrar_seccion_dinamica("Causas Directas", "Causas Indirectas")
