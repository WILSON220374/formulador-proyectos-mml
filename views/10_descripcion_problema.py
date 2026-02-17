import streamlit as st
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización
inicializar_session()
if 'descripcion_problema' not in st.session_state:
    st.session_state['descripcion_problema'] = {
        'tabla_datos': {},
        'redaccion_narrativa': "",
        'antecedentes': ""
    }

# --- FUNCIÓN DE ALTURA SINCRONIZADA ---
def calc_altura_fila(txt_desc, txt_mag, txt_unit, min_h=85):
    """Calcula la altura máxima necesaria basada en el contenido de las 3 columnas principales."""
    def estimar_h(texto, chars_por_linea):
        if not texto: return 0
        texto = str(texto)
        lineas = texto.count('\n') + (len(texto) // chars_por_linea) + 1
        return lineas * 28 # 28px por línea aprox

    # Estimamos la altura requerida para cada campo según su ancho de columna
    h_desc = estimar_h(txt_desc, 45)  # Columna ancha
    h_mag = estimar_h(txt_mag, 35)    # Columna media
    h_unit = estimar_h(txt_unit, 15)  # Columna estrecha
    
    # Retornamos la mayor de las tres para que todas queden iguales
    return max(min_h, h_desc, h_mag, h_unit)

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    .stTextArea textarea {
        padding: 10px !important;
        line-height: 1.5 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        resize: none; /* Evita que el usuario rompa la alineación manual */
    }
    .stTextInput input {
        padding: 10px !important;
        border-radius: 8px !important;
    }
    [data-testid="column"] {
        padding: 0 4px !important;
    }
    .main .block-container {
        padding-bottom: 15rem !important;
    }
    /* Estilo para las etiquetas estáticas (Columna 1 y 2) */
    .static-box {
        display: flex; 
        align-items: center; 
        justify-content: center;
        height: 100%;
        border-radius: 8px;
        padding: 10px;
        font-size: 13px;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

def render_fila_uniforme(etiqueta, descripcion, key_id, color_bg, color_texto):
    # Recuperar valores actuales
    val_m = st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", "")
    val_u = st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", "")
    val_c = st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", "")

    # 1. CALCULAR ALTURA COMÚN PARA TODA LA FILA
    altura_comun = calc_altura_fila(descripcion, val_m, val_u)

    # 2. DIBUJAR COLUMNAS
    # Ajuste: Unidad (c4) ahora es un poco más ancha para comportarse como text_area
    c1, c2, c3, c4, c5 = st.columns([1.5, 3.4, 2.6, 1.4, 0.8], vertical_alignment="center") # Alineación vertical centrada
    
    with c1:
        st.markdown(f"""
            <div class="static-box" style='background-color: {color_bg}; color: {color_texto}; font-weight: 800; text-align: center; border: 1px solid rgba(0,0,0,0.05); height: {altura_comun}px;'>
                {etiqueta}
            </div>""", unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
            <div class="static-box" style='background-color: transparent; color: #1e293b; font-weight: 500; text-align: left; border: 1px solid #f1f5f9; height: {altura_comun}px; align-items: flex-start;'>
                {descripcion if descripcion else '---'}
            </div>""", unsafe_allow_html=True)
    
    # MAGNITUD (Text Area)
    m_val = c3.text_area("M", value=val_m, key=f"m_{key_id}", label_visibility="collapsed", height=altura_comun, placeholder="Descripción...")
    
    # UNIDAD (Text Area - Ahora se comporta igual que Magnitud)
    u_val = c4.text_area("U", value=val_u, key=f"u_{key_id}", label_visibility="collapsed", height=altura_comun, placeholder="Unidad...")
    
    # CANTIDAD (Text Input - Se mantiene simple, pero centrado verticalmente por la columna)
    # Nota: Para alinearlo perfectamente en altura, usamos text_area también o aceptamos el input centrado.
    # Usaremos text_area de una sola línea simulada o input. Input es mejor para números cortos.
    c_val = c5.text_input("C", value=val_c, key=f"c_{key_id}", label_visibility="collapsed", placeholder="#")
    
    # GUARDADO AUTOMÁTICO
    if (m_val != val_m or u_val != val_u or c_val != val_c):
        st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
        st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
        st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
        guardar_datos_nube()
    
    st.write("") # Espaciador entre filas

# --- ENCABEZADO CON BARRA DE PROGRESO E IMAGEN ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown('<div style="font-size: 30px; font-weight: 800; color: #1E3A8A; line-height: 1.2;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">Cuantificación de indicadores y narrativa diagnóstica.</div>', unsafe_allow_html=True)
    
    # Cálculo de progreso simple
    datos_dict = st.session_state['descripcion_problema']['tabla_datos']
    narrativa = st.session_state['descripcion_problema']['redaccion_narrativa']
    total_campos = (len(datos_dict) if datos_dict else 0) + (1 if narrativa else 0)
    # Progreso visual estimativo (tope 100%)
    progreso = min(1.0, total_campos / 20) if total_campos > 0 else 0.0
    st.progress(progreso, text=f"Avance estimado: {int(progreso*100)}%")

with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- DATOS ---
datos_h8 = st.session_state.get('arbol_problemas_final', {})
pc_txt = datos_h8.get("Problema Principal", [{"texto": ""}])[0].get("texto", "")
lista_causas = [c.get("texto") for c in (datos_h8.get("Causas Directas", []) + datos_h8.get("Causas Indirectas", [])) if c.get("texto")]
lista_efectos = [e.get("texto") for e in (datos_h8.get("Efectos Directos", []) + datos_h8.get("Efectos Indirectos", [])) if e.get("texto")]

# --- ENCABEZADOS DE TABLA ---
# Ajustamos proporciones igual que en la función render
h1, h2, h3, h4, h5 = st.columns([1.5, 3.4, 2.6, 1.4, 0.8])
estilo_h = "font-weight: 800; color: #475569; font-size: 11px; text-align: center; text-transform: uppercase; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px;"
h1.markdown(f"<div style='{estilo_h}'>Categoría</div>", unsafe_allow_html=True)
h2.markdown(f"<div style='{estilo_h}'>Descripción del Árbol</div>", unsafe_allow_html=True)
h3.markdown(f"<div style='{estilo_h}'>Magnitud de Medición</div>", unsafe_allow_html=True)
h4.markdown(f"<div style='{estilo_h}'>Unidad</div>", unsafe_allow_html=True)
h5.markdown(f"<div style='{estilo_h}'>Cant.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- CUERPO DE LA TABLA ---
render_fila_uniforme("PROBLEMA CENTRAL", pc_txt, "pc", "#FEE2E2", "#991B1B")

for i, txt in enumerate(lista_causas):
    render_fila_uniforme(f"CAUSA {i+1}", txt, f"causa_{i}", "#FEF3C7", "#92400E")

for i, txt in enumerate(lista_efectos):
    render_fila_uniforme(f"EFECTO {i+1}", txt, f"efecto_{i}", "#DBEAFE", "#1E40AF")

st.divider()

# --- SECCIONES NARRATIVAS (FILAS) ---
st.subheader("🖋️ REDACCIÓN FINAL")

# Fila 1: Narrativa
st.markdown("##### 1. Descripción detallada (Lógica del problema)")
curr_n = st.session_state['descripcion_problema'].get('redaccion_narrativa', "")
# Altura dinámica para narrativa
h_narr = max(120, (str(curr_n).count('\n') + len(str(curr_n))//90 + 1) * 28)
narrativa = st.text_area("Narrativa", value=curr_n, height=h_narr, key="txt_narr_final", label_visibility="collapsed")

# Fila 2: Antecedentes
st.markdown("##### 2. Antecedentes y Contexto")
curr_a = st.session_state['descripcion_problema'].get('antecedentes', "")
# Altura dinámica para antecedentes
h_ant = max(120, (str(curr_a).count('\n') + len(str(curr_a))//90 + 1) * 28)
antecedentes = st.text_area("Antecedentes", value=curr_a, height=h_ant, key="txt_ant_final", label_visibility="collapsed")

# Guardado
if narrativa != curr_n or antecedentes != curr_a:
    st.session_state['descripcion_problema']['redaccion_narrativa'] = narrativa
    st.session_state['descripcion_problema']['antecedentes'] = antecedentes
    guardar_datos_nube()

# --- FOOTER ---
st.markdown('<div style="height: 150px;"></div>', unsafe_allow_html=True)
