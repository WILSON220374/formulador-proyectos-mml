import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Persistencia y Memoria
inicializar_session()

# --- ESTILO: CENTRADO Y TARJETAS ELÁSTICAS ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Source Sans Pro', sans-serif; }
    div[data-testid="stTextArea"] textarea {
        background-color: #f0f2f6 !important;
        border-radius: 0 0 10px 10px !important;
        border: 1px solid #e6e9ef !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #31333F !important;
        text-align: center !important;
        padding-top: 15px !important; 
    }
    div[data-testid="stTextArea"] textarea:focus { border-color: #d0d4dc !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. ENCABEZADO CON LOGO (ZONA AMARILLA) ---
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🎯 5. Árbol de Objetivos")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- FUNCIÓN DE ALTURA DINÁMICA PARA WEB ---
def calcular_altura_web(texto, min_h=100):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 30)
    return max(min_h, (lineas + 2) * 22)

# Configuración Maestra con coordenadas optimizadas para apilamiento
CONFIG_OBJ = {
    "Fin Último": {"color": "#C1E1C1", "y": 12.0, "label": "FIN ÚLTIMO"},
    "Fines Indirectos": {"color": "#B3D9FF", "y": 9.5, "label": "FINES INDIRECTOS"},
    "Fines Directos": {"color": "#80BFFF", "y": 7.0, "label": "FINES DIRECTOS"},
    "Objetivo General": {"color": "#FFB3BA", "y": 4.0, "label": "OBJETIVO GENERAL"},
    "Medios Directos": {"color": "#FFFFBA", "y": 1.0, "label": "OBJETIVOS ESPECÍFICOS"},
    "Medios Indirectos": {"color": "#FFDFBA", "y": -2.0, "label": "ACTIVIDADES"}
}

# --- 3. SIDEBAR: HERRAMIENTAS Y EXPORTACIÓN MEJORADA ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    if st.button("✨ Traer desde Árbol de Problemas", use_container_width=True):
        problemas = st.session_state.get('arbol_tarjetas', {})
        mapeo = {"Efectos Indirectos": "Fines Indirectos", "Efectos Directos": "Fines Directos", 
                 "Problema Principal": "Objetivo General", "Causas Directas": "Medios Directos", 
                 "Causas Indirectas": "Medios Indirectos"}
        for k in CONFIG_OBJ: st.session_state['arbol_objetivos'][k] = []
        for p_sec, o_sec in mapeo.items():
            items_raw = problemas.get(p_sec, [])
            for item in items_raw:
                txt = item['texto'] if isinstance(item, dict) else item
                if isinstance(txt, str) and len(txt.strip()) > 2:
                    if isinstance(item, dict):
                        st.session_state['arbol_objetivos'][o_sec].append({"texto": txt.upper(), "padre": item['padre'].upper()})
                    else:
                        st.session_state['arbol_objetivos'][o_sec].append(txt.upper())
        if not st.session_state['arbol_objetivos']["Fin Último"]:
            st.session_state['arbol_objetivos']["Fin Último"] = ["MEJORAR LA CALIDAD DE VIDA"]
        guardar_datos_nube(); st.rerun()

    st.divider()

    # --- MOTOR DE EXPORTACIÓN (APILAMIENTO VERTICAL FIEL) ---
    def generar_png_objetivos():
        fig, ax = plt.subplots(figsize=(24, 24))
        ax.set_xlim(0, 10); ax.set_ylim(-6, 14); ax.axis('off')
        ax.text(5, 13.2, "ÁRBOL DE OBJETIVOS", fontsize=32, fontweight='bold', ha='center', color='#1E3A8A')
        
        datos = st.session_state['arbol_objetivos']
        
        def dibujar_caja(x, y, texto, color, rect_w=1.8):
            lineas = textwrap.wrap(texto, width=18)
            txt_ajustado = "\n".join(lineas[:10])
            n_lineas = len(lineas[:10])
            rect_h = max(1.0, 0.4 + (n_lineas * 0.28))
            rect = plt.Rectangle((x - rect_w/2, y - rect_h/2), rect_w, rect_h, 
                                 facecolor=color, edgecolor='#333', lw=1.5, zorder=3)
            ax.add_patch(rect)
            ax.text(x, y, txt_ajustado, ha='center', va='center', fontsize=8.5, 
                    fontweight='bold', zorder=4, color='#31333F')

        # 1. Fin Último y Objetivo General (Simples)
        for sec in ["Fin Último", "Objetivo General"]:
            if datos.get(sec):
                dibujar_caja(5, CONFIG_OBJ[sec]["y"], datos[sec][0], CONFIG_OBJ[sec]["color"])

        # 2. Ramas Jerárquicas (Fines y Medios)
        for principal, sec_hija in [("Fines Directos", "Fines Indirectos"), ("Medios Directos", "Medios Indirectos")]:
            padres = datos.get(principal, [])
            if padres:
                espacio = 10 / (len(padres) + 1)
                for i, p_data in enumerate(padres):
                    x_p = (i + 1) * espacio
                    p_txt = p_data["texto"] if isinstance(p_data, dict) else p_data
                    dibujar_caja(x_p, CONFIG_OBJ[principal]["y"], p_txt, CONFIG_OBJ[principal]["color"])
                    
                    # Dibujar hijos agrupados verticalmente bajo/sobre el padre
                    hijos = [h for h in datos.get(sec_hija, []) if isinstance(h, dict) and h.get("padre") == p_txt]
                    direccion = 1 if "Fines" in principal else -1
                    for j, h_data in enumerate(hijos):
                        h_y = CONFIG_OBJ[principal]["y"] + (direccion * (j + 1) * 1.3)
                        dibujar_caja(x_p, h_y, h_data["texto"], CONFIG_OBJ[sec_hija]["color"])

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return buf.getvalue()

    st.download_button("🖼️ Descargar Árbol (PNG)", data=generar_png_objetivos(), file_name="arbol_objetivos_fiel.png", mime="image/png", use_container_width=True)

