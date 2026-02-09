import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa las variables para guardar datos de las 15 pestañas."""
    
    # --- FASE 1: DIAGNÓSTICO ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {
            "problema_central": "",
            "sintomas": "",
            "causas_inmediatas": "",
            "factores_agravantes": ""
        }

    # --- FASE 2: ZONA ---
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {
            "pob_total": 0, "pob_urbana": 0, "pob_rural": 0,
            "ubicacion": "", "limites": "", "economia": "", "vias": ""
        }

    # --- FASE 3: INTERESADOS (9 columnas exactas) ---
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(
            columns=[
                "#", "NOMBRE", "POSICIÓN", "GRUPO", "EXPECTATIVA", 
                "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"
            ]
        )
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = ""
    
    # --- FASE 4: ÁRBOL DE PROBLEMAS (6 secciones de tarjetas) ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {
            "Fin": [],
            "Efectos Indirectos": [],
            "Efectos Directos": [],
            "Problema Central": [],
            "Causas Directas": [],
            "Causas Indirectas": []
        }

    # --- FASE 5: MARCO LÓGICO (6 columnas técnicas) ---
    if 'df_mml' not in st.session_state:
        filas = ["Fin", "Propósito", "Componentes", "Actividades"]
        columnas = [
            "INDICATORS", "SOURCE OF INFORMATION", "METHOD OF ANALYSIS", 
            "FREQUENCY OF COLLECTION", "RESPONSIBLE", "ASSUMPTIONS"
        ]
        st.session_state['df_mml'] = pd.DataFrame("", index=filas, columns=columnas)

# Ejecución automática al importar
inicializar_session()
