<template>
    <div class="clientes-container">
      <h1 class="titulo">Lista de Clientes</h1>
      
      <!-- Barra de Búsqueda -->
      <input 
        type="text" 
        v-model="filtroNombre" 
        placeholder="Buscar por nombre..." 
        class="busqueda"
      />
      
      <!-- Tabla de Clientes -->
      <table class="clientes-tabla">
        <thead>
          <tr>
            <th>RUT/CI</th>
            <th>Nombre</th>
            <th>Alias</th>
            <th>Teléfono</th>
            <th>Whatsapp</th>
            <th>Mail</th>
            <th>Dirección</th>
            <th>Localidad</th>
            <th>Departamento</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cliente in clientesFiltrados" :key="cliente.rut_ci">
            <td>{{ cliente.rut_ci }}</td>
            <td>{{ cliente.nombre }}</td>
            <td>{{ cliente.alias}}</td>
            <td>{{ cliente.telefono }}</td>
            <td>{{ cliente.whatsapp}}</td>
            <td>{{ cliente.mail }}</td>
            <td>{{ cliente.direccion}}</td>
            <td>{{ cliente.localidad_nombre }}</td>
            <td>{{ cliente.departamento_nombre }}</td>            
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
        clientes: [],
        filtroNombre: "",
      };
    },
    computed: {
      clientesFiltrados() {
        return this.clientes.filter(cliente => {
          const nombre = cliente.nombre ? cliente.nombre.toLowerCase() : "";
          return nombre.includes(this.filtroNombre.toLowerCase());
        });
      }
    },
    mounted() {
      this.obtenerClientes();
    },
    methods: {
      async obtenerClientes() {
        try {
          const response = await fetch("https://control-taller-1a9d81bbc513.herokuapp.com/get_cliente");
          this.clientes = await response.json();
        } catch (error) {
          console.error("Error al obtener empleados:", error);
        }
      },
      goTo(routeName) {
        this.$router.push({ name: routeName });
      },
    }
  };
  </script>
  
  
  <style scoped>
  .clientes-container {
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
  .clientes-tabla {
  font-size: 12px; /* Tamaño de fuente más pequeño */
}

.clientes-tabla th, .clientes-tabla td {
  padding: 8px;
}

.clientes-tabla th {
  text-align: left;
}

/* Clase para hacer más pequeña la fuente de la fecha */
.clientes-tabla td {
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
  