import streamlit as st
import pandas as pd

def inicializar_session():
    """Inicializa las variables para guardar datos de las 15 pestañas."""
    
    # --- FASE 1: DIAGNÓSTICO ---
    if 'datos_proyecto' not in st.session_state:
        st.session_state['datos_proyecto'] = {
            "nombre": "",
            "ubicacion": "",
            "descripcion_problema": "",
            "poblacion": 0,
            "problema_central": "",
            "manifestaciones": "",
            "causas_inmediatas": "",
            "factores_agravantes": "",
            "pob_total": 0,
            "pob_urbana": 0,
            "pob_rural": 0,
            "area_total": 0.0,
            "actividad_economica": "",
            "vias_acceso": "",
            "limites": ""
        }

    # --- FASE 2: INTERESADOS ---
    if 'df_interesados' not in st.session_state:
        st.session_state['df_interesados'] = pd.DataFrame(
            columns=["Actor", "Expectativa", "Poder (1-5)", "Interés (1-5)"]
        )

    # --- FASE 3: VESTER ---
    if 'problemas_vester' not in st.session_state:
        st.session_state['problemas_vester'] = [f"Problema {i}" for i in range(1, 6)]
    
    if 'df_vester' not in st.session_state:
        st.session_state['df_vester'] = pd.DataFrame()

    # --- FASE 4: ÁRBOLES ---
    if 'arbol_problemas' not in st.session_state:
        # CORRECCIÓN AQUÍ: Se agregaron los corchetes
        st.session_state['arbol_problemas'] = {"central": "", "causas":, "efectos":}

    # --- FASE 5: MARCO LÓGICO ---
    if 'df_mml' not in st.session_state:
        filas = ["Fin", "Propósito", "Componentes", "Actividades"]
        # CORRECCIÓN AQUÍ: Se definieron las columnas correctamente
        columnas =
        st.session_state['df_mml'] = pd.DataFrame("", index=filas, columns=columnas)
