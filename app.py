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

# --- configuración de la página ---
st.set_page_config(
    page_title="Asistente de RH - Análisis de CVs",
    page_icon="👔",
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

# --- estilos custom (minimalista/profesional) ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
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
    .tag-strength {
        background-color: #d4edda;
        color: #155724;
    }
    .tag-gap {
        background-color: #fff3cd;
        color: #856404;
    }
    .security-alert {
        padding: 10px;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        margin-top: 10px;
        font-weight: bold;
    }
    .spinner {
        border: 12px solid #f3f3f3;
        border-top: 12px solid #007bff;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .history-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
        display: flex;
        justify-content: space-between;
        align_items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .history-card-rejected {
        border: 2px solid #dc3545;
        background-color: #fff8f8;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    # Logo Image
    try:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
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

# --- UI Principal ---

if st.session_state["authentication_status"]:
    st.title("🤖 Asistente de RH - Analizador Inteligente")
    
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
    
    with tab2:
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
