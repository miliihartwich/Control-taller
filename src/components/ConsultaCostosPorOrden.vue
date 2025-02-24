<template>
    <div class="container mx-auto p-4">
      <!-- Título -->
      <div class="titulo text-center">COSTOS POR ORDEN</div>
  
      <!-- Filtros -->
      <div class="p-4 bg-gray-100">
        <h2 class="titulo2">Elegir Orden:</h2>
        <div class="grid grid-cols-3 gap-4 mt-2">
          <label>
            División:
            <select class="busqueda w-full" v-model="selectedDivision" @change="fetchTipos">
              <option value="">Seleccione una opción</option>
              <option v-for="division in divisiones" :key="division" :value="division">{{ division }}</option>
            </select>
          </label>
  
          <label>
            Tipo:
            <select class="busqueda w-full" v-model="selectedTipo" @change="fetchDescripciones">
              <option value="">Seleccione una opción</option>
              <option v-for="tipo in tipos" :key="tipo" :value="tipo">{{ tipo }}</option>
            </select>
          </label>
  
          <label>
            Descripción:
            <select class="busqueda w-full" v-model="selectedDescripcion" @change="fetchOrdenDetalle">
              <option value="">Seleccione una opción</option>
              <option v-for="descripcion in descripciones" :key="descripcion" :value="descripcion">{{ descripcion }}</option>              
            </select>
          </label>
        </div>
        <button class="bg-blue-600 text-white px-4 py-2 rounded" @click="fetchOrdenDetalle">Buscar Orden</button>



      <!-- Datos -->
      <div class="p-4 bg-white">
        <h2 class="titulo2">Datos</h2>
        <div class="grid grid-cols-2 gap-4 mt-2">
            <label>Nro de orden: <input type="text" class="busqueda w-full" v-model="numeroOrden" disabled /></label>
<label>Cliente: <input type="text" class="busqueda w-full" v-model="clienteNombre" disabled /></label>
<label>Fecha inicio: 
  <input type="date" class="busqueda w-full" :value="fechaInicio" @input="fechaInicio = $event.target.value" disabled />
</label>
<label>Fecha fin: 
  <input type="date" class="busqueda w-full" :value="fechaFin" @input="fechaFin = $event.target.value" disabled />
</label>

