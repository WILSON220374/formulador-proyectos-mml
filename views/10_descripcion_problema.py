import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización
inicializar_session()
if 'descripcion_problema' not in st.session_state:
    st.session_state['descripcion_problema'] = {
        'tabla_datos': {},
        'redaccion_narrativa': "",
        'antecedentes': ""
    }

def calc_altura(texto, min_h=60):
    if not texto: return min_h
    # Ajuste dinámico basado en longitud de caracteres
    lineas = str(texto).count('\n') + (len(str(texto)) // 60) + 1
    return max(min_h, lineas * 24)

def render_fila_excel(etiqueta, descripcion, key_id, color_bg, color_texto):
    # Proporciones: Magnitud (c3) ahora tiene más espacio (2.2)
    c1, c2, c3, c4, c5 = st.columns([1.8, 3.0, 2.2, 1.0, 1.0])
    
    with c1:
        st.markdown(f"""
            <div style='background-color: {color_bg}; padding: 10px; border-radius: 8px; 
            font-weight: 800; font-size: 12px; color: {color_texto}; text-align: center; border: 1px solid rgba(0,0,0,0.1);'>
                {etiqueta}
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='padding: 8px; font-size: 13px; color: #334155;'>{descripcion if descripcion else '---'}</div>", unsafe_allow_html=True)
    
    # MAGNITUD: Ahora es un text_area que se ajusta al contenido
    val_m = st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", "")
    m_val = c3.text_area("M", value=val_m, key=f"m_{key_id}", label_visibility="collapsed", height=calc_altura(val_m))
    
    # UNIDAD Y CANTIDAD: Siguen siendo inputs cortos
    u_val = c4.text_input("U", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", ""), key=f"u_{key_id}", label_visibility="collapsed")
    c_val = c5.text_input("C", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", ""), key=f"c_{key_id}", label_visibility="collapsed")
    
    # Guardado automático
    if (m_val != val_m or u_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}") or 
        c_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}")):
        st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
        st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
        st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
        guardar_datos_nube()

# --- DISEÑO DE PÁGINA ---
st.markdown('<div style="font-size: 30px; font-weight: 800; color: #1E3A8A;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
st.divider()

# --- EXTRACCIÓN DE DATOS ---
datos_h8 = st.session_state.get('arbol_problemas_final', {})
pc_txt = datos_h8.get("Problema Principal", [{"texto": ""}])[0].get("texto", "")
lista_causas = [c.get("texto") for c in (datos_h8.get("Causas Directas", []) + datos_h8.get("Causas Indirectas", [])) if c.get("texto")]
lista_efectos = [e.get("texto") for e in (datos_h8.get("Efectos Directos", []) + datos_h8.get("Efectos Indirectos", [])) if e.get("texto")]

# --- ENCABEZADOS ---
h1, h2, h3, h4, h5 = st.columns([1.8, 3.0, 2.2, 1.0, 1.0])
estilo_h = "font-weight: 900; color: #1E3A8A; font-size: 11px; text-align: center; text-transform: uppercase;"
h1.markdown(f"<div style='{estilo_h}'>Categoría</div>", unsafe_allow_html=True)
h2.markdown(f"<div style='{estilo_h}'>Descripción</div>", unsafe_allow_html=True)
h3.markdown(f"<div style='{estilo_h}'>Magnitud de Medición</div>", unsafe_allow_html=True)
h4.markdown(f"<div style='{estilo_h}'>Unidad</div>", unsafe_allow_html=True)
h5.markdown(f"<div style='{estilo_h}'>Cant.</div>", unsafe_allow_html=True)
st.write("")

# --- RENDERIZADO CON COLORES ---
# 1. PROBLEMA (Rojo/Rosa)
render_fila_excel("PROBLEMA CENTRAL", pc_txt, "pc", "#FEE2E2", "#991B1B")

# 2. CAUSAS (Ámbar/Amarillo)
for i, txt in enumerate(lista_causas):
    render_fila_excel(f"CAUSA {i+1}", txt, f"causa_{i}", "#FEF3C7", "#92400E")

# 3. EFECTOS (Azul)
for i, txt in enumerate(lista_efectos):
    render_fila_excel(f"EFECTO {i+1}", txt, f"efecto_{i}", "#DBEAFE", "#1E40AF")

st.divider()

# --- NARRATIVAS ---
st.markdown("### 🖋️ NARRATIVA DEL PROBLEMA")
narrativa = st.text_area("Describa la relación entre el problema, causas y efectos:", 
                        value=st.session_state['descripcion_problema'].get('redaccion_narrativa', ""), 
                        height=calc_altura(st.session_state['descripcion_problema'].get('redaccion_narrativa', ""), 150),
                        key="temp_narrativa")

st.markdown("### 📚 ANTECEDENTES")
antecedentes = st.text_area("Contexto histórico:", 
                           value=st.session_state['descripcion_problema'].get('antecedentes', ""), 
                           height=calc_altura(st.session_state['descripcion_problema'].get('antecedentes', ""), 150),
                           key="temp_antecedentes")

if narrativa != st.session_state['descripcion_problema']['redaccion_narrativa'] or antecedentes != st.session_state['descripcion_problema']['antecedentes']:
    st.session_state['descripcion_problema']['redaccion_narrativa'] = narrativa
    st.session_state['descripcion_problema']['antecedentes'] = antecedentes
    guardar_datos_nube()
