import sys

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update overall CSS
css_start = "# --- estilos custom (luz corporativo) ---"
css_end = '""", unsafe_allow_html=True)'
start_idx = text.find(css_start)
end_idx = text.find(css_end, start_idx) + len(css_end)

if start_idx == -1 or end_idx < start_idx:
    print("Error finding CSS block")
    sys.exit(1)

new_css = '''# --- estilos custom (Figma Redesign) ---
st.markdown("""
<style>
    /* Reset and Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #F0F4F8; /* Figma Background Color */
        color: #1F2937;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, label, .stCaption, p {
        color: #111827 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Hide default header */
    [data-testid="stHeader"] {
        display: none;
    }

    /* Top Navigation Header Card (Post-Login) */
    .top-header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding-bottom: 24px;
        margin-bottom: 32px;
    }
    
    .admin-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .admin-icon svg {
        width: 32px;
        height: 32px;
        fill: #111827;
    }
    
    .admin-text h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .admin-text p {
        margin: 0;
        font-size: 0.85rem;
        color: #6B7280 !important;
    }
    
    .title-center {
        text-align: center;
        flex-grow: 1;
    }
    
    .title-center h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        margin-bottom: 8px;
    }
    
    .title-center p {
        color: #6B7280 !important;
        font-size: 1rem;
    }

    .logout-btn-container button {
        background-color: transparent !important;
        border: 1px solid #D1D5DB !important;
        color: #111827 !important;
        font-weight: 500 !important;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px !important;
        border-radius: 6px !important;
    }

    /* Tabs / Togles as Pills */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 12px;
        background-color: #F3F4F6;
        padding: 4px;
        border-radius: 999px;
        display: inline-flex;
        margin: 0 auto;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: transparent;
        border-radius: 999px !important;
        color: #4B5563;
        font-weight: 500;
        padding: 0 24px;
        border-bottom: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-weight: 600;
        border-bottom: none !important;
    }

    /* Forms & Inputs */
    .stTextInput > div > div, 
    .stTextArea > div > div, 
    .stNumberInput > div > div {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
    }
    .stTextInput input, .stTextArea textarea {
        color: #111827 !important;
    }
    
    /* Login Specific Container */
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
    }
    
    .login-icon {
        width: 64px;
        height: 64px;
        background-color: #E5E7EB;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 24px;
    }
    
    .login-header h1 {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 8px;
    }
    
    .login-header p {
        color: #6B7280 !important;
        text-align: center;
        margin-bottom: 32px;
        font-size: 1rem;
    }
    
    /* Login Card Box */
    .login-card {
        background: #FFFFFF;
        padding: 32px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        width: 100%;
        max-width: 440px;
    }
    .login-card h2 {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .login-card p {
        color: #6B7280 !important;
        font-size: 0.9rem;
        margin-bottom: 24px;
    }

    /* Primary Buttons Form */
    div.stButton > button[kind="primary"] {
        background-color: #0F172A !important; 
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        width: 100%;
        padding: 8px 16px !important;
        margin-top: 16px;
    }
    
    /* Normal Secondary Buttons */
    div.stButton > button[kind="secondary"] {
        background-color: #6B7280 !important; 
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        width: 100%;
        padding: 8px 16px !important;
    }

    /* Cards generic */
    .main-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E5E7EB;
        margin-top: 24px;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        margin-top: 64px;
        color: #6B7280 !important;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)'''

text = text[:start_idx] + new_css + text[end_idx:]

# 2. Remove Sidebar
sidebar_start = "# --- Sidebar ---"
sidebar_end = "# --- Lectura de Logo Global ---"
s_idx = text.find(sidebar_start)
e_idx = text.find(sidebar_end)

if s_idx != -1 and e_idx != -1:
    text = text[:s_idx] + "\n" + text[e_idx:]


# 3. Restructure UI Principal
ui_start = '# --- UI Principal ---'
ui_idx = text.find(ui_start)

