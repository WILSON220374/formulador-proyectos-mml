import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

def mostrar_descripcion_problema():
    inicializar_session()
    
    st.markdown('<div style="font-size: 30px; font-weight: 800; color: #1E3A8A;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
    st.divider()

    # --- EXTRACCIÓN DE DATOS DE LA HOJA 8 ---
    datos_h8 = st.session_state.get('arbol_problemas_final', {})
    pc_h8 = datos_h8.get("Problema Principal", [{"texto": ""}])[0].get("texto", "")
    causas_h8 = [c.get("texto") for c in datos_h8.get("Causas Directas", []) + datos_h8.get("Causas Indirectas", []) if c.get("texto")]
    efectos_h8 = [e.get("texto") for e in datos_h8.get("Efectos Directos", []) + datos_h8.get("Efectos Indirectos", []) if e.get("texto")]

    # --- TABLA DE 5 COLUMNAS (SEGÚN EXCEL) ---
    st.markdown("### 📊 ARBOL DE PROBLEMAS - DIAGNÓSTICO")
    
    # Diseño de columnas con proporciones similares al Excel
    cols_h = st.columns([1.5, 3, 1.5, 1, 1])
    headers = ["ARBOL DE PROBLEMAS", "DESCRIPCION", "MAGNITUD DE MEDICIÓN", "UNIDAD", "CANT."]
    for i, h in enumerate(headers):
        cols_h[i].markdown(f"**{h}**")

    def render_fila_excel(etiqueta, texto_h8, key_id):
        c1, c2, c3, c4, c5 = st.columns([1.5, 3, 1.5, 1, 1])
        c1.info(etiqueta)
        c2.write(texto_h8 if texto_h8 else "---")
        
        # Inputs para Magnitud, Unidad y Cantidad
        m_val = c3.text_input("M", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}", ""), key=f"m_{key_id}", label_visibility="collapsed")
        u_val = c4.text_input("U", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}", ""), key=f"u_{key_id}", label_visibility="collapsed")
        c_val = c5.text_input("C", value=st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}", ""), key=f"c_{key_id}", label_visibility="collapsed")
        
        # Guardado automático al detectar cambios
        if m_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"m_{key_id}") or \
           u_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"u_{key_id}") or \
           c_val != st.session_state['descripcion_problema']['tabla_datos'].get(f"c_{key_id}"):
            st.session_state['descripcion_problema']['tabla_datos'][f"m_{key_id}"] = m_val
            st.session_state['descripcion_problema']['tabla_datos'][f"u_{key_id}"] = u_val
            st.session_state['descripcion_problema']['tabla_datos'][f"c_{key_id}"] = c_val
            guardar_datos_nube()

    # 1. Problema Central
    render_fila_excel("PROBLEMA CENTRAL", pc_h8, "pc")
    
    # 2. Causas (Mostramos las 3 primeras como en el Excel)
    for i in range(3):
        txt = causas_h8[i] if i < len(causas_h8) else ""
        render_fila_excel(f"CAUSA {i+1}", txt, f"causa_{i}")

    # 3. Efectos (Mostramos los 3 primeros)
    for i in range(3):
        txt = efectos_h8[i] if i < len(efectos_h8) else ""
        render_fila_excel(f"EFECTO {i+1}", txt, f"efecto_{i}")

    st.divider()

    # --- SECCIONES DE TEXTO (BLOQUES DE REDACCIÓN) ---
    def guardar_narrativa(key):
        st.session_state['descripcion_problema'][key] = st.session_state[f"temp_{key}"]
        guardar_datos_nube()

    st.markdown("### 🖋️ DESCRIPCIÓN (PROBLEMA - CAUSAS - EFECTOS)")
    st.text_area("Narrativa detallada:", 
                 value=st.session_state['descripcion_problema']['redaccion_narrativa'], 
                 key="temp_redaccion_narrativa", height=150, on_change=guardar_narrativa, args=("redaccion_narrativa",), label_visibility="collapsed")

    st.markdown("### 📚 ANTECENTES")
    st.text_area("Contexto histórico:", 
                 value=st.session_state['descripcion_problema']['antecedentes'], 
                 key="temp_antecedentes", height=150, on_change=guardar_narrativa, args=("antecedentes",), label_visibility="collapsed")

if __name__ == "__main__":
    mostrar_descripcion_problema()
