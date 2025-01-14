FROM python:3.9-slim

# Crear el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY simulation_central_node.py /app/

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir paho-mqtt flask flask_socketio flask_cors eventlet

# Exponer el puerto usado por Flask
EXPOSE 5000

# Establecer las variables de entorno para evitar buffering
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el nodo central
CMD ["python", "simulation_central_node.py"]