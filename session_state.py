import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa la memoria con limpieza automática de versiones antiguas."""
    
    # --- LIMPIEZA DE MEMORIA VIEJA ---
    # Si detecta la estructura antigua, reinicia para evitar errores de nombres
    if 'arbol_tarjetas' in st.session_state:
        if "Fin" in st.session_state['arbol_tarjetas']:
            del st.session_state['arbol_tarjetas']

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
    
    # --- FASE 4: ÁRBOL DE PROBLEMAS (Jerarquía solicitada) ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {
            "Problema Superior": [],   # Nombre actualizado
            "Efectos Indirectos": [],  # Formato: {"texto": "", "padre": ""}
            "Efectos Directos": [],    # Texto simple
            "Problema Central": [],    # Texto simple
            "Causas Directas": [],     # Texto simple
            "Causas Indirectas": []    # Formato: {"texto": "", "padre": ""}
        }

inicializar_session()
