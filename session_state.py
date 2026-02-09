import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa de forma segura todas las variables de estado."""
    
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
    # Esta es la clave para evitar el KeyError
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
