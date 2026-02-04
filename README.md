# 🤖 Human Resources Assistant - Análisis Inteligente de CVs

Asistente de Recursos Humanos potenciado por **Google Gemini AI** para analizar CVs de candidatos y evaluar su compatibilidad con vacantes específicas.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Características

- 📄 **Análisis Inteligente de CVs** - Procesamiento automático de CVs en formato PDF
- 🎯 **Evaluación por Vacante** - Comparación directa con requisitos específicos del puesto
- 🔍 **Detección de Manipulación** - Identifica "keyword stuffing" y datos contradictorios
- 📊 **Sistema de Puntaje Ponderado** - Evaluación basada en criterios profesionales:
  - Experiencia Comprobable (50%)
  - Habilidades Técnicas y Proyectos (30%)
  - Certificaciones Oficiales (15%)
  - Habilidades Blandas (5%)
- 📈 **Historial de Candidatos** - Seguimiento de todas las evaluaciones realizadas
- 🐳 **Docker Ready** - Despliegue fácil con contenedores

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- API Key de Google Gemini ([Obtener aquí](https://ai.google.dev/))
- Docker (opcional, para deployment)

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/angelmontero0107/Human-Resources-Assistant.git
cd Human-Resources-Assistant
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar API Key**
```bash
mkdir .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Editar .streamlit/secrets.toml y agregar tu API Key
```

5. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

La aplicación estará disponible en: **http://localhost:8501**

## 🐳 Despliegue con Docker

### Usando Docker Compose (Recomendado)

```bash
# Configurar API Key en .streamlit/secrets.toml
docker-compose up -d
```

### Usando Docker directamente

```bash
docker build -t hr-assistant:latest .
docker run -d --name hr-assistant -p 8501:8501 \
  -v $(pwd)/.streamlit:/app/.streamlit \
  hr-assistant:latest
```

Ver más detalles en [README-DOCKER.md](./README-DOCKER.md)

## 📖 Uso

### 1. Configurar Vacante
- En la barra lateral, ingresa el **Título del Puesto**
- Define los **Requisitos Detallados** de la vacante
- Guarda la vacante

### 2. Cargar CVs
- Selecciona la vacante a evaluar
- Sube uno o varios CVs en formato **PDF**
- Haz clic en **"Analizar Candidatos"**

### 3. Revisar Resultados
- Visualiza el **score de compatibilidad** (0-100%)
- Revisa **fortalezas** y **brechas** identificadas
- Verifica **alertas de seguridad** si las hay
- Consulta el **historial** de evaluaciones

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Este proyecto usa una API Key de Google Gemini que **NO debe compartirse públicamente**.

- El archivo `.streamlit/secrets.toml` está en `.gitignore`
- Usa `.streamlit/secrets.toml.example` como plantilla
- **NUNCA** commits tu API Key al repositorio

## 🛠️ Tecnologías

- **[Streamlit](https://streamlit.io/)** - Framework web para Python
- **[Google Gemini AI](https://ai.google.dev/)** - Modelo de lenguaje para análisis
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** - Extracción de texto de PDFs
- **[Pandas](https://pandas.pydata.org/)** - Análisis de datos
- **[Docker](https://www.docker.com/)** - Contenedorización

## 📁 Estructura del Proyecto

```
Human-Resources-Assistant/
├── app.py                      # Aplicación principal
├── generate_cv.py              # Módulo de generación de CVs
├── requirements.txt            # Dependencias Python
├── requerimientos.txt          # Dependencias para Docker
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Orquestación Docker
├── .dockerignore              # Archivos excluidos del build
├── .gitignore                 # Archivos excluidos de Git
├── .streamlit/
│   ├── secrets.toml.example   # Plantilla de configuración
│   └── secrets.toml           # API Key (NO tracked)
├── README.md                  # Este archivo
└── README-DOCKER.md           # Guía de despliegue Docker
```

## 🌐 Despliegue en la Nube

Este proyecto está listo para desplegarse en:

- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Heroku**
- **DigitalOcean App Platform**
- Cualquier plataforma compatible con Docker

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas

- El modelo de IA puede identificar posible manipulación de datos
- Se recomienda realizar entrevistas adicionales para candidatos con score > 70
- Los CVs deben estar en formato PDF para un análisis óptimo

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👤 Autor

**Angel Montero**
- GitHub: [@angelmontero0107](https://github.com/angelmontero0107)

## 🙏 Agradecimientos

- Google por proporcionar Gemini AI
- Comunidad de Streamlit por el excelente framework
- Todos los contribuidores del proyecto

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!
