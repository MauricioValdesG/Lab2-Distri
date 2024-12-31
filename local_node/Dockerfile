FROM python:3.9-slim

# Crear el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY simulation_local_node.py /app/

# Instalar las dependencias necesarias
RUN pip install paho-mqtt numpy traci

# Comando para ejecutar el nodo local
CMD ["python", "simulation_local_node.py"]
