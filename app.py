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

# --- estilos custom (luz corporativo) ---
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
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #F9FAFB !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div, 
    [data-testid="stSidebar"] .stTextArea > div > div {
        background-color: #374151 !important;
        border: 1px solid #4B5563 !important;
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
    [data-testid="stSidebar"] div.stButton > button {
        background-color: #374151 !important;
        color: #F9FAFB !important;
        border: 1px solid #4B5563 !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #4B5563 !important;
        border: 1px solid #9CA3AF !important;
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
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    # Logo Image con ajuste de contraste y tamaño
    try:
        if os.path.exists("logo.png"):
            # Leer imagen para base64
            with open("logo.png", "rb") as f:
                data = f.read()
            encoded_image = base64.b64encode(data).decode()
            
            st.markdown(
                f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05); 
                    padding: 15px; 
                    border-radius: 12px; 
                    margin-bottom: 5px; 
                    text-align: center;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                ">
                    <img src="data:image/png;base64,{encoded_image}" style="width: 180px; max-width: 100%; filter: drop-shadow(0px 0px 5px rgba(255, 255, 255, 0.5));">
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.title("🤖 Asistente de RH")
    except Exception:
        # Fallback seguro para evitar error disclosure
        st.title("🤖 Asistente de RH")

    st.markdown("---")

    # Login Widget
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state["authentication_status"]:
        st.write(f'Hola *{st.session_state["name"]}*')
        st.markdown("---")
        
        st.header("Configuración")
        
        # 1. Intentar leer desde variables de entorno (Docker/Cloud)
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # 2. Si no hay variable de entorno, intentar leer secrets.toml (Local)
        if not api_key:
            try:
                if "GEMINI_API_KEY" in st.secrets:
                    api_key = st.secrets["GEMINI_API_KEY"]
                    st.success("🔑 API Key cargada desde configuración.")
            except Exception:
                # st.secrets falla si no existe el archivo secrets.toml
                pass

        if api_key:
            # Solo mostrar éxito si vino del entorno (el caso de secrets ya mostró mensaje arriba)
            if "GEMINI_API_KEY" not in os.environ: 
                 pass # Ya mostramos el mensaje en el bloque try
            else:
                 st.success("🔑 API Key cargada desde entorno.")
        else:
            st.error("⚠️ Falta confirmar API Key")
            st.info("Configura .env (Docker) o .streamlit/secrets.toml (Local)")

        if not api_key:
            st.warning("La aplicación requiere la clave para funcionar.")

        st.markdown("---")
        
        with st.expander("🏢 Configuración de Vacantes", expanded=True):
            v_title = st.text_input("Título del Puesto", placeholder="Ej. Senior Python Dev")
            v_desc = st.text_area("Requisitos Detallados", placeholder="Lista de habilidades...", height=150)
            
            if st.button("Guardar Vacante"):
                if v_title and v_desc:
                    st.session_state['vacancies'][v_title] = v_desc
                    st.success(f"✅ '{v_title}' guardada.")
                else:
                    st.error("❌ Completa ambos campos.")

        st.divider()
        authenticator.logout("Cerrar Sesión", "sidebar")
    
    elif st.session_state["authentication_status"] is False:
        st.error('Usuario/Contraseña incorrecta')
    elif st.session_state["authentication_status"] is None:
        st.markdown("---")
        st.info("👋 Si eres reclutador, inicia sesión arriba.")

# --- Funciones de Lógica ---
def extract_text_from_pdf(uploaded_file):
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error leyendo PDF: {e}")
        return None

def evaluar_cv(texto_cv, vacante, api_key):
    """
    Evalúa el CV usando el SDK Google GenAI (v1.0+) con Thinking Config.
    """
    if not api_key:
        return {"error": "Falta API Key"}

    client = genai.Client(api_key=api_key)

    # Prompt estructurado para JSON
    full_prompt = f"""
    Actúa como un reclutador experto. Analiza este CV para la vacante descrita.
    
    **VACANTE:**
    {vacante}

    **CV:**
    {texto_cv[:15000]}

    **SALIDA REQUERIDA (JSON):**
    Responde ÚNICAMENTE con un JSON válido con esta estructura:
    {{
        "name": "Nombre completo",
        "score": 0-100,
        "summary": "Resumen de 3 líneas",
        "strengths": ["f1", "f2", "f3"],
        "gaps": ["b1", "b2", "b3"],
        "security_warning": "Texto de alerta o null"
    }}
    """

    try:
        # Configuración "Thinking" + Instrucciones del Sistema (Pesos y Reglas)
        result = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="HIGH",
                ),
                system_instruction=types.Part.from_text(text="""Eres un Auditor de Talento experto. Tu misión es calificar CVs basándote estrictamente en los siguientes pesos:

        Experiencia Comprobable (50%): Evalúa años, relevancia de cargos y logros.

        Habilidades Técnicas y Proyectos (30%): Valida lenguajes, herramientas y proyectos prácticos mencionados.

        Certificaciones Oficiales (15%): Verifica certificados emitidos por instituciones o plataformas reconocidas.

        Habilidades Blandas (5%): Identifica rasgos como comunicación, liderazgo o trabajo en equipo.

    Reglas de Oro:

        Si detectas 'keyword stuffing' o información contradictoria, aplica una penalización del 50% al puntaje final y añade la etiqueta: 'ADVERTENCIA: Posible manipulación de datos' en security_warning.

        Si el puntaje es mayor a 70 pero detectas dudas en la veracidad de la experiencia, añade texto: 'Requiere segunda evaluación' en security_warning."""),
                response_mime_type="application/json", 
            ),
        )
        
        # Parsear respuesta
        return json.loads(result.text)

    except Exception as e:
        return {
            "name": "Error", 
            "score": 0, 
            "summary": f"Error técnico: {str(e)}", 
            "strengths": [], 
            "gaps": [], 
            "security_warning": "Fallo en API GenAI"
        }

