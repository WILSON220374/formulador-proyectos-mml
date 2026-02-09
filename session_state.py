import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa la memoria y fuerza la limpieza de versiones antiguas."""
    
    # --- RESET FORZADO SI DETECTA ESTRUCTURA VIEJA ---
    if 'arbol_tarjetas' in st.session_state:
        if "Fin" in st.session_state['arbol_tarjetas'] or "Reglas MML Activas" in str(st.session_state):
            st.session_state.clear() # Borra todo para evitar conflictos
            st.rerun()

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
    
    # --- FASE 4: ÁRBOL DE PROBLEMAS (Estructura Jerárquica Nueva) ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {
            "Problema Superior": [],   
            "Efectos Indirectos": [],  
            "Efectos Directos": [],    
            "Problema Central": [],    
            "Causas Directas": [],     
            "Causas Indirectas": []    
        }

inicializar_session()
