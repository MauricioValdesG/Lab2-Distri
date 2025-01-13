import paho.mqtt.client as mqtt
import json
import os
import time
import numpy as np
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

# Configuración de ACO
NUM_PHASES = 3
ALPHA = 1.0
BETA = 2.0
EVAPORATION_RATE = 0.1
Q = 100
pheromones = np.ones(NUM_PHASES)
traffic_conditions = np.zeros(NUM_PHASES)

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

# ACO: Selección de fase
def select_phase():
    probabilities = [
        (pheromones[phase] ** ALPHA) * (1 / (calculate_pressure(traffic_conditions[phase], inflow, outflow) + 1) ** BETA)
        for phase in range(NUM_PHASES)
    ]
    total = sum(probabilities)
    probabilities = [p / total for p in probabilities]
    return np.random.choice(range(NUM_PHASES), p=probabilities)

# ACO: Actualización de feromonas
def update_pheromones(selected_phase, pressure):
    for phase in range(NUM_PHASES):
        pheromones[phase] *= (1 - EVAPORATION_RATE)
    pheromones[selected_phase] += Q / (max(pressure + 1, 1))

# ACO: Cálculo de presión
def calculate_pressure(queue_length, outflow):
    return sum(queue_length) - sum(outflow)

# Callback al recibir un mensaje
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print(f"[{NODE_ID}] Datos recibidos de {TOPIC}: {data}")

        # Extraer datos como valores escalares
        queue_length = int(data.get("queue_length", 0))
        outflow = int(data.get("outflow", 0))
        vehicles_detected = int(data.get("vehicles_detected", 0))

        # Calcular presión y aplicar ACO
        pressure = calculate_pressure(queue_length, outflow)
        selected_phase = select_phase()
        update_pheromones(selected_phase, pressure)

        # Enviar decisión al nodo central
        send_decision_to_central(client, selected_phase)

    except json.JSONDecodeError as e:
        print(f"[{NODE_ID}] Error al procesar JSON: {e}")
    except Exception as e:
        print(f"[{NODE_ID}] Error inesperado: {e}")

# Enviar decisión al nodo central
def send_decision_to_central(client, selected_phase):
    topic = "central_node/decisions"
    payload = {
        "node_id": NODE_ID,
        "selected_phase": selected_phase
    }
    client.publish(topic, json.dumps(payload), qos=1, retain=True)
    print(f"[{NODE_ID}] Decisión enviada al nodo central: {payload}")

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
