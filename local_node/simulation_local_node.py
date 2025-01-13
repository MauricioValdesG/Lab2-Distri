import paho.mqtt.client as mqtt
import json
import os
import time
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread

# Configuración del broker MQTT
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", logger=True, engineio_logger=True)
BROKER_ADDRESS = os.getenv("MQTT_BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPIC = os.getenv("TOPIC", "sensor/lidar")
NODE_ID = os.getenv("NODE_ID", "local-node")
CLIENT_ORDER = int(os.getenv("CLIENT_ORDER", 1))  # Orden único para cada nodo
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# Callback al conectar con el broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[{NODE_ID}] Conexión exitosa al broker MQTT")
        client.subscribe(TOPIC, qos=1)
        print(f"[{NODE_ID}] Suscrito al tema {TOPIC}")
    else:
        print(f"[{NODE_ID}] Conexión fallida con código {rc}")

@app.route('/health')
def health_check():
    # Simplemente devuelve "Activo" si el contenedor está funcionando
    return jsonify({"status": "Activo"}), 200

# Callback al recibir un mensaje
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print(f"[{NODE_ID}] Datos recibidos de {TOPIC}: {data}")

        # Lógica para tomar decisiones basadas en datos
        vehicle_count = int(data.get("vehicles_detected", 0))
        if vehicle_count > 5:
            print("El semáforo debe cambiar a verde.")
            send_decision_to_central(client, "cambiar_a_verde")
        else:
            print("El semáforo debe mantenerse en rojo.")
            send_decision_to_central(client, "mantener_rojo")
        
        # Lógica para enviar datos al nodo central usando información del sensor
        queue_length = data.get("queue_length", 0)
        inflow = data.get("inflow", 0)
        outflow = data.get("outflow", 0)
        vehicles_detected = int(data.get("vehicles_detected", 0))

        # Enviar datos procesados al nodo central
        send_traffic_data_to_central(client, queue_length, inflow, outflow, vehicles_detected)

    except json.JSONDecodeError as e:
        print(f"[{NODE_ID}] Error al procesar JSON: {e}")
    except Exception as e:
        print(f"[{NODE_ID}] Error inesperado: {e}")

# Publicar decisiones tomadas al nodo central
def send_decision_to_central(client, decision):
    topic = "central_node/decisions"
    client.publish(topic, json.dumps({"node_id": NODE_ID, "decision": decision}), qos=1, retain=True)
    print(f"[{NODE_ID}] Decisión enviada al nodo central: {decision}")

# Publicar datos procesados al nodo central
def send_traffic_data_to_central(client, queue_length, inflow, outflow, vehicles_detected):
    topic = "central_node/decisions"
    payload = {
        "node_id": NODE_ID,
        "queue_length": queue_length,
        "inflow": inflow,
        "outflow": outflow,
        "vehicles_detected": vehicles_detected
    }
    client.publish(topic, json.dumps(payload), qos=1, retain=True)
    print(f"[{NODE_ID}] Datos enviados al nodo central: {payload}")

if __name__ == "__main__":
    try:
        print(f"[{NODE_ID}] Nodo iniciado con orden de cliente: {CLIENT_ORDER}")
        
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
        print(f"[{NODE_ID}] Conectando al broker MQTT en {BROKER_ADDRESS}:{BROKER_PORT}")
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

        # Iniciar aplicación Flask
        thread = Thread(target=lambda: socketio.run(app, host='0.0.0.0', port=FLASK_PORT))
        thread.start()

        # Iniciar loop para escuchar mensajes
        client.loop_forever()

    except Exception as e:
        print(f"[{NODE_ID}] Error al configurar el cliente MQTT: {e}")
