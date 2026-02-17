import streamlit as st
from session_state import inicializar_session, guardar_datos_nube

def mostrar_descripcion_problema():
    # 1. Asegurar persistencia
    inicializar_session()

    # --- LÓGICA DE EXTRACCIÓN AUTOMÁTICA DESDE HOJA 8 ---
    def obtener_resumen_desde_arbol():
        datos_arbol = st.session_state.get('arbol_problemas_final', {})
        
        # Extraer Problema Central
        pp = datos_arbol.get("Problema Principal", [])
        pc = pp[0].get("texto", "").upper() if pp else "AÚN NO DEFINIDO EN LA HOJA 8"
        
        # Extraer y limpiar Causas
        cds = [c.get("texto") for c in datos_arbol.get("Causas Directas", []) if c.get("texto")]
        cis = [c.get("texto") for c in datos_arbol.get("Causas Indirectas", []) if c.get("texto")]
        causas_full = cds + cis
        causas_txt = "\n".join([f"• {c}" for c in causas_full]) if causas_full else "SIN CAUSAS DEFINIDAS"
        
        # Extraer y limpiar Efectos
        eds = [e.get("texto") for e in datos_arbol.get("Efectos Directos", []) if e.get("texto")]
        eis = [e.get("texto") for e in datos_arbol.get("Efectos Indirectos", []) if e.get("texto")]
        efectos_full = eds + eis
        efectos_txt = "\n".join([f"• {e}" for e in efectos_full]) if efectos_full else "SIN EFECTOS DEFINIDOS"
        
        return pc, causas_txt, efectos_txt

    pc_auto, causas_auto, efectos_auto = obtener_resumen_desde_arbol()

    # --- DISEÑO VISUAL ---
    st.markdown('<div style="font-size: 30px; font-weight: 800; color: #1E3A8A;">📝 10. DESCRIPCIÓN DEL PROBLEMA</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #666; margin-bottom: 20px;">Transforme su diagnóstico técnico en una narrativa de proyecto.</div>', unsafe_allow_html=True)
    st.divider()

    # --- TABLA DE REFERENCIA (ESTILO EXCEL) ---
    st.markdown("### 📊 Información Técnica del Diagnóstico")
    st.caption("Los siguientes datos se cargan automáticamente desde el Árbol de Problemas Final (Hoja 8).")
    
    # CSS para la tabla
    st.markdown("""
        <style>
        .tabla-resumen { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .tabla-resumen th { background-color: #1E3A8A; color: white; padding: 12px; border: 1px solid #cbd5e1; text-align: left; }
        .tabla-resumen td { padding: 12px; border: 1px solid #cbd5e1; vertical-align: top; background-color: #f8fafc; font-size: 14px; color: #334155; }
        .col-cat { font-weight: bold; width: 25%; background-color: #f1f5f9 !important; color: #1E3A8A; }
        </style>
    """, unsafe_allow_html=True)

    html_tabla = f"""
    <table class="tabla-resumen">
        <tr><th>CATEGORÍA</th><th>DESCRIPCIÓN TÉCNICA (AUTO)</th></tr>
        <tr><td class="col-cat">PROBLEMA CENTRAL</td><td>{pc_auto}</td></tr>
        <tr><td class="col-cat">CAUSAS</td><td>{causas_auto}</td></tr>
        <tr><td class="col-cat">EFECTOS</td><td>{efectos_auto}</td></tr>
    </table>
    """
    st.markdown(html_tabla, unsafe_allow_html=True)

    st.divider()

    # --- SECCIÓN DE REDACCIÓN (ANÁLISIS CUALITATIVO) ---
    st.subheader("🖋️ Análisis y Redacción")
    st.info("Utilice la tabla superior como base para redactar el análisis detallado del problema. Sus cambios se guardan automáticamente.")

    def guardar_campo(key):
        st.session_state['descripcion_problema'][key] = st.session_state[f"temp_{key}"]
        guardar_datos_nube()

    # 1. Redacción del Problema
    st.markdown("**1. Descripción Narrativa del Problema Central**")
    st.text_area(
        "Describa el contexto, la magnitud y la justificación del problema:",
        value=st.session_state['descripcion_problema'].get('desc_central', ''),
        key="temp_desc_central",
        height=200,
        on_change=guardar_campo,
        args=("desc_central",),
        placeholder="Escriba aquí el análisis cualitativo del problema central..."
    )

    # 2. Redacción de Causas
    st.markdown("**2. Análisis de las Causas Identificadas**")
    st.text_area(
        "Explique el origen y los factores que generan la situación actual:",
        value=st.session_state['descripcion_problema'].get('desc_causas', ''),
        key="temp_desc_causas",
        height=200,
        on_change=guardar_campo,
        args=("desc_causas",),
        placeholder="Escriba aquí el análisis detallado de las causas..."
    )

    # 3. Redacción de Efectos
    st.markdown("**3. Análisis de Efectos e Impactos**")
    st.text_area(
        "Describa las consecuencias actuales y futuras de no intervenir el problema:",
        value=st.session_state['descripcion_problema'].get('desc_efectos', ''),
        key="temp_desc_efectos",
        height=200,
        on_change=guardar_campo,
        args=("desc_efectos",),
        placeholder="Escriba aquí el análisis de los efectos e impactos..."
    )

# Ejecución obligatoria para st.navigation
if __name__ == "__main__":
    mostrar_descripcion_problema()
