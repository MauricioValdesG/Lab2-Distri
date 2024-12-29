import traci
import paho.mqtt.client as mqtt
import time

BROKER = "localhost"  # Dirección del broker MQTT
PORT = 1883  # Puerto por defecto para MQTT
TOPIC = "sensor/data"

# Configuración del cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT, 60)

def send_data(sensor_id, data):
    message = {
        "sensor_id": sensor_id,
        "data": data
    }
    mqtt_client.publish(TOPIC, str(message))

def main():
    traci.start(["sumo-gui", "-c", "test.sumocfg"])

    sensor_ids = [
        "detector_0", "detector_1", "detector_2", "detector_3",
        "detector_4", "detector_5", "detector_6", "detector_7"
    ]

    step = 0
    while step < 1000:  # Configurar la cantidad de pasos deseada
        traci.simulationStep()

        # Leer datos de cada sensor
        for sensor_id in sensor_ids:
            try:
                vehicle_count = traci.inductionloop.getLastStepVehicleNumber(sensor_id)
                send_data(sensor_id, {"vehicle_count": vehicle_count})
            except traci.TraCIException as e:
                print(f"Error al leer el sensor {sensor_id}: {e}")

        step += 1
        time.sleep(0.1)  # Reducir velocidad para simular intervalos reales

    traci.close()

if __name__ == "__main__":
    main()
