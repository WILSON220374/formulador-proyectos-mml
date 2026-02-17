import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización de la sesión
inicializar_session()
if 'descripcion_problema' not in st.session_state:
    st.session_state['descripcion_problema'] = {
        'tabla_datos': {},
        'redaccion_narrativa': "",
        'antecedentes': ""
    }

# --- FUNCIÓN DE ALTURA: Más robusta para evitar scrollbars internos ---
def calc_altura_final(texto, min_h=80):
    if not texto: return min_h
    # Calculamos basándonos en un ancho de columna más estrecho (35 chars) para asegurar espacio
    lineas_est = str(texto).count('\n') + (len(str(texto)) // 35) + 1
    return max(min_h, lineas_est * 26)

# --- CSS PARA ESPACIADO TIPO FORMULARIO PROFESIONAL ---
st.markdown("""
    <style>
    .stTextArea textarea {
        padding: 10px !important;
        line-height: 1.5 !important;
        border: 1px solid #e2e8f0 !important;
    }
    /* Añadimos un espacio entre las filas de la cuadrícula */
    [data-testid="column"] {
        padding: 0 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_fila_optimizada(etiqueta, descripcion, key_id, color_bg, color_texto):
    # Proporciones finales con más espacio para Descripción (3.4) y Magnitud (2.8)
    c1, c2, c3, c4, c5 = st.columns([1.6, 3.4, 2.8, 1.1, 0.9], vertical_alignment="top")
    
    with c1:
        st.markdown(f"""
            <div style='background-color: {color_bg}; padding: 15px 5px; border-radius: 8px; 
            font-weight: 800; font-size: 11px; color: {color_texto}; text-align: center; 
            border: 1px solid rgba(0,0,0,0.05); min-height: 70px; display: flex; align-items: center; justify-content: center;'>
                {etiqueta}
            </div>""", unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
            <div style='padding: 10px 5px; font-size: 13px; color: #1e293b; line-height: 1.4; font-weight: 500;'>
                {descripcion if descripcion else '---'}
            </div>""", unsafe_allow_html=True)
    
    # Campo Magnitud con altura dinámica
    val_m = st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", "")
    m_val = c3.text_area("M", value=val_m, key=f"m_{key_id}", label_visibility="collapsed", 
                        height=calc_altura_final(val_m), placeholder="Describa la medición...")
    
    # Unidad y Cantidad
    u_val = c4.text_input("U", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", ""), 
                         key=f"u_{key_id}", label_visibility="collapsed", placeholder="Unidad")
    c_val = c5.text_input("C", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", ""), 
                         key=f"c_{key_id}", label_visibility="collapsed", placeholder="Cant.")
    
    # Guardado automático
    if (m_val != val_m or u_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}") or 
        c_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}")):
        st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
        st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
        st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
        guardar_datos_nube()
    
    # Espacio extra al final de cada fila
    st.write("")

# --- ESTRUCTURA DE PÁGINA ---
st.markdown('<div style="font-size: 32px; font-weight: 800; color: #1E3A8A; letter-spacing: -0.5px;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
st.divider()

# --- DATOS DEL DIAGNÓSTICO (HOJA 8) ---
datos_h8 = st.session_state.get('arbol_problemas_final', {})
pc_txt = datos_h8.get("Problema Principal", [{"texto": ""}])[0].get("texto", "")
lista_causas = [c.get("texto") for c in (datos_h8.get("Causas Directas", []) + datos_h8.get("Causas Indirectas", [])) if c.get("texto")]
lista_efectos = [e.get("texto") for e in (datos_h8.get("Efectos Directos", []) + datos_h8.get("Efectos Indirectos", [])) if e.get("texto")]

# --- ENCABEZADOS DE LA MATRIZ ---
h1, h2, h3, h4, h5 = st.columns([1.6, 3.4, 2.8, 1.1, 0.9])
estilo_h = "font-weight: 900; color: #475569; font-size: 10px; text-align: center; text-transform: uppercase; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px;"
h1.markdown(f"<div style='{estilo_h}'>Categoría</div>", unsafe_allow_html=True)
h2.markdown(f"<div style='{estilo_h}'>Descripción del Árbol</div>", unsafe_allow_html=True)
h3.markdown(f"<div style='{estilo_h}'>Magnitud de Medición</div>", unsafe_allow_html=True)
h4.markdown(f"<div style='{estilo_h}'>Unidad</div>", unsafe_allow_html=True)
h5.markdown(f"<div style='{estilo_h}'>Cant.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- RENDERIZADO POR BLOQUES ---
render_fila_optimizada("PROBLEMA CENTRAL", pc_txt, "pc", "#FEE2E2", "#991B1B")

for i, txt in enumerate(lista_causas):
    render_fila_optimizada(f"CAUSA {i+1}", txt, f"causa_{i}", "#FEF3C7", "#92400E")

# CORREGIDO: Llamada correcta a la función
for i, txt in enumerate(lista_efectos):
    render_fila_optimizada(f"EFECTO {i+1}", txt, f"efecto_{i}", "#DBEAFE", "#1E40AF")

st.divider()

# --- SECCIONES NARRATIVAS ---
st.subheader("🖋️ NARRATIVA Y ANTECEDENTES")
col_narr, col_ant = st.columns(2, gap="large")

with col_narr:
    curr_n = st.session_state['descripcion_problema'].get('redaccion_narrativa', "")
    narrativa = st.text_area("Descripción detallada del problema:", value=curr_n, height=250, key="txt_narr_final")

with col_ant:
    curr_a = st.session_state['descripcion_problema'].get('antecedentes', "")
    antecedentes = st.text_area("Antecedentes y contexto previo:", value=curr_a, height=250, key="txt_ant_final")

if narrativa != curr_n or antecedentes != curr_a:
    st.session_state['descripcion_problema']['redaccion_narrativa'] = narrativa
    st.session_state['descripcion_problema']['antecedentes'] = antecedentes
    guardar_datos_nube()
