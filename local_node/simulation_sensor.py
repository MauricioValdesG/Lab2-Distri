import numpy as np
import random
import time

def simulate_lidar_data(): # Función para simular datos de un sensor LIDAR, estos datos son solo para probar la comunicación
    
    num_points = 360  # Un punto por grado
    distances = np.random.uniform(0.5, 30.0, num_points)  # Distancias entre 0.5 y 30 metros
    return {f"angle_{i}": round(dist, 2) for i, dist in enumerate(distances)}

def simulate_camera_data(): # Función para simular datos de una cámara, estos datos son solo para probar la comunicación
    
    vehicles_detected = random.randint(0, 20)  # Entre 0 y 20 vehículos
    return {"vehicles_detected": vehicles_detected}

def generate_sensor_data(): # Función para agrupar los datos de los sensores en un solo mensaje
    
    lidar_data = simulate_lidar_data()
    camera_data = simulate_camera_data()
    return {
        "lidar_data": lidar_data,
        "camera_data": camera_data,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    # Simulación en tiempo real de los datos del sensor con 20 escaneos por segundo
    scan_interval = 1 / 20  # 20 escaneos por segundo
    while True:
        sensor_data = generate_sensor_data()
        print("Sensor Data:", sensor_data)
        time.sleep(scan_interval)
