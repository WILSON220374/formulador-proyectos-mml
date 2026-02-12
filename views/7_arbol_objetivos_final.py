import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import textwrap
from session_state import inicializar_session

# 1. Carga de datos con persistencia total
inicializar_session()

st.title("🎯 Árbol de Objetivos Final")
st.info("Este diagrama muestra la cadena de valor completa: desde las actividades seleccionadas hasta los fines que estas impactan.")

# --- 1. DETERMINACIÓN DE LA RUTA TÉCNICA GANADORA ---
alts = st.session_state.get('lista_alternativas', [])
df_cal = st.session_state.get('df_calificaciones', pd.DataFrame())
pesos = st.session_state.get('ponderacion_criterios', {})

if not alts or df_cal.empty:
    st.warning("⚠️ Evaluación incompleta. Regrese al paso 6 para calificar y seleccionar una alternativa.")
else:
    # Cálculo matemático de la ganadora
    criterios = ["COSTO", "FACILIDAD", "BENEFICIOS", "TIEMPO"]
    nombres_alts = [a['nombre'] for a in alts]
    totales = []
    for alt_n in nombres_alts:
        totales.append(sum(df_cal.loc[alt_n, c] * (pesos.get(c, 25)/100) for c in criterios))
    
    alt_ganadora = alts[totales.index(max(totales))]
    st.success(f"🏆 **Alternativa Seleccionada:** {alt_ganadora['nombre'].upper()}")

    # --- 2. LÓGICA DE FILTRADO JERÁRQUICO (ASCENDENTE Y DESCENDENTE) ---
    base = st.session_state['arbol_objetivos']
    
    # A. MEDIOS: Lo que el formulador seleccionó explícitamente
    objs_sel_txt = [c['objetivo'] for c in alt_ganadora['configuracion']]
    acts_sel_txt = []
    for c in alt_ganadora['configuracion']: acts_sel_txt.extend(c['actividades'])

    # B. FINES: Filtrado por relación jerárquica
    # Solo quedan los Fines Directos cuyo padre sea el Objetivo General O uno de los objetivos seleccionados
    fines_d_final = [f for f in base.get("Fines Directos", []) 
                     if (f.get("padre") == base.get("Objetivo General", [""])[0] or f.get("padre") in objs_sel_txt)]
    
    fines_d_txt = [f['texto'] if isinstance(f, dict) else f for f in fines_d_final]
    
    # Solo quedan los Fines Indirectos cuyos padres sean Fines Directos que sobrevivieron
    fines_i_final = [f for f in base.get("Fines Indirectos", []) 
                     if (f['padre'] if isinstance(f, dict) else "") in fines_d_txt]
    
    fines_i_txt = [f['texto'] if isinstance(f, dict) else f for f in fines_i_final]

    # Reconstrucción del diccionario para el gráfico
    arbol_final = {
        "Fin Último": base.get("Fin Último", []),
        "Fines Indirectos": fines_i_final,
        "Fines Directos": fines_d_final,
        "Objetivo General": base.get("Objetivo General", []),
        "Medios Directos": [o for o in base.get("Medios Directos", []) if (o['texto'] if isinstance(o, dict) else o) in objs_sel_txt],
        "Medios Indirectos": [a for a in base.get("Medios Indirectos", []) if (a['texto'] if isinstance(a, dict) else a) in acts_sel_txt]
    }

    # --- 3. RENDERIZADO DEL DIAGRAMA ---
    CONF = {
        "Fin Último": {"color": "#C1E1C1", "y": 5, "label": "FIN ÚLTIMO"},
        "Fines Indirectos": {"color": "#B3D9FF", "y": 4, "label": "FINES INDIRECTOS"},
        "Fines Directos": {"color": "#80BFFF", "y": 3, "label": "FINES DIRECTOS"},
        "Objetivo General": {"color": "#FFB3BA", "y": 2, "label": "OBJETIVO GENERAL"},
        "Medios Directos": {"color": "#FFFFBA", "y": 1, "label": "OBJETIVOS ESPECÍFICOS"},
        "Medios Indirectos": {"color": "#FFDFBA", "y": 0, "label": "ACTIVIDADES"}
    }

    def dibujar_final():
        fig, ax = plt.subplots(figsize=(16, 14))
        ax.set_xlim(0, 10); ax.set_ylim(-1, 8.5); ax.axis('off')
        for nivel, c in CONF.items():
            items = arbol_final.get(nivel, [])
            if not items: continue
            espacio = 10 / (len(items) + 1)
            for i, it in enumerate(items):
                x, y = (i + 1) * espacio, c["y"] * 1.5
                txt = it["texto"] if isinstance(it, dict) else it
                ax.add_patch(plt.Rectangle((x-1.1, y-0.4), 2.2, 0.7, facecolor=c["color"], edgecolor='#333', lw=1.5))
                ax.text(x, y, "\n".join(textwrap.wrap(txt, width=25)), ha='center', va='center', fontsize=9, fontweight='bold')
        buf = io.BytesIO(); plt.savefig(buf, format="png", dpi=300, bbox_inches='tight'); plt.close(fig)
        return buf.getvalue()

    st.image(dibujar_final(), use_container_width=True)
    st.download_button("🖼️ Descargar Árbol Final (PNG)", dibujar_final(), "arbol_objetivos_final.png", "image/png", use_container_width=True)
