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

# --- NORMALIZACIÓN ROBUSTA (evita fallos por estructuras distintas entre grupos) ---
def _a_texto_dict(item):
    if isinstance(item, dict):
        return item
    if item is None:
        return None
    return {"texto": str(item)}

def _a_lista_dicts(valor):
    if valor is None:
        return []
    if isinstance(valor, list):
        out = []
        for it in valor:
            d = _a_texto_dict(it)
            if d is not None:
                out.append(d)
        return out
    if isinstance(valor, dict):
        return [valor]
    return [{"texto": str(valor)}]

# --- FUNCIÓN DE ALTURA SINCRONIZADA PARA TABLA ---
# En la Hoja 10, busca calc_altura_fila
# Fíjate que ahora recibe txt_cant (4 parámetros de texto)
def calc_altura_fila(txt_desc, txt_mag, txt_unit, txt_cant, min_h=85):
    def estimar_h(texto, chars_por_linea):
        if not texto: return 0
        t = str(texto)
        # Calculamos cuántas líneas ocupa el texto según el ancho de la columna
        lineas = t.count('\n') + (len(t) // chars_por_linea) + 1
        return lineas * 24 
    
    # Ajustamos la sensibilidad según el ancho de TUS columnas
    h_desc = estimar_h(txt_desc, 45) # Columna 3.4
    h_mag  = estimar_h(txt_mag, 35)  # Columna 2.6
    h_unit = estimar_h(txt_unit, 18) # Columna 1.4
    h_cant = estimar_h(txt_cant, 10) # Columna 0.8 (la más estrecha)
    
    # La altura de la fila será la de la columna que necesite más espacio
    return max(min_h, h_desc, h_mag, h_unit, h_cant)

# --- NUEVA FUNCIÓN: ALTURA ESTÉTICA PARA TEXT AREAS LARGAS (REDACCIÓN FINAL) ---
def calc_altura_textarea(texto, min_h=200, max_h=520, chars_por_linea=120, px_por_linea=24, padding_px=70):
    """
    Altura más estética y estable:
    - Evita gigantes por sobreestimación
    - Evita demasiado ajustado por subestimación
    """
    if texto is None:
        texto = ""
    texto = str(texto)

    # Contar líneas reales + estimación por longitud
    # (se hace por cada línea para no sobrecontar cuando hay saltos)
    lineas = 0
    for ln in texto.splitlines() or [""]:
        ln = ln.strip("\r")
        # al menos 1 línea por renglón
        lineas += max(1, (len(ln) // chars_por_linea) + 1)

    altura = (lineas * px_por_linea) + padding_px
    if altura < min_h:
        return min_h
    if altura > max_h:
        return max_h
    return altura

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    /* Textareas generales */
    .stTextArea textarea {
        padding: 14px !important;
        line-height: 1.55 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        resize: none;
    }
    .stTextInput input {
        padding: 10px !important;
        border-radius: 8px !important;
    }
    [data-testid="column"] {
        padding: 0 4px !important;
    }
    .main .block-container {
        padding-bottom: 450px !important;
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
    val_m = st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", "")
    val_u = st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", "")
    val_c = st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", "")

    # Ahora incluimos val_c en el cálculo de la altura
    altura_comun = calc_altura_fila(descripcion, val_m, val_u, val_c)

    # Tus proporciones exactas con alineación centrada
    c1, c2, c3, c4, c5 = st.columns([1.5, 3.4, 2.6, 1.4, 0.8], vertical_alignment="center")

    with c1:
        st.markdown(f"""
            <div class="static-box" style='background-color: {color_bg}; color: {color_texto};
                 font-weight: 800; text-align: center; border: 1px solid rgba(0,0,0,0.05);
                 height: {altura_comun}px; display: flex; justify-content: center; align-items: center;'>
                {etiqueta}
            </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="static-box" style='background-color: transparent; color: #1e293b;
                 font-weight: 500; text-align: left; border: 1px solid #f1f5f9;
                 height: {altura_comun}px; display: flex; align-items: flex-start; padding: 5px;'>
                {descripcion if descripcion else '---'}
            </div>""", unsafe_allow_html=True)

    m_val = c3.text_area("M", value=val_m, key=f"m_{key_id}", label_visibility="collapsed",
                         height=altura_comun, placeholder="Descripción...")

    u_val = c4.text_area("U", value=val_u, key=f"u_{key_id}", label_visibility="collapsed",
                         height=altura_comun, placeholder="Unidad...")

    # Cambia text_input por text_area para poder aplicar la altura
    c_val = c5.text_area("C", value=val_c, key=f"c_{key_id}", label_visibility="collapsed", 
                         height=altura_comun, placeholder="#")

    if (m_val != val_m or u_val != val_u or c_val != val_c):
        st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
        st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
        st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
        guardar_datos_nube()

    st.write("")

# --- ENCABEZADO CON BARRA DE PROGRESO E IMAGEN ---
col_t, col_img = st.columns([4, 1], vertical_alignment="center")

with col_t:
    st.markdown(
        '<div style="font-size: 30px; font-weight: 800; color: #1E3A8A; line-height: 1.2;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">Cuantificación de indicadores y narrativa diagnóstica.</div>',
        unsafe_allow_html=True
    )

    datos_dict = st.session_state['descripcion_problema']['tabla_datos']
    narrativa = st.session_state['descripcion_problema'].get('redaccion_narrativa', "")
    total_campos = (len(datos_dict) if datos_dict else 0) + (1 if narrativa else 0)
    progreso = min(1.0, total_campos / 20) if total_campos > 0 else 0.0
    st.progress(progreso, text=f"Avance estimado: {int(progreso*100)}%")

with col_img:
    if os.path.exists("unnamed.jpg"):
        st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- DATOS (ROBUSTO) ---
datos_h8 = st.session_state.get('arbol_problemas_final', {})
if not isinstance(datos_h8, dict):
    datos_h8 = {}

pp_list = _a_lista_dicts(datos_h8.get("Problema Principal"))
if pp_list and isinstance(pp_list[0], dict):
    pc_txt = pp_list[0].get("texto", "") or ""
else:
    pc_txt = ""

causas_directas = _a_lista_dicts(datos_h8.get("Causas Directas"))
causas_indirectas = _a_lista_dicts(datos_h8.get("Causas Indirectas"))
efectos_directos = _a_lista_dicts(datos_h8.get("Efectos Directos"))
efectos_indirectos = _a_lista_dicts(datos_h8.get("Efectos Indirectos"))

lista_causas = [
    c.get("texto") for c in (causas_directas + causas_indirectas)
    if isinstance(c, dict) and c.get("texto")
]
lista_efectos = [
    e.get("texto") for e in (efectos_directos + efectos_indirectos)
    if isinstance(e, dict) and e.get("texto")
]

# --- ENCABEZADOS DE TABLA ---
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

# --- SECCIONES NARRATIVAS ---
st.subheader("🖋️ REDACCIÓN FINAL")

# 1) Narrativa
st.markdown("##### 1. Descripción detallada (Problema - Causa - Efecto)")
curr_n = st.session_state['descripcion_problema'].get('redaccion_narrativa', "")
h_narr = calc_altura_textarea(curr_n, min_h=240, max_h=560, chars_por_linea=125, px_por_linea=24, padding_px=80)
narrativa = st.text_area(
    "Narrativa",
    value=curr_n,
    height=h_narr,
    key="txt_narr_final",
    label_visibility="collapsed"
)

# 2) Antecedentes
st.markdown("##### 2. Antecedentes: ¿Qué se ha hecho previamente con el problema")
curr_a = st.session_state['descripcion_problema'].get('antecedentes', "")
h_ant = calc_altura_textarea(curr_a, min_h=170, max_h=420, chars_por_linea=125, px_por_linea=24, padding_px=75)
antecedentes = st.text_area(
    "Antecedentes",
    value=curr_a,
    height=h_ant,
    key="txt_ant_final",
    label_visibility="collapsed"
)

# Guardado
if narrativa != curr_n or antecedentes != curr_a:
    st.session_state['descripcion_problema']['redaccion_narrativa'] = narrativa
    st.session_state['descripcion_problema']['antecedentes'] = antecedentes
    guardar_datos_nube()

# --- FOOTER ---
st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)
