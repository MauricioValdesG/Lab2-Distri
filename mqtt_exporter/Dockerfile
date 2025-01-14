# Usa una imagen base ligera de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY mqtt_exporter.py /app/

# Instalar dependencias
RUN pip install --no-cache-dir paho-mqtt prometheus_client

# Ejecutar el script
CMD ["python", "mqtt_exporter.py"]
