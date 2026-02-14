import streamlit as st
import pandas as pd
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización
inicializar_session()
df_actual = st.session_state.get('df_interesados', pd.DataFrame())
analisis_txt = st.session_state.get('analisis_participantes', "")

# --- ESTILOS CSS (DISEÑO LIMPIO Y PROFESIONAL) ---
st.markdown("""
    <style>
    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 20px; }
    
    /* Diseño del Editor de Tabla */
    div[data-testid="stDataEditor"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        padding: 5px;
        background-color: white;
    }
    
    /* Tarjetas de KPI */
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 1px solid #eee;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-val { font-size: 22px; font-weight: 800; color: #4F8BFF; }
    .kpi-lbl { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Ajustes generales */
    [data-testid="stImage"] img { border-radius: 10px; pointer-events: none; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_t, col_l = st.columns([4, 1], vertical_alignment="center")
with col_t:
    st.markdown('<div class="titulo-seccion">👥 3. Análisis de Interesados</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gris">Identificación de actores, posiciones y estrategias de gestión.</div>', unsafe_allow_html=True)
    
    # Progreso
    tiene_datos = not df_actual.empty and df_actual['NOMBRE'].dropna().any() if 'NOMBRE' in df_actual.columns else False
    progreso = (0.5 if tiene_datos else 0) + (0.5 if len(str(analisis_txt).strip()) > 20 else 0)
    st.progress(progreso, text=f"Avance de la Fase: {int(progreso * 100)}%")

with col_l:
    if os.path.exists("unnamed.jpg"): st.image("unnamed.jpg", use_container_width=True)
    elif os.path.exists("unnamed-1.jpg"): st.image("unnamed-1.jpg", use_container_width=True)

st.divider()

# --- PANEL DE INDICADORES (KPIs) ---
if tiene_datos:
    # Filtramos buscando el emoji o el texto
    total = len(df_actual.dropna(subset=["NOMBRE"]))
    opos = len(df_actual[df_actual['POSICIÓN'].astype(str).str.contains("Opositor", case=False, na=False)])
    coop = len(df_actual[df_actual['POSICIÓN'].astype(str).str.contains("Cooperante", case=False, na=False)])
    poder = len(df_actual[df_actual['PODER'].astype(str).str.contains("Alto", case=False, na=False)])

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{total}</div><div class="kpi-lbl">Actores Totales</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#ef4444;">{opos}</div><div class="kpi-lbl">Opositores</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#22c55e;">{coop}</div><div class="kpi-lbl">Cooperantes</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{poder}</div><div class="kpi-lbl">Alto Poder</div></div>', unsafe_allow_html=True)
    st.write("")

# --- MATRIZ DE DATOS ---
st.subheader("📝 Matriz de Datos")

# 1. Definición de Opciones CON ICONOS (Esto da el color visual)
opciones_posicion = ["🔴 Opositor", "🟢 Cooperante", "🔵 Beneficiario", "🟣 Perjudicado", "⚪ Indiferente"]
opciones_nivel = ["⚡ Alto", "🔅 Bajo"]

# 2. Configuración de Columnas
config_columnas = {
    "NOMBRE": st.column_config.TextColumn("Nombre del Actor", width="medium", required=True),
    "GRUPO": st.column_config.TextColumn("Grupo", width="small"),
    "POSICIÓN": st.column_config.SelectboxColumn("Posición", options=opciones_posicion, width="small"),
    "EXPECTATIVA": st.column_config.TextColumn("Expectativa Principal", width="large"),
    "CONTRIBUCION AL PROYECTO": st.column_config.TextColumn("Contribución", width="medium"),
    "PODER": st.column_config.SelectboxColumn("Poder", options=opciones_nivel, width="small"),
    "INTERÉS": st.column_config.SelectboxColumn("Interés", options=opciones_nivel, width="small"),
    "ESTRATEGIA DE INVOLUCRAMIENTO": st.column_config.TextColumn("Estrategia Sugerida", disabled=True, width="medium")
}

# 3. Preparación de Datos
columnas_finales = list(config_columnas.keys())
if df_actual.empty: df_actual = pd.DataFrame(columns=columnas_finales)
if "#" in df_actual.columns: df_actual = df_actual.drop(columns=["#"])
# Asegurar columnas
for col in columnas_finales:
    if col not in df_actual.columns: df_actual[col] = None
df_actual = df_actual[columnas_finales]

# 4. Renderizado (Nativo de Streamlit)
df_editado = st.data_editor(
    df_actual,
    column_config=config_columnas,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="editor_interesados_nativo_final"
)

st.divider()

# --- MAPA DE INFLUENCIA (TARJETAS DE ESTRATEGIA) ---
st.subheader("📊 Mapa de Estratégico (Consolidado)")

if tiene_datos:
    # Limpieza de Emojis para el filtrado lógico
    df_clean = df_editado.copy()
    # Función segura para limpiar
    def limpiar_str(val, texto_a_quitar):
        return str(val).replace(texto_a_quitar, "").strip()

    # Preparamos los datos para visualización
    color_map = {"Opositor": "🔴", "Beneficiario": "🟢", "Cooperante": "🔵", "Perjudicado": "🟣"}
    
    def obtener_actores(p_val, i_val):
        # Filtramos buscando el texto clave (ej: "Alto") dentro de la celda que puede tener "⚡ Alto"
        filtro = df_clean[
            (df_clean['PODER'].astype(str).str.contains(p_val, na=False)) & 
            (df_clean['INTERÉS'].astype(str).str.contains(i_val, na=False)) & 
            (df_clean['NOMBRE'].notna())
        ]
        
        resultado = []
        for _, row in filtro.iterrows():
            pos_raw = str(row['POSICIÓN'])
            # Buscamos qué icono poner
            icono = "⚪"
            for k, v in color_map.items():
                if k in pos_raw:
                    icono = v
                    break
            resultado.append(f"{icono} {row['NOMBRE']}")
        
        return resultado if resultado else ["*Ninguno*"]

    # Diseño de Cuadrantes (Tarjetas)
    c1, c2 = st.columns(2)
    
    with c1:
        with st.container(border=True):
            st.error("🤝 SATISFACER (Poder Alto / Interés Bajo)")
            st.caption("Estrategia: Consultar regularmente, asegurar que sus requisitos clave se cumplan.")
            for actor in obtener_actores("Alto", "Bajo"): st.markdown(actor)
            
        with st.container(border=True):
            st.warning("🔍 MONITORIZAR (Poder Bajo / Interés Bajo)")
            st.caption("Estrategia: Mínimo esfuerzo, mantener informados solo si es necesario.")
            for actor in obtener_actores("Bajo", "Bajo"): st.markdown(actor)

    with c2:
        with st.container(border=True):
            st.success("🚀 INVOLUCRAR (Poder Alto / Interés Alto)")
            st.caption("Estrategia: Gestionar atentamente. Son los actores clave para el éxito.")
            for actor in obtener_actores("Alto", "Alto"): st.markdown(f"**{actor}**")
            
        with st.container(border=True):
            st.info("📧 INFORMAR (Poder Bajo / Interés Alto)")
            st.caption("Estrategia: Mantener informados para evitar que se vuelvan opositores.")
            for actor in obtener_actores("Bajo", "Alto"): st.markdown(actor)

else:
    st.info("💡 Ingrese actores en la tabla superior para visualizar las tarjetas de estrategia.")

st.divider()

# --- ANÁLISIS CUALITATIVO ---
st.subheader("📝 Análisis de Participantes")
analisis_actual = st.text_area(
    "Escriba sus conclusiones aquí...", 
    value=analisis_txt, 
    height=200, 
    key="txt_analisis_final_panel", 
    label_visibility="collapsed",
    placeholder="Describa las alianzas potenciales, riesgos críticos y pasos a seguir..."
)

# --- LÓGICA DE GUARDADO (AL FINAL PARA EVITAR CORTES) ---

# 1. Recalcular estrategias en el DataFrame editado
def calcular_estrategia(row):
    # Limpiamos los emojis antes de comparar
    p = str(row.get('PODER', '')).replace('⚡ ', '').replace('🔅 ', '').strip()
    i = str(row.get('INTERÉS', '')).replace('⚡ ', '').replace('🔅 ', '').strip()
    
    if p == "Alto" and i == "Alto": return "Involucrar y mantener cerca"
    if p == "Alto" and i == "Bajo": return "Consultar y mantener satisfechos"
    if p == "Bajo" and i == "Alto": return "Mantener informados"
    if p == "Bajo" and i == "Bajo": return "Monitorizar"
    return ""

if not df_editado.empty:
    df_editado["ESTRATEGIA DE INVOLUCRAMIENTO"] = df_editado.apply(calcular_estrategia, axis=1)

# 2. Detectar cambios
hubo_cambios_tabla = not df_editado.equals(df_actual)
hubo_cambios_texto = analisis_actual != analisis_txt

# 3. Guardar y Recargar (SOLO si es necesario)
if hubo_cambios_tabla or hubo_cambios_texto:
    if hubo_cambios_tabla:
        st.session_state['df_interesados'] = df_editado
    if hubo_cambios_texto:
        st.session_state['analisis_participantes'] = analisis_actual
        
    guardar_datos_nube()
    st.rerun()
