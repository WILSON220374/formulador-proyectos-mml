import streamlit as st
import json
import pandas as pd
from session_state import inicializar_session

st.title("📁 Gestión del Proyecto")
st.info("Desde aquí puedes guardar tu progreso en un archivo o cargar un trabajo previo.")

# Inicializar por si acaso
inicializar_session()

# --- BOTÓN PARA GUARDAR ---
st.subheader("1. Guardar Progreso")
if st.button("💾 Generar Archivo de Proyecto"):
    # Empaquetamos todo lo que hay en la memoria
    datos_exportar = {
        "datos_problema": st.session_state['datos_problema'],
        "datos_zona": st.session_state['datos_zona'],
        "df_interesados": st.session_state['df_interesados'].to_dict(), # Convertimos tabla a texto
        "analisis_participantes": st.session_state['analisis_participantes'],
        "arbol_tarjetas": st.session_state['arbol_tarjetas'],
        "arbol_objetivos": st.session_state['arbol_objetivos']
    }
    
    # Convertir a formato JSON (texto)
    json_string = json.dumps(datos_exportar, indent=4)
    
    st.download_button(
        label="📥 Descargar archivo .json",
        data=json_string,
        file_name="proyecto_mml.json",
        mime="application/json",
        use_container_width=True
    )
    st.success("Archivo listo. Guárdalo en tu computadora o USB.")

st.divider()

# --- BOTÓN PARA CARGAR ---
st.subheader("2. Recuperar Trabajo")
archivo_subido = st.file_uploader("Sube tu archivo .json para continuar", type=["json"])

if archivo_subido is not None:
    try:
        datos_cargados = json.load(archivo_subido)
        
        # Inyectar los datos de vuelta a la memoria de la app
        st.session_state['datos_problema'] = datos_cargados['datos_problema']
        st.session_state['datos_zona'] = datos_cargados['datos_zona']
        st.session_state['df_interesados'] = pd.DataFrame(datos_cargados['df_interesados'])
        st.session_state['analisis_participantes'] = datos_cargados['analisis_participantes']
        st.session_state['arbol_tarjetas'] = datos_cargados['arbol_tarjetas']
        st.session_state['arbol_objetivos'] = datos_cargados['arbol_objetivos']
        
        st.success("✅ ¡Progreso cargado con éxito! Ya puedes navegar a las otras fases.")
    except Exception as e:
        st.error(f"Hubo un error al cargar el archivo: {e}")
