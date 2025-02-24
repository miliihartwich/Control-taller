<template>
    <div class="form-container">
      <h1 class="titulo">ORDENES</h1>
      <form @submit.prevent="guardarOrden">
  
        <!-- Cliente -->
        <label>Cliente</label>
        <select v-model="orden.cliente">
          <option v-for="cliente in clientes" :key="cliente.rut_ci" :value="cliente.rut_ci">
            {{ cliente.nombre }} ({{ cliente.rut_ci }})
          </option>
        </select>
  
        <label>División</label>
        <select v-model="orden.division" @change="cargarTipos">
          <option v-for="division in divisiones" :key="division" :value="division">
            {{ division }}
          </option>
        </select>
  
        <label>Tipo</label>
        <select v-model="orden.tipo">
          <option v-for="tipo in tipos" :key="tipo" :value="tipo">
            {{ tipo }}
          </option>
        </select>
  
        <label>Descripción</label>
        <input type="text" v-model="orden.descripcion" />
  
        <label>Fecha inicio</label>
        <input type="date" v-model="orden.fecha_inicio" />
  
        <label>Fecha fin</label>
        <input type="date" v-model="orden.fecha_fin" />
  
        <div class="buttons-container">
        <button class="btn" type="submit">GUARDAR</button>
        <button @click="goTo(menuDestino)" class="btn">{{ menuTexto }}</button>
      </div>
    </form>
      
  
      <div v-if="mensaje" :class="['mensaje', exito ? 'exito' : 'error']">
        {{ mensaje }}
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        orden: {
          cliente: "", 
          division: "",
          tipo: "",
          descripcion: "",
          fecha_inicio: "",
          fecha_fin: ""
        },
        clientes: [], 
        divisiones: [],
        tipos: [],
        mensaje: "",
        exito: false,
        usuarioRol: localStorage.getItem("rol") || "", // Obtener el rol del usuario desde localStorage
      };
    },
    computed: {
    menuTexto() {
      return this.usuarioRol === "operario" ? "Intervención" : "Menú";
    },
    menuDestino() {
      return this.usuarioRol === "operario" ? "IntervencionOperario" : "MenuPage";
    }
  },
    methods: {
      async cargarClientes() {
        try {
          const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/clientes");
          this.clientes = response.data; // [{ rut_ci: "12345678", nombre: "Cliente X" }, {...}]
        } catch (error) {
          console.error("Error al cargar clientes:", error);
        }
      },
      async cargarDivisiones() {
        try {
          const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/divisiones");
          this.divisiones = response.data.divisiones || response.data;
        } catch (error) {
          console.error("Error al cargar divisiones:", error);
        }
      },
      async cargarTipos() {
        if (!this.orden.division) return;
        try {
          const response = await axios.get(
            `https://control-taller-1a9d81bbc513.herokuapp.com/tipos_por_division/${encodeURIComponent(this.orden.division)}`
          );
          this.tipos = response.data.tipos || response.data;
        } catch (error) {
          console.error("Error al cargar tipos:", error);
        }
      },
      async guardarOrden() {
        try {
          const response = await fetch("https://control-taller-1a9d81bbc513.herokuapp.com/ordenes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(this.orden)
          });
  
          if (response.ok) {
            const data = await response.json();
            this.mensaje = data.message;
            this.exito = true;
            this.limpiarFormulario();
          } else {
            const errorData = await response.json();
            this.mensaje = errorData.message || "Error al guardar la orden.";
            this.exito = false;
          }
        } catch (error) {
          console.error("Error:", error);
          this.mensaje = "Error al conectar con el servidor.";
          this.exito = false;
        }
      },
      limpiarFormulario() {
        this.orden = {
          cliente: "",
          division: "",
          tipo: "",
          descripcion: "",
          fecha_inicio: "",
          fecha_fin: ""
        };
      },
      goTo(routeName) {
      this.$router.push({ name: routeName });
    },
    },
    mounted() {
      this.cargarClientes();
      this.cargarDivisiones();
      if (!localStorage.getItem("access_token")) {
    this.$router.push({ name: "Login" });
  }
    }
  };
  </script>
  
  
  
  <style scoped>
.form-container {
  width: 90%; /* Usar la mayor parte del ancho en móviles */
  max-width: 600px; /* No exceder 600px en pantallas grandes */
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
  
  .titulo {
    background-color: #b53b3b;
    color: white;
    padding: 10px;
    text-align: center;
    border-radius: 4px;
  }
  
  label {
    display: block;
    font-size: 1.2rem;
  }
  
  input, select {
    width: 100%;
    padding: 10px;
    font-size: 1rem;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  
  .buttons-container {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }
  
  .btn {
    background-color: #b53b3b;
    color: white;
    font-size: 1.2rem;
    padding: 10px 20px;
    cursor: pointer;
    border: none;
    border-radius: 4px;
  }
  
  .mensaje {
    margin-top: 20px;
    padding: 10px;
    border-radius: 4px;
    font-weight: bold;
    text-align: center;
  }
  
  .exito {
    background-color: #4caf50;
    color: white;
  }
  
  .error {
    background-color: #f44336;
    color: white;
  }
  /* Media Queries para Responsividad */
@media (min-width: 768px) { 
  .form-container {
    width: 50%;
  }
  .buttons-container {
    flex-direction: row; /* Botones en fila en pantallas grandes */
    gap: 10px; /* Espacio entre botones */
  }
}

@media (max-width: 767px) { 
  .buttons-container {
    flex-direction: column; /* Botones en columna en móviles */
    gap: 10px; /* Espacio entre botones */
  }
}
  </style>
  