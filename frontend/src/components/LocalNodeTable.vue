<template>
  <div>
    <h2>Estado de Nodos Locales</h2>
    <table v-if="Object.keys(localNodes).length > 0" class="sensor-table">
      <thead>
        <tr>
          <th>ID Nodo</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(estado, id) in localNodes" :key="id">
          <td>{{ id }}</td>
          <td :class="estado === 'Activo' ? 'activo' : 'inactivo'">
            {{ estado }}
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="no-data">No hay datos de nodos locales disponibles.</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      localNodes: {},
    };
  },
  methods: {
    async obtenerEstadoNodos() {
      const nodosUrls = {
        "Nodo 1": "http://localhost:5002/health",
        "Nodo 2": "http://localhost:5003/health",
        "Nodo 3": "http://localhost:5004/health",
        "Nodo 4": "http://localhost:5005/health",
      };

      for (const [id, url] of Object.entries(nodosUrls)) {
        try {
          const response = await axios.get(url);
          this.localNodes[id] = response.status === 200 ? "Activo" : "Inactivo";
        } catch (err) {
          console.error(`Error al obtener el estado del ${id}:`, err);
          this.localNodes[id] = "Inactivo";
        }
      }
    },
  },
  mounted() {
    this.obtenerEstadoNodos();
    setInterval(this.obtenerEstadoNodos, 5000);
  },
};
</script>
