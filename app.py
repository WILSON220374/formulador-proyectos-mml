import streamlit as st
import os
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- PURIFICACIÓN DE RAÍZ ---
if 'integrantes' in st.session_state and isinstance(st.session_state['integrantes'], list):
    st.session_state['integrantes'] = [p for p in st.session_state['integrantes'] if p is not None and isinstance(p, dict)]

# --- LÓGICA DE ACCESO (LOGIN) CON DISEÑO DIVIDIDO (IZQ: FORM / DER: LOGO) ---
if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        /* Título alineado a la izquierda para combinar con el formulario */
        .titulo-acceso { 
            font-size: 32px !important; 
            font-weight: 800 !important; 
            color: #4F8BFF; 
            text-align: left; 
            margin-bottom: 10px; 
            margin-top: 20px;
        }
        .label-mediana { 
            font-size: 16px !important; 
            font-weight: bold; 
            color: #1E3A8A; 
            margin-bottom: 5px !important; 
            margin-top: 10px !important; 
            display: block; 
        }
        input { 
            font-size: 18px !important; 
            height: 45px !important; 
            border-radius: 10px !important; 
        }
        div.stButton > button { 
            font-size: 20px !important; 
            height: 50px !important; 
            font-weight: bold !important; 
            background-color: #4F8BFF !important; 
            border-radius: 12px !important; 
            margin-top: 25px; 
        }
        </style>
    """, unsafe_allow_html=True)

    # Creamos dos columnas: Izquierda (Formulario) y Derecha (Imagen Grande)
    # Ajustamos la proporción (1.2 vs 1.8) para dar más espacio a la imagen si es necesario
    col_form, col_img = st.columns([1.2, 1.8], gap="large")

    with col_form:
        st.markdown('<div class="titulo-acceso">Acceso Grupal<br>Posgrado</div>', unsafe_allow_html=True)
        
        # Contenedor del formulario
        with st.container(border=True):
            st.markdown('<label class="label-mediana">USUARIO (GRUPO)</label>', unsafe_allow_html=True)
            u = st.text_input("u", label_visibility="collapsed", placeholder="Ej: grupo1")
            
            st.markdown('<label class="label-mediana">CONTRASEÑA</label>', unsafe_allow_html=True)
            p = st.text_input("p", type="password", label_visibility="collapsed")
            
            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
                try:
                    db = conectar_db()
                    # Mantenemos tu lógica exacta de validación
                    res = db.table("proyectos").select("*").eq("user_id", u).eq("password", p).execute()
                    if res.data:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_id'] = u
                        cargar_datos_nube(u)
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")
                except Exception:
                    st.error("Error de conexión.")

    with col_img:
        # Imagen a la derecha, ocupando todo el ancho disponible para verse grande
        if os.path.exists("unnamed.jpg"):
            st.image("unnamed.jpg", use_container_width=True) 
        else:
            # Placeholder por si la imagen no carga
            st.info("Logotipo JC Flow (Cargar imagen 'unnamed.jpg')")

    st.stop()

# --- SIDEBAR Y NAVEGACIÓN (Original intacto) ---
with st.sidebar:
    st.header(f"👷 {st.session_state['usuario_id']}")
    
    integrantes = st.session_state.get('integrantes', [])
    if integrantes and isinstance(integrantes, list):
        for persona in integrantes:
            try:
                if persona and isinstance(persona, dict):
                    nombre_full = persona.get("Nombre Completo", "").strip()
                    if nombre_full:
                        nombre_pila = nombre_full.split()[0].upper()
                        st.markdown(f"**👤 {nombre_pila}**")
            except Exception:
                continue
    
    st.divider()
    if st.button("☁️ GUARDAR TODO EN NUBE", use_container_width=True, type="primary"):
        guardar_datos_nube()
        st.toast("✅ Avance guardado", icon="🚀")
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

pg = st.navigation({
    "Configuración": [st.Page("views/0_equipo.py", title="Equipo", icon="👥")],
    "Fase I: Identificación": [
        st.Page("views/1_diagnostico.py", title="1. Diagnóstico", icon="🧐"),
        st.Page("views/2_zona.py", title="2. Zona de Estudio", icon="🗺️"),
        st.Page("views/3_interesados.py", title="3. Interesados", icon="👥"),
    ],
    "Fase II: Análisis": [
        st.Page("views/4_arbol_problemas.py", title="4. Árbol de Problemas", icon="🌳"),
        st.Page("views/5_arbol_objetivos.py", title="5. Árbol de Objetivos", icon="🎯"),
        st.Page("views/6_alternativas.py", title="6. Análisis de Alternativas", icon="⚖️"),
        st.Page("views/7_arbol_objetivos_final.py", title="7. Árbol de Objetivos Final", icon="🚀"),
        st.Page("views/8_arbol_problemas_final.py", title="8. Árbol de Problemas Final", icon="🌳"),
    ]
})
pg.run()
