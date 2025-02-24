<template>
  <div class="register">
    <div class="header">
      <h1>REGISTRARSE</h1>
    </div>
    
    <div class="form-container">
      <div class="input-group">
        <label for="username">Usuario</label>
        <input type="text" id="username" v-model="usuario" placeholder="Escriba aquí..." />
      </div>


      <div class="input-group">
        <label for="contrasena">Contraseña</label>
        <input type="password" id="contrasena" v-model="contrasena" placeholder="Escriba aquí..." />
      </div>

      <div class="input-group">
        <label for="confirm-password">Repita contraseña</label>
        <input type="password" id="confirm-password" v-model="confirmContrasena" placeholder="Escriba aquí..." />
      </div>

      <div class="input-group">
        <label for="empleado">Empleado</label>
        <select id="empleado" v-model="empleado">
          <option value="" disabled>Elija una opción...</option>
          <option v-for="e in empleados" :key="e.cedula" :value="e.cedula">{{ e.nombre }}</option>
        </select>
      </div>

      <div class="buttons-container">
        <button class="btn" @click="registrar">REGISTRARME</button>
        <router-link to="/">
          <button class="btn">Volver</button>
        </router-link>
      </div>

      <div v-if="mensaje" :class="['mensaje', tipoMensaje]">
        {{ mensaje }}
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  name: "RegisterPage",
  data() {
    return {
      usuario: "",
      rol: "operario",
      contrasena: "",
      confirmContrasena: "",
      empleado: "",
      empleados: [],
      mensaje: "",  // Agregar mensaje para feedback
      tipoMensaje: "" // Puede ser "exito" o "error"
    };
  },
  methods: {
    async fetchEmpleados() {
      try {
        const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/obtener_empleados");
        this.empleados = response.data;
      } catch (error) {
        console.error("Error obteniendo empleados", error);
      }
    },
    async registrar() {
      if (!this.usuario || !this.contrasena || !this.confirmContrasena || !this.empleado) {
        this.mensaje = "Todos los campos son obligatorios.";
        this.tipoMensaje = "error";
        return;
      }
      if (this.contrasena !== this.confirmContrasena) {
        this.mensaje = "Las contraseñas no coinciden.";
        this.tipoMensaje = "error";
        return;
      }

      try {
        const response = await axios.post("https://control-taller-1a9d81bbc513.herokuapp.com/registrar_usuario", {
          usuario: this.usuario,
          rol: this.rol,
          contrasena: this.contrasena,
          cedula: this.empleado
        });

        if (response.data.success) {
  this.mensaje = response.data.message; // Muestra el mensaje del backend
  this.tipoMensaje = "exito"; // Asegura que el mensaje se vea en verde
} else {
  this.mensaje = response.data.message || "Error desconocido";
  this.tipoMensaje = "error";
}



      } catch (error) {
        if (error.response && error.response.data) {
          this.mensaje = error.response.data.message || "Error al registrar usuario";
        } else {
          this.mensaje = "Error de conexión con el servidor";
        }
        this.tipoMensaje = "error";
        console.error(error);
      }
    }
  },
  mounted() {
    this.fetchEmpleados();
  }
};
</script>


<style scoped>
.register {
  text-align: center;
}

.header {
  background-color: rgba(214, 15, 15, 0.8);
  padding: 40px;
  color: white;
}

h1 {
  margin: 0;
  font-size: 3rem;
}

.form-container {
  margin-top: 30px;
  padding: 20px;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  font-size: 1.2rem;
  margin-bottom: 8px;
  display: block;
}

input, select {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 5px;
}

.buttons-container {
  display: flex;
  justify-content: center;
  gap: 20px; /* Espacio entre botones */
}


.btn {
  background-color: rgba(214, 15, 15, 0.8);
  color: white;
  font-size: 1.2rem;
  padding: 15px 40px;
  margin: 10px;
  border: none;
  cursor: pointer;
  width: 200px;
  text-align: center; /* Asegura que el texto esté centrado */
  display: flex;
  align-items: center;
  justify-content: center; /* Centra el texto horizontalmente */
}

.btn:hover {
  background-color: rgba(43, 0, 255);
}

.mensaje {
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  text-align: center;
  font-weight: bold;
}

.exito {
  background-color: #4caf50 !important;
  color: white !important;
}

.error {
  background-color: #f44336 !important;
  color: white !important;
}

</style>
