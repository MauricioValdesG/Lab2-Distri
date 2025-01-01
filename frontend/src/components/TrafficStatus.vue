<template>
  <div>
    <h1>Estado de los Sensores</h1>
    <ul>
      <li v-for="(status, sensor) in sensors" :key="sensor">
        {{ sensor }}: {{ status ? "Activo" : "Inactivo" }}
      </li>
    </ul>
  </div>
</template>

<script>
import { reactive, onMounted } from "vue";
import mqttClient from "../mqttService";

export default {
  setup() {
    const sensors = reactive({
      "sensor/lidar/1": false,
      "sensor/lidar/2": false,
      "sensor/lidar/3": false,
      "sensor/lidar/4": false,
    });

    const timeouts = {};

    onMounted(() => {
      mqttClient.on("message", (topic) => {
        if (sensors[topic] !== undefined) {
          sensors[topic] = true;

          // Reinicia el temporizador para detectar inactividad
          clearTimeout(timeouts[topic]);
          timeouts[topic] = setTimeout(() => {
            sensors[topic] = false;
          }, 60000); // Cambiado a 1 minuto
        }
      });
    });

    return { sensors };
  },
};
</script>

<style scoped>
ul {
  list-style: none;
  padding: 0;
}

li {
  margin: 10px 0;
  padding: 10px;
  background: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 5px;
}
</style>
