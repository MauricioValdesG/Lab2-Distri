from prometheus_client import start_http_server, Gauge, Counter
import paho.mqtt.client as mqtt
import json
import time

# Definición de métricas actualizadas
mqtt_connected = Gauge('mqtt_connected', 'Estado de la conexión MQTT', ['node_id'])
mqtt_sensors_active = Gauge('mqtt_sensors_active', 'Cantidad de sensores enviando información')
mqtt_messages_sent_per_sensor = Counter('mqtt_messages_sent_per_sensor', 'Mensajes enviados por sensor', ['sensor_id'])
mqtt_messages_received_central = Counter('mqtt_messages_received_central', 'Mensajes recibidos por el nodo central')
mqtt_nodes_active = Gauge('mqtt_nodes_active', 'Cantidad de nodos locales enviando decisiones')

# Configuración del broker MQTT y certificados
MQTT_BROKER = "mqtt-broker"
MQTT_PORT = 8883
MQTT_CA_CERT = "/certs/ca.crt"
MQTT_CLIENT_CERT = "/certs/server.crt"
MQTT_CLIENT_KEY = "/certs/server.key"
MQTT_TOPICS = [("sensor/lidar/#", 0), ("central_node/decisions", 0)]

# Variables para contar sensores y nodos activos
active_sensors = set()
active_nodes = set()

# Extraer información desde el tópico
def extract_node_and_sensor(topic):
    parts = topic.split("/")
    if topic.startswith("sensor/lidar/"):
        return "sensor", parts[-1]  # Ej: sensor/lidar/1 → (sensor, 1)
    elif topic == "central_node/decisions":
        return "central_node", "decision"
    return "unknown_node", "unknown_sensor"

# Callback de conexión al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conexión exitosa al broker MQTT")
        mqtt_connected.labels(node_id="monitoring_node").set(1)
        for topic, qos in MQTT_TOPICS:
            client.subscribe(topic, qos)
    else:
        print(f"Error de conexión: {rc}")
        mqtt_connected.labels(node_id="monitoring_node").set(0)

# Callback de recepción de mensajes
def on_message(client, userdata, msg):
    global active_sensors, active_nodes
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        node_id, sensor_id = extract_node_and_sensor(msg.topic)

        # Si el mensaje es de un sensor
        if msg.topic.startswith("sensor/lidar/"):
            if sensor_id not in active_sensors:
                active_sensors.add(sensor_id)
                mqtt_sensors_active.set(len(active_sensors))
            mqtt_messages_sent_per_sensor.labels(sensor_id=sensor_id).inc()
            print(f"[Sensor {sensor_id}] Mensaje recibido")

        # Si el mensaje es del nodo central
        elif msg.topic == "central_node/decisions":
            if node_id not in active_nodes:
                active_nodes.add(node_id)
                mqtt_nodes_active.set(len(active_nodes))
            mqtt_messages_received_central.inc()
            print(f"[Nodo Central] Decisión recibida de {node_id}")

    except Exception as e:
        print(f"Error al procesar el mensaje del tópico {msg.topic}: {e}")

# Cliente MQTT con TLS
client = mqtt.Client()
client.tls_set(ca_certs=MQTT_CA_CERT, certfile=MQTT_CLIENT_CERT, keyfile=MQTT_CLIENT_KEY)
client.on_connect = on_connect
client.on_message = on_message

# Iniciar el servidor Prometheus
start_http_server(9641)

# Conexión al broker con reconexión automática
while True:
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_forever()
    except Exception as e:
        print(f"Error de conexión: {e}")
        mqtt_connected.labels(node_id="monitoring_node").set(0)
        time.sleep(5)
