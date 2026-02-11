import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session

# Inicialización de seguridad
inicializar_session()

st.title("🌳 4. Árbol de Problemas (Vista Jerárquica)")

# 1. Configuración Maestra
CONFIG = {
    "Problema Superior": {"color": "#C1E1C1", "limite": 1, "tipo": "simple", "y": 5},
    "Efectos Indirectos": {"color": "#B3D9FF", "limite": 99, "tipo": "hijo", "padre": "Efectos Directos", "y": 4},
    "Efectos Directos": {"color": "#80BFFF", "limite": 99, "tipo": "simple", "y": 3},
    "Problema Central": {"color": "#FFB3BA", "limite": 1, "tipo": "simple", "y": 2},
    "Causas Directas": {"color": "#FFFFBA", "limite": 99, "tipo": "simple", "y": 1},
    "Causas Indirectas": {"color": "#FFDFBA", "limite": 99, "tipo": "hijo", "padre": "Causas Directas", "y": 0}
}

# --- SIDEBAR (Sin Cambios) ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("1. Seleccione Sección:", list(CONFIG.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("2. Descripción de la idea:")
        padre_asociado = None
        if CONFIG[tipo_sel]["tipo"] == "hijo":
            opciones_p = st.session_state['arbol_tarjetas'][CONFIG[tipo_sel]["padre"]]
            if opciones_p:
                padre_asociado = st.selectbox(f"3. Vincular a {CONFIG[tipo_sel]['padre']}:", opciones_p)
            else:
                st.warning(f"Primero cree un {CONFIG[tipo_sel]['padre']}.")
        
        if st.form_submit_button("Generar Ficha") and texto_input:
            if len(st.session_state['arbol_tarjetas'][tipo_sel]) < CONFIG[tipo_sel]["limite"]:
                if CONFIG[tipo_sel]["tipo"] == "hijo" and padre_asociado:
                    st.session_state['arbol_tarjetas'][tipo_sel].append({"texto": texto_input, "padre": padre_asociado})
                else:
                    st.session_state['arbol_tarjetas'][tipo_sel].append(texto_input)
                st.rerun()
            else:
                st.error("Límite de 1 tarjeta alcanzado para esta sección.")

    st.divider()
    st.subheader("📥 Exportar Árbol")
    # (Función de imagen PNG omitida para ahorrar espacio, es la misma de antes)
    # ... (Tu código de generar_png_arbol aquí si lo necesitas) ...

# --- FUNCIONES DE RENDERIZADO CON CONECTORES ---

# 1. HTML para las tarjetas (con un pequeño ajuste de margen)
def card_html(texto, color):
    return f"""<div style="background-color:{color}; padding:10px; border-radius:8px; 
               border-left:6px solid rgba(0,0,0,0.2); color:#333; font-weight:500; 
               margin: 5px 0; min-height:60px; box-shadow: 2px 2px 4px #ddd; 
               display: flex; align-items: center; justify-content: center; text-align: center; font-size:14px;">
               {texto}</div>"""

# 2. HTML para la LÍNEA CONECTORA VERTICAL (NUEVO)
HTML_CONECTOR = """
<div style="display: flex; justify-content: center; margin: -8px 0 -8px 0; z-index: 0; position: relative;">
    <div style="width: 4px; height: 30px; background-color: #aaa; border-radius: 2px;"></div>
</div>
"""

# 3. Renderizado de elementos simples (Problema Central/Superior)
def render_simple(nombre):
    col_l, col_c = st.columns([1, 4])
    with col_l:
        st.markdown(f"<div style='font-weight:bold; color:#444; text-align:right; margin-top:20px;'>{nombre.upper()}</div>", unsafe_allow_html=True)
    with col_c:
        items = st.session_state['arbol_tarjetas'][nombre]
        if items:
            # Si es Problema Central, usamos el texto de la Fase 1
            if nombre == "Problema Central":
                 texto_pc = st.session_state.get('datos_problema', {}).get('problema_central', items[0])
                 st.markdown(card_html(texto_pc, CONFIG[nombre]["color"]), unsafe_allow_html=True)
            else:
                 st.markdown(card_html(items[0], CONFIG[nombre]["color"]), unsafe_allow_html=True)
                 
            if nombre != "Problema Central" and st.button("🗑️ Borrar", key=f"del_{nombre}"):
                st.session_state['arbol_tarjetas'][nombre] = []
                st.rerun()
        else:
             if nombre == "Problema Central":
                  texto_pc = st.session_state.get('datos_problema', {}).get('problema_central', "No definido en Fase 1")
                  st.markdown(card_html(texto_pc, CONFIG[nombre]["color"]), unsafe_allow_html=True)
             else:
                  st.caption("Sección vacía")