new_ui = '''# --- UI Principal ---

# Intentar leer API Key desde entorno
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except: ...

if st.session_state["authentication_status"]:
    # --- POST LOGIN VIEW ---
    st.markdown("""
        <div class="top-header-container">
            <div class="admin-info">
                <div class="admin-icon">
                    <svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                </div>
                <div class="admin-text">
                    <h3>Administrador RH</h3>
                    <p>Administrador</p>
                </div>
            </div>
            
            <div class="title-center">
                <h1>Asistente de Recursos Humanos</h1>
                <p>Analiza CVs de candidatos con Gemini AI y encuentra la coincidencia perfecta</p>
            </div>
            
            <div class="logout-btn-container" style="visibility: hidden;">
                <!-- Placeholder para el layout flexbox en HTML crudo -->
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Renderizamos el botón de logout de streamlit usando layout de columnas para colocarlo a la derecha (hack)
    _, col_logout = st.columns([8, 1])
    with col_logout:
        # Streamlit-authenticator logout logic if we want a manual button, otherwise use generic:
        authenticator.logout("Cerrar Sesión", "main")

    # Navigation Toggle
    st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["💼 Definir Vacante", "📄 Analizar CVs"])
    st.markdown('</div>', unsafe_allow_html=True)

    with tab1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Definir Vacante")
        st.caption("Complete los detalles de la posición para analizar candidatos")
        
        v_title = st.text_input("Título del Puesto *", placeholder="Ej: Desarrollador Full Stack Senior")
        v_desc = st.text_area("Descripción del Puesto *", placeholder="Describa el rol, las funciones principales y el perfil ideal...", height=120)
        v_resp = st.text_area("Responsabilidades", placeholder="Liste las responsabilidades clave del puesto...", height=100)
        
        col_exp, col_edu = st.columns(2)
        with col_exp:
            v_exp = st.number_input("Años de Experiencia", min_value=0, step=1, value=0)
        with col_edu:
            v_edu = st.text_input("Educación Requerida", placeholder="Ej: Ingeniería en Sistemas")
            
        col_hab_input, col_hab_btn = st.columns([4, 1])
        with col_hab_input:
            v_hab = st.text_input("Habilidades Requeridas *", placeholder="Escriba una habilidad y presione Agregar")
        with col_hab_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("+ Agregar", use_container_width=True, type="primary") # Assuming we want dark button
            
        # Para propósito del demo de guardado
        if st.button("Guardar Vacante", type="secondary", use_container_width=True): # Gray button based on Figma
            if v_title and v_desc:
                st.session_state['vacancies'][v_title] = v_desc + "\\n" + v_resp
                st.success(f"✅ Vacante '{v_title}' configurada.")
            else:
                st.error("Completa Título y Descripción")
                
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
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
        st.markdown('</div>', unsafe_allow_html=True)

    # Global footer
    st.markdown('<div class="app-footer">🤖 Potenciado por Google Gemini AI para análisis inteligente de candidatos</div>', unsafe_allow_html=True)

elif st.session_state["authentication_status"] is False:
    # Error message rendered where the login widget would be (see exact same login code below for standard structure, but the stauth widget handles its own error messages)
    pass
    
# LOGIN VIEW RENDERING
if not st.session_state["authentication_status"]:
    con1, con2, con3 = st.columns([1, 2, 1])
    with con2:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="#111827"/>
                    <path d="M16 17H22V19H16V17Z" fill="#111827"/>
                </svg>
            </div>
            <div class="login-header">
                <h1>Asistente de RH</h1>
                <p>Inicia sesión para analizar candidatos</p>
            </div>
            
            <div class="login-card">
                <h2>Iniciar Sesión</h2>
                <p>Accede con tus credenciales de Recursos Humanos</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Override the streamlit authenticator specific CSS to match Figma inside this container
        st.markdown("""
        <style>
            /* Hack to make the Streamlit Authenticator fit our login-card div */
            [data-testid="stForm"] {
                background: #FFFFFF !important;
                border: none !important;
                padding: 0 !important;
                box-shadow: none !important;
            }
            [data-testid="stForm"] > div:last-child {
                border-top: 1px solid #E5E7EB;
                padding-top: 24px;
                margin-top: 24px;
            }
            [data-testid="stForm"] div[data-testid="stButton"] button {
                 background-color: #0F172A !important; 
                 color: white !important;
                 border-radius: 8px !important;
                 width: 100%;
                 font-weight: 500 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # We wrap the login inside our own UI container by just calling it here
        # Note: the widget will create its own Form.
        try:
            authenticator.login("main")
        except Exception as e:
            st.error(e)
            
        if st.session_state["authentication_status"] is False:
             st.error('Usuario/Contraseña incorrecta')
             
        # Footer in the login card
        st.markdown("""
        <div style="text-align: center; margin-top: 24px; color: #111827; font-weight: 500; font-size: 0.9rem;">
            Ver credenciales de demostración
        </div>
        </div>
        """, unsafe_allow_html=True)
'''

text = text[:ui_idx] + new_ui

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Patch applied.")
