FROM python:3.9-slim

# Crear el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY simulation_central_node.py /app/

# Instalar las dependencias necesarias
RUN pip install paho-mqtt

# Comando para ejecutar el nodo central
CMD ["python", "simulation_central_node.py"]