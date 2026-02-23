# Dockerfile (raíz del proyecto)
FROM python:3.10-slim

WORKDIR /app/src

# Dependencias del sistema necesarias para compilación y red
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential gcc curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlas
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# SpaCy ya viene desde requirements.txt (evitamos descargar modelos grandes en deploy gratuito)

# Copiar el código fuente (lo colocamos en /app/src)
COPY src/ /app/src/

# Copiar datos y modelos
COPY data/ /app/data/
COPY models/ /app/models/
COPY frontend/ /app/frontend/

# Variables útiles
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Arrancar la app (compatible con plataformas que inyectan PORT, p.ej. Render)
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
  
