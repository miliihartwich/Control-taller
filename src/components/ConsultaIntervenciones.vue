<template>
  <div class="empleados-container">
    <h1 class="titulo">INTERVENCIONES POR EMPLEADO</h1>

    <!-- Filtros -->
    <div class="filtros">
      <label for="empleado">Empleado</label>
      <div class="empleado-container">
        <input 
          type="text" 
          v-model="searchEmpleado" 
          @input="filterEmpleados" 
          @focus="showDropdown = true" 
          @blur="hideDropdown"
          placeholder="Escriba para buscar..." 
          class="busqueda" 
        />
        <ul v-show="showDropdown && filteredEmpleados.length" class="dropdown">
          <li 
            v-for="empleado in filteredEmpleados" 
            :key="empleado.id" 
            @mousedown.prevent="selectEmpleado(empleado)"
          >
            {{ empleado.nombre }}
          </li>
        </ul>
      </div>

      <label for="fechaDesde">Desde</label>
      <input type="date" v-model="fechaDesde" class="busqueda" />

      <label for="fechaHasta">Hasta</label>
      <input type="date" v-model="fechaHasta" class="busqueda" />

      <button @click="buscarIntervenciones" class="menu-boton">Buscar</button>
    </div>

    <!-- Tabla de Intervenciones -->
    <div class="tabla-intervenciones">
      <table class="empleados-tabla">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>División</th>
            <th>Descripción</th>
            <th>Horas</th>
            <th>Costo</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="intervencion in intervenciones.intervenciones" :key="intervencion.id">
            <td>{{ intervencion.tipo }}</td>
            <td>{{ intervencion.division }}</td>
            <td>{{ intervencion.descripcion }}</td>
            <td>{{ intervencion.horas_trabajadas }}</td>  
            <td>{{ intervencion.costo_intervencion }}</td> 
          </tr>
        </tbody>
        <tfoot>
          <!-- Fila para los totales -->
          <tr>
            <td colspan="3"></td>
            <!-- Total de horas -->
            <td>
              <div class="total-label">Total Horas</div>
              <div class="total-value">{{ intervenciones.total_horas }}</div>
            </td>
            <!-- Total de costo -->
            <td>
              <div class="total-label">Total Costo</div>
              <div class="total-value">{{ intervenciones.total_costo }}</div>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
    <button @click="goTo('MenuPage')" class="botones">Menú</button>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      empleados: [],
      filteredEmpleados: [],
      empleadoSeleccionado: "",
      searchEmpleado: "",
      fechaDesde: "",  
      fechaHasta: "",  
      intervenciones: [],
      showDropdown: false,
    };
  },
  mounted() {
    this.obtenerEmpleados();
  },
  methods: {
    async obtenerEmpleados() {
      try {
        const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/obtener_empleados");
        this.empleados = response.data;
        this.filteredEmpleados = this.empleados;
      } catch (error) {
        console.error("Error al obtener empleados:", error);
      }
    },
    filterEmpleados() {
      this.filteredEmpleados = this.searchEmpleado
        ? this.empleados.filter(e => e.nombre.toLowerCase().includes(this.searchEmpleado.toLowerCase()))
        : this.empleados;
      this.showDropdown = true;
    },
    selectEmpleado(empleado) {
      this.searchEmpleado = empleado.nombre;
      this.empleadoSeleccionado = empleado.cedula;
      this.showDropdown = false;
    },
    hideDropdown() {
      setTimeout(() => {
        this.showDropdown = false;
      }, 200);
    },
    async buscarIntervenciones() {
  if (!this.empleadoSeleccionado || !this.fechaDesde || !this.fechaHasta) {
    alert("Por favor, seleccione un empleado y un rango de fechas.");
    return;
  }
  try {
    const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/get_intervenciones", {
      params: {
        empleado_id: this.empleadoSeleccionado,
        fecha_desde: this.fechaDesde,
        fecha_hasta: this.fechaHasta
      }
    });
    this.intervenciones = response.data;  
  } catch (error) {
    console.error("Error al obtener intervenciones:", error);
  }
    },
    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
  }
};
</script>

<style scoped>
.empleados-container {
  width: 100%;
  margin: 20px auto;
  text-align: center;
}
.titulo {
  background-color: #b53b3b;
  color: white;
  padding: 10px;
  font-weight: bold;
}
.busqueda {
  width: 100%;
  padding: 8px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.empleado-container {
  position: relative;
  display: flex;
  flex-direction: column;
}
.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  background-color: white;
  border: 1px solid #ccc;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  padding: 0;
  margin: 0;
  z-index: 100;
}
.dropdown li {
  padding: 10px;
  cursor: pointer;
  list-style: none;
  transition: background-color 0.2s;
}
.dropdown li:hover {
  background-color: #f0f0f0;
}
.empleados-tabla {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.empleados-tabla th, .empleados-tabla td {
  border: 1px solid #000;
  padding: 8px;
  text-align: left;
}
.empleados-tabla thead {
  background-color: #b53b3b;
  color: white;
}
.filtros label {
  display: block;
  font-weight: bold;
  text-align: left;
  margin-bottom: 5px;
}
button {
  background-color: red;
  color: white;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
}
.botones {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}
.total-cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.total-label {
  font-weight: bold;
  font-size: 14px;
  color: #555;
}

.total-value {
  font-size: 16px;
  font-weight: bold;
  margin-top: 4px;
}


</style>
