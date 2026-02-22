import streamlit as st
import graphviz
import os
import uuid
import textwrap
import copy
import io
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia y memoria
inicializar_session()

# --- SANEAMIENTO DE DATOS ---
if 'arbol_problemas_final' not in st.session_state or not isinstance(st.session_state.get('arbol_problemas_final'), dict):
    st.session_state['arbol_problemas_final'] = {}

# --- NORMALIZACIÓN DE ESTRUCTURA (evita errores por datos guardados con formatos distintos) ---
def _a_texto_dict(item):
    """Convierte item a dict con clave 'texto' si llega como str/None/etc."""
    if isinstance(item, dict):
        return item
    if item is None:
        return None
    return {"texto": str(item)}

def _a_lista_dicts(valor):
    """
    Garantiza lista de dicts.
    - None -> []
    - dict -> [dict]
    - str/int -> [{'texto': '...'}]
    - list -> normaliza cada elemento a dict
    """
    if valor is None:
        return []
    if isinstance(valor, list):
        out = []
        for it in valor:
            d = _a_texto_dict(it)
            if d is not None:
                out.append(d)
        return out
    if isinstance(valor, dict):
        return [valor]
    return [{"texto": str(valor)}]

# Normalizamos las secciones esperadas dentro del state (esto corrige grupo2 y cualquier otro)
_SECCIONES = [
    "Problema Principal",
    "Efectos Indirectos",
    "Efectos Directos",
    "Causas Directas",
    "Causas Indirectas",
]
for _k in _SECCIONES:
    st.session_state['arbol_problemas_final'][_k] = _a_lista_dicts(st.session_state['arbol_problemas_final'].get(_k))

# --- FUNCIÓN DE EXTRACCIÓN AUTOMÁTICA ---
def obtener_resumen_diagnostico():
    """Lee el estado actual de las tarjetas y genera el resumen limpio."""
    datos = st.session_state['arbol_problemas_final']
    resumen = {
        "problema_central": "",
        "efectos_indirectos": [],
        "efectos_directos": [],
        "causas_directas": [],
        "causas_indirectas": []
    }

    pp = _a_lista_dicts(datos.get("Problema Principal"))
    if pp and isinstance(pp[0], dict):
        resumen["problema_central"] = pp[0].get("texto", "") or ""

    resumen["efectos_indirectos"] = [
        t.get("texto") for t in _a_lista_dicts(datos.get("Efectos Indirectos"))
        if isinstance(t, dict) and t.get("texto")
    ]
    resumen["efectos_directos"] = [
        t.get("texto") for t in _a_lista_dicts(datos.get("Efectos Directos"))
        if isinstance(t, dict) and t.get("texto")
    ]
    resumen["causas_directas"] = [
        t.get("texto") for t in _a_lista_dicts(datos.get("Causas Directas"))
        if isinstance(t, dict) and t.get("texto")
    ]
    resumen["causas_indirectas"] = [
        t.get("texto") for t in _a_lista_dicts(datos.get("Causas Indirectas"))
        if isinstance(t, dict) and t.get("texto")
    ]
    return resumen

def eliminar_tarjeta_poda(seccion, idx):
    """Elimina tarjeta y descendientes con guardado automático."""
    datos = st.session_state['arbol_problemas_final']

    # Asegurar estructura antes de operar
    datos[seccion] = _a_lista_dicts(datos.get(seccion))

    if idx < 0 or idx >= len(datos[seccion]):
        return

    item_a_borrar = datos[seccion].pop(idx)
    texto_padre = item_a_borrar.get("texto") if isinstance(item_a_borrar, dict) else None

    if seccion == "Causas Directas":
        if "Causas Indirectas" in datos:
            datos["Causas Indirectas"] = [
                h for h in _a_lista_dicts(datos.get("Causas Indirectas"))
                if isinstance(h, dict) and h.get("padre") != texto_padre
            ]
    elif seccion == "Efectos Directos":
        if "Efectos Indirectos" in datos:
            datos["Efectos Indirectos"] = [
                h for h in _a_lista_dicts(datos.get("Efectos Indirectos"))
                if isinstance(h, dict) and h.get("padre") != texto_padre
            ]

    guardar_datos_nube()

