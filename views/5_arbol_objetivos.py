import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session

# Asegurar persistencia del estado
inicializar_session()

st.title("🎯 5. Árbol de Objetivos (Editor Directo)")

# Configuración Maestra
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 5, "tipo": "simple", "limite": 1},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "tipo": "hijo", "padre": "Fines Directos", "limite": 99},
    "Fines Directos": {"color": "#80BFFF", "y": 3, "tipo": "simple", "limite": 99},
    "Objetivo General": {"color": "#D1C4E9", "y": 2, "tipo": "simple", "limite": 1},
    "Medios Directos": {"color": "#FFF9C4", "y": 1, "tipo": "simple", "limite": 99},
    "Medios Indirectos": {"color": "#FFE0B2", "y": 0, "tipo": "hijo", "padre": "Medios Directos", "limite": 99}
}

# --- SIDEBAR: HERRAMIENTAS ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    # Mapeo exacto sin prefijos
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True):
        problemas = st.session_state['arbol_tarjetas']
        mapeo = {
            "Problema Superior": "Fin Último", "Efectos Indirectos": "Fines Indirectos",
            "Efectos Directos": "Fines Directos", "Problema Central": "Objetivo General",
            "Causas Directas": "Medios Directos", "Causas Indirectas": "Medios Indirectos"
        }
        for p_sec, o_sec in mapeo.items():
            st.session_state['arbol_objetivos'][o_sec] = []
            for item in problemas[p_sec]:
                if isinstance(item, dict):
                    # Copia exacta de texto y relación padre
                    st.session_state['arbol_objetivos'][o_sec].append({
                        "texto": item['texto'], 
                        "padre": item['padre']
                    })
                else:
                    st.session_state['arbol_objetivos'][o_sec].append(item)
        st.success("¡Información copiada! Ahora puedes editar cada caja.")
        st.rerun()

    st.divider()

    # Exportación a Imagen PNG profesional
    def exportar_objetivos_png():
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 10); ax.set_ylim(-0.5, 6); ax.axis('off')
        datos = st.session_state['arbol_objetivos']
        for sec, conf in CONFIG_OBJ.items():
            items = datos.get(sec, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            for i, item in enumerate(items):
                x = (i + 1) * espacio
                txt = item["texto"] if isinstance(item, dict) else item
                rect = plt.Rectangle((x-0.8, conf["y"]-0.3), 1.6, 0.6, facecolor=conf["color"], edgecolor='black', lw=0.7)
                ax.add_patch(rect)
                txt_wrap = "\n".join(textwrap.wrap(txt, width=18))
                ax.text(x, conf["y"], txt_wrap, ha='center', va='center', fontsize=8, fontweight='bold')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol como Imagen", data=exportar_objetivos_png(), file_name="arbol_objetivos.png", mime="image/png", use_container_width=True)

# --- FUNCIONES DE EDICIÓN Y RENDERIZADO ---

def render_simple_obj(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l: 
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_objetivos'].get(nombre, [])
        if items:
            # Obtener valor actual
            val_actual = items[0]["texto"] if isinstance(items[0], dict) else items[0]
            
            # Caja editable con color de fondo dinámico
            nuevo_val = st.text_area(f"Editar {nombre}:", value=val_actual, key=f"edit_{nombre}", label_visibility="collapsed")
            
            if nuevo_val != val_actual:
                if isinstance(items[0], dict):
                    st.session_state['arbol_objetivos'][nombre][0]["texto"] = nuevo_val
                else:
                    st.session_state['arbol_objetivos'][nombre][0] = nuevo_val
                st.rerun()
        else: st.caption("Sección vacía")

def render_rama_objetivos(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]

    for seccion, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l:
            st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{seccion.upper()}</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_item in enumerate(padres):
                    with cols[i]:
                        if es_hijo:
                            # Renderizar hijos vinculados
                            p_nombre = p_item["texto"] if isinstance(p_item, dict) else p_item
                            hijos_p = [h for h in hijos if h.get("padre") == p_nombre]
                            for h_idx, h_data in enumerate(hijos_p):
                                # Buscar índice real del hijo para actualizarlo
                                real_h_idx = next(idx for idx, x in enumerate(hijos) if x == h_data)
                                
                                # Editor para hijo
                                n_val_h = st.text_area(f"Hijo {i}_{h_idx}", value=h_data["texto"], key=f"ed_h_{seccion}_{i}_{h_idx}", label_visibility="collapsed")
                                if n_val_h != h_data["texto"]:
                                    st.session_state['arbol_objetivos'][seccion][real_h_idx]["texto"] = n_val_h
                                    st.rerun()
                        else:
                            # Editor para padre
                            p_txt = p_item["texto"] if isinstance(p_item, dict) else p_item
                            n_val_p = st.text_area(f"Padre {i}", value=p_txt, key=f"ed_p_{seccion}_{i}", label_visibility="collapsed")
                            
                            if n_val_p != p_txt:
                                # 1. Actualizar el padre
                                if isinstance(p_item, dict):
                                    st.session_state['arbol_objetivos'][seccion][i]["texto"] = n_val_p
                                else:
                                    st.session_state['arbol_objetivos'][seccion][i] = n_val_p
                                
                                # 2. ACTUALIZAR VÍNCULOS DE HIJOS automáticamente
                                for h in hijos:
                                    if h["padre"] == p_txt:
                                        h["padre"] = n_val_p
                                st.rerun()
            else: st.caption("Esperando datos...")

# --- DIBUJO DEL ÁRBOL ---
st.divider()
render_simple_obj("Fin Último")
st.markdown("---")
render_rama_objetivos("Fines Directos", "Fines Indirectos", inversion=True)
st.markdown("---")
st.success("🎯 OBJETIVO GENERAL (Editar para redactar en positivo)")
render_simple_obj("Objetivo General")
st.markdown("---")
render_rama_objetivos("Medios Directos", "Medios Indirectos", inversion=False)

st.divider()
if st.button("Limpiar Árbol de Objetivos", type="secondary"):
    st.session_state['arbol_objetivos'] = {k: [] for k in st.session_state['arbol_objetivos']}
    st.rerun()
