import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa la memoria para todas las fases, incluyendo el nuevo Árbol de Objetivos."""
    
    # --- FASE 1: DIAGNÓSTICO ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {
            "problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""
        }

    # --- FASE 3: INTERESADOS ---
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(
            columns=["#", "NOMBRE", "POSICIÓN", "GRUPO", "EXPECTATIVA", 
                     "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
        )
    
    # --- FASE 4: ÁRBOL DE PROBLEMAS ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {
            "Problema Superior": [], "Efectos Indirectos": [], "Efectos Directos": [],
            "Problema Central": [], "Causas Directas": [], "Causas Indirectas": []
        }

    # --- FASE 5: ÁRBOL DE OBJETIVOS ---
    if 'arbol_objetivos' not in st.session_state:
        st.session_state['arbol_objetivos'] = {
            "Fin Último": [],           # Positivo de Problema Superior
            "Fines Indirectos": [],     # Positivo de Efectos Indirectos
            "Fines Directos": [],       # Positivo de Efectos Directos
            "Objetivo General": [],     # Positivo de Problema Central
            "Medios Directos": [],      # Positivo de Causas Directas
            "Medios Indirectos": []     # Positivo de Causas Indirectas
        }

inicializar_session()