# --- DISEÑO PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 10rem !important; }
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 15px; }
    .resumen-card {
        background-color: #f8fafc; border: 1px solid #e2e8f0;
        padding: 10px 15px; border-radius: 10px; margin-bottom: 8px;
        font-size: 13px; color: #1e293b; border-left: 5px solid #1E3A8A;
        font-weight: 500;
    }
    .poda-card {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 0 0 10px 10px;
        padding: 15px; text-align: center; font-size: 14px; font-weight: 700;
        color: #1e293b; min-height: 80px; display: flex; align-items: center; justify-content: center; margin-bottom: 5px;
    }
    .header-tabla { font-weight: 800; color: #1E3A8A; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; }
    .main .stButton button { border: none !important; background: transparent !important; color: #ef4444 !important; font-size: 1.1rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
resumen_actual = obtener_resumen_diagnostico()
col_t, col_img = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">🌳 8. Árbol de Problemas Final</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Resumen ejecutivo y ajuste definitivo del diagnóstico.</div>', unsafe_allow_html=True)
    niveles = [resumen_actual["problema_central"], resumen_actual["efectos_directos"], resumen_actual["causas_directas"]]
    puntos = len([n for n in niveles if n])
    st.progress(puntos / 3)

with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)

st.divider()

# --- CONFIGURACIÓN GRAFOS ---
CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#B3D9FF"},
    "Efectos Directos":   {"color": "#80BFFF"},
    "Problema Principal": {"color": "#FFB3BA"},
    "Causas Directas":    {"color": "#FFFFBA"},
    "Causas Indirectas":  {"color": "#FFDFBA"}
}

def generar_grafo_problemas():
    datos = st.session_state.get('arbol_problemas_final', {})
    if not isinstance(datos, dict):
        return None

    # Normalizar lectura para evitar fallos por formato
    tiene_algo = any(_a_lista_dicts(datos.get(k)) for k in CONFIG_PROB.keys())
    if not tiene_algo:
        return None

    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='BT', nodesep='0.4', ranksep='0.6', splines='ortho')
    dot.attr('node', fontsize='11', fontname='Arial', style='filled', shape='box', margin='0.3,0.2', width='2.5')

    def limpiar(t):
        return "\\n".join(textwrap.wrap(str(t).upper(), width=25))

    pp = [it for it in _a_lista_dicts(datos.get("Problema Principal")) if isinstance(it, dict) and it.get('texto')]
    if pp:
        dot.node(
            "PP",
            limpiar(pp[0].get('texto')),
            fillcolor=CONFIG_PROB["Problema Principal"]["color"],
            fontcolor='black',
            color='none',
            width='4.5'
        )

    for tipo, p_id, h_tipo in [
        ("Efectos Directos", "PP", "Efectos Indirectos"),
        ("Causas Directas", "PP", "Causas Indirectas")
    ]:
        items = [it for it in _a_lista_dicts(datos.get(tipo)) if isinstance(it, dict) and it.get('texto')]
        for i, item in enumerate(items):
            n_id = f"{tipo[:2]}{i}"
            dot.node(
                n_id,
                limpiar(item.get('texto')),
                fillcolor=CONFIG_PROB[tipo]["color"],
                fontcolor='black',
                color='none'
            )
            if "Efecto" in tipo:
                dot.edge("PP", n_id)
            else:
                dot.edge(n_id, "PP")

            hijos = [
                h for h in _a_lista_dicts(datos.get(h_tipo))
                if isinstance(h, dict) and h.get('padre') == item.get('texto') and h.get('texto')
            ]
            for j, h in enumerate(hijos):
                h_id = f"{h_tipo[:2]}{i}_{j}"
                dot.node(
                    h_id,
                    limpiar(h.get('texto')),
                    fillcolor=CONFIG_PROB[h_tipo]["color"],
                    fontcolor='black',
                    color='none',
                    fontsize='10'
                )
                if "Efecto" in tipo:
                    dot.edge(n_id, h_id)
                else:
                    dot.edge(h_id, n_id)

    return dot

def render_poda_card(seccion, item, idx):
    if not isinstance(item, dict):
        return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    color_barra = CONFIG_PROB.get(seccion, {}).get("color", "#ccc")
    st.markdown(f'<div style="background-color: {color_barra}; height: 10px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="poda-card">{str(item.get("texto", "")).upper()}</div>', unsafe_allow_html=True)
    st.button("🗑️", key=f"poda_btn_{id_u}", on_click=eliminar_tarjeta_poda, args=(seccion, idx))

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Herramientas")

    def importar_p4():
        st.session_state['arbol_problemas_final'] = copy.deepcopy(st.session_state.get('arbol_tarjetas', {}))
        # Re-normalizar luego de importar
        if not isinstance(st.session_state.get('arbol_problemas_final'), dict):
            st.session_state['arbol_problemas_final'] = {}
        for _k in _SECCIONES:
            st.session_state['arbol_problemas_final'][_k] = _a_lista_dicts(st.session_state['arbol_problemas_final'].get(_k))
        guardar_datos_nube()

    st.button("♻️ Importar desde Paso 4", use_container_width=True, type="primary", on_click=importar_p4)
    st.divider()
    grafo = generar_grafo_problemas()
    if grafo:
        st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol_final.png", use_container_width=True)

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🌳 Visualización", "✂️ Poda y Ajuste"])

