import carla
import numpy as np

def process_lidar(data):
    points = np.frombuffer(data.raw_data, dtype=np.float32).reshape(-1, 4)
    print(f"LiDAR captured {len(points)} points")
    # Opcional: guarda o procesa los puntos como desees

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    # Configurar el sensor LiDAR
    blueprint_library = world.get_blueprint_library()
    lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
    lidar_bp.set_attribute('channels', '32')
    lidar_bp.set_attribute('range', '50')
    lidar_bp.set_attribute('rotation_frequency', '20')
    lidar_bp.set_attribute('points_per_second', '56000')

    transform = carla.Transform(carla.Location(x=0, y=0, z=2.5))
    lidar_sensor = world.spawn_actor(lidar_bp, transform)

    lidar_sensor.listen(process_lidar)

    try:
        print("LiDAR estático ejecutándose... Presiona Ctrl+C para detener.")
        while True:
            pass
    except KeyboardInterrupt:
        print("Finalizando simulación...")
    finally:
        lidar_sensor.destroy()

if __name__ == '__main__':
    main()
