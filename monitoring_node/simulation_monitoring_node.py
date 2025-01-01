from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import paho.mqtt.client as mqtt
import threading
import os
import time

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", logger=True, engineio_logger=True)

# Configuración del broker MQTT
BROKER_ADDRESS = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPICS = [
    "sensor/lidar/1",
    "sensor/lidar/2",
    "sensor/lidar/3",
    "sensor/lidar/4"
]

# Diccionario para almacenar los estados de los sensores
estado_sensores = {sensor.split("/")[-1]: False for sensor in TOPICS}

# Diccionario para registrar el último tiempo de actividad de los sensores
ultimo_tiempo_sensores = {sensor.split("/")[-1]: time.time() for sensor in TOPICS}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conexión exitosa al broker MQTT")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"Suscrito al tópico: {topic}")
    else:
        print(f"Conexión fallida con código {rc}")


def on_message(client, userdata, msg):
    global estado_sensores, ultimo_tiempo_sensores
    try:
        payload = msg.payload.decode("utf-8")
        sensor_id = msg.topic.split("/")[-1]  # Extraer ID del sensor desde el tópico

        # Marcar el sensor como activo
        estado_sensores[sensor_id] = True
        ultimo_tiempo_sensores[sensor_id] = time.time()

        # Emitir actualizaciones al frontend
        print(f"Sensor {sensor_id} activo. Enviando actualización al frontend.")
        socketio.emit('estadoSensores', estado_sensores)
    except Exception as e:
        print(f"Error procesando mensaje MQTT: {e}")


def verificar_sensores_inactivos():
    while True:
        tiempo_actual = time.time()
        cambios = False
        for sensor_id, ultimo_tiempo in ultimo_tiempo_sensores.items():
            # Si han pasado más de 30 segundos sin recibir datos, marcar como inactivo
            if tiempo_actual - ultimo_tiempo > 30 and estado_sensores[sensor_id]:
                estado_sensores[sensor_id] = False
                print(f"Sensor {sensor_id} marcado como inactivo.")
                cambios = True

        # Emitir actualizaciones al frontend si hubo cambios
        if cambios:
            print("Enviando actualizaciones al frontend por sensores inactivos.")
            socketio.emit('estadoSensores', estado_sensores)
        time.sleep(1)  # Revisar cada 1 segundos


def iniciar_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, BROKER_PORT)
    client.loop_forever()


@app.route('/sensores', methods=['GET'])
def obtener_estado_sensores():
    return jsonify(estado_sensores)


if __name__ == '__main__':
    # Iniciar cliente MQTT en un hilo separado
    threading.Thread(target=iniciar_mqtt, daemon=True).start()
    # Iniciar verificación periódica de sensores inactivos en un hilo separado
    threading.Thread(target=verificar_sensores_inactivos, daemon=True).start()
    # Iniciar servidor Flask con WebSockets
    socketio.run(app, host='0.0.0.0', port=5001)
