# Imagen base
FROM python:3.9-slim

# Directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir flask flask-socketio eventlet paho-mqtt flask_cors

# Exponer el puerto
EXPOSE 5001

# Comando por defecto
CMD ["python", "simulation_monitoring_node.py"]
