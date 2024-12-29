import os
import time
import paho.mqtt.client as mqtt
import traci  # Importar el módulo para interactuar con SUMO

# Configuración del nodo local
BROKER = "localhost"  # Permitir configurar el broker con una variable de entorno
PORT = 1883  # Puerto por defecto para MQTT
TOPIC = "traffic/sensor_data"  # Tópico para publicar datos procesados
NODE_NAME = os.getenv("NODE_NAME", "Unknown")  # Leer nombre del nodo desde las variables de entorno
SUMO_PORT = int(os.getenv("SUMO_PORT", 8813))  # Puerto de SUMO

def connect_to_sumo():
    """
    Conecta a SUMO mediante TraCI.
    """
    try:
        traci.init(SUMO_PORT)
        print(f"{NODE_NAME} conectado a SUMO en el puerto {SUMO_PORT}.")
    except Exception as e:
        print(f"Error al conectar a SUMO: {e}")
        raise

def get_sensor_data():
    """
    Obtiene datos de sensores de SUMO.
    """
    try:
        vehicle_ids = traci.vehicle.getIDList()
        vehicle_count = len(vehicle_ids)
        lidar_distances = [traci.vehicle.getPosition(veh_id)[0] for veh_id in vehicle_ids]
        timestamp = traci.simulation.getTime()

        return {
            "lidar_data": lidar_distances,
            "camera_data": {"vehicles_detected": vehicle_count},
            "timestamp": timestamp
        }
    except Exception as e:
        print(f"Error al obtener datos de SUMO: {e}")
        return None

def process_sensor_data(sensor_data):
    """
    Procesa los datos recibidos desde los sensores de SUMO.
    """
    lidar_distances = sensor_data.get("lidar_data", [])
    vehicle_count = sensor_data.get("camera_data", {}).get("vehicles_detected", 0)
    timestamp = sensor_data.get("timestamp", time.time())

    # Mejor lógica de procesamiento
    decision = "Low traffic" if vehicle_count <= 10 else "High traffic"
    avg_distance = sum(lidar_distances) / len(lidar_distances) if lidar_distances else float('inf')

    return {
        "node": NODE_NAME,
        "decision": decision,
        "average_distance": avg_distance,
        "vehicle_count": vehicle_count,
        "timestamp": timestamp
    }

def on_connect(client, userdata, flags, rc):
    """
    Callback ejecutado al conectarse al broker MQTT.
    """
    if rc == 0:
        print(f"{NODE_NAME} conectado al broker MQTT.")
    else:
        print(f"Error al conectar al broker MQTT: Código {rc}")

def publish_data(client, topic, data):
    """
    Publica los datos procesados en un tópico MQTT.
    """
    client.publish(topic, str(data))
    print(f"Datos publicados: {data}")

if __name__ == "__main__":
    client = mqtt.Client(protocol=mqtt.MQTTv311)  # Crear un cliente MQTT especificando el protocolo a utilizar
    client.on_connect = on_connect

    try:
        # Conectar al broker MQTT
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        # Conectar a SUMO
        connect_to_sumo()

        while True:
            # Obtener datos de sensores de SUMO
            sensor_data = get_sensor_data()
            if sensor_data:
                # Procesar los datos del sensor
                processed_data = process_sensor_data(sensor_data)

                # Publicar los datos procesados al tópico configurado
                publish_data(client, TOPIC, processed_data)

            time.sleep(1)  # Esperar 1 segundo antes de la siguiente iteración

    except KeyboardInterrupt:
        print("Desconectando del broker MQTT y SUMO...")
        client.loop_stop()
        client.disconnect()
        traci.close()
