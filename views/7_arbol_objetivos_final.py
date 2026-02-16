# --- SIDEBAR ---
with st.sidebar:
    st.header("➕ Gestión de Fichas")
    tipo_sel = st.selectbox("Sección:", list(CONFIG_PROB.keys()))
    
    with st.form("crear_ficha", clear_on_submit=True):
        texto_input = st.text_area("Descripción:")
        padre_asociado = None
        
        # Validación para secciones que requieren un padre (Indirectas)
        if "Indirect" in tipo_sel:
            p_key = "Efectos Directos" if "Efecto" in tipo_sel else "Causas Directas"
            
            # SOLUCIÓN AL TYPEERROR: 
            # Filtramos la lista para asegurar que 'it' sea un diccionario y tenga la llave 'texto'
            lista_raw = st.session_state.get('arbol_tarjetas', {}).get(p_key, [])
            opciones = [it['texto'] for it in lista_raw if isinstance(it, dict) and 'texto' in it]
            
            if opciones: 
                padre_asociado = st.selectbox("Vincular a:", opciones)
            else:
                st.warning(f"⚠️ Primero cree {p_key} para poder vincular esta ficha.")
        
        # Botón de generación
        generar = st.form_submit_button("Generar")
        
        if generar and texto_input:
            nueva = {"texto": texto_input, "id_unico": str(uuid.uuid4())}
            if padre_asociado: 
                nueva["padre"] = padre_asociado
            
            # Lógica de guardado en el estado local
            if tipo_sel == "Problema Principal": 
                st.session_state['arbol_tarjetas'][tipo_sel] = [nueva]
            else: 
                # Inicializar la sección si no existe por algún error de carga
                if tipo_sel not in st.session_state['arbol_tarjetas']:
                    st.session_state['arbol_tarjetas'][tipo_sel] = []
                st.session_state['arbol_tarjetas'][tipo_sel].append(nueva)
            
            guardar_datos_nube()
            st.rerun()

    st.divider()
    grafo = generar_grafo_problemas()
    if grafo: 
        st.download_button("🖼️ Descargar PNG", data=grafo.pipe(format='png'), file_name="arbol.png", use_container_width=True)
