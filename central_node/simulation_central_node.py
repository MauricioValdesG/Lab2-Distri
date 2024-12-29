import json
import time
import paho.mqtt.client as mqtt

# Configuración del nodo central
BROKER = "localhost"
PORT = 1883  # Puerto por defecto para MQTT
TOPIC = "traffic/central_data"  # Tópico para recibir datos del nodo local

# Callback para conexión exitosa al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Nodo central conectado al broker MQTT.")
        client.subscribe(TOPIC)
    else:
        print(f"Error al conectar al broker MQTT: Código {rc}")

# Callback para procesar mensajes recibidos
def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
        print(f"Datos recibidos desde el nodo local: {data}")
        # Añadir aquí lógica adicional para procesar o almacenar los datos
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")

# Inicializar cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Conectar al broker y comenzar el loop
mqtt_client.connect(BROKER, PORT, 60)
print("Nodo central escuchando datos...")
mqtt_client.loop_forever()
