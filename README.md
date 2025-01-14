# Laboratorio 3 - Sistemas Distribuidos

**Autores:**

- Mauricio Valdés G.
- Mauricio Vicencio P.

**Descripción:**

# Sistema Distribuido para Gestión de Tráfico Vehicular en Santiago de Chile

Este proyecto es un sistema distribuido diseñado para gestionar el tráfico vehicular de Santiago de Chile mediante técnicas de aprendizaje automático. Utiliza una simulación en **SUMO (Simulation of Urban Mobility)** y se basa en una arquitectura distribuida con comunicación entre sensores, nodos locales y un nodo central, todo implementado utilizando **Docker** y **Mosquitto MQTT**.

## Arquitectura del Sistema

El sistema está compuesto por:

- **Sensores simulados en SUMO:** Capturan datos del tráfico en tiempo real y los envían a los nodos locales.
- **Nodos locales:** Se comunican con los sensores y procesan los datos recibidos utilizando la metaheurística **ACO (Ant Colony Optimization)** para tomar decisiones sobre la gestión de semáforos.
- **Nodo central:** Centraliza la información proveniente de los nodos locales y realiza una gestión global del tráfico con base en los datos recibidos.

Toda la comunicación entre estos componentes se realiza a través de un **broker Mosquitto MQTT**, con mensajes securizados y persistentes.

## Funcionalidades Implementadas

1. **Recolección de datos desde sensores simulados con SUMO.**
2. **Comunicación distribuida mediante Mosquitto MQTT:**
   - Los sensores envían los datos a los nodos locales.
   - Los nodos locales procesan y reenvían decisiones al nodo central.
3. **Toma de decisiones en nodos locales usando ACO (Ant Colony Optimization).**
4. **Monitoreo de sensores y nodos.**
5. **Seguridad en la comunicación (TLS/SSL):**
   - El broker utiliza el puerto **8883** con seguridad habilitada.
6. **Persistencia de mensajes:**
   - Los mensajes que no se logran enviar se almacenan temporalmente en la base de datos del broker.
7. **Calidad de Servicio (QoS):**
   - Garantía de entrega con al menos una recepción confirmada.
8. **Monitoreo del Broker:**
   - Métricas clave como cantidad de mensajes enviados/recibidos, latencia y nodos conectados.

## Tecnologías Utilizadas

- **SUMO (Simulation of Urban Mobility)**: Simulación del tráfico.
- **Mosquitto MQTT Broker**: Comunicación entre nodos.
- **Docker y Docker Compose**: Para la contenerización y despliegue del sistema.
- **Python**: Lenguaje principal para la implementación de los nodos.
- **Prometheus y Grafana**: Monitoreo y visualización de métricas.

## Requerimientos previos

- **Sumo (Simulation of Urban Mobility)**: Es necesario tener instalado SUMO, para su ejecución local.

## Instalación y Despliegue

1. Clona este repositorio:

   ```bash
   git clone https://github.com/MauricioValdesG/Lab2-Distri.git

   ```

2. Inicia la simulación:

   ```bash
   sumo-gui.exe --remote-port 8813 --xml-validation auto --num-clients 4 -c "[Ruta al archivo .sumocfg]"

   ```

3. Inicio de los contendores:
   ```bash
   docker-compose up --build
   ```
