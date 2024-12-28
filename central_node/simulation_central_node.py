import time
import paho.mqtt.client as mqtt

# Configuración del nodo central
BROKER = "localhost"  
PORT = 1883 # Puerto por defecto para MQTT
TOPIC = "traffic/sensor_data" # Tópico para recibir datos de los nodos locales

def on_connect(client, userdata, flags, rc): # Función que se ejecuta al conectarse al broker MQTT
    if rc == 0:
        print("Nodo central conectado al broker MQTT.")
        client.subscribe(TOPIC)
    else:
        print(f"Error al conectar al broker MQTT: Código {rc}")

def on_message(client, userdata, msg): # Función que se ejecuta al recibir un mensaje
    
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}") # Imprime un mensaje al recibir datos de un nodo local

if __name__ == "__main__":
    # Configuración del cliente MQTT
    client = mqtt.Client(protocol=mqtt.MQTTv311) # Crear un cliente MQTT especificando el protocolo a utilizar (MQTTv3.1.1)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()  # Mantener el nodo central escuchando

    except KeyboardInterrupt:
        print("Desconectando del broker MQTT...")
        client.disconnect()
