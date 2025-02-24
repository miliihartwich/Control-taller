<template>
  <div class="form-container">
    <h1 class="titulo">REGISTRAR INTERVENCIÓN</h1>
    <form @submit.prevent="guardarIntervencion">
      
      <!-- Empleado -->
      <label>Empleado</label>
      <select v-model="intervencion.empleado">
        <option v-for="empleado in empleados" :key="empleado.id" :value="empleado.nombre">
  {{ empleado.nombre }}
</option>

      </select>

      <!-- División -->
      <label>División</label>
      <select v-model="intervencion.division" @change="cargarTipos">
        <option v-for="division in divisiones" :key="division" :value="division">
          {{ division }}
        </option>
      </select>

<!-- Tipo -->
<label>Tipo</label>
<select v-model="intervencion.tipo" @change="cargarDescripciones">
<option v-for="tipo in tipos" :key="tipo" :value="tipo">
  {{ tipo }}
</option>
</select>


<!-- Descripción -->
<label>Descripción</label>
<select v-model="intervencion.descripcion">
<option v-for="descripcion in descripciones" :key="descripcion" :value="descripcion">
  {{ descripcion }}
</option>
</select>

      <!-- Fecha -->
      <label>Fecha</label>
      <input type="date" v-model="intervencion.fecha" />

      <!-- Hora Inicio -->
      <label>Hora Inicio</label>
      <input type="time" v-model="intervencion.hora_inicio" />

      <!-- Hora Fin -->
      <label>Hora Fin</label>
      <input type="time" v-model="intervencion.hora_fin" />

      <div class="buttons-container">
        <button class="btn" type="submit">GUARDAR</button>
        <button @click="goTo('MenuPage')" class="btn">Menú</button>
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
      intervencion: {
        empleado: "",
        division: "",
        tipo: "",
        descripcion: "",
        fecha: "",
        hora_inicio: "",
        hora_fin: ""
      },
      empleados: [],
      divisiones: [],
      tipos: [],
      descripciones: [],
      mensaje: "",
      exito: false
    };
  },
  methods: {
    async cargarEmpleados() {
      try {
        const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/obtener_empleados");
        this.empleados = response.data;
        console.log("Lista de empleados:", this.empleados);
      } catch (error) {
        console.error("Error al cargar empleados:", error);
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
  if (!this.intervencion.division) return;
  try {
    const response = await axios.get(
      `https://control-taller-1a9d81bbc513.herokuapp.com/tipos_por_division/${encodeURIComponent(this.intervencion.division)}`
    );
    this.tipos = response.data.tipos || response.data;
  } catch (error) {
    console.error("Error al cargar tipos:", error);
  }
},

cargarDescripciones() {
  if (!this.intervencion.tipo) {
    console.warn("El tipo de intervención está vacío");
    return;
  }
  axios.get(`https://control-taller-1a9d81bbc513.herokuapp.com/descripcion_por_tipo/${this.intervencion.tipo}`)
    .then(response => {
      console.log("Datos recibidos:", response.data);
      this.descripciones = response.data;
    })
    .catch(error => {
      console.error("Error al cargar descripciones:", error);
    });
},
    async guardarIntervencion() {
      console.log("Datos enviados:", this.intervencion);
      try {
        const response = await fetch("https://control-taller-1a9d81bbc513.herokuapp.com/intervenciones", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.intervencion)
        });

        if (response.ok) {
          const data = await response.json();
          this.mensaje = data.message;
          this.exito = true;
          this.limpiarFormulario();
        } else {
          const errorData = await response.json();
          this.mensaje = errorData.message || "Error al guardar la intervención.";
          this.exito = false;
        }
      } catch (error) {
        console.error("Error:", error);
        this.mensaje = "Error al conectar con el servidor.";
        this.exito = false;
      }
    },
    limpiarFormulario() {
      this.intervencion = {
        empleado: "",
        division: "",
        tipo: "",
        descripcion: "",
        fecha: "",
        hora_inicio: "",
        hora_fin: ""
      };
    },
    goTo(routeName) {
        this.$router.push({ name: routeName });
      },
  },
  mounted() {
    this.cargarEmpleados();
    this.cargarDivisiones();
  }
};
</script>

  
  <style scoped>
  .form-container {
    width: 50%;
    margin: 0 auto;
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
  </style>
  