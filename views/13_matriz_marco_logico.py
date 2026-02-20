import streamlit as st
from session_state import inicializar_session

# 1. Asegurar persistencia
inicializar_session()

# --- DISEÑO DE ALTO IMPACTO (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Estenedores de tarjetas */
    .card-mml {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 8px solid #1E3A8A; /* Azul oscuro institucional */
    }
    
    /* Títulos de columnas dentro de la tarjeta */
    .col-title {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 0.85rem;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 8px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 5px;
    }
    
    /* Contenido de los datos */
    .col-content {
        font-size: 0.95rem;
        color: #334155;
        text-align: center;
        line-height: 1.5;
        padding: 5px;
    }

    .titulo-seccion { font-size: 30px !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo-gris { font-size: 16px !important; color: #666; margin-bottom: 25px; }
    
    /* Badge para el TIPO */
    .tipo-badge {
        background-color: #1E3A8A;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO Y BARRA DE AVANCE ---
st.markdown('<div class="titulo-seccion">📋 13. Matriz de Marco Lógico (MML)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-gris">Validación final de la coherencia narrativa y operativa del proyecto.</div>', unsafe_allow_html=True)

# Barra de avance (Estática por ahora)
st.progress(0.75) 
st.caption("Progreso de validación: 75%")
st.divider()

# --- DATOS DE EJEMPLO (SIN ENLAZAR AÚN) ---
# Esta lista simula lo que luego traeremos de las otras hojas
datos_ejemplo = [
    {"tipo": "FIN / OBJETIVO GENERAL", "objetivo": "Ejemplo de Objetivo General traído de la Hoja 7", "indicador": "Indicador automático de la Hoja 11", "meta": "Dato de meta", "supuesto": "Supuesto de la Hoja 12"},
    {"tipo": "PROPÓSITO / ESPECÍFICO", "objetivo": "Ejemplo de Objetivo Específico", "indicador": "Indicador calculado", "meta": "Dato de meta", "supuesto": "Supuesto de riesgo"},
    {"tipo": "COMPONENTE / PRODUCTO", "objetivo": "Resultado o producto esperado", "indicador": "Indicador de producto", "meta": "Dato de meta", "supuesto": "Condición externa"},
    {"tipo": "ACTIVIDAD", "objetivo": "Acción principal a ejecutar", "indicador": "Presupuesto / Avance", "meta": "Dato de meta", "supuesto": "Disponibilidad de recursos"}
]

# --- RENDERIZADO DE BLOQUES IMPACTANTES ---

for fila in datos_ejemplo:
    with st.container():
        st.markdown(f"""
            <div class="card-mml">
                <div class="tipo-badge">{fila['tipo']}</div>
                <div style="display: flex; flex-direction: row; gap: 15px;">
                    <div style="flex: 2;">
                        <div class="col-title">🎯 Objetivo</div>
                        <div class="col-content">{fila['objetivo']}</div>
                    </div>
                    <div style="flex: 1.5;">
                        <div class="col-title">📊 Indicador</div>
                        <div class="col-content">{fila['indicador']}</div>
                    </div>
                    <div style="flex: 1;">
                        <div class="col-title">🏁 Meta</div>
                        <div class="col-content">{fila['meta']}</div>
                    </div>
                    <div style="flex: 1.5;">
                        <div class="col-title">🛡️ Supuestos</div>
                        <div class="col-content">{fila['supuesto']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- BOTONES DE ACCIÓN ---
st.divider()
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🖨️ Exportar MML"):
        st.info("Función de exportación lista para configurar.")
