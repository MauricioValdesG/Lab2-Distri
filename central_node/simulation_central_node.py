import paho.mqtt.client as mqtt
import os

SUMO_HOST = os.getenv("SUMO_HOST", "host.docker.internal")
SUMO_PORT = int(os.getenv("SUMO_PORT", 8813))

print(f"Conectando a SUMO en {SUMO_HOST}:{SUMO_PORT}")

# Aquí iría el código para conectarse al puerto remoto de SUMO


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Central Node] Conectado al broker MQTT exitosamente")
        # Suscribirse al tópico general para recibir mensajes de los nodos locales
        client.subscribe("local_nodes/#")
    else:
        print(f"[Central Node] Error al conectar al broker MQTT: {rc}")

def on_message(client, userdata, msg):
    print(f"[Central Node] Mensaje recibido en el tópico {msg.topic}: {msg.payload.decode('utf-8')}")

# Configuración del cliente MQTT para el nodo central
mqtt_broker = "localhost"
mqtt_port = 1883

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(mqtt_broker, mqtt_port, 60)
    print("[Central Node] Esperando mensajes de los nodos locales...")
    client.loop_forever()
except Exception as e:
    print(f"[Central Node] Error al conectar con el broker MQTT: {e}")
