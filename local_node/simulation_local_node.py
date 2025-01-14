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
ALPHA = 1.0
BETA = 2.0
EVAPORATION_RATE = 0.1
Q = 100


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
    return jsonify({"status": "Activo"}), 200

# ACO: Cálculo de presión considerando inflow y outflow
def calculate_pressure(queue_length, inflow, outflow):
    return queue_length + inflow - outflow

# ACO: Selección de fase considerando presión y feromonas

def select_phase(queue_length, inflow, outflow):
    global pheromones, phases, NUM_PHASES  # Se modifican directamente
    pressures = [calculate_pressure(queue_length, inflow, outflow) for _ in range(NUM_PHASES)]
    probabilities = [
        (pheromones[phase] ** ALPHA) * (1 / (pressures[phase] + 1) ** BETA)
        for phase in range(NUM_PHASES)
    ]
    total = sum(probabilities)
    probabilities = [p / total for p in probabilities]
    selected_index = np.random.choice(range(NUM_PHASES), p=probabilities)
    return phases[selected_index]  


# ACO: Actualización de feromonas basada en la presión calculada
def update_pheromones(selected_phase, pressure):
    global phases, pheromones
    selected_index = phases.index(selected_phase)
    
    # Evaporación de feromonas
    for phase in range(NUM_PHASES):
        pheromones[phase] *= (1 - EVAPORATION_RATE)
        
    # Refuerzo de la fase seleccionada
    pheromones[selected_index] += Q / (pressure + 1)



# Callback al recibir un mensaje desde el nodo sensor
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print(f"[{NODE_ID}] Datos recibidos de {TOPIC}: {data}")
        global phases, NUM_PHASES, pheromones, traffic_conditions
        phases = data.get("phases", [])
        NUM_PHASES = len(phases)
        pheromones = np.ones(NUM_PHASES)
        traffic_conditions = np.zeros(NUM_PHASES)

        # Extraer datos de cada carril recibido
        for lane_data in data.get("lane_data", []):
            queue_length = lane_data.get("queue_length", 0)
            inflow = lane_data.get("inflow", 0)
            outflow = lane_data.get("outflow", 0)

            # Calcular presión y aplicar ACO considerando presión por carril
            selected_phase = select_phase(queue_length, inflow, outflow)
            pressure = calculate_pressure(queue_length, inflow, outflow)
            update_pheromones(selected_phase, pressure)
            print(f"[{NODE_ID}] Fase seleccionada: {selected_phase}, de tipo de dato: {type(selected_phase)}")
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

if __name__ == "__main__":
    try:
        print(f"[{NODE_ID}] Nodo iniciado con orden de cliente: {CLIENT_ORDER}")

        # Crear cliente MQTT
        client = mqtt.Client()
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
