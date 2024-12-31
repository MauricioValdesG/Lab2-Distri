import paho.mqtt.client as mqtt
import json
import os

# Configuración del broker MQTT
BROKER_ADDRESS = os.getenv("MQTT_BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPIC = os.getenv("TOPIC", "sensor/lidar")
NODE_ID = os.getenv("NODE_ID", "local-node")
CLIENT_ORDER = int(os.getenv("CLIENT_ORDER", 1))  # Orden único para cada nodo

# Callback al conectar con el broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[{NODE_ID}] Conexión exitosa al broker MQTT")
        client.subscribe(TOPIC)
        print(f"[{NODE_ID}] Suscrito al tema {TOPIC}")
    else:
        print(f"[{NODE_ID}] Conexión fallida con código {rc}")

# Callback al recibir un mensaje
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print(f"[{NODE_ID}] Datos recibidos de {TOPIC}: {data}")
    except json.JSONDecodeError as e:
        print(f"[{NODE_ID}] Error al procesar JSON: {e}")
    except Exception as e:
        print(f"[{NODE_ID}] Error inesperado: {e}")

if __name__ == "__main__":
    try:
        print(f"[{NODE_ID}] Nodo iniciado con orden de cliente: {CLIENT_ORDER}")
        
        # Crear cliente MQTT
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        # Conectar al broker
        print(f"[{NODE_ID}] Conectando al broker MQTT en {BROKER_ADDRESS}:{BROKER_PORT}")
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

        # Iniciar loop para escuchar mensajes
        client.loop_forever()

    except Exception as e:
        print(f"[{NODE_ID}] Error al configurar el cliente MQTT: {e}")
