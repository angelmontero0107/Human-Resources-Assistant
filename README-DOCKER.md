# 🐳 Despliegue con Docker - HR Assistant

## Requisitos Previos
- Docker instalado
- Docker Compose instalado (opcional, para usar docker-compose.yml)

## Método 1: Usando Docker directamente

### 1. Construir la imagen
```bash
docker build -t hr-assistant:latest .
```

### 2. Ejecutar el contenedor
```bash
docker run -d \
  --name hr-assistant \
  -p 8501:8501 \
  -v $(pwd)/.streamlit:/app/.streamlit \
  hr-assistant:latest
```

### 3. Acceder a la aplicación
Abre tu navegador en: `http://localhost:8501`

### 4. Detener el contenedor
```bash
docker stop hr-assistant
docker rm hr-assistant
```

## Método 2: Usando Docker Compose (Recomendado)

### 1. Levantar la aplicación
> ```bash
docker-compose up -d
```

### 2. Ver los logs
```bash
docker-compose logs -f
```

### 3. Detener la aplicación
```bash
docker-compose down
```

## Configuración de API Key

Asegúrate de que el archivo `.streamlit/secrets.toml` contenga tu API Key de Gemini:

```toml
GEMINI_API_KEY = "TU_API_KEY_AQUI"
```

## Notas Importantes

- El puerto expuesto por defecto es `8501`
- La aplicación se ejecuta en modo headless (sin interfaz gráfica)
- Los archivos se persisten a través del volumen montado en `.streamlit`
- Para actualizar la aplicación, reconstruye la imagen con `docker-compose build`

## Troubleshooting

### Error al conectar
Verifica que el puerto 8501 no esté en uso:
```bash
lsof -i :8501
```

### Ver logs del contenedor
```bash
docker logs hr-assistant
```

### Acceder al contenedor
```bash
docker exec -it hr-assistant /bin/bash
```
