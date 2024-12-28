import os
import time
import paho.mqtt.client as mqtt
import simulation_sensor as sensor_sim

# Configuración del nodo local
BROKER = "localhost"
PORT = 1883 # Puerto por defecto para MQTT
TOPIC = "traffic/sensor_data" # Tópico para publicar datos al nodo central
NODE_NAME = os.getenv("NODE_NAME", "Unknown")  # Leer nombre del nodo desde las variables de entorno

def process_sensor_data(sensor_data): # Función para procesar datos del sensor

    lidar_distances = sensor_data["lidar_data"]
    vehicle_count = sensor_data["camera_data"]["vehicles_detected"]

    # Ejemplo de procesamiento simple para probar la comunicación entre los nodos
    if vehicle_count > 10:
        decision = "High traffic"
    else:
        decision = "Low traffic"
    # Devolver datos procesados
    return {
        "node": NODE_NAME,
        "decision": decision,
        "timestamp": sensor_data["timestamp"]
    }

def on_connect(client, userdata, flags, rc): # Función que se ejecuta al conectarse al broker MQTT
    if rc == 0:
        print(f"{NODE_NAME} conectado al broker MQTT.")
    else:
        print(f"Error al conectar al broker MQTT: Código {rc}")

def publish_data(client, topic, data): # Función para publicar datos en un tópico MQTT
    
    client.publish(topic, str(data))

if __name__ == "__main__":
    client = mqtt.Client(protocol=mqtt.MQTTv311) # Crear un cliente MQTT especificando el protocolo a utilizar (MQTTv3.1.1)
    client.on_connect = on_connect

    try:
        client.connect(BROKER, PORT, 60) # Conectar al broker MQTT
        client.loop_start()

        while True:
            # Obtener datos del sensor
            sensor_data = sensor_sim.generate_sensor_data()

            # Procesar datos del sensor
            processed_data = process_sensor_data(sensor_data)

            # Publicar datos procesados
            publish_data(client, TOPIC, processed_data)

            time.sleep(1)  # Publicar cada segundo

    except KeyboardInterrupt:
        print("Desconectando del broker MQTT...")
        client.loop_stop()
        client.disconnect()
