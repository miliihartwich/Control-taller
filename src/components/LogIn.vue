<template>
  <div class="login">
    <div class="header">
      <h1>Iniciar sesión</h1>
    </div>

    <div class="form-container">
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="input-group">
        <label for="username">Usuario</label>
        <input
          type="text"
          v-model="username"
          id="username"
          placeholder="Ingrese su usuario"
        />
      </div>

      <div class="input-group">
        <label for="password">Contraseña</label>
        <input
          type="password"
          v-model="password"
          id="password"
          placeholder="Ingrese su contraseña"
        />
        <router-link to="/forgot-password" class="forgot-password-link">
          Olvidé mi contraseña
        </router-link>
      </div>

      <div class="buttons-container">
        <button @click="login" class="btn">Iniciar sesión</button>
        <router-link to="/">
          <button class="btn">Volver</button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "LoginPage",
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
    };
  },
  methods: {
    async login() {
      this.errorMessage = ""; // Limpiar mensaje de error previo

      if (!this.username || !this.password) {
        this.errorMessage = "Por favor, complete todos los campos.";
        return;
      }

      console.log("Intentando iniciar sesión con:", this.username, this.password);

      try {
        const response = await axios.post("https://control-taller-1a9d81bbc513.herokuapp.com/login", {
          usuario: this.username,
          contrasena: this.password,
        });

        console.log("Respuesta del backend:", response.data);

        if (response.data.access_token) {
          const { usuario, cedula, rol } = response.data;

          // Guardar datos en localStorage
          localStorage.setItem("access_token", response.data.access_token);
          localStorage.setItem("usuario", usuario);
          localStorage.setItem("cedula", cedula);
          localStorage.setItem("rol", rol);

          // 📌 Redirigir según el rol
          if (rol === "operario") {
            this.$router.push("/intervencion-operario"); // Página de operarios
          } else if (rol === "propietario" || rol === "administracion") {
            this.$router.push("/menu"); // Página principal para admin y propietario
          }
        }
      } catch (error) {
        console.error("Error en la solicitud:", error);

        if (error.response) {
          if (error.response.status === 400) {
            this.errorMessage = "Solicitud incorrecta. Verifique los datos.";
          } else if (error.response.status === 401) {
            this.errorMessage = "Contraseña incorrecta.";
          } else if (error.response.status === 404) {
            this.errorMessage = "Usuario no encontrado.";
          } else {
            this.errorMessage = "Error en el servidor. Intente más tarde.";
          }
        } else {
          this.errorMessage = "No se pudo conectar con el servidor.";
        }
      }
    },
  },
};
</script>



<style scoped>
.login {
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

input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 5px;
}

.forgot-password-link {
  display: block;
  margin-top: 10px;
  color: rgba(214, 15, 15, 0.8);
  text-decoration: none;
  font-size: 1rem;
}

.forgot-password-link:hover {
  text-decoration: underline;
}

.buttons-container {
  margin-top: 30px;
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
}

.btn:hover {
  background-color: rgba(43, 0, 255);
}

.error-message {
  color: red;
  margin-bottom: 15px;
  font-size: 1.1rem;
  font-weight: bold;
}
</style>
