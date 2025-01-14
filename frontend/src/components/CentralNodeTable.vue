<template>
  <div>
    <h2>Estado del Nodo Central</h2>
    <table v-if="centralNode.status" class="sensor-table">
      <thead>
        <tr>
          <th>ID Nodo</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Nodo Central</td>
          <td :class="centralNode.status === 'Activo' ? 'activo' : 'inactivo'">
            {{ centralNode.status }}
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="no-data">No hay datos del nodo central disponibles.</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      centralNode: { status: null },
    };
  },
  methods: {
    async obtenerEstadoNodoCentral() {
      try {
        const response = await axios.get("http://localhost:5006/health");
        this.centralNode = {
          status: response.status === 200 ? "Activo" : "Inactivo",
        };
      } catch (error) {
        console.error("Error al obtener datos del nodo central:", error);
        this.centralNode = "Inactivo";
      }
    },
  },
  mounted() {
    this.obtenerEstadoNodoCentral();
    setInterval(this.obtenerEstadoNodoCentral, 5000);
  },
};
</script>
