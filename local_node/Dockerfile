# Usar una imagen base ligera de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar curl y actualizar el sistema
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar los archivos necesarios al contenedor
COPY . /app

# Instalar las dependencias necesarias de Python
RUN pip install --no-cache-dir paho-mqtt flask flask_socketio flask_cors eventlet numpy

# Exponer el puerto usado por Flask
EXPOSE 5000

# Establecer las variables de entorno para evitar buffering
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el nodo local
CMD ["python", "simulation_local_node.py"]
