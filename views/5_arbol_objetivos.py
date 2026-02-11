import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session, guardar_datos_nube

# Asegurar persistencia del estado
inicializar_session()

# --- ESTILO MAESTRO UNIFICADO ---
st.markdown("""
    <style>
    /* 1. Tipografía general */
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif;
        color: #31333F;
    }
    
    /* 2. Botón de Guardar (Primario): Texto blanco siempre visible */
    .stButton button[kind="primary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* 3. Papeleras en el área central: Rojo y negrita */
    .main .stButton button:not([kind="primary"]) p {
        color: #ff4b4b !important;
        font-weight: bold !important;
        font-size: 1.1rem;
    }

    /* 4. Botón Cerrar Sesión (Sidebar): Negro y sin negrilla */
    [data-testid="stSidebar"] .stButton button:not([kind="primary"]) p {
        color: black !important;
        font-weight: normal !important;
        font-size: 1rem;
    }
    
    .stButton button {
        border-color: rgba(49, 51, 63, 0.2) !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 5. Árbol de Objetivos")

# 1. Configuración Maestra (Fin Último restaurado en visualización)
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5, "tipo": "simple"}, # Restaurado
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "tipo": "hijo", "padre": "Fines Directos"},
    "Fines Directos": {"color": "#80BFFF", "y": 3, "tipo": "simple"},
    "Objetivo General": {"color": "#D1C4E9", "y": 2, "tipo": "simple"},
    "Medios Directos": {"color": "#FFF9C4", "y": 1, "tipo": "simple"},
    "Medios Indirectos": {"color": "#FFE0B2", "y": 0, "tipo": "hijo", "padre": "Medios Directos"}
}

# --- SIDEBAR: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    # Mapeo: No incluye "Fin Último", cumpliendo tu solicitud de no traer nada para esa tarjeta
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {
            "Efectos Indirectos": "Fines Indirectos",
            "Efectos Directos": "Fines Directos", 
            "Problema Principal": "Objetivo General", 
            "Causas Directas": "Medios Directos", 
            "Causas Indirectas": "Medios Indirectos"
        }
        for p_sec, o_sec in mapeo.items():
            if p_sec in problemas:
                st.session_state['arbol_objetivos'][o_sec] = []
                for item in problemas[p_sec]:
                    if isinstance(item, dict):
                        st.session_state['arbol_objetivos'][o_sec].append({
                            "texto": item['texto'], 
                            "padre": item['padre']
                        })
                    else:
                        st.session_state['arbol_objetivos'][o_sec].append(item)
        st.success("¡Datos convertidos! Fin Último se mantiene vacío para tu redacción.")
        st.rerun()

    st.divider()

    # Función de exportación completa
    def exportar_objetivos_png():
        fig, ax = plt.subplots(figsize=(14, 14))
        ax.set_xlim(0, 10); ax.set_ylim(-0.5, 6); ax.axis('off')
        datos = st.session_state['arbol_objetivos']
        for sec, conf in CONFIG_OBJ.items():
            items = datos.get(sec, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            for i, item in enumerate(items):
                x = (i + 1) * espacio
                txt = item["texto"] if isinstance(item, dict) else item
                rect = plt.Rectangle((x-1.0, conf["y"]-0.3), 2.0, 0.6, facecolor=conf["color"], edgecolor='#333', lw=1)
                ax.add_patch(rect)
                txt_wrap = "\n".join(textwrap.wrap(txt, width=22))
                ax.text(x, conf["y"], txt_wrap, ha='center', va='center', fontsize=8, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol (PNG)", data=exportar_objetivos_png(), file_name="arbol_objetivos.png", mime="image/png", use_container_width=True)

# --- FUNCIONES DE RENDERIZADO (ESTILO INTERESADOS) ---

def render_simple_obj(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l: 
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        # Asegurar que la llave exista para evitar errores
        if nombre not in st.session_state['arbol_objetivos']: st.session_state['arbol_objetivos'][nombre] = []
        
        items = st.session_state['arbol_objetivos'].get(nombre, [])
        
        # Permitir creación manual si está vacío (especialmente para Fin Último)
        if not items:
            if st.button(f"➕ Definir {nombre}", key=f"add_{nombre}"):
                st.session_state['arbol_objetivos'][nombre] = ["Nueva idea"]; st.rerun()
        else:
            with st.container(border=True):
                val_actual = items[0]["texto"] if isinstance(items[0], dict) else items[0]
                nuevo_val = st.text_area(f"Editar {nombre}:", value=val_actual, key=f"edit_{nombre}", label_visibility="collapsed")
                if nuevo_val != val_actual:
                    if isinstance(items[0], dict): st.session_state['arbol_objetivos'][nombre][0]["texto"] = nuevo_val
                    else: st.session_state['arbol_objetivos'][nombre][0] = nuevo_val
                    st.rerun()
            if st.button("🗑️", key=f"del_{nombre}"):
                st.session_state['arbol_objetivos'][nombre] = []; st.rerun()

def render_rama_objetivos(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:30px;'>{seccion.upper()}</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_item in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            p_nombre = p_item["texto"] if isinstance(p_item, dict) else p_item
                            hijos_p = [h for h in hijos if isinstance(h, dict) and h.get("padre") == p_nombre]
                            for h_idx, h_data in enumerate(hijos_p):
                                with st.container(border=True):
                                    n_val_h = st.text_area(f"Hijo {i}_{h_idx}", value=h_data["texto"], key=f"ed_h_{seccion}_{i}_{h_idx}", label_visibility="collapsed")
                                    if n_val_h != h_data["texto"]:
                                        real_idx = next(idx for idx, x in enumerate(hijos) if x == h_data)
                                        st.session_state['arbol_objetivos'][seccion][real_idx]["texto"] = n_val_h; st.rerun()
                                if st.button("🗑️", key=f"del_h_{seccion}_{i}_{h_idx}"):
                                    st.session_state['arbol_objetivos'][seccion].remove(h_data); st.rerun()
                        else:
                            p_txt = p_item["texto"] if isinstance(p_item, dict) else p_item
                            with st.container(border=True):
                                n_val_p = st.text_area(f"Padre {i}", value=p_txt, key=f"ed_p_{seccion}_{i}", label_visibility="collapsed")
                                if n_val_p != p_txt:
                                    if isinstance(p_item, dict): st.session_state['arbol_objetivos'][seccion][i]["texto"] = n_val_p
                                    else: st.session_state['arbol_objetivos'][seccion][i] = n_val_p
                                    for h in hijos: 
                                        if isinstance(h, dict) and h.get("padre") == p_txt: h["padre"] = n_val_p
                                    st.rerun()
                            if st.button("🗑️", key=f"del_p_{seccion}_{i}"):
                                st.session_state['arbol_objetivos'][seccion].pop(i); st.rerun()
            else: st.caption("Sección vacía")

# --- DIBUJO DEL ÁRBOL ---
st.divider()
render_simple_obj("Fin Último")
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_rama_objetivos("Fines Directos", "Fines Indirectos", inversion=True)
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
st.success("🎯 **OBJETIVO GENERAL** (Redactar en positivo)")
render_simple_obj("Objetivo General")
st.markdown("<hr style='border: 1.5px solid #31333F; opacity: 0.1;'>", unsafe_allow_html=True)
render_rama_objetivos("Medios Directos", "Medios Indirectos", inversion=False)

st.divider()
if st.button("🗑️ Limpiar Todo el Árbol", type="secondary"):
    for k in st.session_state['arbol_objetivos']: st.session_state['arbol_objetivos'][k] = []
    st.rerun()
