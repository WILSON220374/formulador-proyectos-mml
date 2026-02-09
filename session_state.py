import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa la memoria con la nueva jerarquía de Problema Superior y dependencias."""
    
    # --- FASE 1: DIAGNÓSTICO ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {
            "problema_central": "", "sintomas": "", "causas_inmediatas": "", "factores_agravantes": ""
        }

    # --- FASE 2: ZONA ---
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {
            "pob_total": 0, "pob_urbana": 0, "pob_rural": 0,
            "ubicacion": "", "limites": "", "economia": "", "vias": ""
        }

    # --- FASE 3: INTERESADOS ---
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(
            columns=["#", "NOMBRE", "POSICIÓN", "GRUPO", "EXPECTATIVA", 
                     "CONTRIBUCION AL PROYECTO", "PODER", "INTERÉS", "ESTRATEGIA DE INVOLUCRAMIENTO"]
        )
    if 'analisis_participantes' not in st.session_state:
        st.session_state['analisis_participantes'] = ""
    
    # --- FASE 4: ÁRBOL DE PROBLEMAS (Nombres y Estructura Actualizada) ---
    if 'arbol_tarjetas' not in st.session_state:
        st.session_state['arbol_tarjetas'] = {
            "Problema Superior": [],   # Antes 'Fin'
            "Efectos Indirectos": [],  # Lista de dicts: {"texto": "", "padre": ""}
            "Efectos Directos": [],    # Lista de strings
            "Problema Central": [],    # Lista de strings
            "Causas Directas": [],     # Lista de strings
            "Causas Indirectas": []    # Lista de dicts: {"texto": "", "padre": ""}
        }

# Ejecución forzada
inicializar_session()
