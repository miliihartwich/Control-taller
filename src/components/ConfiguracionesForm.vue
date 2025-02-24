<template>
  <div class="parametros-container">
    <h1 class="titulo">Parámetros</h1>

    <!-- Mensajes -->
    <div v-if="mensaje.texto" :class="['mensaje', mensaje.tipo]">
      {{ mensaje.texto }}
      <div v-if="mensaje.tipo === 'confirmacion'">
        <button @click="guardarConfiguracion(mensaje.clave)">Aceptar</button>
        <button @click="cancelarConfirmacion(mensaje.clave)">Cancelar</button>
      </div>
    </div>

    <!-- Factor Fijo -->
    <div class="parametro">
      <label>Factor fijo</label>
      <input 
        type="text" 
        v-model="configuraciones.factor_fijo" 
        @input="validarNumero('factor_fijo')"
        :disabled="!editando.factor_fijo"
      />
      <button v-if="!editando.factor_fijo" @click="iniciarEdicion('factor_fijo')">Editar</button>
      <button v-else @click="confirmarGuardado('factor_fijo')">Guardar</button>
    </div>

    <!-- Costo Fijo por Hora -->
    <div class="parametro">
      <label>Costo fijo por hora</label>
      <input 
        type="text" 
        v-model="configuraciones.costo_fijo_por_hora" 
        @input="validarNumero('costo_fijo_por_hora')"
        :disabled="!editando.costo_fijo_por_hora"
      />
      <button v-if="!editando.costo_fijo_por_hora" @click="iniciarEdicion('costo_fijo_por_hora')">Editar</button>
      <button v-else @click="confirmarGuardado('costo_fijo_por_hora')">Guardar</button>
    </div>

    <div class="botones">
      <button @click="goTo('MenuPage')" class="botones">Menú</button>
      <button @click="goTo('ConsultaCostosPorOrden')" class="botones">Costos por orden</button>      
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      configuraciones: {}, // Valores desde la base de datos
      valoresAnteriores: {}, // Almacena valores antes de la edición
      editando: { factor_fijo: false, costo_fijo_por_hora: false }, // Estado de edición
      mensaje: { texto: '', tipo: '', clave: '' },
    };
  },
  mounted() {
    this.obtenerConfiguraciones();
  },
  methods: {
    async obtenerConfiguraciones() {
      try {
        const response = await fetch("https://control-taller-1a9d81bbc513.herokuapp.com/configuraciones");
        const data = await response.json();

        if (data.error) {
          this.mostrarMensaje("Error al obtener configuraciones", "error");
          return;
        }

        this.configuraciones = data;
      } catch (error) {
        this.mostrarMensaje("Error en la solicitud", "error");
      }
    },

    iniciarEdicion(clave) {
      this.valoresAnteriores[clave] = this.configuraciones[clave]; // Guarda el valor original
      this.editando[clave] = true;
    },

    confirmarGuardado(clave) {
      this.mensaje = { texto: `¿Seguro desea editar el ${clave.replace('_', ' ')}?`, tipo: "confirmacion", clave };
    },

    async guardarConfiguracion(clave) {
      try {
        const nuevoValor = this.configuraciones[clave];

        if (isNaN(nuevoValor) || nuevoValor === "") {
          this.mostrarMensaje("El valor debe ser numérico", "error");
          return;
        }

        const response = await fetch(`https://control-taller-1a9d81bbc513.herokuapp.com/configuraciones/${clave}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ valor: nuevoValor }),
        });

        const data = await response.json();

        if (data.error) {
          this.mostrarMensaje("Error al actualizar: " + data.error, "error");
        } else {
          this.mostrarMensaje("Configuración actualizada con éxito", "exito");
          this.editando[clave] = false; // Desactivar modo edición
        }
      } catch (error) {
        this.mostrarMensaje("Error en la solicitud: " + error.message, "error");
      }
    },

    cancelarConfirmacion(clave) {
      this.configuraciones[clave] = this.valoresAnteriores[clave]; // Restaurar valor anterior
      this.editando[clave] = false;
      this.mensaje = { texto: '', tipo: '', clave: '' };
    },

    validarNumero(clave) {
      this.configuraciones[clave] = this.configuraciones[clave].replace(/[^0-9.]/g, '');
    },
    goTo(routeName) {
        this.$router.push({ name: routeName });
      },

    mostrarMensaje(texto, tipo, clave = '') {
      this.mensaje = { texto, tipo, clave };
      if (tipo !== 'confirmacion') {
        setTimeout(() => {
          this.mensaje.texto = "";
        }, 3000);
      }
    }
  }
};
</script>

<style scoped>
.parametros-container {
  width: 400px;
  margin: 20px auto;
  text-align: center;
}

.titulo {
  background-color: #a84d4d;
  color: white;
  padding: 10px;
  font-weight: bold;
}

.mensaje {
  padding: 10px;
  margin: 10px 0;
  font-weight: bold;
  border-radius: 5px;
}

.mensaje.exito {
  background-color: #4caf50;
  color: white;
}

.mensaje.error {
  background-color: #f44336;
  color: white;
}

.mensaje.confirmacion {
  background-color: #ff9800;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mensaje.confirmacion button {
  margin: 5px;
  background-color: white;
  color: black;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
}

.parametro {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 10px 0;
}

input {
  flex: 1;
  margin: 0 10px;
  padding: 5px;
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
</style>
