import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicializar sesión
inicializar_session()

# Estilos CSS para mantener la estética de JCFlow y la simetría de la tabla
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 20px; }
    .tabla-header {
        background-color: #1E3A8A; color: white; font-weight: bold; padding: 10px;
        text-align: center; border-radius: 5px; margin-bottom: 5px; font-size: 13px;
        display: flex; align-items: center; justify-content: center; height: 50px;
    }
    .col-objetivo { 
        background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; 
        border-radius: 8px; height: 100%; font-size: 14px; min-height: 100px;
    }
    .col-indicador { 
        background-color: #F0F9FF; border: 1px solid #BAE6FD; padding: 12px; 
        border-radius: 8px; height: 100%; font-weight: 600; color: #0369A1; 
        font-size: 14px; min-height: 100px; display: flex; align-items: center;
    }
    .tipo-etiqueta {
        font-size: 10px; font-weight: 900; text-transform: uppercase;
        padding: 2px 6px; border-radius: 4px; margin-bottom: 5px; display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="titulo-seccion">📈 Fase IV: Indicadores</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo-gris">Construcción de indicadores a partir de los objetivos y actividades seleccionados.</p>', unsafe_allow_html=True)

# --- EXTRACCIÓN DE DATOS DESDE LA PODA (HOJA 7) ---
ref_poda = st.session_state.get('arbol_objetivos_final', {}).get('referencia_manual', {})
obj_general = ref_poda.get('objetivo', "")
especificos = ref_poda.get('especificos', [])
actividades = ref_poda.get('actividades', [])

# Construir lista unificada para la tabla
lista_items = []
if obj_general: 
    lista_items.append({"tipo": "OBJETIVO GENERAL", "texto": obj_general, "color": "#1E3A8A"})
for esp in especificos: 
    lista_items.append({"tipo": "OBJETIVO ESPECÍFICO", "texto": esp, "color": "#334155"})
for act in actividades: 
    lista_items.append({"tipo": "ACTIVIDAD", "texto": act, "color": "#64748b"})

if not lista_items:
    st.warning("⚠️ No se detectaron objetivos ni actividades en la 'Poda' de la Hoja 7. Por favor, asegúrate de haber seleccionado los elementos del árbol final.")
else:
    # --- ENCABEZADOS DE TABLA ---
    h1, h2, h3, h4, h5 = st.columns([2.5, 1.5, 2, 1.5, 2.5])
    with h1: st.markdown('<div class="tabla-header">OBJETIVOS / ACTIVIDADES</div>', unsafe_allow_html=True)
    with h2: st.markdown('<div class="tabla-header">OBJETO</div>', unsafe_allow_html=True)
    with h3: st.markdown('<div class="tabla-header">CONDICIÓN DESEADA</div>', unsafe_allow_html=True)
    with h4: st.markdown('<div class="tabla-header">LUGAR</div>', unsafe_allow_html=True)
    with h5: st.markdown('<div class="tabla-header">INDICADOR</div>', unsafe_allow_html=True)

    # Recuperar almacenamiento de indicadores
    storage_ind = st.session_state['indicadores'].get('tabla_indicadores', {})

    # --- RENDERIZADO DE FILAS ---
    for i, item in enumerate(lista_items):
        key_id = f"ind_{i}"
        # Recuperar datos previos o inicializar vacíos
        prev_data = storage_ind.get(key_id, {"objeto": "", "condicion": "", "lugar": ""})
        
        c1, c2, c3, c4, c5 = st.columns([2.5, 1.5, 2, 1.5, 2.5])
        
        with c1:
            st.markdown(f"""<div class="col-objetivo">
                <span class="tipo-etiqueta" style="background:#E2E8F0; color:{item['color']};">{item['tipo']}</span><br>
                {item['texto']}
            </div>""", unsafe_allow_html=True)
        
        with c2:
            obj_txt = st.text_area("Objeto", value=prev_data['objeto'], key=f"txt_obj_{i}", height=100, label_visibility="collapsed", placeholder="¿Qué?")
        
        with c3:
            cond_txt = st.text_area("Condición", value=prev_data['condicion'], key=f"txt_cond_{i}", height=100, label_visibility="collapsed", placeholder="Verbo conjugado...")
        
        with c4:
            lug_txt = st.text_area("Lugar", value=prev_data['lugar'], key=f"txt_lug_{i}", height=100, label_visibility="collapsed", placeholder="¿Dónde?")
        
        # Lógica de concatenación (Indicador)
        # Limpiamos espacios extras para que la unión sea estética
        partes = [obj_txt.strip(), cond_txt.strip(), lug_txt.strip()]
        indicador_final = " ".join([p for p in partes if p])
        
        with c5:
            if indicador_final:
                st.markdown(f'<div class="col-indicador">{indicador_final}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="col-indicador" style="color:#94A3B8; font-style:italic;">Complete los campos para generar el indicador...</div>', unsafe_allow_html=True)

        # Guardar en el diccionario local para persistencia
        storage_ind[key_id] = {
            "objeto": obj_txt,
            "condicion": cond_txt,
            "lugar": lug_txt,
            "texto_indicador": indicador_final,
            "origen": item['texto']
        }

    # Actualizar el session_state global
    st.session_state['indicadores']['tabla_indicadores'] = storage_ind

    # --- BOTÓN DE GUARDADO ---
    st.write("")
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("💾 Guardar Indicadores", type="primary", use_container_width=True):
            guardar_datos_nube()
            st.toast("Indicadores sincronizados con la nube", icon="✅")
