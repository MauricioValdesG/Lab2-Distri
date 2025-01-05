# simulation_central_node.py
import paho.mqtt.client as mqtt
import json
import os

# Configuración del broker MQTT
BROKER_ADDRESS = os.getenv("MQTT_BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPIC = os.getenv("TOPIC", "central_node/decisions")

# Callback al conectar al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Central Node] Conexión exitosa al broker MQTT")
        client.subscribe(TOPIC)
        print(f"[Central Node] Suscrito al tema {TOPIC}")
    else:
        print(f"[Central Node] Conexión fallida con código {rc}")

# Callback al recibir un mensaje
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        decision_data = json.loads(payload)
        print(f"[Central Node] Decisión recibida: {decision_data}")
        process_decision(decision_data)
    except json.JSONDecodeError as e:
        print(f"[Central Node] Error al procesar JSON: {e}")
    except Exception as e:
        print(f"[Central Node] Error inesperado: {e}")

# Procesar la decisión recibida
def process_decision(decision_data):
    decision = decision_data.get("decision", "")
    node_id = decision_data.get("node_id", "unknown")
    if decision == "cambiar_a_verde":
        print(f"[Central Node] Nodo {node_id}: Cambiar semáforo a verde.")
    elif decision == "mantener_rojo":
        print(f"[Central Node] Nodo {node_id}: Mantener semáforo en rojo.")
    else:
        print(f"[Central Node] Nodo {node_id}: Decisión desconocida: {decision}")

if __name__ == "__main__":
    try:
        print("[Central Node] Nodo central iniciado")

        # Crear cliente MQTT
        client = mqtt.Client()
        # Configurar la seguridad TLS con los certificados
        client.tls_set(
            ca_certs="/certs/ca.crt",
            certfile="/certs/server.crt",
            keyfile="/certs/server.key"
        )
        client.on_connect = on_connect
        client.on_message = on_message
        # Conectar al broker
        print(f"[Central Node] Conectando al broker MQTT en {BROKER_ADDRESS}:{BROKER_PORT}")
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

        # Iniciar loop para escuchar mensajes
        client.loop_forever()

    except Exception as e:
        print(f"[Central Node] Error al configurar el cliente MQTT: {e}")
