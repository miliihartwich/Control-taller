import { createRouter, createWebHistory } from 'vue-router';
import Home from './components/HomePage.vue';
import Login from './components/LogIn.vue';
import Register from './components/Register.vue';
import EmpleadoForm from './components/EmpleadoForm.vue';
import ProveedorForm from './components/ProveedorForm.vue';
import ClienteForm from './components/ClienteForm.vue';
import OrdenesForm from './components/OrdenesForm.vue';
import IntervencionForm from './components/IntervencionForm.vue';
import IntervencionOperario from './components/IntervencionOperario.vue';
import ComprasForm from './components/ComprasForm.vue';
import ConfiguracionesForm from './components/ConfiguracionesForm.vue';
import VerEmpleados from './components/VerEmpleados.vue';
import VerClientes from './components/VerClientes.vue';
import VerProveedores from './components/VerProveedores.vue';
import ConsultaIntervenciones from './components/ConsultaIntervenciones.vue';
import ConsultaCostosPorOrden from './components/ConsultaCostosPorOrden.vue';
import ClasificacionOrdenesForm from './components/ClasificacionOrdenesForm.vue';
import MenuPage from './components/MenuPage.vue';
import CambiarContrasena from './components/CambiarContrasena.vue';
import EditarRoles from './components/EditarRoles.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/menu', name: 'MenuPage', component: MenuPage, meta: { requiresAuth: true } },
  { path: '/empleado-form', name: 'EmpleadoForm', component: EmpleadoForm, meta: { requiresAuth: true } },
  { path: '/proveedor-form', name: 'ProveedorForm', component: ProveedorForm, meta: { requiresAuth: true } },
  { path: '/cliente-form', name: 'ClienteForm', component: ClienteForm, meta: { requiresAuth: true } },
  { path: '/ordenes-form', name: 'OrdenesForm', component: OrdenesForm, meta: { requiresAuth: true } },
  { path: '/intervencion-form', name: 'IntervencionForm', component: IntervencionForm, meta: { requiresAuth: true } },
  { path: '/intervencion-operario', name: 'IntervencionOperario', component: IntervencionOperario, meta: { requiresAuth: true, role: 'operario' } },
  { path: '/compras-form', name: 'ComprasForm', component: ComprasForm, meta: { requiresAuth: true } },
  { path: '/parametros-form', name: 'ConfiguracionesForm', component: ConfiguracionesForm, meta: { requiresAuth: true } },
  { path: '/ver-empleados', name: 'VerEmpleados', component: VerEmpleados, meta: { requiresAuth: true } },
  { path: '/ver-clientes', name: 'VerClientes', component: VerClientes, meta: { requiresAuth: true } },
  { path: '/ver-proveedores', name: 'VerProveedores', component: VerProveedores, meta: { requiresAuth: true } },
  { path: '/consulta-intervenciones', name: 'ConsultaIntervenciones', component: ConsultaIntervenciones, meta: { requiresAuth: true } },
  { path: '/consulta-costos-por-orden', name: 'ConsultaCostosPorOrden', component: ConsultaCostosPorOrden, meta: { requiresAuth: true } },
  { path: '/clasificacion-ordenes', name: 'ClasificacionOrdenes', component: ClasificacionOrdenesForm, meta: { requiresAuth: true } },
  { path: '/cambiar-contrasena', name: 'CambiarContrasena', component: CambiarContrasena, meta: { requiresAuth: true } },
  { path: '/editar-roles', name: 'EditarRoles', component: EditarRoles, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const usuarioAutenticado = !!localStorage.getItem('access_token'); // Convierte a booleano
  const rol = localStorage.getItem('rol') || ''; 

  // ✅ Permitir el acceso libre a Home y Login
  if (to.path === '/' || to.path === '/login'|| to.path === '/register') {
    return next(); 
  }

  // 🔒 Si el usuario NO está autenticado, mandarlo al login
  if (!usuarioAutenticado) {
    console.log("Usuario no autenticado, redirigiendo a login.");
    return next('/login');
  }

  // 🔒 Si es operario, solo puede acceder a estas rutas
  if (rol === 'operario' && !['/intervencion-operario', '/ordenes-form','/cambiar-contrasena'].includes(to.path)) {
    console.log("Operario intentando acceder a una ruta no permitida, redirigiendo.");
    return next('/intervencion-operario'); 
  }

  // 🔒 Solo el propietario puede acceder a Editar Roles
  if (to.path === '/editar-roles' && rol !== 'propietario') {
    console.log("Usuario sin permisos para editar roles, redirigiendo.");
    return next('/'); 
  }

  // ✅ Si ninguna condición lo bloquea, permitir el acceso
  next();
});




export default router;