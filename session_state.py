import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa las variables de memoria para todas las fases del proyecto."""
    
    # --- FASE 1: DIAGNÓSTICO (Solo el Problema) ---
    if 'datos_problema' not in st.session_state:
        st.session_state['datos_problema'] = {
            "problema_central": "",
            "sintomas": "",
            "causas_inmediatas": "",
            "factores_agravantes": ""
        }

    # --- FASE 2: ZONA (Territorio y Población) ---
    if 'datos_zona' not in st.session_state:
        st.session_state['datos_zona'] = {
            "pob_total": 0,
            "pob_urbana": 0,
            "pob_rural": 0,
            "ubicacion": "",
            "limites": "",
            "economia": "",
            "vias": ""
        }

    # --- FASE 3: INTERESADOS ---
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(
            columns=["Actor", "Expectativa", "Poder (1-5)", "Interés (1-5)"]
        )

    # --- FASE 4: VESTER ---
    if 'problemas_vester' not in st.session_state:
        # Iniciamos con 10 problemas vacíos
        st.session_state['problemas_vester'] = [f"Problema {i}" for i in range(1, 11)]
    
    if 'df_vester' not in st.session_state:
        st.session_state['df_vester'] = pd.DataFrame()

    # --- FASE 5: ÁRBOLES ---
    if 'arbol_problemas' not in st.session_state:
        st.session_state['arbol_problemas'] = {}

    # --- FASE 6: MARCO LÓGICO ---
    if 'df_mml' not in st.session_state:
        filas = ["Fin", "Propósito", "Componentes", "Actividades"]
        cols =
        st.session_state['df_mml'] = pd.DataFrame("", index=filas, columns=cols)
