# Base de Python
FROM python:3.9-slim

# Crear el directorio de trabajo
WORKDIR /app

# Copiar el archivo del sensor al contenedor
COPY simulation_sensor.py /app/

# Instalar las dependencias necesarias
RUN pip install paho-mqtt numpy traci

# Comando por defecto para ejecutar el sensor
CMD ["python", "simulation_sensor.py"]
