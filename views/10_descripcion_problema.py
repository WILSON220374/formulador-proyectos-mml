import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización (Basado en tu proyecto JCFlow)
inicializar_session()
if 'descripcion_problema' not in st.session_state:
    st.session_state['descripcion_problema'] = {
        'tabla_datos': {},
        'redaccion_narrativa': "",
        'antecedentes': ""
    }

# --- MEJORA: Cálculo de altura más sensible para evitar cortes ---
def calc_altura_pro(texto, min_h=70):
    if not texto: return min_h
    # Consideramos que cada 40 caracteres suele haber un salto de línea en estas columnas
    lineas_manuales = str(texto).count('\n')
    lineas_automaticas = len(str(texto)) // 40 
    total_lineas = lineas_manuales + lineas_automaticas + 1
    return max(min_h, total_lineas * 24)

# --- CSS PARA "MODO EXCEL" (Evita que los widgets ocupen demasiado espacio) ---
st.markdown("""
    <style>
    /* Reduce el espacio interno de los text_area y text_input */
    .stTextArea textarea, .stTextInput input {
        padding: 5px 10px !important;
        line-height: 1.4 !important;
    }
    /* Quita el margen inferior de los widgets para que las filas queden pegadas */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -5px !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_fila_excel(etiqueta, descripcion, key_id, color_bg, color_texto):
    # Ajuste de proporciones: c3 (Magnitud) ahora tiene 2.5 para mayor amplitud
    c1, c2, c3, c4, c5 = st.columns([1.5, 3.2, 2.5, 1.0, 0.8], vertical_alignment="top")
    
    with c1:
        st.markdown(f"""
            <div style='background-color: {color_bg}; padding: 12px 5px; border-radius: 8px; 
            font-weight: 800; font-size: 11px; color: {color_texto}; text-align: center; 
            border: 1px solid rgba(0,0,0,0.1); min-height: 60px; display: flex; align-items: center; justify-content: center;'>
                {etiqueta}
            </div>""", unsafe_allow_html=True)
    
    with c2:
        # Usamos un div con altura mínima para que coincida visualmente
        st.markdown(f"""
            <div style='padding: 8px; font-size: 13px; color: #334155; line-height: 1.3;'>
                {descripcion if descripcion else '---'}
            </div>""", unsafe_allow_html=True)
    
    # MAGNITUD: Se expande según el texto
    val_m = st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", "")
    m_val = c3.text_area("M", value=val_m, key=f"m_{key_id}", label_visibility="collapsed", 
                        height=calc_altura_pro(val_m), placeholder="Magnitud...")
    
    # UNIDAD Y CANTIDAD
    u_val = c4.text_input("U", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", ""), 
                         key=f"u_{key_id}", label_visibility="collapsed", placeholder="Unidad")
    c_val = c5.text_input("C", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", ""), 
                         key=f"c_{key_id}", label_visibility="collapsed", placeholder="Cant.")
    
    # Guardado automático si hay cambios
    if (m_val != val_m or u_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}") or 
        c_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}")):
        st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
        st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
        st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
        guardar_datos_nube()

# --- CABECERA (Acorde al doctorado en Project Management) ---
st.markdown('<div style="font-size: 30px; font-weight: 800; color: #1E3A8A;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
st.divider()

# --- DATOS PROVENIENTES DE LA ETAPA DE DIAGNÓSTICO ---
datos_h8 = st.session_state.get('arbol_problemas_final', {})
pc_txt = datos_h8.get("Problema Principal", [{"texto": ""}])[0].get("texto", "")
lista_causas = [c.get("texto") for c in (datos_h8.get("Causas Directas", []) + datos_h8.get("Causas Indirectas", [])) if c.get("texto")]
lista_efectos = [e.get("texto") for e in (datos_h8.get("Efectos Directos", []) + datos_h8.get("Efectos Indirectos", [])) if e.get("texto")]

# --- ENCABEZADOS DE LA MATRIZ ---
h1, h2, h3, h4, h5 = st.columns([1.5, 3.2, 2.5, 1.0, 0.8])
estilo_h = "font-weight: 900; color: #1E3A8A; font-size: 10px; text-align: center; text-transform: uppercase; border-bottom: 2px solid #eee; padding-bottom: 5px;"
h1.markdown(f"<div style='{estilo_h}'>Categoría</div>", unsafe_allow_html=True)
h2.markdown(f"<div style='{estilo_h}'>Descripción</div>", unsafe_allow_html=True)
h3.markdown(f"<div style='{estilo_h}'>Magnitud de Medición</div>", unsafe_allow_html=True)
h4.markdown(f"<div style='{estilo_h}'>Unidad</div>", unsafe_allow_html=True)
h5.markdown(f"<div style='{estilo_h}'>Cant.</div>", unsafe_allow_html=True)
st.write("")

# --- RENDERIZADO POR CATEGORÍAS CON COLORES ---
# 1. PROBLEMA CENTRAL
render_fila_excel("PROBLEMA CENTRAL", pc_txt, "pc", "#FEE2E2", "#991B1B")

# 2. CAUSAS
for i, txt in enumerate(lista_causas):
    render_fila_excel(f"CAUSA {i+1}", txt, f"causa_{i}", "#FEF3C7", "#92400E")

# 3. EFECTOS
for i, txt in enumerate(lista_efectos):
    render_fila_excel(f"EFECTO {i+1}", txt, f"efecto_{i}", "#DBEAFE", "#1E40AF")

st.divider()

# --- ÁREAS NARRATIVAS ---
st.markdown("### 🖋️ NARRATIVA DEL PROBLEMA")
curr_narrativa = st.session_state['descripcion_problema'].get('redaccion_narrativa', "")
narrativa = st.text_area("Describa la lógica del diagnóstico:", 
                        value=curr_narrativa, 
                        height=calc_altura_pro(curr_narrativa, 150),
                        key="area_narrativa_final")

st.markdown("### 📚 ANTECEDENTES")
curr_antecedentes = st.session_state['descripcion_problema'].get('antecedentes', "")
antecedentes = st.text_area("Contexto histórico del proyecto:", 
                           value=curr_antecedentes, 
                           height=calc_altura_pro(curr_antecedentes, 150),
                           key="area_antecedentes_final")

if narrativa != curr_narrativa or antecedentes != curr_antecedentes:
    st.session_state['descripcion_problema']['redaccion_narrativa'] = narrativa
    st.session_state['descripcion_problema']['antecedentes'] = antecedentes
    guardar_datos_nube()