with tab1:
    g_f = generar_grafo_problemas()
   if g_f:
            # Muestra la imagen en pantalla (Esto ya lo tienes)
            st.image(g_f.pipe(format='png'), use_container_width=True)
            
            # 👇 NUEVA LÍNEA: Guardamos la foto idéntica en la memoria para el Word 👇
            st.session_state['arbol_problemas_img'] = io.BytesIO(g_f.pipe(format='png'))
with tab2:
    st.markdown("### 📌 Resumen del Diagnóstico Definitivo")
    st.info("La tabla se sincroniza automáticamente con el panel de acción inferior.")

    # 1. PROBLEMA CENTRAL
    st.markdown('<div class="header-tabla">🔴 PROBLEMA CENTRAL</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="resumen-card">{resumen_actual["problema_central"].upper() if resumen_actual["problema_central"] else "SIN DEFINIR"}</div>',
        unsafe_allow_html=True
    )

    # 2. CAUSAS
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown('<div class="header-tabla">🟡 CAUSAS DIRECTAS</div>', unsafe_allow_html=True)
        for c in resumen_actual["causas_directas"]:
            st.markdown(f'<div class="resumen-card">{c}</div>', unsafe_allow_html=True)
    with col_c2:
        st.markdown('<div class="header-tabla">🟠 CAUSAS INDIRECTAS</div>', unsafe_allow_html=True)
        for c in resumen_actual["causas_indirectas"]:
            st.markdown(f'<div class="resumen-card">{c}</div>', unsafe_allow_html=True)

    # 3. EFECTOS
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown('<div class="header-tabla">🔵 EFECTOS DIRECTOS</div>', unsafe_allow_html=True)
        for e in resumen_actual["efectos_directos"]:
            st.markdown(f'<div class="resumen-card">{e}</div>', unsafe_allow_html=True)
    with col_e2:
        st.markdown('<div class="header-tabla">🔵 EFECTOS INDIRECTOS</div>', unsafe_allow_html=True)
        for e in resumen_actual["efectos_indirectos"]:
            st.markdown(f'<div class="resumen-card">{e}</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Panel de Poda (Acción)")

    def mostrar_seccion_final(tipo_padre, tipo_hijo):
        datos_state = st.session_state.get('arbol_problemas_final', {})
        if not isinstance(datos_state, dict):
            return

        # Asegurar estructura para operar con índices reales del state
        datos_state[tipo_padre] = _a_lista_dicts(datos_state.get(tipo_padre))
        datos_state[tipo_hijo] = _a_lista_dicts(datos_state.get(tipo_hijo))

        datos_sec = datos_state.get(tipo_padre, [])
        padres_con_idx = [(idx, p) for idx, p in enumerate(datos_sec) if isinstance(p, dict) and p.get('texto')]
        if not padres_con_idx:
            return

        st.write(f"**{tipo_padre}**")
        hijos = datos_state.get(tipo_hijo, [])
        h_por_p = [
            [(idx_h, h) for idx_h, h in enumerate(hijos) if isinstance(h, dict) and h.get('padre') == p_d.get('texto')]
            for _, p_d in padres_con_idx
        ]
        max_h = max([len(l) for l in h_por_p]) if h_por_p else 0

        if "Efectos" in tipo_padre:
            for h_idx in range(max_h - 1, -1, -1):
                cols = st.columns(len(padres_con_idx))
                for p_col, col in enumerate(cols):
                    with col:
                        if h_idx < len(h_por_p[p_col]):
                            render_poda_card(tipo_hijo, h_por_p[p_col][h_idx][1], h_por_p[p_col][h_idx][0])
            cols_p = st.columns(len(padres_con_idx))
            for i, (idx_o, p_d) in enumerate(padres_con_idx):
                with cols_p[i]:
                    render_poda_card(tipo_padre, p_d, idx_o)
        else:
            cols_p = st.columns(len(padres_con_idx))
            for i, (idx_o, p_d) in enumerate(padres_con_idx):
                with cols_p[i]:
                    render_poda_card(tipo_padre, p_d, idx_o)
            for h_idx in range(max_h):
                cols = st.columns(len(padres_con_idx))
                for p_col, col in enumerate(cols):
                    with col:
                        if h_idx < len(h_por_p[p_col]):
                            render_poda_card(tipo_hijo, h_por_p[p_col][h_idx][1], h_por_p[p_col][h_idx][0])

    mostrar_seccion_final("Efectos Directos", "Efectos Indirectos")
    st.markdown("---")

    # Problema Principal (central) con estructura robusta
    st.session_state['arbol_problemas_final']["Problema Principal"] = _a_lista_dicts(
        st.session_state['arbol_problemas_final'].get("Problema Principal")
    )
    pp_f = st.session_state['arbol_problemas_final'].get("Problema Principal", [])
    if pp_f and isinstance(pp_f[0], dict):
        render_poda_card("Problema Principal", pp_f[0], 0)

    st.markdown("---")
    mostrar_seccion_final("Causas Directas", "Causas Indirectas")
