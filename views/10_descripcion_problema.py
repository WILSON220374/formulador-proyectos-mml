import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# 1. Asegurar inicialización del estado para esta página
inicializar_session()
if 'descripcion_problema' not in st.session_state:
    st.session_state['descripcion_problema'] = {
        'tabla_datos': {},
        'redaccion_narrativa': "",
        'antecedentes': ""
    }

def calc_altura(texto, min_h=100):
    if not texto: return min_h
    lineas = str(texto).count('\n') + (len(str(texto)) // 85) + 2
    return max(min_h, lineas * 24)

def actualizar_valor_tabla(key, valor):
    st.session_state['descripcion_problema']['tabla_datos'][key] = valor
    guardar_datos_nube()

def render_fila_excel(etiqueta, descripcion, key_id):
    # Proporciones de columna para emular el Excel
    c1, c2, c3, c4, c5 = st.columns([1.8, 3.5, 1.5, 1.2, 1])
    
    with c1:
        st.markdown(f"<div style='background-color: #f1f5f9; padding: 8px; border-radius: 5px; font-weight: bold; font-size: 13px; color: #1E3A8A;'>{etiqueta}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='padding: 8px; font-size: 13px; border-bottom: 1px solid #eee;'>{descripcion if descripcion else '---'}</div>", unsafe_allow_html=True)
    
    # Inputs de la tabla
    m_val = c3.text_input("M", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", ""), key=f"m_{key_id}", label_visibility="collapsed")
    u_val = c4.text_input("U", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", ""), key=f"u_{key_id}", label_visibility="collapsed")
    c_val = c5.text_input("C", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", ""), key=f"c_{key_id}", label_visibility="collapsed")
    
    # Guardado automático si cambian los valores manuales
    if (m_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}") or
        u_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}") or
        c_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}")):
        st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
        st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
        st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
        guardar_datos_nube()

# --- INTERFAZ PRINCIPAL ---
st.markdown('<div style="font-size: 30px; font-weight: 800; color: #1E3A8A;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
st.markdown('<div style="color: #666; margin-bottom: 20px;">Cuantificación de indicadores y redacción de antecedentes.</div>', unsafe_allow_html=True)

# --- EXTRACCIÓN DINÁMICA DE LA HOJA 8 ---
datos_h8 = st.session_state.get('arbol_problemas_final', {})
# Extraemos problema, causas y efectos tal cual están en la Hoja 8
pc_txt = datos_h8.get("Problema Principal", [{"texto": ""}])[0].get("texto", "")
# Combinamos directas e indirectas para la lista larga
lista_causas = [c.get("texto") for c in (datos_h8.get("Causas Directas", []) + datos_h8.get("Causas Indirectas", [])) if c.get("texto")]
lista_efectos = [e.get("texto") for e in (datos_h8.get("Efectos Directos", []) + datos_h8.get("Efectos Indirectos", [])) if e.get("texto")]

# --- ENCABEZADO DE TABLA ---
st.write("")
h1, h2, h3, h4, h5 = st.columns([1.8, 3.5, 1.5, 1.2, 1])
estilo_h = "font-weight: 900; color: #1E3A8A; font-size: 12px; text-align: center; border-bottom: 2px solid #1E3A8A;"
h1.markdown(f"<div style='{estilo_h}'>ÁRBOL DE PROBLEMAS</div>", unsafe_allow_html=True)
h2.markdown(f"<div style='{estilo_h}'>DESCRIPCIÓN</div>", unsafe_allow_html=True)
h3.markdown(f"<div style='{estilo_h}'>MAGNITUD</div>", unsafe_allow_html=True)
h4.markdown(f"<div style='{estilo_h}'>UNIDAD</div>", unsafe_allow_html=True)
h5.markdown(f"<div style='{estilo_h}'>CANT.</div>", unsafe_allow_html=True)

# --- RENDERIZADO DE FILAS ---
# 1. Problema Central
render_fila_excel("PROBLEMA CENTRAL", pc_txt, "pc")

# 2. Causas
for idx, txt in enumerate(lista_causas):
    render_fila_excel(f"CAUSA {idx+1}", txt, f"causa_{idx}")

# 3. Efectos
for idx, txt in enumerate(lista_efectos):
    render_fila_excel(f"EFECTO {idx+1}", txt, f"efecto_{idx}")

st.divider()

# --- BLOQUES DE TEXTO AUTO-AJUSTABLES ---
st.markdown("### 🖋️ DESCRIPCIÓN Y NARRATIVA")
narrativa = st.text_area(
    "Narrativa detallada (Problema - Causas - Efectos):",
    value=st.session_state['descripcion_problema'].get('redaccion_narrativa', ""),
    height=calc_altura(st.session_state['descripcion_problema'].get('redaccion_narrativa', "")),
    key="area_narrativa",
    placeholder="Redacte aquí la lógica del problema..."
)

st.markdown("### 📚 ANTECEDENTES")
antecedentes = st.text_area(
    "Contexto histórico y situación previa:",
    value=st.session_state['descripcion_problema'].get('antecedentes', ""),
    height=calc_altura(st.session_state['descripcion_problema'].get('antecedentes', "")),
    key="area_antecedentes",
    placeholder="Mencione estudios previos o antecedentes del problema..."
)

# Guardado de textos
if (narrativa != st.session_state['descripcion_problema']['redaccion_narrativa'] or
    antecedentes != st.session_state['descripcion_problema']['antecedentes']):
    st.session_state['descripcion_problema']['redaccion_narrativa'] = narrativa
    st.session_state['descripcion_problema']['antecedentes'] = antecedentes
    guardar_datos_nube()
