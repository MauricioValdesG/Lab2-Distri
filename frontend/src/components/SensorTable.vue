<template>
  <div>
    <h2>Estado de Sensores</h2>
    <table v-if="Object.keys(sensores).length > 0" class="sensor-table">
      <thead>
        <tr>
          <th>ID Sensor</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(estado, id) in sensores" :key="id">
          <td>{{ id }}</td>
          <td :class="estado ? 'activo' : 'inactivo'">
            {{ estado ? "Activo" : "Inactivo" }}
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="no-data">No hay datos de sensores disponibles.</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      sensores: {},
    };
  },
  methods: {
    async obtenerEstadoSensores() {
      try {
        const response = await axios.get("http://localhost:5001/sensores");
        this.sensores = response.data;
      } catch (err) {
        console.error("Error al obtener el estado de los sensores:", err);
        this.error = "No se pudo conectar al backend.";
      }
    },
  },
  mounted() {
    this.obtenerEstadoSensores();
    setInterval(this.obtenerEstadoSensores(), 5000);
  },
};
</script>
