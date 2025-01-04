<template>
  <div id="app">
    <header class="header">
      <h1>Estado de los Sensores y Nodos Locales</h1>
    </header>

    <main class="main-content">
      <!-- Mensaje de error si falla la conexión -->
      <p v-if="error" class="error">{{ error }}</p>

      <!-- Tabla de Sensores -->
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

      <!-- Tabla de Nodos Locales -->
      <h2>Estado de Nodos Locales</h2>
      <table v-if="Object.keys(nodos).length > 0" class="sensor-table">
        <thead>
          <tr>
            <th>ID Nodo</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(estado, id) in nodos" :key="id">
            <td>{{ id }}</td>
            <td :class="estado === 'Activo' ? 'activo' : 'inactivo'">
              {{ estado }}
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">No hay datos de nodos locales disponibles.</p>
    </main>

    <footer class="footer">
      <p>
        Monitoreo en tiempo real de tráfico urbano - Proyecto Universidad de
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
      nodos: {},
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
    // Obtener el estado de los nodos locales desde varios endpoints
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
          this.nodos[id] = response.status === 200 ? "Activo" : "Inactivo";
        } catch (err) {
          console.error(`Error al obtener el estado del ${id}:`, err);
          this.nodos[id] = "Inactivo";
        }
      }
    },
  },
  created() {
    this.obtenerEstadoSensores();
    this.obtenerEstadoNodos();
    setInterval(() => {
      this.obtenerEstadoSensores();
      this.obtenerEstadoNodos();
    }, 5000);
  },
};
</script>

<style>
/* Estilo General */
.header {
  text-align: center;
  padding: 20px;
  background-color: #0f6b7d; /* Azul petróleo */
  color: white;
}

/* Contenedor principal */
.main-content {
  margin: 20px auto;
  width: 60%;
  text-align: center;
}

/* Estilo de las tablas */
.sensor-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Encabezado de las tablas */
.sensor-table thead {
  background-color: #0f6b7d; /* Azul petróleo */
  color: white;
  font-size: 1.2rem;
}

/* Celdas */
.sensor-table th,
.sensor-table td {
  padding: 15px;
  border: 1px solid #ddd;
  text-align: center;
}

/* Estados Activo e Inactivo */
.activo {
  color: green;
  font-weight: bold;
}

.inactivo {
  color: #b22222; /* Rojo oscuro */
  font-weight: bold;
}

/* Mensajes de error y sin datos */
.error {
  color: red;
  font-weight: bold;
  margin-top: 20px;
}

.no-data {
  text-align: center;
  font-style: italic;
}

/* Footer */
.footer {
  text-align: center;
  padding: 20px;
  font-size: 0.9rem;
  color: #555;
}
</style>
