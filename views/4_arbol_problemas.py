import streamlit as st
import graphviz
import os
import uuid
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar persistencia
inicializar_session()

# --- ESTILO DE TABLA RÍGIDA (Alineación Horizontal Forzada) ---
st.markdown("""
    <style>
    /* Contenedor de celda de tabla */
    .celda-tabla {
        border: 1px dashed #ccc; /* Guía visual opcional, puedes quitarla */
        padding: 5px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 120px;
    }

    /* Estética de Tarjetas: Fusión total (Aprobada) */
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        border: none !important;           
        border-radius: 0 0 10px 10px !important;
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #000 !important;
        box-shadow: none !important;
        min-height: 80px !important;
    }
    
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.1rem !important;
        margin-top: -10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- PALETA DE COLORES ---
CONFIG_PROB = {
    "Efectos Indirectos": {"color": "#884EA0", "label": "EFECTOS INDIRECTOS"},
    "Efectos Directos": {"color": "#2E86C1", "label": "EFECTOS DIRECTOS"},
    "Problema Principal": {"color": "#A93226", "label": "PROBLEMA CENTRAL"},
    "Causas Directas": {"color": "#D4AC0D", "label": "CAUSAS DIRECTAS"},
    "Causas Indirectas": {"color": "#CA6F1E", "label": "CAUSAS INDIRECTAS"}
}

# --- FUNCIONES DE APOYO ---
def render_card(seccion, item, idx):
    if not isinstance(item, dict): return
    id_u = item.get('id_unico', str(uuid.uuid4()))
    st.markdown(f'<div style="background-color: {CONFIG_PROB[seccion]["color"]}; height: 12px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    nuevo = st.text_area("t", value=item['texto'], key=f"txt_{id_u}", label_visibility="collapsed")
    if st.button("🗑️", key=f"btn_{id_u}"):
        if seccion in st.session_state['arbol_tarjetas']:
            st.session_state['arbol_tarjetas'][seccion].pop(idx)
            guardar_datos_nube()
            st.rerun()
    if nuevo != item['texto']:
        item['texto'] = nuevo
        guardar_datos_nube()

# --- SIDEBAR (GESTIÓN) ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Sección:", list(CONFIG_PROB.keys()))
    with st.form("crear_ficha", clear_on_submit=True):
        txt = st.text_area("Descripción:")
        padre = None
        if "Indirect" in tipo_sel:
            p_key = "Efectos Directos" if "Efecto" in tipo_sel else "Causas Directas"
            opciones = [it['texto'] for it in st.session_state['arbol_tarjetas'].get(p_key, [])]
            if opciones: padre = st.selectbox("Vincular a:", opciones)
        if st.form_submit_button("Agregar") and txt:
            nueva = {"texto": txt, "id_unico": str(uuid.uuid4())}
            if padre: nueva["padre"] = padre
            if tipo_sel == "Problema Principal": st.session_state['arbol_tarjetas'][tipo_sel] = [nueva]
            else: st.session_state['arbol_tarjetas'][tipo_sel].append(nueva)
            guardar_datos_nube(); st.rerun()

# --- PANEL PRINCIPAL ---
st.title("🌳 Árbol de Problemas (Estructura Rígida)")

if any(st.session_state['arbol_tarjetas'].values()):
    # 1. SECCIÓN DE EFECTOS (ESTRUCTURA DE TABLA)
    st.subheader("📋 Efectos")
    ef_dir = st.session_state['arbol_tarjetas'].get("Efectos Directos", [])
    ef_ind = st.session_state['arbol_tarjetas'].get("Efectos Indirectos", [])

    if ef_dir:
        # Fila para Efectos Indirectos (Hijos)
        # Buscamos el máximo de hijos para saber cuántas sub-filas necesitamos
        max_hijos = 0
        hijos_por_padre = []
        for ed in ef_dir:
            hijos = [(idx, h) for idx, h in enumerate(ef_ind) if h.get('padre') == ed['texto']]
            hijos_por_padre.append(hijos)
            max_hijos = max(max_hijos, len(hijos))

        # Renderizamos los hijos fila por fila para que se mantengan alineados
        for h_idx in range(max_hijos):
            cols = st.columns(len(ef_dir))
            for p_idx, col in enumerate(cols):
                with col:
                    if h_idx < len(hijos_por_padre[p_idx]):
                        idx_real, hijo_data = hijos_por_padre[p_idx][h_idx]
                        render_card("Efectos Indirectos", hijo_data, idx_real)
                    else:
                        st.write("") # Espacio vacío para mantener la celda

        st.divider()
        # Fila Final de Padres (Efectos Directos) - AQUÍ SE LOGRA EL ANCLAJE HORIZONTAL
        cols_p = st.columns(len(ef_dir))
        for i, ed in enumerate(ef_dir):
            with cols_p[i]:
                render_card("Efectos Directos", ed, i)

    st.markdown("---")
    # 2. PROBLEMA CENTRAL
    st.subheader("🔴 Problema Principal")
    pc = st.session_state['arbol_tarjetas'].get("Problema Principal", [])
    if pc: render_card("Problema Principal", pc[0], 0)

    st.markdown("---")
    # 3. SECCIÓN DE CAUSAS (ESTRUCTURA ORIGINAL - FUNCIONA BIEN)
    st.subheader("🟡 Causas")
    ca_dir = st.session_state['arbol_tarjetas'].get("Causas Directas", [])
    ca_ind = st.session_state['arbol_tarjetas'].get("Causas Indirectas", [])
    if ca_dir:
        cols_ca = st.columns(len(ca_dir))
        for i, cd in enumerate(ca_dir):
            with cols_ca[i]:
                render_card("Causas Directas", cd, i)
                for idx_hc, hc in enumerate(ca_ind):
                    if hc.get('padre') == cd['texto']:
                        render_card("Causas Indirectas", hc, idx_hc)