# 4. NUEVA FUNCIÓN: Renderizado de Ramas Conectadas
def render_rama_conectada(nombre_directo, nombre_indirecto, efectos=False):
    """Dibuja una rama completa (Directo + Indirectos asociados) en una sola columna con conectores."""
    directos = st.session_state['arbol_tarjetas'][nombre_directo]
    indirectos = st.session_state['arbol_tarjetas'][nombre_indirecto]

    # Etiquetas laterales
    col_l, col_c = st.columns([1, 4])
    with col_l:
        if efectos:
             st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{nombre_indirecto.upper()}</div>", unsafe_allow_html=True)
             st.markdown("<br>"*3, unsafe_allow_html=True) # Espacio para alinear
             st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right;'>{nombre_directo.upper()}</div>", unsafe_allow_html=True)
        else:
             st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right; margin-top:25px;'>{nombre_directo.upper()}</div>", unsafe_allow_html=True)
             st.markdown("<br>"*3, unsafe_allow_html=True)
             st.markdown(f"<div style='font-weight:bold; color:#666; text-align:right;'>{nombre_indirecto.upper()}</div>", unsafe_allow_html=True)

    # Contenido de las tarjetas
    with col_c:
        if not directos:
            st.info(f"👉 Agregue primero un '{nombre_directo}' desde el menú lateral.")
            return

        # Creamos una columna por cada elemento directo
        cols = st.columns(len(directos))
        for i, padre_txt in enumerate(directos):
            with cols[i]:
                # Buscar hijos asociados a este padre
                hijos_asociados = [h for h in indirectos if h["padre"] == padre_txt]

                if efectos:
                    # LÓGICA PARA EFECTOS (Indirectos ARRIBA -> Directos ABAJO)
                    for h_idx, h_data in enumerate(hijos_asociados):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_indirecto]["color"]), unsafe_allow_html=True)
                        # Botón de borrar pequeño para el hijo
                        if st.button("ｘ", key=f"del_h_{nombre_indirecto}_{i}_{h_idx}", help="Borrar efecto indirecto"):
                             st.session_state['arbol_tarjetas'][nombre_indirecto].remove(h_data)
                             st.rerun()
                        # CONECTOR ENTRE HIJOS (opcional, si hay varios)
                        if h_idx < len(hijos_asociados) - 1:
                             st.markdown(HTML_CONECTOR, unsafe_allow_html=True)

                    # CONECTOR PRINCIPAL (Si hay hijos, conecta el grupo al padre)
                    if hijos_asociados:
                        st.markdown(HTML_CONECTOR, unsafe_allow_html=True)
                    
                    # Tarjeta del Padre (Efecto Directo)
                    st.markdown(card_html(padre_txt, CONFIG[nombre_directo]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️ Borrar Directo", key=f"del_p_{nombre_directo}_{i}"):
                        if hijos_asociados:
                            st.error("Borre primero los efectos indirectos asociados.")
                        else:
                            st.session_state['arbol_tarjetas'][nombre_directo].pop(i)
                            st.rerun()

                else:
                    # LÓGICA PARA CAUSAS (Directos ARRIBA -> Indirectos ABAJO)
                    # Tarjeta del Padre (Causa Directa)
                    st.markdown(card_html(padre_txt, CONFIG[nombre_directo]["color"]), unsafe_allow_html=True)
                    if st.button("🗑️ Borrar Directo", key=f"del_p_c_{nombre_directo}_{i}"):
                        if hijos_asociados:
                            st.error("Borre primero las causas indirectas asociadas.")
                        else:
                            st.session_state['arbol_tarjetas'][nombre_directo].pop(i)
                            st.rerun()

                    # CONECTOR PRINCIPAL (Si hay hijos)
                    if hijos_asociados:
                        st.markdown(HTML_CONECTOR, unsafe_allow_html=True)
                    
                    # Tarjetas de los Hijos (Causas Indirectas)
                    for h_idx, h_data in enumerate(hijos_asociados):
                        st.markdown(card_html(h_data["texto"], CONFIG[nombre_indirecto]["color"]), unsafe_allow_html=True)
                        # Botón de borrar pequeño
                        if st.button("ｘ", key=f"del_h_c_{nombre_indirecto}_{i}_{h_idx}", help="Borrar causa indirecta"):
                             st.session_state['arbol_tarjetas'][nombre_indirecto].remove(h_data)
                             st.rerun()
                        # Conector entre hijos sucesivos
                        if h_idx < len(hijos_asociados) - 1:
                             st.markdown(HTML_CONECTOR, unsafe_allow_html=True)

# --- CONSTRUCCIÓN FINAL DEL ÁRBOL ---
st.divider()
render_simple("Problema Superior")

# Conector visual hacia los efectos
st.markdown("""<div style="display: flex; justify-content: center;"><div style="width: 4px; height: 40px; background-color: #aaa;"></div></div>""", unsafe_allow_html=True)

# RAMA DE EFECTOS (Conectada verticalmente)
render_rama_conectada("Efectos Directos", "Efectos Indirectos", efectos=True)

# Conector visual hacia el problema central
st.markdown("""<div style="display: flex; justify-content: center;"><div style="width: 4px; height: 40px; background-color: #e57373;"></div></div>""", unsafe_allow_html=True)

# PROBLEMA CENTRAL (Sin banner extra)
render_simple("Problema Central")

# Conector visual desde las causas
st.markdown("""<div style="display: flex; justify-content: center;"><div style="width: 4px; height: 40px; background-color: #aaa;"></div></div>""", unsafe_allow_html=True)

# RAMA DE CAUSAS (Conectada verticalmente)
render_rama_conectada("Causas Directas", "Causas Indirectas", efectos=False)