def save_to_firestore(data, recruiter_username):
    """Guarda el resultado del análisis en Firestore"""
    if not db:
        st.warning("⚠️ Sin conexión a Firestore - Datos no persisten en la nube")
        return

    try:
        doc_ref = db.collection("analisis_cv").document()
        doc_ref.set({
            "candidate_name": data.get("name", "Desconocido"),
            "vacancy": data.get("vacancy", "General"),
            "score": data.get("score", 0),
            "summary": data.get("summary", ""),
            "recruiter": recruiter_username,
            "timestamp": datetime.now(),
            "strengths": data.get("strengths", []),
            "gaps": data.get("gaps", [])
        })
        return True
    except Exception as e:
        st.error(f"Error guardando en Firestore: {e}")
        return False

def load_history(recruiter_username=None):
    """Carga historial desde Firestore"""
    if not db:
        return []
    
    try:
        docs = db.collection("analisis_cv").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        history = []
        for doc in docs:
            d = doc.to_dict()
            # Opcional: Filtrar por reclutador si se desea privacidad por usuario
            # if recruiter_username and d.get("recruiter") != recruiter_username:
            #     continue
            history.append(d)
        return history
    except Exception as e:
        st.error(f"Error leyendo Firestore: {e}")
        return []


# --- Lectura de Logo Global ---
encoded_logo = ""
try:
    if os.path.exists("icon.png"):
        with open("icon.png", "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()
except:
    pass

# --- UI Principal ---

if st.session_state["authentication_status"]:
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
        analyze_btn = st.button("Analizar Candidatos", type="primary", use_container_width=True)

        # --- Fila 2: Resultados (Solo visible tras clic) ---
        if analyze_btn:
            st.divider()
            
            # Validación de entradas
            if not job_description:
                 st.error("⚠️ Debes seleccionar una vacante activa.")
            elif not uploaded_files:
                 st.error("⚠️ Debes subir al menos un archivo PDF.")
            elif not api_key:
                 st.error("❌ Por favor ingresa tu API Key en la barra lateral.")
            else:
                st.subheader("3. Resultados del Análisis")
                progress_bar = st.progress(0)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    # --- Lógica de Procesamiento ---
                    text = extract_text_from_pdf(uploaded_file)
                    
                    if text:
                        # UX: Mensajes de estado
                        status_messages = [
                            "Leyendo estructura del CV...",
                            "Extrayendo certificaciones y experiencia...",
                            "Validando coherencia de trayectoria...",
                            "Cruzando perfil con vacante..."
                        ]
                        
                        status_placeholder = st.empty()
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(evaluar_cv, text, job_description, api_key)
                            
                            # Animación de espera
                            for msg_text in status_messages:
                                if future.done():
                                    break
                                
                                status_placeholder.markdown(f"""
                                    <div style="text-align: center; margin: 20px 0;">
                                        <h3 style="color: #444;">{msg_text}</h3>
                                        <div class="spinner"></div>
                                    </div>
                                """, unsafe_allow_html=True)
                                time.sleep(1.5)
                            
                            # Esperar si falta poco
                            if not future.done():
                                status_placeholder.markdown("""
                                    <div style="text-align: center; margin: 20px 0;">
                                        <h3 style="color: #444;">Generando veredicto final...</h3>
                                        <div class="spinner"></div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            result = future.result()
                            status_placeholder.empty()
                        
                        candidate_name = result.get('name', uploaded_file.name)
                        
                        # Datos Estructurados
                        analysis_data = {
                            "name": candidate_name,
                            "vacancy": selected_vacancy,
                            "score": result.get('score', 0),
                            "strengths": result.get('strengths', []),
                            "gaps": result.get('gaps', []),
                            "summary": result.get('summary', 'Sin resumen')
                        }

                        # Persistencia
                        st.session_state['historial_candidatos'].append(analysis_data)
                        if not result.get('error'):
                            save_to_firestore(analysis_data, st.session_state.get("username", "Unknown"))
                        
                        # Renderizado de Tarjeta de Resultados
                        with st.container():
                            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                            
                            c_col1, c_col2 = st.columns([1, 3])
                            
                            with c_col1:
                                score = result.get('score', 0)
                                st.metric(label="Compatibilidad", value=f"{score}%")
                                st.progress(score/100)
                            
                            with c_col2:
                                st.markdown(f"### {candidate_name}")
                                st.markdown(f"**Resumen IA:**")
                                st.markdown(f"_{result.get('summary', 'Sin resumen')}_")
                                
                                st.markdown("---")
                                
                                s_col, g_col = st.columns(2)
                                with s_col:
                                    st.caption("✅ Fortalezas")
                                    for s in result.get('strengths', []):
                                        st.markdown(f'<span class="tag tag-strength">{s}</span>', unsafe_allow_html=True)
                                
                                with g_col:
                                    st.caption("⚠️ Brechas / A desarrollar")
                                    for g in result.get('gaps', []):
                                        st.markdown(f'<span class="tag tag-gap">{g}</span>', unsafe_allow_html=True)
                                
                                security_warning = result.get('security_warning')
                                if security_warning:
                                     st.markdown(f'<div class="security-alert">🚨 {security_warning}</div>', unsafe_allow_html=True)

                            st.markdown('</div>', unsafe_allow_html=True)
                        
                    else:
                         st.error(f"Error al leer el archivo: {uploaded_file.name}")
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.success("✅ Análisis Completado")

        # --- Sección Footer: Historial Session ---
        st.markdown("---")
        st.subheader("📜 Historial de Sesión Actual")

        if st.session_state['historial_candidatos']:
            # Mostrar más reciente primero
            for item in reversed(st.session_state['historial_candidatos']):
                is_rejected = item.get('score', 0) == 0
                card_class = "history-card history-card-rejected" if is_rejected else "history-card"
                status_badge = '<span style="color: #dc3545; font-weight: bold;">⛔ ACCESO DENEGADO</span>' if is_rejected else f"✅ Score: {item.get('score', 0)}%"
                
                tags_html = ""
                for s in item.get('strengths', [])[:2]:
                    tags_html += f'<span class="tag tag-strength">{s}</span>'
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="flex: 2;">
                        <div style="font-size: 1.1em; font-weight: bold;">{item['name']}</div>
                        <div style="color: #666; font-size: 0.9em;">Postulando a: {item['vacancy']}</div>
                    </div>
                    <div style="flex: 3; padding: 0 15px;">
                        {tags_html}
                    </div>
                    <div style="flex: 1; text-align: right;">
                        <div style="font-size: 1.2em;">{status_badge}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aún no hay evaluaciones registradas en esta sesión.")
    
    st.markdown("---")
    with st.expander("📂 Historial de Análisis Global", expanded=False):
        # Encabezado con columnas
        h_col1, h_col2 = st.columns([3, 1])
        
        with h_col1:
            st.subheader("📂 Historial de Análisis")
            st.caption("Registros persistentes recuperados de Google Firestore.")
        
        with h_col2:
            st.markdown("###") # Spacer para alineación vertical
            if st.button("🔄 Refrescar Tabla", use_container_width=True):
                st.session_state.pop('firestore_data', None)
                # El rerun es automático en Streamlit al interactuar

        # Cargar datos
        history_data = load_history()
        
        if history_data:
            df = pd.DataFrame(history_data)
            
            # Formatear columnas
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Reordenar columnas para mejor visualización
            cols = ['timestamp', 'candidate_name', 'score', 'vacancy', 'recruiter', 'summary']
            # Asegurar que existan
            cols = [c for c in cols if c in df.columns]
            
            st.dataframe(
                df[cols],
                column_config={
                    "timestamp": "Fecha",
                    "candidate_name": "Candidato",
                    "score": st.column_config.ProgressColumn("Puntaje", format="%d%%", min_value=0, max_value=100),
                    "vacancy": "Vacante",
                    "recruiter": "Reclutador",
                    "summary": "Resumen IA"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay registros en la base de datos o no hay conexión.")

else:
    # --- Vista Pública (Candidatos) ---
    st.title("🎓 Portal de Recepción de Candidatos")
    st.markdown("#### Envía tu hoja de vida a nuestro equipo de Talento Humano")
    
    c_uploaded_file = st.file_uploader("Carga tu CV (Formato PDF)", type=["pdf"])
    
    if c_uploaded_file:
        if st.button("Enviar Postulación"):
            # Simulación de envío
            with st.spinner("Enviando documento..."):
                time.sleep(1.5)
            st.success("✅ Tu CV ha sido recibido exitosamente. Te contactaremos pronto.")
            st.balloons()
    
    st.markdown("---")
    st.info("ℹ️ Este es un canal seguro. Tus datos serán tratados con confidencialidad.")
