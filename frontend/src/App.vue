<template>
  <div>
    <h1 class="header">Monitoreo de Sensores y Nodos</h1>
    <CentralNodeTable />
    <LocalNodeTable />
    <SensorTable />
  </div>
</template>

<script>
import SensorTable from "./components/SensorTable.vue";
import LocalNodeTable from "./components/LocalNodeTable.vue";
import CentralNodeTable from "./components/CentralNodeTable.vue";

export default {
  data() {
    return {
      sensores: {},
      localNodes: {},
      centralNode: "Inactivo",
    };
  },
  components: {
    SensorTable,
    LocalNodeTable,
    CentralNodeTable,
  },
};
</script>
