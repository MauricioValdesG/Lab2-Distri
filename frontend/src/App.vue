<template>
  <div id="app">
    <header class="header">
      <h1>Estado de los Sensores</h1>
    </header>

    <main class="main-content">
      <p v-if="error" class="error">{{ error }}</p>
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
    </main>

    <footer class="footer">
      <p>
        Monitoreo en tiempo real de trafico urbano - Proyecto Universidad de
        Santiago de Chile
      </p>
    </footer>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      sensores: {},
      error: null,
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
  created() {
    this.obtenerEstadoSensores();
  },
};
</script>

<style>
body {
  margin: 0;
  font-family: "Arial", sans-serif;
  background-color: #f3f4f6;
  color: #2c3e50;
}

.header {
  background-color: #005f73;
  color: #ffffff;
  text-align: center;
  padding: 20px 0;
  font-size: 24px;
  font-weight: bold;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.main-content {
  padding: 20px;
  max-width: 900px;
  margin: 40px auto;
  background: #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.sensor-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.sensor-table th {
  background-color: #0a9396;
  color: #ffffff;
  text-align: center;
  padding: 12px;
  font-size: 16px;
}

.sensor-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  text-align: center;
  font-size: 14px;
}

.sensor-table .activo {
  color: #007f5f;
  font-weight: bold;
}

.sensor-table .inactivo {
  color: #ae2012;
  font-weight: bold;
}

.no-data {
  text-align: center;
  color: #64748b;
  font-size: 16px;
  margin-top: 20px;
}

.footer {
  text-align: center;
  background-color: #005f73;
  color: white;
  padding: 10px 0;
  position: fixed;
  bottom: 0;
  width: 100%;
  box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.1);
}

.error {
  color: #e63946;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
}
</style>