# --- 4. RENDERIZADO WEB (VÍNCULOS Y ALTURA DINÁMICA) ---
def render_objective_card(seccion, indice_global, item):
    texto_actual = item["texto"] if isinstance(item, dict) else item
    color = CONFIG_OBJ[seccion]["color"]
    st.markdown(f'<div style="background-color: {color}; height: 6px; border-radius: 10px 10px 0 0; margin-bottom: 0px;"></div>', unsafe_allow_html=True)
    
    # Altura dinámica aplicada para que no se corte el texto
    nuevo_texto = st.text_area(
        label=f"edit_{seccion}_{indice_global}", 
        value=texto_actual, 
        label_visibility="collapsed", 
        key=f"area_{seccion}_{indice_global}", 
        height=calcular_altura_web(texto_actual)
    )
    
    if nuevo_texto != texto_actual:
        if isinstance(item, dict):
            st.session_state['arbol_objetivos'][seccion][indice_global]["texto"] = nuevo_texto
        else:
            st.session_state['arbol_objetivos'][seccion][indice_global] = nuevo_texto
        
        relaciones = {"Fines Directos": "Fines Indirectos", "Medios Directos": "Medios Indirectos"}
        if seccion in relaciones:
            seccion_hija = relaciones[seccion]
            for h in st.session_state['arbol_objetivos'][seccion_hija]:
                if isinstance(h, dict) and h.get("padre") == texto_actual:
                    h["padre"] = nuevo_texto
        guardar_datos_nube(); st.rerun()

# --- FUNCIONES DE ESTRUCTURA ---
def mostrar_seccion_simple(key_interna):
    label_visual = CONFIG_OBJ[key_interna]["label"]
    col_l, col_c = st.columns([1, 4])
    with col_l: st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{label_visual}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_objetivos'].get(key_interna, [])
        if items: render_objective_card(key_interna, 0, items[0])
        else: st.caption("Sección vacía.")

def mostrar_rama_jerarquica(nombre_padre, nombre_hijo, inversion=False):
    padres = st.session_state['arbol_objetivos'].get(nombre_padre, [])
    hijos = st.session_state['arbol_objetivos'].get(nombre_hijo, [])
    orden = [(nombre_hijo, True), (nombre_padre, False)] if inversion else [(nombre_padre, False), (nombre_hijo, True)]
    for seccion_actual, es_hijo in orden:
        label_visual = CONFIG_OBJ[seccion_actual]["label"]
        col_l, col_c = st.columns([1, 4])
        with col_l: st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:25px;'>{label_visual}</div>", unsafe_allow_html=True)
        with col_c:
            if padres:
                cols = st.columns(len(padres))
                for i, p_data in enumerate(padres):
                    p_txt = p_data["texto"] if isinstance(p_data, dict) else p_data
                    with cols[i]:
                        if es_hijo:
                            h_rel = [(idx, h) for idx, h in enumerate(hijos) if isinstance(h, dict) and h.get("padre") == p_txt]
                            for h_idx_orig, h_data in h_rel: render_objective_card(seccion_actual, h_idx_orig, h_data)
                        else: render_objective_card(seccion_actual, i, p_data)
            else: st.caption(f"Debe definir {nombre_padre} primero.")

# --- CONSTRUCCIÓN DEL ÁRBOL ---
st.divider()
mostrar_seccion_simple("Fin Último")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
mostrar_rama_jerarquica("Fines Directos", "Fines Indirectos", inversion=True)
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
mostrar_seccion_simple("Objetivo General")
st.markdown("<hr style='border: 1.5px solid #eee; opacity: 0.1;'>", unsafe_allow_html=True)
mostrar_rama_jerarquica("Medios Directos", "Medios Indirectos", inversion=False)
