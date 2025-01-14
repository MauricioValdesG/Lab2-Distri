import paho.mqtt.client as mqtt
import traci
import os
import time
import json

# Variables de entorno
SUMO_HOST = os.getenv("SUMO_HOST", "localhost")
SUMO_PORT = int(os.getenv("SUMO_PORT", 8813))
BROKER_ADDRESS = os.getenv("MQTT_BROKER_HOST", "mqtt")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPIC = os.getenv("TOPIC", "sensor/lidar/")
SENSOR_INDEX = int(os.getenv("SENSOR_INDEX", 0))
CLIENT_ORDER = int(os.getenv("CLIENT_ORDER", 0))

# Función para manejar conexión MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conexión exitosa al broker MQTT")
    else:
        print(f"Error en la conexión al broker MQTT: {rc}")

# Función para conectarse a SUMO
def connect_to_sumo():
    print(f"Conectando a SUMO en {SUMO_HOST}:{SUMO_PORT}")
    try:
        traci.init(port=SUMO_PORT, host=SUMO_HOST)
        traci.setOrder(CLIENT_ORDER)
        print(f"Conexión a SUMO exitosa con orden {CLIENT_ORDER}.")
    except Exception as e:
        print(f"Error al conectar con SUMO: {e}")
        exit(1)

# Función para seleccionar semáforo
def seleccionar_semaforo():
    traffic_light_ids = traci.trafficlight.getIDList()
    if SENSOR_INDEX >= len(traffic_light_ids):
        print(f"Error: No hay suficiente semáforos para el índice {SENSOR_INDEX}.")
        exit(1)
    return traffic_light_ids[SENSOR_INDEX]

# Función para obtener datos de tráfico diferenciado por carril
def get_traffic_data(traffic_light_id):
    incoming_lanes = []
    outgoing_lanes = []

    incoming_edges = traci.junction.getIncomingEdges(traffic_light_id)
    outgoing_edges = traci.junction.getOutgoingEdges(traffic_light_id)

    # Obtener carriles de entrada
    for edge_id in incoming_edges:
        incoming_lanes.extend([f"{edge_id}_{i}" for i in range(traci.edge.getLaneNumber(edge_id))])

    # Obtener carriles de salida
    for edge_id in outgoing_edges:
        outgoing_lanes.extend([f"{edge_id}_{i}" for i in range(traci.edge.getLaneNumber(edge_id))]) 

    # Calcular métricas por carril
    lane_data = []
    for lane_id in incoming_lanes:
        queue_length = traci.lane.getLastStepHaltingNumber(lane_id)
        inflow = traci.lane.getLastStepVehicleNumber(lane_id)
        lane_data.append({"lane_id": lane_id, "queue_length": queue_length, "inflow": inflow})

    for lane_id in outgoing_lanes:
        outflow = traci.lane.getLastStepVehicleNumber(lane_id)
        lane_data.append({"lane_id": lane_id, "outflow": outflow})
    
    return lane_data

def get_phases_from_sumo(traffic_light_id):
    return [phase.state for phase in traci.trafficlight.getAllProgramLogics(traffic_light_id)[0].getPhases()]
# Función principal para publicar datos
def run_simulation(client, traffic_light_id):
    try:
        step = 0
        print(f"Sensor asignado al semáforo: {traffic_light_id}")

        phases = get_phases_from_sumo(traffic_light_id)

        while step < 1000:
            traci.simulationStep()
            step += 1

            position = traci.junction.getPosition(traffic_light_id)
            lane_data = get_traffic_data(traffic_light_id)

            sensor_data = {
                "position": position,
                "lane_data": lane_data,
                "phases": phases
            }

            topic = f"{TOPIC}"
            if client.is_connected():
                result = client.publish(topic, json.dumps(sensor_data), qos=1, retain=True)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"Datos publicados correctamente en {topic}: {sensor_data}")
                else:
                    print(f"Error al publicar datos en {topic}: {result.rc}")
            else:
                print("Cliente MQTT no conectado. Reintentando...")
            time.sleep(0.001)

    except Exception as e:
        print(f"Error durante la simulación: {e}")
    finally:
        traci.close()
        print("Simulación finalizada y conexión cerrada.")

if __name__ == "__main__":
    connect_to_sumo()
    traffic_light_id = seleccionar_semaforo()

    client = mqtt.Client()
    client.tls_set(
        ca_certs="/certs/ca.crt",
        certfile="/certs/server.crt",
        keyfile="/certs/server.key"
    )
    client.on_connect = on_connect

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        client.loop_start()
        run_simulation(client, traffic_light_id)
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
