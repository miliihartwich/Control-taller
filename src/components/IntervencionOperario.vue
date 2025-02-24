<template>
  <div class="form-container">
    <h1 class="titulo">INTERVENCIÓN</h1>

    <label>Operario</label>
    <input type="text" v-model="intervencion.empleado" disabled />

    <label for="division">División</label>
    <select id="division" v-model="intervencion.division" @change="cargarTipos(); limpiarMensaje()">
      <option value="">Seleccione una división</option>
      <option v-for="div in divisiones" :key="div" :value="div">{{ div }}</option>
    </select>

    <label for="tipo">Tipo</label>
    <select id="tipo" v-model="intervencion.tipo" @change="cargarDescripciones(); limpiarMensaje()">
      <option value="">Seleccione un tipo</option>
      <option v-for="tipo in tipos" :key="tipo" :value="tipo">{{ tipo }}</option>
    </select>

    <label for="descripcion">Descripción</label>
    <select id="descripcion" v-model="intervencion.descripcion" @change="limpiarMensaje">
      <option value="">Seleccione una descripción</option>
      <option v-for="desc in descripciones" :key="desc" :value="desc">{{ desc }}</option>
    </select>

    <div class="buttons-container">
      <button @click="goTo('OrdenesForm')" class="btn btn-red">Nueva Orden</button>
    </div>

    <div v-if="!mostrandoIntervencion">
      <button class="btn btn-red" @click="iniciarIntervencion(); limpiarMensaje()">Inicio intervención</button>
    </div>

    <div v-if="mostrandoIntervencion">
      <label for="fecha">Fecha</label>
      <input id="fecha" type="text" v-model="intervencion.fecha" disabled />

      <label for="hora-inicio">Hora inicio</label>
      <input id="hora-inicio" type="text" v-model="intervencion.hora_inicio" disabled />

      <div class="buttons-container">
        <button class="btn btn-red" @click="finalizarIntervencion">Finalizar Intervención</button>

      </div>

      <label for="hora-fin">Hora fin</label>
      <input id="hora-fin" type="text" v-model="intervencion.hora_fin" disabled />
    </div>

    <div v-if="mensaje" :class="['mensaje', exito ? 'mensaje-exito' : 'mensaje-error']">
  {{ mensaje }}
</div>

<div class="buttons-container">
  <button class="btn" @click="nuevaIntervencion">Nueva intervención</button>
  <button class="btn" @click="confirmarCerrarSesion">Cerrar sesión</button>
  <button class="btn">Cambiar Contraseña</button>
</div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
  return {
    empleados: [],
    divisiones: [],
    tipos: [],
    descripciones: [],
    intervencion: {
      empleado: "",
      division: "",
      tipo: "",
      descripcion: "",
      fecha: "",
      hora_inicio: "",
      hora_fin: "",
    },
    ultimaIntervencion: {  // Guarda los valores de la última intervención finalizada
      division: "",
      tipo: "",
      descripcion: ""
    },
    mensaje: "",
    exito: false,
    mostrandoIntervencion: false,
  };

  },
  methods: {
    async cargarEmpleados() {
      try {
        const cedulaUsuario = localStorage.getItem("cedula");
        if (!cedulaUsuario) {
          this.intervencion.empleado = "Cédula no disponible";
          return;
        }
        this.intervencion.empleado = cedulaUsuario;
      } catch (error) {
        console.error("Error al cargar empleados:", error);
      }
    },
    async cargarDivisiones() {
      try {
        const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/divisiones");
        this.divisiones = response.data;
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
        this.tipos = response.data;
      } catch (error) {
        console.error("Error al cargar tipos:", error);
      }
    },
    async cargarDescripciones() {
      if (!this.intervencion.tipo) return;
      try {
        const response = await axios.get(`https://control-taller-1a9d81bbc513.herokuapp.com/descripcion_por_tipo/${this.intervencion.tipo}`);
        this.descripciones = response.data;
      } catch (error) {
        console.error("Error al cargar descripciones:", error);
      }
    },
    async guardarIntervencion() {
  const token = localStorage.getItem("access_token") || "";
  if (!token) {
    this.mensaje = "Error: No tienes una sesión activa.";
    this.exito = false;
    return;
  }

  try {
    // Evitar guardar si solo se inició la intervención pero no se ha finalizado
    if (!this.intervencion.hora_fin) {
      return;
    }

    await axios.post("https://control-taller-1a9d81bbc513.herokuapp.com/intervenciones", this.intervencion, {
      headers: { Authorization: `Bearer ${token}` },
    });

    this.mensaje = "Intervención guardada correctamente.";
    this.exito = true;
  } catch (error) {
    this.mensaje = error.response?.data?.error || "Error en el servidor.";
    this.exito = false;
  }

    },
    iniciarIntervencion() {
      const now = new Date();
      this.intervencion.fecha = now.toISOString().split("T")[0];
      this.intervencion.hora_inicio = now.toLocaleTimeString("es-ES", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
      this.mostrandoIntervencion = true;
      this.guardarIntervencion();
    },
    finalizarIntervencion() {
  this.intervencion.hora_fin = new Date().toLocaleTimeString("es-ES", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  // Guardar los últimos valores usados en la intervención
  this.ultimaIntervencion = {
    division: this.intervencion.division,
    tipo: this.intervencion.tipo,
    descripcion: this.intervencion.descripcion
  };

  this.guardarIntervencion();
},
async nuevaIntervencion() {
  if (this.mostrandoIntervencion && this.intervencion.hora_inicio && !this.intervencion.hora_fin) {
    // Solo guardar si la intervención ha iniciado pero no se ha finalizado aún
    this.intervencion.hora_fin = new Date().toLocaleTimeString("es-ES", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  // Reiniciar intervención con los últimos valores usados
  this.intervencion = {
    empleado: this.intervencion.empleado,
    division: this.ultimaIntervencion.division || "",
    tipo: this.ultimaIntervencion.tipo || "",
    descripcion: this.ultimaIntervencion.descripcion || "",
    fecha: "",
    hora_inicio:"",
    hora_fin: "",
  };

  this.mostrandoIntervencion = false; 

},
limpiarMensaje() {
  this.mensaje = "";
},
confirmarCerrarSesion() {
    if (window.confirm("¿Seguro que quieres cerrar sesión?")) {
      localStorage.removeItem("access_token");
      this.$router.push("/"); // Redirige a la página de inicio
    }
  },
  goTo(routeName) {
        this.$router.push({ name: routeName });
      },

  },
  mounted() {
    this.cargarEmpleados();
    this.cargarDivisiones();
    if (!localStorage.getItem("access_token")) {
    this.$router.push({ name: "Login" });
  }
  },
};
</script>


<style scoped>
.form-container {
  width: 100%; /* Ocupar todo el ancho en móviles */
  max-width: 500px; /* No demasiado ancho en pantallas grandes */
  margin: 0 auto;
  padding: 20px;
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
    margin-top: 10px;
  }

  input, select {
    width: 100%;
    padding: 10px;
    font-size: 1rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    margin-top: 5px;
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
    text-align: center;
    flex-grow: 1;
    margin: 5px;
  width: 100%;
  display: block;
}


  .mensaje {
  text-align: center;
  font-size: 1rem;
  font-weight: bold;
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
}

.mensaje-exito {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.mensaje-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

</style>