<label>Costo total: <input type="text" class="busqueda w-full" v-model="costoTotalOrden" disabled /></label>
        </div>
      </div>


            <!-- Modal de autenticación -->
            <div v-if="mostrarModal" class="modal">
        <div class="modal-contenido">
        <h2>La edición de estos datos modificará los resultados de los costos</h2>
          <h3>Ingrese la contraseña para acceder</h3>
          <input type="password" v-model="password" class="busqueda w-full" />
          <div class="flex justify-end mt-4">
            <button class="bg-red-600 text-white px-4 py-2 rounded" @click="validarPassword">Aceptar</button>
            <button class="bg-gray-400 text-white px-4 py-2 rounded ml-2" @click="cerrarModal">Cerrar</button>
          </div>
        </div>
      </div>
    
  
      <!-- Mano de obra -->
      <div class="p-4 bg-gray-100">
        <h2 class="titulo2">Mano de obra</h2>
        <table class="empleados-tabla w-full mt-2">
          <thead>
            <tr>
              <th>Empleado</th>
              <th>Horas</th>
              <th>Costo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(empleado, index) in empleados" :key="index">
              <td>{{ empleado.nombre }}</td>
              <td>{{ empleado.horas }}</td>
              <td>{{ empleado.costo }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td></td>
              <td class="total">Total horas:<br>{{ totalHoras }}</td>
              <td class="total">Total costo:<br>{{ totalCosto }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
  
      <!-- Compras -->
      <div class="p-4 bg-white">
        <h2 class="titulo">Compras</h2>
        <table class="empleados-tabla w-full mt-2">
          <thead>
            <tr>
              <th>Proveedor</th>
              <th>Nro Factura</th>
              <th>Material</th>
              <th>Importe</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(compra, index) in compras" :key="index">
              <td>{{ compra.proveedor }}</td>
              <td>{{ compra.numero_factura }}</td>
              <td>{{ compra.material }}</td>
              <td>{{ compra.importe }}</td>
            </tr>
          </tbody>
          <tfoot>
      <tr>
        <td colspan="3"></td>
        <td class="total"><strong>Total importe:<br>{{ totalImporte }}</strong></td>
      </tr>
    </tfoot>
        </table>
      </div>

      <div class="p-4 bg-gray-100">
        <h2 class="titulo2">Parámetros</h2>
        <div class="grid grid-cols-3 gap-4 mt-2">         
          <label>Factor Fijo: <input type="text" class="busqueda w-24" v-model="factorFijo" disabled /></label>
          <label>Costo Fijo por Hora: <input type="text" class="busqueda w-24" v-model="costoFijoHora" disabled /></label>
          <button class="bg-red-600 text-white px-4 py-2 rounded" @click="solicitarAutenticacion">Editar parámetros</button>
        </div>
      </div>
    </div>
 
  
      <!-- Botón de menú -->
      <div class="text-center mt-4">
        <button @click="goTo('MenuPage')" class="botones">Menú</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        empleados: [
          { nombre: "nombre", horas: 0, costo: 0 },
          { nombre: "nombre", horas: 0, costo: 0 },
        ],
        compras: [
          { proveedor: "nombre", factura: "Número de factura", material: "Material", importe: "Importe" },
          { proveedor: "nombre", factura: "Número de factura", material: "Material", importe: "Importe" },
        ],
        divisiones: [],
        tipos: [],
        descripciones: [],
        selectedDivision: "",
        selectedTipo: "",
        selectedDescripcion: "",
        factorFijo: "",
        costoFijoHora: "",
        mostrarModal: false,
        password: "",
        numeroOrden: "",
        clienteNombre: "",
        fechaInicio: "",
        fechaFin: "",
        costoTotalOrden: "",  
        totalHoras: "00:00", // Inicializa en formato hh:mm      
      };
    },
    computed: {
  totalCosto() {
    return this.empleados.reduce((sum, e) => sum + Number(e.costo), 0);
  },
  totalImporte() {
    return this.compras.reduce((sum, c) => sum + Number(c.importe), 0);
  },
},
    methods: {
      async fetchDivisiones() {
        const response = await fetch('https://control-taller-1a9d81bbc513.herokuapp.com/divisiones');
        this.divisiones = await response.json();
      },
      async fetchTipos() {
        if (this.selectedDivision) {
          const response = await fetch(`https://control-taller-1a9d81bbc513.herokuapp.com/tipos_por_division/${this.selectedDivision}`);
          this.tipos = await response.json();
        }
      },
      async fetchDescripciones() {
        if (this.selectedTipo) {
          const response = await fetch(`https://control-taller-1a9d81bbc513.herokuapp.com/descripcion_por_tipo/${this.selectedTipo}`);
          this.descripciones = await response.json();
        }
      },
      async fetchConfiguraciones() {
        try {
          const response = await fetch('https://control-taller-1a9d81bbc513.herokuapp.com/configuraciones');
          const data = await response.json();
          this.factorFijo = data["factor_fijo"] || "N/A";
          this.costoFijoHora = data["costo_fijo_por_hora"] || "N/A";
        } catch (error) {
          console.error("Error al obtener configuraciones", error);
        }
      },
      solicitarAutenticacion() {
        this.mostrarModal = true;
      },
      cerrarModal() {
        this.mostrarModal = false;
        this.password = "";
      },
      validarPassword() {
        if (this.password === "1234") { 
          window.location.href = "/parametros-form";
        } else {
          alert("Contraseña incorrecta");
        }
      },
      goTo(routeName) {
        this.$router.push({ name: routeName });
      },

      async fetchOrdenDetalle() {
  if (!this.selectedDivision || !this.selectedTipo || !this.selectedDescripcion) {
    alert("Seleccione División, Tipo y Descripción.");
    return;
  }

  try {
    const response = await fetch(`https://control-taller-1a9d81bbc513.herokuapp.com/ordenes/detalle?division=${this.selectedDivision}&tipo=${this.selectedTipo}&descripcion=${this.selectedDescripcion}`);
    const data = await response.json();
    console.log("Datos recibidos:", data); // Verifica la estructura de los datos

    if (data.error) {
      alert(data.error);
      return;
    }
    this.fechaInicio = data.fecha_inicio ? new Date(data.fecha_inicio).toISOString().split("T")[0] : "";
this.fechaFin = data.fecha_fin ? new Date(data.fecha_fin).toISOString().split("T")[0] : "";
this.$forceUpdate();  // <-- Esto fuerza la actualización del DOM
    console.log("Fecha inicio cruda:", data.fecha_inicio);
console.log("Fecha fin cruda:", data.fecha_fin);
console.log("Fecha inicio procesada:", this.fechaInicio);
console.log("Fecha fin procesada:", this.fechaFin);
console.log("Datos recibidos:", JSON.stringify(data, null, 2)); 

    // Asignar los datos al formulario
    this.numeroOrden = data.numero_orden || "";
    this.clienteNombre = data.cliente_nombre || "";
    // Convertir fechas al formato YYYY-MM-DD para inputs tipo "date"
    this.fechaInicio = data.fecha_inicio
      ? new Date(data.fecha_inicio).toISOString().split("T")[0]
      : "";
    this.fechaFin = data.fecha_fin
      ? new Date(data.fecha_fin).toISOString().split("T")[0]
      : "";
    this.costoTotalOrden = data.costo_total_orden || "";
    this.factorFijo = data.configuraciones?.factor_fijo || "";
    this.costoFijoHora = data.configuraciones?.costo_fijo_por_hora || "";
    this.totalHoras = data.total_horas || "00:00"; 


    this.compras = data.compras || [];
    this.empleados = data["mano de obra"]?.map(emp => ({
  nombre: emp.nombre,
  horas: emp.total_horas_trabajadas,
  costo: emp.costo_total
})) || [];


  } catch (error) {
    console.error("Error al obtener los detalles de la orden:", error);
  }
}
    },
    mounted() {
      this.fetchDivisiones();
      this.fetchConfiguraciones();
    }
  };
  </script>
  
  
  <style scoped>
  .titulo {
    background-color: #b53b3b;
    color: white;
    padding: 20px;
    font-weight: bold;
    font-size: 1.5rem;
  }
  .titulo2 {
    background-color: #b53b3b;
    color: white;
    padding: 10px;
    font-weight: bold;
  }
  
  .busqueda {
    width: 100%;
    padding: 8px;
    margin: 5px 0;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .empleados-tabla {
    width: 100%;
    border-collapse: collapse;
  }
  
  .empleados-tabla th, .empleados-tabla td {
    border: 1px solid #000;
    padding: 8px;
    text-align: left;
  }
  
  .empleados-tabla thead {
    background-color: #b53b3b;
    color: white;
  }
  
  .total {
    font-weight: bold;
    text-align: right;
  }
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .modal-contenido {
    background: white;
    padding: 20px;
    border-radius: 5px;
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
  