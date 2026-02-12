import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap
import os
from session_state import inicializar_session, guardar_datos_nube

# 1. Inicialización y Estilos
inicializar_session()

st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 14px !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    /* Ajuste para flechas y conectores en web */
    .flecha-bajada { font-size: 24px; text-align: center; color: #4F8BFF; margin: -10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. ENCABEZADO CON LOGO (ZONA AMARILLA) ---
# Usamos la misma estructura que en las otras hojas para consistencia.
col_titulo, col_logo = st.columns([0.8, 0.2], vertical_alignment="center")
with col_titulo:
    st.title("🎯 5. Árbol de Objetivos")
with col_logo:
    if os.path.exists("unnamed-1.jpg"):
        st.image("unnamed-1.jpg", use_container_width=True)

# --- 3. LÓGICA DE TRANSFORMACIÓN (Problema -> Objetivo) ---
def transformar_a_positivo(texto):
    if not texto: return "---"
    reemplazos = {
        "Alta": "Baja", "Baja": "Alta", "Alto": "Bajo", "Bajo": "Alto",
        "Deficiente": "Eficiente", "Inadecuado": "Adecuado", "Escasa": "Suficiente",
        "Falta de": "Presencia de", "No hay": "Existe", "Pérdida": "Recuperación",
        "Aumento": "Disminución", "Incremento": "Reducción"
    }
    for mal, bien in reemplazos.items():
        # Reemplazo simple (se puede mejorar con regex si es necesario)
        texto = texto.replace(mal, bien).replace(mal.lower(), bien.lower())
    return texto

# Cargar datos del árbol de problemas
datos_prob = st.session_state.get('arbol_tarjetas', {})

# Inicializar estructura de objetivos si no existe
if 'datos_objetivos' not in st.session_state:
    st.session_state['datos_objetivos'] = {
        "obj_central": transformar_a_positivo(datos_prob.get("Problema Principal", [""])[0] if datos_prob.get("Problema Principal") else ""),
        "fines_directos": [transformar_a_positivo(t) for t in datos_prob.get("Efectos Directos", [])],
        "fines_indirectos": [transformar_a_positivo(t.get("texto")) for t in datos_prob.get("Efectos Indirectos", []) if isinstance(t, dict)],
        "medios_directos": [transformar_a_positivo(t) for t in datos_prob.get("Causas Directas", [])],
        "medios_indirectos": [transformar_a_positivo(t.get("texto")) for t in datos_prob.get("Causas Indirectas", []) if isinstance(t, dict)]
    }

datos_obj = st.session_state['datos_objetivos']

# --- 4. FUNCIÓN PARA ALTURA DINÁMICA EN WEB ---
# Esta función asegura que los text_area crezcan según el contenido.
def calcular_altura(texto, min_h=85):
    if not texto: return min_h
    # Cálculo aproximado de líneas basado en longitud y saltos de línea
    lineas = str(texto).count('\n') + (len(str(texto)) // 40) 
    return max(min_h, (lineas + 1) * 25)

# --- 5. RENDERIZADO EN PANTALLA (WEB ELÁSTICA) ---

# Nivel 1: Fines Indirectos (Arriba)
st.subheader("🌟 Fines (Impacto a Largo Plazo)")
if datos_obj["fines_indirectos"]:
    cols = st.columns(len(datos_obj["fines_indirectos"]))
    for i, texto in enumerate(datos_obj["fines_indirectos"]):
        with cols[i]:
            datos_obj["fines_indirectos"][i] = st.text_area(
                f"Fin Ind. {i+1}", value=texto, 
                height=calcular_altura(texto), # <--- Altura dinámica aplicada
                key=f"fi_{i}", label_visibility="collapsed"
            )
            st.markdown('<div class="flecha-bajada">⬆️</div>', unsafe_allow_html=True)

# Nivel 2: Fines Directos
if datos_obj["fines_directos"]:
    cols = st.columns(len(datos_obj["fines_directos"]))
    for i, texto in enumerate(datos_obj["fines_directos"]):
        with cols[i]:
            datos_obj["fines_directos"][i] = st.text_area(
                f"Fin Dir. {i+1}", value=texto, 
                height=calcular_altura(texto, min_h=100), # <--- Altura dinámica aplicada
                key=f"fd_{i}", label_visibility="collapsed"
            )
            st.markdown('<div class="flecha-bajada">⬆️</div>', unsafe_allow_html=True)

# Nivel 3: Objetivo Central (Centro)
st.markdown("---")
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.subheader("🎯 Objetivo Central (Propósito)")
    datos_obj["obj_central"] = st.text_area(
        "OBJETIVO CENTRAL", value=datos_obj["obj_central"], 
        height=calcular_altura(datos_obj["obj_central"], min_h=120), # <--- Altura dinámica aplicada
        key="obj_central_txt", label_visibility="collapsed"
    )
    st.markdown('<div class="flecha-bajada">⬆️</div>', unsafe_allow_html=True)
st.markdown("---")

# Nivel 4: Medios Directos (Abajo)
st.subheader("🛠️ Medios (Componentes)")
if datos_obj["medios_directos"]:
    cols = st.columns(len(datos_obj["medios_directos"]))
    for i, texto in enumerate(datos_obj["medios_directos"]):
        with cols[i]:
            datos_obj["medios_directos"][i] = st.text_area(
                f"Medio Dir. {i+1}", value=texto, 
                height=calcular_altura(texto, min_h=100), # <--- Altura dinámica aplicada
                key=f"md_{i}", label_visibility="collapsed"
            )

# Nivel 5: Medios Indirectos (Base)
if datos_obj["medios_indirectos"]:
    cols = st.columns(len(datos_obj["medios_indirectos"]))
    for i, texto in enumerate(datos_obj["medios_indirectos"]):
        with cols[i]:
            st.markdown('<div class="flecha-bajada">⬆️</div>', unsafe_allow_html=True)
            datos_obj["medios_indirectos"][i] = st.text_area(
                f"Medio Ind. {i+1}", value=texto, 
                height=calcular_altura(texto), # <--- Altura dinámica aplicada
                key=f"mi_{i}", label_visibility="collapsed"
            )

# Guardado automático de ediciones en pantalla
st.session_state['datos_objetivos'] = datos_obj
guardar_datos_nube()

st.divider()

# --- 6. MOTOR DE EXPORTACIÓN ROBUSTO (Copia del Árbol de Problemas) ---
def generar_png_objetivos():
    # 1. Lienzo grande para soportar 10 líneas de texto
    fig, ax = plt.subplots(figsize=(22, 24))
    ax.set_xlim(0, 12); ax.set_ylim(-6, 14); ax.axis('off')

    # 2. Título del PNG
    ax.text(6, 13, "ÁRBOL DE OBJETIVOS", fontsize=32, fontweight='bold', ha='center', color='#1E3A8A')

    # 3. Configuración de la Rejilla de Seguridad (Coordenadas Y fijas)
    CONFIG_OBJ = {
        "Fines Indirectos": {"y": 11, "color": "#D4EDDA"},
        "Fines Directos": {"y": 8, "color": "#C3E6CB"},
        "Objetivo Central": {"y": 4.5, "color": "#FFF3CD"},
        "Medios Directos": {"y": 1, "color": "#D1ECF1"},
        "Medios Indirectos": {"y": -3, "color": "#BEE5EB"}
    }

    # 4. Función de dibujo inteligente (Contrato de 180 caracteres)
    def dibujar_caja(x, y, texto, color):
        # Envoltura a 18 caracteres
        lineas = textwrap.wrap(texto, width=18) if texto else ["---"]
        # Límite duro de 10 líneas
        txt_ajustado = "\n".join(lineas[:10])
        n_lineas = len(lineas[:10])

        # Altura dinámica y Ancho de seguridad
        rect_h = max(1.0, 0.5 + (n_lineas * 0.28))
        rect_w = 2.0 # Ancho suficiente para no tocarse lateralmente

        # Ajuste de fuente
        f_size = 10 if n_lineas <= 5 else 8.5

        # Dibujo del rectángulo y texto
        rect = plt.Rectangle((x - rect_w/2, y - rect_h/2), rect_w, rect_h,
                             facecolor=color, edgecolor='#2C5F2D', lw=2, zorder=3, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, y, txt_ajustado, ha='center', va='center', fontsize=f_size,
                fontweight='bold', zorder=4, color='#155724')

    # 5. Dibujado por niveles usando la data actual de la sesión

    # Objetivo Central
    dibujar_caja(6, CONFIG_OBJ["Objetivo Central"]["y"], datos_obj["obj_central"], CONFIG_OBJ["Objetivo Central"]["color"])

    # Fines (Directos e Indirectos)
    for nivel, clave_data in [("Fines Directos", "fines_directos"), ("Fines Indirectos", "fines_indirectos")]:
        items = datos_obj[clave_data]
        if items:
            espacio = 12 / (len(items) + 1)
            for i, txt in enumerate(items):
                dibujar_caja((i + 1) * espacio, CONFIG_OBJ[nivel]["y"], txt, CONFIG_OBJ[nivel]["color"])

    # Medios (Directos e Indirectos)
    for nivel, clave_data in [("Medios Directos", "medios_directos"), ("Medios Indirectos", "medios_indirectos")]:
        items = datos_obj[clave_data]
        if items:
            espacio = 12 / (len(items) + 1)
            for i, txt in enumerate(items):
                dibujar_caja((i + 1) * espacio, CONFIG_OBJ[nivel]["y"], txt, CONFIG_OBJ[nivel]["color"])
    
    # Flecha central gigante (decorativa)
    ax.annotate("", xy=(6, 7), xytext=(6, 2), arrowprops=dict(arrowstyle="->", lw=4, color="#1E3A8A"))

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return buf.getvalue()

# Botón de descarga con el nuevo motor
st.download_button("🖼️ Descargar Árbol de Objetivos PNG", data=generar_png_objetivos(), file_name="arbol_objetivos_final.png", mime="image/png", use_container_width=True)
