<template>
    <div class="form-container">
      <h1 class="titulo">PROVEEDOR</h1>
  
      <div class="input-group">
        <label for="rut-ci">RUT/CI</label>
        <input v-model="proveedor.rut_ci" type="text" id="rut-ci" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="nombre">Nombre</label>
        <input v-model="proveedor.nombre" type="text" id="nombre" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="alias">Alias</label>
        <input v-model="proveedor.alias" type="text" id="alias" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="telefono">Teléfono</label>
        <input v-model="proveedor.telefono" type="text" id="telefono" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="whatsapp">Whatsapp</label>
        <input v-model="proveedor.whatsapp" type="text" id="whatsapp" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="mail">Mail</label>
        <input v-model="proveedor.mail" type="text" id="mail" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="departamento">Departamento</label>
        <select v-model="proveedor.departamento" id="departamento" @change="cargarLocalidades">
          <option v-for="departamento in departamentos" :key="departamento" :value="departamento">{{ departamento }}</option>
        </select>
      </div>
  
      <div class="input-group">
        <label for="localidad">Localidad</label>
        <select v-model="proveedor.localidad" id="localidad">
          <option v-for="localidad in localidades" :key="localidad" :value="localidad">{{ localidad }}</option>
        </select>
      </div>
  
      <div class="input-group">
        <label for="direccion">Dirección</label>
        <input v-model="proveedor.direccion" type="text" id="direccion" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="rubro">Rubro</label>
        <select v-model="proveedor.rubro" id="rubro">
          <option v-for="rubro in rubros" :key="rubro.id" :value="rubro.nombre">{{ rubro.nombre }}</option>
        </select>
        <button @click="mostrarCampoNuevoRubro" class="btn-nuevo">NUEVO</button>
      </div>
  
      <!-- Campo de Nuevo Rubro -->
      <div v-if="mostrarNuevoRubro" class="nuevo-rubro">
        <input v-model="nuevoRubroNombre" type="text" placeholder="Ingrese nuevo rubro..." />
        <button @click="guardarNuevoRubro" class="btn-guardar">Guardar</button>
        <button @click="cerrarNuevoRubro" class="btn-cerrar">Cerrar</button>
      </div>
  
      <div class="input-group">
        <label for="comentarios">Comentarios</label>
        <input v-model="proveedor.comentarios" type="text" id="comentarios" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="calificacion">Calificación</label>
        <select v-model="proveedor.calificacion" id="calificacion">
          <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>
  
      <div class="buttons-container">
        <button class="btn" @click="guardarProveedor">GUARDAR</button>
        <button @click="goTo('MenuPage')" class="btn">Menú</button>
      </div>
  
      <div v-if="mensaje" :class="['mensaje', exito ? 'exito' : 'error']">
        {{ mensaje }}
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        proveedor: {
          rut_ci: '',
          nombre: '',
          alias: '',
          telefono: '',
          whatsapp: '',
          mail: '',
          departamento: '',
          localidad: '',
          direccion: '',
          rubro: '',
          comentarios: '',
          calificacion: ''
        },
        departamentos: [],
        localidades: [],
        rubros: [],
        nuevoRubroNombre: '',
        mostrarNuevoRubro: false,
        mensaje: '',
        exito: false
      };
    },
    methods: {
      async cargarDepartamentos() {
        try {
          const response = await fetch('https://control-taller-1a9d81bbc513.herokuapp.com/departamentos');
          const data = await response.json();
          this.departamentos = data.departamentos;
        } catch (error) {
          console.error('Error:', error);
        }
      },
      async cargarLocalidades() {
        try {
          const response = await fetch(`https://control-taller-1a9d81bbc513.herokuapp.com/localidades?departamento=${this.proveedor.departamento}`);
          const data = await response.json();
          this.localidades = data.localidades;
        } catch (error) {
          console.error('Error:', error);
        }
      },
      async cargarRubros() {
        try {
          const response = await fetch('https://control-taller-1a9d81bbc513.herokuapp.com/rubros');
          const data = await response.json();
          this.rubros = data.rubros;
        } catch (error) {
          console.error('Error:', error);
        }
      },
      mostrarCampoNuevoRubro() {
        this.mostrarNuevoRubro = true;
      },
      cerrarNuevoRubro() {
        this.mostrarNuevoRubro = false;
        this.nuevoRubroNombre = '';
      },
      async guardarNuevoRubro() {
        if (!this.nuevoRubroNombre.trim()) {
          this.mensaje = 'Debe ingresar un nombre para el rubro.';
          this.exito = false;
          return;
        }
  
        try {
          const response = await fetch('https://control-taller-1a9d81bbc513.herokuapp.com/rubroscrear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rubro_nombre: this.nuevoRubroNombre })
          });
  
          if (response.ok) {
            this.mensaje = 'Rubro creado exitosamente.';
            this.exito = true;
            this.cargarRubros();
            this.cerrarNuevoRubro();
          } else {
            const errorData = await response.json();
            this.mensaje = errorData.mensaje || 'Error al crear el rubro.';
            this.exito = false;
          }
        } catch (error) {
          console.error('Error:', error);
          this.mensaje = 'Error al conectar con el servidor.';
          this.exito = false;
        }
      },
      async guardarProveedor() {
      try {
        const response = await fetch('https://control-taller-1a9d81bbc513.herokuapp.com/proveedor', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.proveedor)
        });

        if (response.ok) {
          const data = await response.json();
          this.mensaje = data.message;
          this.exito = true;
          this.limpiarFormulario();
        } else {
          const errorData = await response.json();
          this.mensaje = errorData.message || 'Error al guardar el proveedor.';
          this.exito = false;
        }
      } catch (error) {
        console.error('Error:', error);
        this.mensaje = 'Error al conectar con el servidor.';
        this.exito = false;
      }
    },
    limpiarFormulario() {
      this.proveedor= {
        rut_ci: '',
          nombre: '',
          alias: '',
          telefono: '',
          whatsapp: '',
          mail: '',
          departamento: '',
          localidad: '',
          direccion: '',
          rubro: '',
          comentarios: '',
          calificacion: '' 
      };
    },
    goTo(routeName) {
        this.$router.push({ name: routeName });
      },
    },
    created() {
      this.cargarDepartamentos();
      this.cargarRubros();
    },

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
  
  .input-group {
    margin-bottom: 20px;
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
  .nuevo-rubro-container {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 10px;
  }
  
  .nuevo-rubro-container input {
    flex-grow: 1;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  
  .btn-guardar, .btn-cerrar {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 4px;
  }
  
  .btn-cerrar {
    background-color: #f44336;
  }
  </style>
  