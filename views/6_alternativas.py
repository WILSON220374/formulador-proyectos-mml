import streamlit as st
import pandas as pd
import itertools
from session_state import inicializar_session, guardar_datos_nube

inicializar_session()

st.title("⚖️ 6. Análisis de Alternativas")

# ... (Las Secciones 1, 2, 3 y 4 se mantienen iguales a tu código actual) ...
# (Asegúrate de mantener el código previo de selección de actividades y consolidación)

# --- 5. EVALUACIÓN MULTICRITERIO (LA TABLA COMPLETA) ---
st.divider()
st.subheader("📊 5. Evaluación de Alternativas")

alts = st.session_state.get('lista_alternativas', [])

if not alts:
    st.info("Debe consolidar al menos una alternativa para habilitar la matriz de evaluación.")
else:
    # 5.1. Configuración de Ponderación
    with st.expander("⚙️ Configurar Ponderación de Criterios (Suma = 100%)", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        p = st.session_state['ponderacion_criterios']
        with c1: p_costo = st.number_input("Costo (%)", 0, 100, int(p['COSTO']), key="w_c")
        with c2: p_facil = st.number_input("Facilidad (%)", 0, 100, int(p['FACILIDAD']), key="w_f")
        with c3: p_benef = st.number_input("Beneficios (%)", 0, 100, int(p['BENEFICIOS']), key="w_b")
        with c4: p_tiempo = st.number_input("Tiempo (%)", 0, 100, int(p['TIEMPO']), key="w_t")
        
        total_p = p_costo + p_facil + p_benef + p_tiempo
        if total_p == 100:
            st.success(f"Suma total: {total_p}% ✅")
            if p_costo != p['COSTO'] or p_facil != p['FACILIDAD'] or p_benef != p['BENEFICIOS'] or p_tiempo != p['TIEMPO']:
                st.session_state['ponderacion_criterios'] = {"COSTO": p_costo, "FACILIDAD": p_facil, "BENEFICIOS": p_benef, "TIEMPO": p_tiempo}
                guardar_datos_nube()
        else:
            st.error(f"La suma actual es {total_p}%. Debe ser exactamente 100%.")

    # 5.2. Matriz de Calificación
    st.markdown(f"### Matriz de Decisión (Rango de puntaje: 1 a {len(alts)})")
    
    # Inicializamos tabla de calificaciones si es nueva o cambió el número de alts
    nombres_alts = [a['nombre'] for a in alts]
    criterios = ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]
    
    df_cal = st.session_state['df_calificaciones']
    if df_cal.empty or set(df_cal.index) != set(nombres_alts):
        st.session_state['df_calificaciones'] = pd.DataFrame(1, index=nombres_alts, columns=criterios)
        guardar_datos_nube()

    # Editor de puntajes simples
    df_scores = st.data_editor(
        st.session_state['df_calificaciones'],
        column_config={c: st.column_config.NumberColumn(f"Puntaje {c}", min_value=1, max_value=len(alts), step=1) for c in criterios},
        use_container_width=True, key="editor_scores"
    )

    if not df_scores.equals(st.session_state['df_calificaciones']):
        st.session_state['df_calificaciones'] = df_scores
        guardar_datos_nube(); st.rerun()

    # 5.3. TABLA COMPLETA CON RESULTADOS (ESTILO EXCEL)
    st.markdown("### 📈 Tabla de Resultados Finales")
    
    pesos = st.session_state['ponderacion_criterios']
    datos_completos = []
    
    for alt_nombre in nombres_alts:
        fila = {"Alternativa": alt_nombre}
        puntaje_total = 0
        for c in criterios:
            score = df_scores.loc[alt_nombre, c]
            peso_decimal = pesos[c] / 100
            total_criterio = score * peso_decimal
            fila[f"{c}"] = score
            fila[f"Peso {c}"] = f"{pesos[c]}%"
            fila[f"Total {c}"] = round(total_criterio, 2)
            puntaje_total += total_criterio
        fila["CALIFICACIÓN FINAL"] = round(puntaje_total, 2)
        datos_completos.append(fila)

    df_final = pd.DataFrame(datos_completos)
    st.dataframe(df_final, use_container_width=True, hide_index=True)

    # 5.4. Selección Automática
    ganadora = df_final.loc[df_final['CALIFICACIÓN FINAL'].idxmax()]
    st.success(f"🏆 **Alternativa Seleccionada:** {ganadora['Alternativa']} (Puntaje: {ganadora['CALIFICACIÓN FINAL']})")
