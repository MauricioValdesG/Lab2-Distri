FROM ubuntu:20.04

# Evitar interacción manual con tzdata
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Instalar SUMO y dependencias necesarias para la GUI
RUN apt-get update && apt-get install -y \
    sumo sumo-tools sumo-doc python3 python3-pip x11-apps && \
    pip3 install traci && \
    apt-get clean

# Crear un directorio de trabajo
WORKDIR /sumo

# Copiar los archivos del proyecto
COPY ./sumo_examples /sumo/examples

# Comando por defecto para ejecutar SUMO con GUI y el ejemplo seleccionado
CMD ["sumo-gui", "-c", "/sumo/examples/test.sumocfg"]
