<template>
  <div class="form-container">
    <div class="titulo">COMPRAS</div>
    
    <label>Proveedor</label>
    <div class="proveedor-container">
      <input type="text" ref="proveedorInput" v-model="searchProveedor" @input="filterProveedores" @focus="handleProveedorFocus"  placeholder="Escriba para buscar..." > 
      <button class="btn-nuevo" @click="mostrarConfirmacion = true">Nuevo</button>
    </div>
    <ul v-if="showDropdown && filteredProveedores.length" class="dropdown">
      <li v-for="proveedor in filteredProveedores" :key="proveedor.rut_ci" @mousedown="selectProveedor(proveedor)">
        {{ proveedor.nombre }} - {{ proveedor.rut_ci }}
      </li>
    </ul>
    
    <div v-if="mostrarConfirmacion" class="confirmacion">
      <p>¿Crear un nuevo proveedor?</p>
      <button @click="irAProveedorForm">Crear</button>
      <button @click="mostrarConfirmacion = false">Cancelar</button>
    </div>
    
    <label>Nro de factura</label>
    <input type="text" v-model="compra.numero_factura">
    
    <label>Fecha</label>
    <input type="date" v-model="compra.fecha">
    
    <label>Moneda</label>
    <select v-model="compra.moneda">
      <option value="USD">USD</option>
      <option value="UYU">UYU</option>
    </select>
    
    <label>Importe</label>
    <input type="number" v-model="compra.importe">
    
    <label>Tipo de IVA</label>
    <select v-model="compra.tipo_iva">
      <option>Básico</option>
      <option>Mínimo</option>
      <option>Exento</option>
    </select>
    
    <label>Tipo de cambio</label>
    <input type="number" v-model="compra.tipo_cambio" :disabled="compra.moneda === 'UYU'">
    
    <label>Importe pesos</label>
    <input type="number" v-model="compra.importe_pesos" disabled>

    <label for="material">Materiales</label>
<div class="material-container">
  <input 
    type="text" 
    ref="materialInput"
    v-model="searchMaterial" 
    @input="filterMateriales" 
    @focus="showAllMateriales" 
    @blur="handleBlurMaterial" 
    placeholder="Escriba para buscar material..."
  >
</div>
<ul v-if="showDropdownMaterial && filteredMateriales.length" class="dropdown">
  <li 
  v-for="material in filteredMateriales" 
  :key="material"
  @mousedown.prevent="selectMaterial(material)" 
>
  {{ material }}
</li>

</ul>



<div class="button-container">
  <button class="btn btn-primary" @click="agregarMaterial">Agregar Material</button>
  <button class="btn btn-secondary" @click="crearNuevoMaterial">Crear Nuevo Material</button>
  <button @click="goTo('MenuPage')" class="btn">Menú</button>
</div>

    <!-- Campo para ingresar nuevo material -->
    <div v-if="mostrarCampo">
    <input type="text" v-model="nuevoMaterial" placeholder="Nombre del material" />
    <button class="btn btn-secondary" @click="agregarNuevoMaterial">Crear</button>
  </div>

<div v-if="materialesAgregados && materialesAgregados.length">
  <table class="table-materiales">
  <thead>
    <tr>
      <th>Material</th>
      <th>Importe</th>
      <th>División</th>
      <th>Tipo</th>
      <th>Descripción</th>
      <th>Número de Factura</th> <!-- Nueva columna -->
    </tr>
  </thead>
  <tbody>
    <tr v-for="(mat, index) in materialesAgregados" :key="index">
      <td>{{ mat.nombre }}</td>
      <td><input v-model="mat.precio" type="number" /></td>
      
      <!-- Selección de División -->
      <td>
        <select v-model="mat.division" @change="cargarTipos(index)">
          <option value="" disabled>Seleccione</option>
          <option v-for="div in mat.divisiones" :key="div" :value="div">{{ div }}</option>
        </select>
      </td>

      <!-- Selección de Tipo -->
      <td>
        <select v-model="mat.tipo" @change="cargarDescripciones(index)">
          <option value="" disabled>Seleccione</option>
          <option v-for="tipo in mat.tipos" :key="tipo" :value="tipo">{{ tipo }}</option>
        </select>
      </td>

      <!-- Selección de Descripción -->
      <td>
        <select v-model="mat.descripcion">
          <option value="" disabled>Seleccione</option>
          <option v-for="desc in mat.descripciones" :key="desc" :value="desc">{{ desc }}</option>
        </select>
      </td>

      <!-- Campo Número de Factura (usando el de la compra) -->
      <td>
        <input v-model="compra.numero_factura" type="text" disabled />
      </td>
    </tr>
  </tbody>
</table>
  <!-- Botón para guardar toda la compra y materiales -->
