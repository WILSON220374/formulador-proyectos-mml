import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session

# 1. Carga de datos con persistencia total
inicializar_session()

# Título ajustado según tu solicitud
st.title("🎯 Árbol de Objetivos Final")

st.info("Este diagrama representa la estructura técnica definitiva del proyecto basada en la alternativa seleccionada.")

# --- 1. CÁLCULO DE LA ALTERNATIVA GANADORA ---
alts = st.session_state.get('lista_alternativas', [])
df_cal = st.session_state.get('df_calificaciones', pd.DataFrame())
pesos = st.session_state.get('ponderacion_criterios', {})

if not alts or df_cal.empty:
    st.warning("⚠️ No se encontró una evaluación completa. Por favor, califique las alternativas en el paso anterior.")
else:
    # Identificamos matemáticamente cuál es la mejor opción
    criterios = ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]
    nombres_alts = [a['nombre'] for a in alts]
    totales = []
    
    for alt_n in nombres_alts:
        p_total = 0
        for c in criterios:
            p_total += df_cal.loc[alt_n, c] * (pesos.get(c, 25) / 100)
        totales.append(p_total)
    
    indice_ganador = totales.index(max(totales))
    alt_ganadora = alts[indice_ganador]
    
    st.success(f"🏆 **Ruta Técnica Seleccionada:** {alt_ganadora['nombre'].upper()}")

    # --- 2. FILTRADO JERÁRQUICO ---
    # Extraemos los componentes específicos que el formulador decidió ejecutar
    objs_finales = [c['objetivo'] for c in alt_ganadora['configuracion']]
    acts_finales = []
    for c in alt_ganadora['configuracion']:
        acts_finales.extend(c['actividades'])

    # Reconstruimos el árbol solo con los datos de la ganadora
    base = st.session_state['arbol_objetivos']
    arbol_final = {
        "Fin Último": base.get("Fin Último", []),
        "Fines Indirectos": base.get("Fines Indirectos", []),
        "Fines Directos": base.get("Fines Directos", []),
        "Objetivo General": base.get("Objetivo General", []),
        # Aquí aplicamos el filtro de la alternativa
        "Medios Directos": [o for o in base.get("Medios Directos", []) 
                            if (o['texto'] if isinstance(o, dict) else o) in objs_finales],
        "Medios Indirectos": [a for a in base.get("Medios Indirectos", []) 
                              if (a['texto'] if isinstance(a, dict) else a) in acts_finales]
    }

    # --- 3. GENERACIÓN DEL GRÁFICO ---
    CONFIG_GRAFICO = {
        "Fin Último": {"color": "#C1E1C1", "y": 5, "label": "FIN ÚLTIMO"},
        "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "label": "FINES INDIRECTOS"},
        "Fines Directos": {"color": "#80BFFF", "y": 3, "label": "FINES DIRECTOS"},
        "Objetivo General": {"color": "#FFB3BA", "y": 2, "label": "OBJETIVO GENERAL"},
        "Medios Directos": {"color": "#FFFFBA", "y": 1, "label": "OBJETIVOS ESPECÍFICOS"},
        "Medios Indirectos": {"color": "#FFDFBA", "y": 0, "label": "ACTIVIDADES"}
    }

    def dibujar_arbol_final():
        fig, ax = plt.subplots(figsize=(16, 14))
        ax.set_xlim(0, 10); ax.set_ylim(-1, 8.5); ax.axis('off')
        
        for nivel, conf in CONFIG_GRAFICO.items():
            items = arbol_final.get(nivel, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            y = conf["y"] * 1.5 
            
            for i, item in enumerate(items):
                x = (i + 1) * espacio
                texto = item["texto"] if isinstance(item, dict) else item
                
                # Rectángulo de la tarjeta
                ax.add_patch(plt.Rectangle((x-1.1, y-0.4), 2.2, 0.7, facecolor=conf["color"], edgecolor='#333', lw=1.5))
                
                # Texto ajustado para que no se corte
                txt_wrap = "\n".join(textwrap.wrap(texto, width=25))
                ax.text(x, y, txt_wrap, ha='center', va='center', fontsize=9, fontweight='bold')
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return buf.getvalue()

    # Visualización y descarga
    st.image(dibujar_arbol_final(), use_container_width=True)
    
    st.download_button(
        label="🖼️ Descargar Árbol de Objetivos Final (PNG)",
        data=dibujar_arbol_final(),
        file_name=f"arbol_final_{alt_ganadora['nombre']}.png",
        mime="image/png",
        use_container_width=True
    )

    st.divider()
    
    # --- 4. RESUMEN TEXTUAL PARA LA MML ---
    st.subheader("📋 Estructura de Planificación Seleccionada")
    for nivel, conf in CONFIG_GRAFICO.items():
        with st.expander(f"🔹 {conf['label']}"):
            elementos = arbol_final.get(nivel, [])
            for e in elementos:
                t = e["texto"] if isinstance(e, dict) else e
                st.write(f"**✓** {t}")
