import sys

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update CSS to include CV parsing items
css_start = "/* Cards generic */"
css_end = "/* Footer */"
idx1 = text.find(css_start)
idx2 = text.find(css_end, idx1)

if idx1 != -1 and idx2 != -1:
    cv_css = '''/* Cards generic */
    .main-card {
        background-color: #FFFFFF;
        padding: 32px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E5E7EB;
        margin-top: 24px;
    }
    
    /* Active Vacancy Display */
    .vacancy-active-box {
        background-color: #F3F4F6;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 32px;
    }
    .vacancy-icon {
        background-color: #D1D5DB;
        padding: 8px;
        border-radius: 8px;
    }
    .vacancy-info h4 {
        margin: 0;
        font-weight: 600;
        color: #111827;
    }
    .vacancy-info p {
        margin: 0;
        font-size: 0.85rem;
        color: #6B7280;
    }
    
    /* Toggle Switch Container */
    .toggle-container {
        border-radius: 8px;
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        border: 1px solid #E5E7EB;
    }
    .toggle-active {
        background-color: #ECFDF5;
        border-color: #A7F3D0;
    }
    .toggle-inactive {
        background-color: #F9FAFB;
    }
    .toggle-text {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .toggle-text h4 {
        margin: 0;
        font-weight: 600;
        color: #111827;
    }
    .toggle-text p {
        margin: 0;
        font-size: 0.85rem;
        color: #6B7280;
    }
    /* Streamlit Toggle Override inside specific container */
    [data-testid="stToggle"] {
        margin-bottom: 0 !important;
    }
    
    /* API Error Alert */
    .api-alert {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 24px;
    }
    .api-alert h4 {
        margin: 0;
        font-weight: 600;
        color: #1E40AF;
        font-size: 0.95rem;
    }
    .api-alert p {
        margin: 0;
        font-size: 0.85rem;
        color: #DC2626;
        font-weight: 500;
    }
    
    /* Upload Box Override */
    [data-testid="stFileUploader"] {
        border: 1px dashed #D1D5DB !important;
        border-radius: 12px;
        background-color: #FAFAFA !important;
        padding: 32px 16px !important;
        text-align: center;
    }
    
    '''
    text = text[:idx1] + cv_css + text[idx2:]

# 2. Update Tab2 content
tab2_target = '''    with tab2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Cargar Documentos")
        vacancy_names = list(st.session_state['vacancies'].keys())
        
        if vacancy_names:
            selected_vacancy = st.selectbox("Selecciona Vacante a evaluar", vacancy_names)
            job_description = st.session_state['vacancies'][selected_vacancy]
        else:
            st.warning("👈 Define una vacante primero en la pestaña 'Definir Vacante'.")
            job_description = None
            
        uploaded_files = st.file_uploader("Arrastra y suelta los CVs (PDF)", type=["pdf"], accept_multiple_files=True)
        
        if st.button("Analizar Candidatos", type="primary", use_container_width=True):
             if not job_description:
                 st.error("⚠️ Debes seleccionar una vacante activa.")
             elif not uploaded_files:
                 st.error("⚠️ Debes subir al menos un archivo PDF.")
             elif not api_key:
                 st.error("❌ Por favor configura GEMINI_API_KEY en secrets.toml / entorno.")
             else:
                 st.subheader("Resultados del Análisis")
                 progress_bar = st.progress(0)
                 
                 for i, uploaded_file in enumerate(uploaded_files):
                     text = extract_text_from_pdf(uploaded_file)
                     if text:
                         status_placeholder = st.empty()
                         status_placeholder.info(f"Procesando {uploaded_file.name}...")
                         
                         result = evaluar_cv(text, job_description, api_key)
                         
                         status_placeholder.empty()
                         
                         candidate_name = result.get('name', uploaded_file.name)
                         
                         analysis_data = {
                             "name": candidate_name,
                             "vacancy": selected_vacancy if job_description else "General",
                             "score": result.get('score', 0),
                             "strengths": result.get('strengths', []),
                             "gaps": result.get('gaps', []),
                             "summary": result.get('summary', 'Sin resumen')
                         }
                         st.session_state['historial_candidatos'].append(analysis_data)
                         save_to_firestore(analysis_data, st.session_state.get("username", "Unknown"))
                         
                         st.success(f"Candidato: {candidate_name} | Score: {result.get('score', 0)}%")
                         st.write(result.get('summary', 'Sin resumen'))
                         
                     progress_bar.progress((i + 1) / len(uploaded_files))
                 
                 st.success("✅ Análisis Completado")
        st.markdown('</div>', unsafe_allow_html=True)'''

