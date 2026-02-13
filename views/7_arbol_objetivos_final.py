import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import copy
import os
import uuid # Sistema de Pasaportes Únicos
from session_state import inicializar_session, guardar_datos_nube

# 1. Carga de datos persistentes
inicializar_session()

# --- ESTILO: PAPELERAS ROJAS VS BOTONES NORMALES ---
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
    /* Solo las papeleras del área principal son rojas y transparentes */
    .main .stButton button {
        border: none !important;
        background: transparent !important;
        color: #ff4b4b !important;
        font-size: 1.2rem !important;
        margin-top: -15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO Y TÍTULO ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🎯 7. Árbol de Objetivos Final")
with col_logo:
    # Ajuste para evitar avisos: width="stretch"
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", width="stretch")

st.info("Podado Manual: Los cambios aquí no afectan al Árbol original de la Fase 5.")

# --- FUNCIÓN DE ALTURA DINÁMICA ---
def calcular_altura_web(texto, min_h=100):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 30)
    return max(min_h, (lineas + 2) * 22)

CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "label": "ACTIVIDADES"}
}

# --- SIDEBAR: HERRAMIENTAS Y EXPORTACIÓN PNG ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    # 1. Importación con IDs Únicos
    if st.button("♻️ Importar desde Paso 5", use_container_width=True):
        datos_original = copy.deepcopy(st.session_state.get('arbol_objetivos', {}))
        datos_con_id = {}
        for seccion, lista in datos_original.items():
            procesados = []
            for item in lista:
                if isinstance(item, dict):
                    item['id_unico'] = str(uuid.uuid4())
                    procesados.append(item)
                else:
                    procesados.append({'texto': item, 'id_unico': str(uuid.uuid4())})
            datos_con_id[seccion] = procesados
        st.session_state['arbol_objetivos_final'] = datos_con_id
        guardar_datos_nube(); st.rerun()

    st.divider()

    # 2. Función de Generación de PNG con ajuste de altura
    def generar_png_final():
        fig, ax = plt.subplots(figsize=(22, 26)) # Lienzo más alto
        # Ampliamos el techo del gráfico (ylim de 14 a 22)
        ax.set_xlim(0, 10); ax.set_ylim(-12, 22); ax.axis('off')
        
        # Subimos el título a y=20 para que no lo toquen los Fines
        ax.text(5, 20, "ÁRBOL DE OBJETIVOS FINAL", fontsize=32, fontweight='bold', ha='center', color='#1E3A8A')
        
        datos = st.session_state.get('arbol_objetivos_final', {})
        # Re-ajuste de niveles base para dar más aire
        Y_LEVELS = {"Fin Último": 14.0, "Fines Indirectos": 11.5, "Fines Directos": 8.0, 
                    "Objetivo General": 4.0, "Medios Directos": 0.5, "Medios Indirectos": -4.0}
        stacks = {}

        def dibujar_caja(x, y, texto, color):
            lineas = textwrap.wrap(texto, width=18)
            txt_ajustado = "\n".join(lineas[:10])
            n_lineas = len(lineas[:10])
            rect_h = max(1.2, 0.4 + (n_lineas * 0.3)) # Altura para 10 líneas
            rect_w = 2.0
            ax.add_patch(plt.Rectangle((x-rect_w/2, y-rect_h/2), rect_w, rect_h, facecolor=color, edgecolor='#333', lw=1.5, zorder=3))
            ax.text(x, y, txt_ajustado, ha='center', va='center', fontsize=8.5, fontweight='bold', zorder=4, color='#31333F')
            return rect_h

        m_dir = datos.get("Medios Directos", [])
        pos_x_medios = {(m.get('texto') if isinstance(m, dict) else m): (i+1)*(10/(len(m_dir)+1)) for i, m in enumerate(m_dir)}
        f_dir = datos.get("Fines Directos", [])
        pos_x_fines = {(f.get('texto') if isinstance(f, dict) else f): (i+1)*(10/(len(f_dir)+1)) for i, f in enumerate(f_dir)}

        for sec, y_base in Y_LEVELS.items():
            items = datos.get(sec, [])
            for it in items:
                txt = it.get("texto", "") if isinstance(it, dict) else it
                if sec in ["Fin Último", "Objetivo General"]: x = 5.0
                elif sec == "Medios Directos": x = pos_x_medios.get(txt, 5.0)
                elif sec == "Fines Directos": x = pos_x_fines.get(txt, 5.0)
                elif sec == "Medios Indirectos": x = pos_x_medios.get(it.get("padre"), 5.0)
                elif sec == "Fines Indirectos": x = pos_x_fines.get(it.get("padre"), 5.0)
                
                offset = stacks.get((sec, x), 0)
                # Para Fines crecemos hacia arriba, para Medios hacia abajo
                current_y = y_base + offset if "Fin" in sec else y_base - offset
                h_caja = dibujar_caja(x, current_y, txt, CONFIG_OBJ[sec]["color"])
                stacks[(sec, x)] = offset + h_caja + 0.8 # Espaciado entre cajas hermanas

        buf = io.BytesIO(); plt.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor='white'); plt.close(fig)
        return buf.getvalue()

    # Limpieza de avisos: width="stretch"
    st.download_button("🖼️ Descargar Árbol Final", data=generar_png_final(), file_name="arbol_objetivos_final.png", width="stretch")