<button class="btn" @click="guardarCompra">Guardar Todo</button>
<button @click="goTo('MenuPage')" class="btn">Menú</button>
<div v-if="mensajeEstado" :class="['mensaje', tipoMensaje]">
{{ mensajeEstado }}
</div>
</div>
</div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
return {
  compra: {
    proveedor_rut_ci: '',
    numero_factura: '',
    fecha: '',
    moneda: '',
    importe: '',
    tipo_iva: '',
    tipo_cambio: 1,
    importe_pesos: '',
    materiales: [] // Aquí se almacenan los materiales seleccionados
  },
  materialSeleccionado: '', 
  materialesAgregados: [],  
  materiales: [], // aquí se almacenan los materiales de la BD
  searchProveedor: '',
  proveedores: [],
  filteredProveedores: [],
  showDropdown: false,
  mostrarConfirmacion: false,
  mostrarCampo:false,
  mensajeEstado: "",
  tipoMensaje: "", // "exito" o "error"
  nuevoMaterial: "",
  listaMateriales: [], // Aquí se guardarán los materiales de forma temporal
  numeroFactura: "",  // Se llenará al crear la compra
  searchMaterial: '',  // Para almacenar el texto de búsqueda
  filteredMateriales: [],  // Lista filtrada de materiales
  showDropdownMaterial: false,  // Mostrar/ocultar el dropdown
  bloqueandoDropdownProveedor: false, // Nueva bandera
    };
  },
  watch: {
    'compra.moneda'(newMoneda) {
      if (newMoneda === 'UYU') {
        this.compra.tipo_cambio = 1;
        this.compra.importe_pesos = this.compra.importe;
      } else if (newMoneda === 'USD') {
        this.compra.tipo_cambio = null; // Permitir que el usuario lo ingrese
        this.compra.importe_pesos = this.compra.importe * (this.compra.tipo_cambio || 0);
      }
    },
    'compra.importe'(newImporte) {
      if (this.compra.moneda === 'UYU') {
        this.compra.importe_pesos = newImporte;
      } else if (this.compra.moneda === 'USD') {
        this.compra.importe_pesos = newImporte * (this.compra.tipo_cambio || 0);
      }
    },
    'compra.tipo_cambio'(newTipoCambio) {
      if (this.compra.moneda === 'USD') {
        this.compra.importe_pesos = this.compra.importe * (newTipoCambio || 0);
      }
    }
  },
  methods: {
  async fetchProveedores() {
    try {
      const response = await axios.get('https://control-taller-1a9d81bbc513.herokuapp.com/proveedores');
      this.proveedores = response.data;
      this.filteredProveedores = this.proveedores;
    } catch (error) {
      console.error('Error obteniendo proveedores:', error);
    }
  },
  handleProveedorFocus() {
  if (!this.bloqueandoDropdownProveedor) {
    this.showDropdown = true;
  }
},
  filterProveedores() {
    if (this.searchProveedor) {
      this.filteredProveedores = this.proveedores.filter(p =>
        p.nombre.toLowerCase().includes(this.searchProveedor.toLowerCase()) ||
        String(p.rut_ci).toLowerCase().includes(this.searchProveedor.toLowerCase())
      );
    } else {
      this.filteredProveedores = this.proveedores;
    }
    this.showDropdown = true;
  },
  selectProveedor(proveedor) {
    this.searchProveedor = `${proveedor.nombre} - ${proveedor.rut_ci}`;
    this.compra.proveedor_rut_ci = proveedor.rut_ci;
    this.showDropdown = false;
},
  hideDropdown() {
    setTimeout(() => { this.showDropdown = false; }, 200);
  },
  irAProveedorForm() {
    this.$router.push('/proveedor-form');
  },
  async obtenerMateriales() {
  try {
    const response = await axios.get('https://control-taller-1a9d81bbc513.herokuapp.com/materiales-nombres');
    if (!response.data || !Array.isArray(response.data)) {
      console.error("Respuesta inesperada de materiales:", response.data);
      return;
    }
    this.materiales = [...new Set(response.data)]; // Evita duplicados
    console.log("Materiales cargados correctamente:", this.materiales);
  } catch (error) {
    console.error('Error obteniendo materiales:', error);
  }
},
showAllMateriales() {
    this.filteredMateriales = this.materiales;
    this.showDropdownMaterial = true;
    console.log("Material dropdown activado");
  },
filterMateriales() {
    if (this.searchMaterial) {
      this.filteredMateriales = this.materiales.filter(m =>
        m.toLowerCase().includes(this.searchMaterial.toLowerCase())
      );
    } else {
      this.filteredMateriales = this.materiales;
    }
    this.showDropdownMaterial = true;
  },
  selectMaterial(material) {
    this.bloqueandoDropdownProveedor = true; // Bloquear antes de cambiar el valor
  this.searchMaterial = material;  // Guarda el nombre
  this.showDropdownMaterial = false;
  setTimeout(() => document.querySelector("input").focus(), 0); // Evita que el blur borre el texto
    // Asegurar que el foco se mantenga en el input del material
    setTimeout(() => {
    this.$refs.materialInput?.focus();  
  }, 0);
},
  hideDropdownMaterial() {
    setTimeout(() => { this.showDropdownMaterial = false; }, 200);
  },
  // Ocultar el dropdown al hacer clic afuera y limpiar si no se seleccionó nada
  handleBlurMaterial() {
  setTimeout(() => {
    // Si lo que está escrito en el input no está en la lista, lo borra
    if (this.searchMaterial && !this.materiales.includes(this.searchMaterial)) {
      this.searchMaterial = '';  
    }
    this.showDropdownMaterial = false;  
  }, 200);
},
agregarMaterial() {
  if (!this.materiales.includes(this.searchMaterial)) {
    alert("Seleccione un material válido.");
    return;
  }

  console.log("Material agregado:", this.searchMaterial);
  // Aquí agregas el material a la lista de compras

  const nuevoMat = {
        nombre: this.searchMaterial,
        precio: '',
        division: '',
        tipo: '',
        descripcion: '',
        divisiones: [],
        tipos: [],
        descripciones: []
    };

    this.materialesAgregados.push(nuevoMat);
    this.cargarDivisiones(this.materialesAgregados.length - 1);
},
crearNuevoMaterial() {
    this.mostrarCampo = true;
  },
agregarNuevoMaterial() {
    if (this.nuevoMaterial.trim() !== "") {
        // Crear el objeto del material con el mismo formato de los demás
        const nuevoMat = {
            nombre: this.nuevoMaterial, 
            precio: '',
            division: '',
            tipo: '',
            descripcion: '',
            divisiones: [],
            tipos: [],
            descripciones: []
        };

        // Agregar a la lista desplegable
        this.materiales.push(this.nuevoMaterial);

        // Agregar directamente a la tabla
        this.materialesAgregados.push(nuevoMat);

        // Cargar divisiones para el nuevo material
        this.cargarDivisiones(this.materialesAgregados.length - 1);

        // Limpiar el campo de entrada
        this.nuevoMaterial = "";
        this.mostrarCampo = false; // Ocultar el campo después de crear
    }
},

async cargarDivisiones(index) {
    try {
        const response = await axios.get("https://control-taller-1a9d81bbc513.herokuapp.com/divisiones");
        // Asignar las divisiones directamente al material correspondiente
        this.materialesAgregados[index].divisiones = response.data.divisiones || response.data;
    } catch (error) {
        console.error("Error al cargar divisiones:", error);
    }
},

async cargarTipos(index) {
    if (!this.materialesAgregados[index].division) return;

    try {
      const response = await axios.get(
    `https://control-taller-1a9d81bbc513.herokuapp.com/tipos_por_division/${encodeURIComponent(this.materialesAgregados[index].division)}`
);
        // Asignar los tipos directamente al material correspondiente
        this.materialesAgregados[index].tipos = response.data.tipos || response.data;
    } catch (error) {
        console.error("Error al cargar tipos:", error);
    }
},
async cargarDescripciones(index) {
    if (!this.materialesAgregados[index].tipo) {
        console.warn("El tipo de material está vacío");
        return;
    }

    try {
      const response = await axios.get(
    `https://control-taller-1a9d81bbc513.herokuapp.com/descripcion_por_tipo/${encodeURIComponent(this.materialesAgregados[index].tipo)}`
);


        // Asignar las descripciones directamente al material correspondiente
        this.materialesAgregados[index].descripciones = response.data;
    } catch (error) {
        console.error("Error al cargar descripciones:", error);
    }
},

async guardarCompra() {
    if (!this.validarCompra()) return;

    const compraData = {
        proveedor_rut_ci: this.compra.proveedor_rut_ci,
        numero_factura: this.compra.numero_factura,
        fecha: this.compra.fecha,
        moneda: this.compra.moneda,
        importe: this.compra.importe,
        tipo_iva: this.compra.tipo_iva,
        tipo_cambio: this.compra.tipo_cambio,
        importe_pesos: this.compra.importe_pesos,
        materiales: this.materialesAgregados
    };

    try {
        const response = await axios.post('https://control-taller-1a9d81bbc513.herokuapp.com/compras', compraData);
        
        // Mostrar mensaje ANTES de limpiar
        this.mensajeEstado = response.data.message;
        this.tipoMensaje = "exito";
        setTimeout(() => {
    this.mensajeEstado = "";
}, 3000);


        setTimeout(() => {
            this.limpiarFormulario();
        }, 2000); // Espera 2 segundos antes de limpiar
        
    } catch (error) {
        this.mensajeEstado = error.response?.data?.error || "Error al guardar la compra";
        this.tipoMensaje = "error";
    }
},

  validarCompra() {
  if (!this.compra.proveedor_rut_ci || !this.compra.numero_factura || !this.compra.fecha || !this.compra.importe) {
    this.mostrarMensaje("Todos los campos de la compra son obligatorios", "error");
    return false;
  }
  if (!this.materialesAgregados.length) {
    this.mostrarMensaje("Debe agregar al menos un material", "error");
    return false;
  }
  return true;
},
mostrarMensaje(mensaje, tipo) {
  this.mensajeEstado = mensaje;
  this.tipoMensaje = tipo;

  // Opcional: Limpiar el mensaje después de unos segundos
  setTimeout(() => {
    this.mensajeEstado = "";
    this.tipoMensaje = "";
  }, 3000);
},
  limpiarFormulario() {
    this.compra = {
      proveedor_rut_ci: '',
      numero_factura: '',
      fecha: '',
      moneda: '',
      importe: '',
      tipo_iva: '',
      tipo_cambio: 1,
      importe_pesos: '',
    };
    this.materialesAgregados = [];
    this.searchProveedor = '';
  },
  goTo(routeName) {
        this.$router.push({ name: routeName });
      },
},
mounted() {
  this.fetchProveedores();
  this.obtenerMateriales();
  console.log("Materiales cargados:", this.materiales);
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
  padding: 20px;
  text-align: center;
  border-radius: 4px;
  font-size: 2rem;
  font-weight: bold;
}

