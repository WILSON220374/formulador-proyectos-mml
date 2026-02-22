import streamlit as st
import os
import hashlib
from session_state import inicializar_session, conectar_db, cargar_datos_nube, guardar_datos_nube

# 1. Configuración de la página
st.set_page_config(page_title="JC Flow - Formulador MML", layout="wide")
inicializar_session()

# --- PURIFICACIÓN DE RAÍZ ---
if 'integrantes' in st.session_state and isinstance(st.session_state['integrantes'], list):
    st.session_state['integrantes'] = [p for p in st.session_state['integrantes'] if p is not None and isinstance(p, dict)]

# --- ESTILOS CSS GLOBALES (SOLO TÍTULOS DE FASE EN NEGRILLA) ---
st.markdown("""
    <style>
    div[data-testid="stSidebarNavItems"] > ul > li span[title^="Fase"] {
        font-weight: 900 !important;
        color: #1E3A8A !important;
        font-size: 14px !important;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)


# -----------------------------
# Seguridad: Hash de contraseñas (sin cambiar estructura DB)
# - Guardamos hash en el mismo campo "password" con prefijo: sha256$<hex>
# - Compatibilidad: si está en texto plano, valida y migra automáticamente a hash
# -----------------------------
def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _is_hashed(value: str) -> bool:
    return isinstance(value, str) and value.startswith("sha256$") and len(value) > len("sha256$")

def _make_hashed(password_plain: str) -> str:
    return f"sha256${_sha256_hex(password_plain)}"

def _verify_password(stored: str, provided_plain: str) -> bool:
    if not isinstance(stored, str):
        return False
    if _is_hashed(stored):
        return stored == _make_hashed(provided_plain)
    # Texto plano (compatibilidad)
    return stored == provided_plain


# -----------------------------
# Cierre de sesión limpio
# -----------------------------
def _logout_clean():
    # Mantener solo mínimos necesarios; todo lo demás se limpia para evitar arrastre entre grupos
    keep = {
        "autenticado": False,
    }
    keys = list(st.session_state.keys())
    for k in keys:
        try:
            st.session_state.pop(k, None)
        except Exception:
            pass
    for k, v in keep.items():
        st.session_state[k] = v
    inicializar_session()
    st.rerun()


# --- LÓGICA DE ACCESO (LOGIN) - IMAGEN IZQUIERDA / FORMULARIO DERECHA ---
if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        .titulo-acceso {
            font-size: 32px !important;
            font-weight: 800 !important;
            color: #4F8BFF;
            text-align: left;
            margin-bottom: 15px;
            margin-top: 10px;
        }
        .label-mediana {
            font-size: 16px !important;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 5px !important;
            margin-top: 10px !important;
            display: block;
        }
        input {
            font-size: 18px !important;
            height: 45px !important;
            border-radius: 10px !important;
        }
        div.stButton > button {
            font-size: 20px !important;
            height: 50px !important;
            font-weight: bold !important;
            background-color: #4F8BFF !important;
            border-radius: 12px !important;
            margin-top: 25px;
        }
        [data-testid="stVerticalBlock"] {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)

    col_img, col_form = st.columns([1.8, 1.2], gap="large")

    with col_img:
        if os.path.exists("unnamed.jpg"):
            st.image("unnamed.jpg", use_container_width=True)
        else:
            st.info("Carga la imagen 'unnamed.jpg' en la carpeta raíz.")

    with col_form:
        st.markdown('<div class="titulo-acceso"><br>ESPECIALIZACIÓN EN GERENCIA DE PROYECTOS</div>', unsafe_allow_html=True)

        with st.container(border=True):

            st.markdown('<label class="label-mediana">USUARIO</label>', unsafe_allow_html=True)
            u = st.text_input("u", label_visibility="collapsed")

            st.markdown('<label class="label-mediana">CONTRASEÑA</label>', unsafe_allow_html=True)
            p = st.text_input("p", type="password", label_visibility="collapsed")

            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
                try:
                    db = conectar_db()

                    # 1) Traer por user_id (no filtramos por password en SQL para soportar hash y migración)
                    res = db.table("proyectos").select("*").eq("user_id", u).limit(1).execute()
                    row = res.data[0] if res.data else None

                    if not row:
                        st.error("Credenciales incorrectas.")
                        st.stop()

                    stored_pw = row.get("password")

                    # 2) Verificación robusta (hash o texto plano)
                    if _verify_password(stored_pw, p):
                        # 3) Migración automática: si estaba en texto plano, lo convertimos a hash
                        if isinstance(stored_pw, str) and (not _is_hashed(stored_pw)):
                            try:
                                db.table("proyectos").update({"password": _make_hashed(p)}).eq("user_id", u).execute()
                            except Exception:
                                # Si falla la migración, no bloqueamos el login
                                pass

                        st.session_state['autenticado'] = True
                        st.session_state['usuario_id'] = u
                        cargar_datos_nube(u)
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")

                except Exception:
                    st.error("Error de conexión.")

    st.stop()

# --- SIDEBAR Y NAVEGACIÓN ---
with st.sidebar:
    st.header(f"👷 {st.session_state.get('usuario_id', '')}")

    integrantes = st.session_state.get('integrantes', [])
    if integrantes and isinstance(integrantes, list):
        for persona in integrantes:
            try:
                if persona and isinstance(persona, dict):
                    nombre_full = persona.get("Nombre Completo", "").strip()
                    if nombre_full:
                        nombre_pila = nombre_full.split()[0].upper()
                        st.markdown(f"**👤 {nombre_pila}**")
            except Exception:
                continue

    st.divider()
    if st.button("☁️ GUARDAR TODO EN NUBE", use_container_width=True, type="primary"):
        guardar_datos_nube()
        st.toast("✅ Avance guardado", icon="🚀")

    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        _logout_clean()

# --- DEFINICIÓN DE PÁGINAS POR SECCIONES ---
pg = st.navigation({
    "Configuración": [
        st.Page("views/0_equipo.py", title="Equipo", icon="👥")
    ],
    "Fase I: Identificación": [
        st.Page("views/1_diagnostico.py", title="1. Diagnóstico", icon="🧐"),
        st.Page("views/2_zona.py", title="2. Zona de Estudio", icon="🗺️"),
        st.Page("views/3_interesados.py", title="3. Interesados", icon="👥"),
    ],
    "Fase II: Definición de problemas y objetivos": [
        st.Page("views/4_arbol_problemas.py", title="4. Árbol de Problemas", icon="🌳"),
        st.Page("views/5_arbol_objetivos.py", title="5. Árbol de Objetivos", icon="🎯"),
        st.Page("views/6_alternativas.py", title="6. Análisis de Alternativas", icon="⚖️"),
        st.Page("views/7_arbol_objetivos_final.py", title="7. Árbol de Objetivos Final", icon="🚀"),
        st.Page("views/8_arbol_problemas_final.py", title="8. Árbol de Problemas Final", icon="🌳"),
    ],
    "Fase III: Análisis del problema": [
        st.Page("views/9_descripcion_zona.py", title="9. Descripción de la Zona", icon="🗺️"),
        st.Page("views/10_descripcion_problema.py", title="10. Descripción del Problema", icon="📝"),
    ],
    "Fase IV: Análisis de objetivos": [
        st.Page("views/11_indicadores.py", title="11. Indicadores", icon="📊"),
        st.Page("views/12_riesgos.py", title="12. Riesgos", icon="⚠️"),
        st.Page("views/13_matriz_marco_logico.py", title="13. Matriz Marco Lógico", icon="🧩"),
        st.Page("views/14_necesidad.py", title="14. Necesidad", icon="📌"),
        st.Page("views/15_producto.py", title="15. Producto", icon="🧾"),
        st.Page("views/16_reportes.py", title="16. Reportes", icon="📄"),
    ],
})

pg.run()
