FROM python:3.9-slim

# Instalar dependencias necesarias para conectarse a CARLA
RUN pip install --no-cache-dir carla numpy

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el script al contenedor
COPY static_lidar_simulation.py .

# Ejecutar el script por defecto
CMD ["python", "static_lidar_simulation.py"]
