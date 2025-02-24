<template>
    <div class="empleados-container">
      <h1 class="titulo">Lista de Empleados</h1>
      
      <!-- Barra de Búsqueda -->
      <input 
        type="text" 
        v-model="filtroNombre" 
        placeholder="Buscar por nombre..." 
        class="busqueda"
      />
      
      <!-- Tabla de Empleados -->
      <table class="empleados-tabla">
        <thead>
          <tr>
            <th>Cédula</th>
            <th>Nombre</th>
            <th>Dirección</th>
            <th>Celular</th>
            <th>Remuneración</th>
            <th>Factor</th>
            <th>Fecha Vencimiento Carnet</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="empleado in empleadosFiltrados" :key="empleado.cedula">
            <td>{{ empleado.cedula }}</td>
            <td>{{ empleado.nombre }}</td>
            <td>{{ empleado.direccion }}</td>
            <td>{{ empleado.celular }}</td>
            <td>{{ empleado.remuneracion }}</td>
            <td>{{ empleado.factor }}</td>
            <td>{{ formatearFecha(empleado.fecha_vencimiento_carnet) }}</td>
          </tr>
        </tbody>
      </table>

          <!-- Botón de Menú -->
    <div class="menu-boton-container">
      <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
    </div>
  </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        empleados: [],
        filtroNombre: "",
      };
    },
    computed: {
      empleadosFiltrados() {
        return this.empleados.filter(empleado => {
          const nombre = empleado.nombre ? empleado.nombre.toLowerCase() : "";
          return nombre.includes(this.filtroNombre.toLowerCase());
        });
      }
    },
    mounted() {
      this.obtenerEmpleados();
    },
    methods: {
      async obtenerEmpleados() {
        try {
          const response = await fetch("https://control-taller-1a9d81bbc513.herokuapp.com/get_empleado");
          this.empleados = await response.json();
        } catch (error) {
          console.error("Error al obtener empleados:", error);
        }
      },
      // Método para formatear la fecha en el frontend
      formatearFecha(fecha) {
        const opciones = { day: '2-digit', month: '2-digit', year: 'numeric' };
        return new Date(fecha).toLocaleDateString('es-ES', opciones);
      },
      goTo(routeName) {
        this.$router.push({ name: routeName });
      },
    },
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
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  
  thead {
    background-color: #b53b3b;
    color: white;
  }
  
  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }
  .empleados-tabla {
  font-size: 12px; /* Tamaño de fuente más pequeño */
}

.empleados-tabla th, .empleados-tabla td {
  padding: 8px;
}

.empleados-tabla th {
  text-align: left;
}

/* Clase para hacer más pequeña la fuente de la fecha */
.empleados-tabla td {
  font-size: 12px; /* Ajustar tamaño de la fuente */
}
/* Estilos para el botón de Menú */
.menu-boton-container {
  margin-top: 20px;
  text-align: center;
}

.menu-boton {
  padding: 10px 20px;
  font-size: 14px;
  background-color: #b53b3b;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.menu-boton:hover {
  background-color: #b53b3b;
}
  </style>
  