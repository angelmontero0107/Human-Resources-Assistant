import sys
import os
import base64

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Replace CSS
css_start = "# --- estilos custom (minimalista/profesional) ---"
css_end = '""", unsafe_allow_html=True)'
start_idx = text.find(css_start)
end_idx = text.find(css_end, start_idx) + len(css_end)

if start_idx == -1 or end_idx < start_idx:
    print("Error finding CSS block")
    sys.exit(1)

new_css = '''# --- estilos custom (luz corporativo) ---
st.markdown("""
<style>
    /* Reset and Typography */
    .stApp {
        background-color: #f8f9fa;
        color: #333333;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, label, .stCaption {
        color: #1F2937 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Top Navigation Header Card */
    .top-header-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 12px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .top-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .top-header-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: #111827;
        margin: 0;
        line-height: 1.2;
    }
    .top-header-subtitle {
        font-size: 0.8rem;
        color: #6B7280;
        margin: 0;
    }
    .top-header-button {
        border: 1px solid #0284C7;
        background-color: transparent;
        color: #0284C7;
        padding: 6px 16px;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 600;
    }

    /* Sidebar Constraints */
    [data-testid="stSidebar"] {
        background-color: #1F2937;
        border-right: 1px solid #374151;
    }
    [data-testid="stSidebar"] * {
        color: #F9FAFB !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div, 
    [data-testid="stSidebar"] .stTextArea > div > div {
        background-color: #374151 !important;
        border: 1px solid #4B5563;
    }
    [data-testid="stSidebar"] .stTextInput input, 
    [data-testid="stSidebar"] .stTextArea textarea {
        color: #F9FAFB !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: #374151 !important;
        color: #F9FAFB !important;
        border-radius: 4px;
    }
    
    /* Layout Containers for Sections */
    .section-block {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 16px;
        margin-top: 8px;
        margin-bottom: 32px;
        border: 1px solid #E5E7EB;
        color: #4B5563;
        font-size: 0.95rem;
    }

    /* Primary Buttons */
    div.stButton > button:first-child[data-testid="baseButton-primary"] {
        background-color: #0284C7; 
        color: white !important;
        border: none;
        font-weight: 600;
    }

    /* Metrics & History Cards (Light App) */
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #E5E7EB;
    }
    .history-card {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #FFFFFF;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .history-card-rejected {
        border-left: 4px solid #EF4444;
    }
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        margin-right: 5px;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .tag-strength { background-color: #D1FAE5; color: #065F46 !important; }
    .tag-gap { background-color: #FEF3C7; color: #92400E !important; }

</style>
""", unsafe_allow_html=True)'''

text = text[:start_idx] + new_css + text[end_idx:]

# 2. Add global logo reading explicitly before UI UI Principal
imports_end = "# --- UI Principal ---\n"
imports_idx = text.find(imports_end)
if imports_idx != -1:
    global_logo = """
# --- Lectura de Logo Global ---
encoded_logo = ""
try:
    if os.path.exists("icon.png"):
        with open("icon.png", "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()
except:
    pass

"""
    text = text[:imports_idx] + global_logo + text[imports_idx:]

# 3. Replace the UI block logic
ui_target = """if st.session_state["authentication_status"]:
    # Nueva Cabecera con Branding
    col_icon, col_title = st.columns([1, 8], gap="small")
    with col_icon:
        st.image("icon.png", width=60)
    with col_title:
        st.title("TalentForge AI")
    
    tab1, tab2 = st.tabs(["🔍 Nuevo Análisis", "📂 Historial Cloud"])

    with tab1:
        st.markdown("Sube los CVs de los candidatos y define la vacante para obtener un análisis potenciado por **Google Gemini**.")

        # --- Fila 1: Layout en 2 Columnas ---
        row1_col1, row1_col2 = st.columns(2)

        # Columna Izquierda: Vacante Activa
        with row1_col1:
            with st.container(border=True):
                st.subheader("1. Vacante Activa")
                vacancy_names = list(st.session_state['vacancies'].keys())
                
                if vacancy_names:
                    selected_vacancy = st.selectbox("Selecciona Vacante", vacancy_names)
                    job_description = st.session_state['vacancies'][selected_vacancy]
                    st.success(f"**Puesto Seleccionado:** {selected_vacancy}")
                    st.caption(f"Requisitos cargados: {len(job_description)} caracteres.")
                    with st.expander("Ver descripción completa"):
                        st.write(job_description)
                else:
                    st.warning("👈 Agrega una vacante en la barra lateral para comenzar.")
                    job_description = None
        
        # Columna Derecha: Carga y Acción
        with row1_col2:
            with st.container(border=True):
                st.subheader("2. Cargar Candidatos")
                uploaded_files = st.file_uploader("Arrastra y suelta los CVs (PDF)", type=["pdf"], accept_multiple_files=True)
                
                st.markdown("###") # Espaciado visual
                analyze_btn = st.button("Analizar Candidatos", type="primary", use_container_width=True)"""

ui_replacement = """if st.session_state["authentication_status"]:
    # --- Top Navigation Navbar ---
    img_tag = f'<img src="data:image/png;base64,{encoded_logo}" style="width: 28px; height: 28px; object-fit: contain;" alt="Logo">' if encoded_logo else '<span>💠</span>'
    st.markdown(f'''
        <div class="top-header-card">
            <div class="top-header-left">
                {img_tag}
                <div>
                    <h1 class="top-header-title">TalentForge AI</h1>
                    <p class="top-header-subtitle">Smart Recruitment Solutions</p>
                </div>
            </div>
            <div class="top-header-button">logo.png</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Main Title Area
    st.markdown("<h2 style='margin-bottom: 0;'>1 Asistente de RH - Analizador Inteligente</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280; font-size: 14px; margin-top: 5px; margin-bottom: 30px;'>Fissat Qealyles Oloow' (titrie)</p>", unsafe_allow_html=True)

    # --- Fila 1: Layout en Secciones Apiladas ---
    
    # Columna Izquierda: Vacante Activa
    st.markdown("<h3 style='margin-bottom: 10px; font-size: 1.3rem;'>1. Vacante Activa</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        vacancy_names = list(st.session_state['vacancies'].keys())
        
        if vacancy_names:
            selected_vacancy = st.selectbox("Selecciona Vacante", vacancy_names)
            job_description = st.session_state['vacancies'][selected_vacancy]
            st.success(f"**Puesto Seleccionado:** {selected_vacancy}")
            st.caption(f"Requisitos cargados: {len(job_description)} caracteres.")
            with st.expander("Ver descripción completa"):
                st.write(job_description)
        else:
            st.warning("👈 Agrega una vacante en la barra lateral para comenzar.")
            job_description = None
    
    # Columna Derecha: Carga y Acción
    st.markdown("<h3 style='margin-top: 20px; margin-bottom: 10px; font-size: 1.3rem;'>2. Cargar Candidatos</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        st.info("TalentForge AI evalúa rápidamente los perfiles de los candidatos. Selecciona tus archivos PDF para iniciar el análisis automático.")
        uploaded_files = st.file_uploader("Arrastra y suelta los CVs (PDF)", type=["pdf"], accept_multiple_files=True)
        
        st.markdown("###") # Espaciado visual
        analyze_btn = st.button("Analizar Candidatos", type="primary", use_container_width=True)"""

text = text.replace(ui_target, ui_replacement)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Patch applied.")
