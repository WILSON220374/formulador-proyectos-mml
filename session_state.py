import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa de forma segura todas las variables de estado."""
    
    # --- FASE 1: DIAGNÓSTICO ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {
            "problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""
        }

    # --- FASE 2: ZONA DE ESTUDIO (Faltaba esta inicialización) ---
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {}

    # --- FASE 3: INTERESADOS ---
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(
            columns=["#", "NOMBRE", "POSICIÓN", "GRUPO", "EXPECTATIVA", 
                     "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
        )
    
    # Variable que causaba el error en la línea 59 de interesados.py
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = ""
    
    # --- FASE 4: ÁRBOL DE PROBLEMAS ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {
            "Problema Superior": [], "Efectos Indirectos": [], "Efectos Directos": [],
            "Problema Central": [], "Causas Directas": [], "Causas Indirectas": []
        }

    # --- FASE 5: ÁRBOL DE OBJETIVOS ---
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = {
            "Fin Último": [],           
            "Fines Indirectos": [],     
            "Fines Directos": [],       
            "Objetivo General": [],     
            "Medios Directos": [],      
            "Medios Indirectos": []     
        }

# Ejecutar siempre al importar
inicializar_session()
