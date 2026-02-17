import streamlit as st
from session_state import inicializar_session, conectar_db, guardar_datos_nube

# 1. Asegurar inicialización de la sesión
inicializar_session()
if 'descripcion_problema' not in st.session_state:
    st.session_state['descripcion_problema'] = {
        'tabla_datos': {},
        'redaccion_narrativa': "",
        'antecedentes': ""
    }

# --- FUNCIÓN DE ALTURA: Generosa para evitar scrollbars internos ---
def calc_altura_final(texto, min_h=100):
    if not texto: return min_h
    # Al ser ahora filas anchas, el texto fluye mejor, pero mantenemos sensibilidad
    lineas_est = str(texto).count('\n') + (len(str(texto)) // 80) + 1
    return max(min_h, lineas_est * 28)

# --- CSS PARA ESPACIADO PROFESIONAL Y FOOTER ---
st.markdown("""
    <style>
    .stTextArea textarea {
        padding: 15px !important;
        line-height: 1.6 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        margin-bottom: 25px !important; 
    }
    /* Espaciado para columnas de la tabla superior */
    [data-testid="column"] {
        padding: 0 8px !important;
    }
    /* Margen global para evitar cortes al final */
    .main .block-container {
        padding-bottom: 12rem !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_fila_optimizada(etiqueta, descripcion, key_id, color_bg, color_texto):
    c1, c2, c3, c4, c5 = st.columns([1.6, 3.4, 2.8, 1.1, 0.9], vertical_alignment="top")
    
    with c1:
        st.markdown(f"""
            <div style='background-color: {color_bg}; padding: 15px 5px; border-radius: 8px; 
            font-weight: 800; font-size: 11px; color: {color_texto}; text-align: center; 
            border: 1px solid rgba(0,0,0,0.05); min-height: 75px; display: flex; align-items: center; justify-content: center;'>
                {etiqueta}
            </div>""", unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
            <div style='padding: 12px 5px; font-size: 13px; color: #1e293b; line-height: 1.5; font-weight: 500;'>
                {descripcion if descripcion else '---'}
            </div>""", unsafe_allow_html=True)
    
    val_m = st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", "")
    m_val = c3.text_area("M", value=val_m, key=f"m_{key_id}", label_visibility="collapsed", 
                        height=calc_altura_final(val_m), placeholder="Describa la medición...")
    
    u_val = c4.text_input("U", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", ""), 
                         key=f"u_{key_id}", label_visibility="collapsed", placeholder="Unidad")
    c_val = c5.text_input("C", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", ""), 
                         key=f"c_{key_id}", label_visibility="collapsed", placeholder="Cant.")
    
    if (m_val != val_m or u_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}") or 
        c_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}")):
        st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
        st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
        st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
        guardar_datos_nube()

# --- ESTRUCTURA DE PÁGINA ---
st.markdown('<div style="font-size: 32px; font-weight: 800; color: #1E3A8A;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
st.divider()

# --- DATOS DEL DIAGNÓSTICO (HOJA 8) ---
datos_h8 = st.session_state.get('arbol_problemas_final', {})
pc_txt = datos_h8.get("Problema Principal", [{"texto": ""}])[0].get("texto", "")
lista_causas = [c.get("texto") for c in (datos_h8.get("Causas Directas", []) + datos_h8.get("Causas Indirectas", [])) if c.get("texto")]
lista_efectos = [e.get("texto") for e in (datos_h8.get("Efectos Directos", []) + datos_h8.get("Efectos Indirectos", [])) if e.get("texto")]

# --- ENCABEZADOS ---
h1, h2, h3, h4, h5 = st.columns([1.6, 3.4, 2.8, 1.1, 0.9])
estilo_h = "font-weight: 900; color: #475569; font-size: 10px; text-align: center; text-transform: uppercase; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px;"
h1.markdown(f"<div style='{estilo_h}'>Categoría</div>", unsafe_allow_html=True)
h2.markdown(f"<div style='{estilo_h}'>Descripción del Árbol</div>", unsafe_allow_html=True)
h3.markdown(f"<div style='{estilo_h}'>Magnitud de Medición</div>", unsafe_allow_html=True)
h4.markdown(f"<div style='{estilo_h}'>Unidad</div>", unsafe_allow_html=True)
h5.markdown(f"<div style='{estilo_h}'>Cant.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- FILAS DE LA MATRIZ ---
render_fila_optimizada("PROBLEMA CENTRAL", pc_txt, "pc", "#FEE2E2", "#991B1B")

for i, txt in enumerate(lista_causas):
    render_fila_optimizada(f"CAUSA {i+1}", txt, f"causa_{i}", "#FEF3C7", "#92400E")

for i, txt in enumerate(lista_efectos):
    render_fila_optimizada(f"EFECTO {i+1}", txt, f"efecto_{i}", "#DBEAFE", "#1E40AF")

st.divider()

# --- SECCIONES NARRATIVAS (EN FILAS INDEPENDIENTES) ---
st.subheader("🖋️ REDACCIÓN FINAL")

# 1. Narrativa (Fila 1)
st.markdown("##### Descripción detallada del problema (Problema - Causas - Efectos)")
curr_n = st.session_state['descripcion_problema'].get('redaccion_narrativa', "")
narrativa = st.text_area("Narrativa", value=curr_n, height=calc_altura_final(curr_n, 200), 
                         key="txt_narr_v_final", label_visibility="collapsed")

# 2. Antecedentes (Fila 2)
st.markdown("##### Antecedentes y contexto previo")
curr_a = st.session_state['descripcion_problema'].get('antecedentes', "")
antecedentes = st.text_area("Antecedentes", value=curr_a, height=calc_altura_final(curr_a, 200), 
                           key="txt_ant_v_final", label_visibility="collapsed")

# Guardado automático de textos
if narrativa != curr_n or antecedentes != curr_a:
    st.session_state['descripcion_problema']['redaccion_narrativa'] = narrativa
    st.session_state['descripcion_problema']['antecedentes'] = antecedentes
    guardar_datos_nube()

# --- ESPACIADOR FINAL (FOOTER) ---
st.markdown('<div style="height: 180px;"></div>', unsafe_allow_html=True)
