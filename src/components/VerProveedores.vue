<template>
    <div class="proveedores-container">
      <h1 class="titulo">Lista de Proveedores</h1>
      
      <!-- Barra de Búsqueda -->
      <input 
        type="text" 
        v-model="filtroNombre" 
        placeholder="Buscar por nombre..." 
        class="busqueda"
      />
      
      <!-- Tabla de Proveedoress -->
      <table class="proveedores-tabla">
        <thead>
          <tr>
            <th>RUT/CI</th>
            <th>Nombre</th>
            <th>Alias</th>
            <th>Teléfono</th>
            <th>Whatsapp</th>
            <th>Mail</th>
            <th>Rubro</th>
            <th>Dirección</th>
            <th>Localidad</th>
            <th>Departamento</th>
            <th>Calificación</th>
            <th>Comentarios</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="proveedor in proveedoresFiltrados" :key="proveedor.rut_ci">
            <td>{{ proveedor.rut_ci }}</td>
            <td>{{ proveedor.nombre }}</td>
            <td>{{ proveedor.alias}}</td>
            <td>{{ proveedor.telefono }}</td>
            <td>{{ proveedor.whatsapp}}</td>
            <td>{{ proveedor.mail }}</td>
            <td>{{ proveedor.rubro }}</td>
            <td>{{ proveedor.direccion}}</td>
            <td>{{ proveedor.localidad_nombre }}</td>
            <td>{{ proveedor.departamento_nombre }}</td>  
            <td>{{ proveedor.calificación }}</td> 
            <td>{{ proveedor.comentarios }}</td>           
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
        proveedores: [],
        filtroNombre: "",
      };
    },
    computed: {
      proveedoresFiltrados() {
        return this.proveedores.filter(proveedor => {
          const nombre = proveedor.nombre ? proveedor.nombre.toLowerCase() : "";
          return nombre.includes(this.filtroNombre.toLowerCase());
        });
      }
    },
    mounted() {
      this.obtenerProveedores();
    },
    methods: {
      async obtenerProveedores() {
        try {
          const response = await fetch("https://control-taller-1a9d81bbc513.herokuapp.com/get_proveedor");
          this.proveedores = await response.json();
        } catch (error) {
          console.error("Error al obtener proveedores:", error);
        }
      },
      goTo(routeName) {
        this.$router.push({ name: routeName });
      },
    }
  };
  </script>
  
  
  <style scoped>
  .proveedores-container {
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
  .proveedores-tabla {
  font-size: 12px; /* Tamaño de fuente más pequeño */
}

.proveedores-tabla th, .proveedores-tabla td {
  padding: 8px;
}

.proveedores-tabla th {
  text-align: left;
}

/* Clase para hacer más pequeña la fuente de la fecha */
.proveedores-tabla td {
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
  