.proveedor-container {
  display: flex;
  gap: 10px;
}

.btn-nuevo {
  background-color: #b53b3b;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.confirmacion {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-top: 10px;
  text-align: center;
}

.confirmacion button {
  margin: 5px;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.confirmacion button:first-child {
  background-color: #4CAF50;
  color: white;
}

.confirmacion button:last-child {
  background-color: #b53b3b;
  color: white;
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

.btn {
  background-color: #b53b3b;
  color: white;
  font-size: 1.2rem;
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  text-align: center;
  margin-top: 20px;
}

.dropdown {
  border: 1px solid #ccc;
  border-radius: 4px;
  background: white;
  position: absolute;
  width: calc(50% - 20px);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  list-style: none;
  padding: 0;
  margin: 0;
}

.dropdown li {
  padding: 10px;
  cursor: pointer;
}

.dropdown li:hover {
  background-color: #f1f1f1;
}
.mensaje {
margin-top: 10px;
padding: 10px;
border-radius: 4px;
text-align: center;
font-weight: bold;
}

.exito {
background-color: #4CAF50;
color: white;
}

.error {
background-color: #b53b3b;
color: white;
}
.botones-container {
  display: flex;
  gap: 20px; /* Espacio entre los botones */
}

.btn:first-child {
  margin-right: 20px;
}
.form-group select {
  display: block;
  width: 100%;
  margin-bottom: 10px;
}

.button-container {
  display: flex;
  justify-content: flex-start;
  gap: 20px; /* Espaciado entre botones */
  margin-top: 10px;
}

.btn {
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background-color: #a02424;
  color: white;
}

.btn-secondary {
  background-color: #5a5a5a;
  color: white;
}

.btn-danger {
  background-color: #d9534f;
  color: white;
}
.tabla-container {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Alineado a la izquierda */
}

.guardar-btn {
  margin-top: 10px; /* Espacio entre la tabla y el botón */
  align-self: flex-start; /* Asegura que quede alineado con la tabla */
}
.table-materiales {
  width: 100%;
  /* Quita table-layout: fixed para permitir que las celdas crezcan */
  table-layout: auto;
  
  /* Para que haya espacio entre celdas */
  border-collapse: separate;
  border-spacing: 0 8px;
}

.table-materiales th,
.table-materiales td {
  /* Mínimo de ancho para que no se aplasten demasiado */
  min-width: 120px;
  
  /* Borde para visualizar la separación */
  border: 1px solid #ccc;

  /* Ajusta el padding para hacerlo más fino verticalmente */
  padding: 4px 8px;
  
  /* Ajusta la alineación de texto según prefieras */
  text-align: left;
  
  /* Evita que inputs y selects se desborden */
  box-sizing: border-box;
}

.table-materiales th {
  /* Centra el texto de los encabezados */
  text-align: center;
}

.table-materiales input,
.table-materiales select {
  /* Haz que inputs y selects ocupen todo el ancho de la celda */
  width: 100%;
  box-sizing: border-box;
}


</style>