import streamlit as st
import os
import pdfplumber
import pandas as pd
from google import genai
from google.genai import types
import json
import time
import concurrent.futures
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from google.cloud import firestore
from datetime import datetime
import base64

# --- configuración de la página ---
st.set_page_config(
    page_title="TalentForge AI",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inicialización de Estado ---
if 'vacancies' not in st.session_state:
    st.session_state['vacancies'] = {}
if 'historial_candidatos' not in st.session_state:
    st.session_state['historial_candidatos'] = []

# --- Autenticación Setup ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    # preauthorized=config['preauthorized'] # Optional
)

# --- Firestore Setup ---
# Usar variable de entorno o credenciales por defecto
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    # Opción para desarrollo local si no hay auth configurada explícitamente, 
    # aunque Firestore requiere credenciales. 
    # Streamlit Cloud usualmente inyecta secretos o usa key files.
    pass

@st.cache_resource
def get_db():
    try:
        return firestore.Client()
    except Exception as e:
        return None

db = get_db()

# --- estilos custom (Figma Redesign) ---
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
    
    /* Footer */
    .app-footer {
        text-align: center;
        margin-top: 64px;
        color: #6B7280 !important;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Lectura de Logo Global ---
encoded_logo = ""
try:
    if os.path.exists("icon.png"):
        with open("icon.png", "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()
except:
    pass

# --- UI Principal ---

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
                st.session_state['vacancies'][v_title] = v_desc + "\n" + v_resp
                st.success(f"✅ Vacante '{v_title}' configurada.")
            else:
                st.error("Completa Título y Descripción")
                
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
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
        <div class="login-wrapper" style="min-height: auto; margin-top: 10vh; margin-bottom: 0;">
            <div class="login-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="#111827"/>
                    <path d="M16 17H22V19H16V17Z" fill="#111827"/>
                </svg>
            </div>
            <div class="login-header">
                <h1>Asistente de RH</h1>
                <p style="margin-bottom: 16px;">Inicia sesión para analizar candidatos</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <style>
            /* Target ONLY the deepest container protecting from recursive padding issues */
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) {
                background: #FFFFFF !important;
                padding: 40px 32px !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
                max-width: 440px !important;
                margin: -24px auto 0 auto !important;
                width: 100% !important;
            }
            /* Make the stForm transparent since the container is white */
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) [data-testid="stForm"] {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                box-shadow: none !important;
            }
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) [data-testid="stForm"] > div:last-child {
                border-top: 1px solid #E5E7EB;
                padding-top: 24px;
                margin-top: 24px;
            }
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) [data-testid="stButton"] button {
                 background-color: #0F172A !important; 
                 color: white !important;
                 border-radius: 8px !important;
                 width: 100%;
                 font-weight: 500 !important;
            }
            /* Hide default Login header from authenticator */
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) h1,
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) h2,
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) h3 {
                display: none;
            }
            /* Show our custom headers */
            div[data-testid="stVerticalBlock"]:has(.login-card-anchor):not(:has(div[data-testid="stVerticalBlock"]:has(.login-card-anchor))) .custom-login-header {
                display: block !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # We wrap the login inside our own UI container by just calling it here
        with st.container():
            st.markdown('<div class="login-card-anchor"></div>', unsafe_allow_html=True)
            st.markdown(
                '<h2 class="custom-login-header" style="font-size: 1.25rem; font-weight: 600; margin-bottom: 4px; color: #111827;">Iniciar Sesión</h2>'
                '<p class="custom-login-header" style="color: #6B7280; font-size: 0.9rem; margin-bottom: 24px;">Accede con tus credenciales de Recursos Humanos</p>',
                unsafe_allow_html=True
            )
            
            try:
                authenticator.login("main")
            except Exception as e:
                st.error(e)
                
            if st.session_state["authentication_status"] is False:
                 st.error('Usuario/Contraseña incorrecta')
                 
            # Footer in the login card
            st.markdown(
                '<div style="text-align: center; margin-top: 24px; color: #111827; font-weight: 500; font-size: 0.9rem;">Ver credenciales de demostración</div>',
                unsafe_allow_html=True
            )
