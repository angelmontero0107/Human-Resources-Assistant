# Utilizar imagen base oficial de Python
FROM python:3.11-slim

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requerimientos.txt .

# Instalar dependencias del sistema necesarias para pdfplumber
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requerimientos.txt

# Copiar todo el código de la aplicación
COPY . .

# Exponer puerto de Streamlit
EXPOSE 8501

# Configurar Streamlit para producción
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