new_tab2 = '''    with tab2:
        # Título General de Tab (fuera del card principal, según screenshot pero integrado al flujo)
        
        # 1. Vacancy Info Header Box (outside main card)
        vacancy_names = list(st.session_state['vacancies'].keys())
        selected_vacancy = None
        job_description = None

        if vacancy_names:
            # For this UI design, we just auto-pick the top one or allow selecting invisibly
            # The mockup assumes "Active Vacancy", we will use the first one if not explicitly selected
            selected_vacancy = vacancy_names[-1] # Usually the most recent
            job_description = st.session_state['vacancies'][selected_vacancy]
            
            st.markdown(f"""
            <div class="vacancy-active-box">
                <div class="vacancy-icon">💼</div>
                <div class="vacancy-info">
                    <h4>{selected_vacancy}</h4>
                    <p>{job_description[:40]}...</p>
                    <span style="font-size: 0.75rem; background: #E5E7EB; padding: 2px 8px; border-radius: 12px; font-weight: 500;">Habilidades requeridas param.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("⚠️ Debes ir a 'Definir Vacante' primero y guardar una posición.")

        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Analizar CV con Gemini AI")
        if selected_vacancy:
            st.caption(f"Vacante actual: **{selected_vacancy}**")
        else:
            st.caption("Vacante actual: **Ninguna**")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Toggle and Alerts
        t_col1, t_col2 = st.columns([8, 2])
        
        # Using session state to maintain toggle visually
        if "gemini_active" not in st.session_state:
            st.session_state.gemini_active = False

        with t_col2:
            toggle_state = st.toggle("", key="gemini_active")
            
        with t_col1:
            if toggle_state:
                st.markdown("""
                <div class="toggle-container toggle-active">
                    <div class="toggle-text">
                        <span style="color: #059669; font-size: 1.2rem;">✨</span>
                        <div>
                            <h4>API de Gemini Activada</h4>
                            <p>Los CVs serán analizados con inteligencia artificial</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="toggle-container toggle-inactive">
                    <div class="toggle-text">
                        <span style="color: #9CA3AF; font-size: 1.2rem;">✨</span>
                        <div>
                            <h4>API de Gemini Desactivada</h4>
                            <p>Active la API para comenzar a analizar CVs</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if toggle_state and not api_key:
             st.markdown("""
             <div class="api-alert">
                 <span style="font-size: 1.2rem;">🔌</span>
                 <div>
                     <h4>API Key configurada:</h4>
                     <p>No configurada - Edita el archivo /src/app/config.ts o secrets.toml</p>
                 </div>
             </div>
             """, unsafe_allow_html=True)

        # 3. File Upload Area
        if toggle_state:
            st.markdown('<div style="width: 50%;">', unsafe_allow_html=True)
            uploaded_files = st.file_uploader("Cargar CV del Candidato", type=["pdf", "docx", "txt"], accept_multiple_files=False)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Analizar Candidato", type="secondary"):
                 if not uploaded_files:
                     st.error("Carga un archivo primero.")
                 elif not api_key:
                     st.error("Configura la API Key primero.")
                 elif not job_description:
                     st.error("Define una vacante primero.")
                 else:
                     with st.spinner("Analizando con Gemini AI..."):
                         text = extract_text_from_pdf(uploaded_files)
                         if text:
                             result = evaluar_cv(text, job_description, api_key)
                             candidate_name = result.get('name', uploaded_files.name)
                             
                             analysis_data = {
                                 "name": candidate_name,
                                 "vacancy": selected_vacancy,
                                 "score": result.get('score', 0),
                                 "strengths": result.get('strengths', []),
                                 "gaps": result.get('gaps', []),
                                 "summary": result.get('summary', 'Sin resumen')
                             }
                             st.session_state['historial_candidatos'].append(analysis_data)
                             save_to_firestore(analysis_data, st.session_state.get("username", "Unknown"))
                             
                             st.success(f"✅ Candidato: {candidate_name} | Score: {result.get('score', 0)}%")
                             st.write(result.get('summary', 'Sin resumen'))

        st.markdown('</div>', unsafe_allow_html=True)'''

text = text.replace(tab2_target, new_tab2)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Patch applied")