# --- RENDERIZADO WEB (CON PASAPORTES) ---
def render_poda_card(seccion, item):
    id_id = item.get('id_unico', 'temp')
    texto_actual = item.get("texto", "")
    color = CONFIG_OBJ[seccion]["color"]
    
    st.markdown(f'<div style="background-color: {color}; height: 8px; border-radius: 10px 10px 0 0;"></div>', unsafe_allow_html=True)
    
    nuevo_texto = st.text_area(
        label=f"p_{id_id}", value=texto_actual, label_visibility="collapsed", 
        height=calcular_altura_web(texto_actual), key=f"txt_{id_id}"
    )
    
    if st.button("🗑️", key=f"btn_{id_id}"):
        st.session_state['arbol_objetivos_final'][seccion] = [
            x for x in st.session_state['arbol_objetivos_final'][seccion] if x.get('id_unico') != id_id
        ]
        guardar_datos_nube(); st.rerun()
    
    if nuevo_texto != texto_actual:
        item["texto"] = nuevo_texto
        guardar_datos_nube()

# --- FUNCIONES DE ESTRUCTURA ---
def mostrar_seccion_simple_poda(key_interna):
    label_visual = CONFIG_OBJ[key_interna]["label"]
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"**{label_visual}**")
    with col_c:
        items = st.session_state['arbol_objetivos_final'].get(key_interna, [])
        if items: render_poda_card(key_interna, items[0])

def mostrar_rama_jerarquica_poda(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos_final'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos_final'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]
    
    for seccion_actual, es_hijo in orden:
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='margin-top:25px;'>**{CONFIG_OBJ[seccion_actual]['label']}**</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    p_txt = p_data.get("texto", "")
                    with cols[i]:
                        if es_hijo:
                            h_rel = [h for h in hijos if h.get("padre") == p_txt]
                            for h_data in h_rel: render_poda_card(seccion_actual, h_data)
                        else: render_poda_card(seccion_actual, p_data)

# --- CONSTRUCCIÓN ---
arbol_f = st.session_state.get('arbol_objetivos_final', {})
if not arbol_f:
    st.warning("El árbol está vacío. Use 'Importar desde Paso 5' en la barra lateral.")
else:
    st.divider()
    mostrar_seccion_simple_poda("Fin Último")
    st.markdown("---")
    mostrar_rama_jerarquica_poda("Fines Directos", "Fines Indirectos", inversion=True)
    st.markdown("---")
    mostrar_seccion_simple_poda("Objetivo General")
    st.markdown("---")
    mostrar_rama_jerarquica_poda("Medios Directos", "Medios Indirectos", inversion=False)
