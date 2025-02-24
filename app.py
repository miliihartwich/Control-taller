from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
from flask_jwt_extended import jwt_required,get_jwt_identity,create_access_token
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from flask_cors import CORS
import os
from datetime import datetime
import re
from datetime import timedelta
import traceback
import logging
from flask import request, jsonify

app = Flask(__name__)

# Configuración del token JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "default_secret")
jwt = JWTManager(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# URL de la base de datos en Heroku
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgres://u3h5e2brsm53rv:p3451d21bb1b0ad579c0ade985e62832be96a3828c552090af0526f84cfd5c6d3@c9pv5s2sq0i76o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8nc93m2rfo40l"
)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  # Heroku usa 'require'
        return conn
    except Exception as e:
        raise RuntimeError(f"Error al conectar a la base de datos: {e}")


@app.route('/')
def index():
    return '¡Hola desde Flask!'

#obtener todo de empleado
print(">>> Cargando función todo empleado()")
@app.route('/get_empleado', methods=['GET'])
def get_empleados():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Selecciona las columnas en el orden correcto
    cursor.execute('''
        SELECT cedula, nombre, direccion, celular, remuneracion, factor, fecha_vencimiento_carnet 
        FROM empleado
    ''')
    rows = cursor.fetchall()
    conn.close()

    # Mapea las columnas con sus nombres correspondientes
    empleados = []
    for row in rows:
        empleado = {
            'cedula': row[0],
            'nombre': row[1],
            'direccion': row[2],
            'celular': row[3],
            'remuneracion': row[4],
            'factor': row[5],
            'fecha_vencimiento_carnet': row[6]
        }
        empleados.append(empleado)

    return jsonify(empleados)


#obtener todo de proveedor
print(">>> Cargando función todo proveedor()")
@app.route('/get_proveedor', methods=['GET'])
def get_proveedor():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hacemos un JOIN entre proveedor, localidad, departamento y rubro para obtener los nombres
    cursor.execute('''
        SELECT 
            p.rut_ci, 
            p.nombre, 
            p.alias, 
            p.telefono, 
            p.whatsapp, 
            p.mail, 
            r.rubro_nombre AS rubro,
            p.direccion, 
            l.localidad_nombre AS localidades, 
            d.departamento_nombre AS departamentos,
            p.calificación,
            p.comentarios
        FROM proveedor p
        LEFT JOIN localidades l ON p.localidad_id = l.localidad_id
        LEFT JOIN departamentos d ON p.departamento_id = d.departamento_id
        LEFT JOIN rubro r ON p.rubro_id = r.rubro_id
    ''')
    
    rows = cursor.fetchall()
    conn.close()

    # Mapeo de columnas a un formato JSON amigable para el frontend
    proveedores = [
        {
            'rut_ci': row[0],
            'nombre': row[1],
            'alias': row[2],
            'telefono': row[3],
            'whatsapp': row[4],
            'mail': row[5],
            'rubro': row[6],
            'direccion': row[7],
            'localidad_nombre': row[8],
            'departamento_nombre': row[9],
            'calificación': row[10],
            'comentarios': row[11],
        }
        for row in rows
    ]
    
    return jsonify(proveedores)

#obtener todo de cliente
print(">>> Cargando función todo cliente()")
@app.route('/get_cliente', methods=['GET'])
def get_cliente():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hacemos un JOIN entre cliente, localidad y departamento para obtener los nombres
    cursor.execute('''
        SELECT 
            c.rut_ci, 
            c.nombre, 
            c.alias, 
            c.telefono, 
            c.whatsapp, 
            c.mail, 
            c.direccion, 
            l.localidad_nombre AS localidades, 
            d.departamento_nombre AS departamentos
        FROM cliente c
        LEFT JOIN localidades l ON c.localidad_id = l.localidad_id
        LEFT JOIN departamentos d ON c.departamento_id = d.departamento_id
    ''')
    
    rows = cursor.fetchall()
    conn.close()

    # Mapeo de columnas a un formato JSON amigable para el frontend
    clientes = [
        {
            'rut_ci': row[0],
            'nombre': row[1],
            'alias': row[2],
            'telefono': row[3],
            'whatsapp': row[4],
            'mail': row[5],
            'direccion': row[6],
            'localidad_nombre': row[7],
            'departamento_nombre': row[8]
        }
        for row in rows
    ]
    
    return jsonify(clientes)


#obtener todo de ordenes
print(">>> Cargando función todo ordenes()")
@app.route('/get_orden', methods=['GET'])
def get_orden():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordenes')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# Crear un nuevo cliente
print(">>> Cargando función crearcliente()")
@app.route('/cliente', methods=['POST'])
def create_cliente():
    data = request.get_json()

    # Validar que todos los campos necesarios están presentes
    required_fields = ['rut_ci', 'nombre', 'alias', 'telefono', 'whatsapp', 'mail', 'departamento', 'localidad', 'direccion']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo "{field}" es obligatorio.'}), 400

    # Datos del cliente desde el frontend
    rut_ci = data['rut_ci']
    nombre = data['nombre']
    alias = data['alias']
    telefono = data['telefono']
    whatsapp = data['whatsapp']
    mail = data['mail']
    departamento_nombre = data['departamento']
    localidad_nombre = data['localidad']
    direccion = data['direccion']

    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Obtener el ID del departamento
        cursor.execute('SELECT departamento_id FROM departamentos WHERE departamento_nombre = %s', (departamento_nombre,))
        departamento = cursor.fetchone()

        if not departamento:
            return jsonify({'error': f'El departamento "{departamento_nombre}" no existe.'}), 400

        departamento_id = departamento['departamento_id']

        # Obtener el ID de la localidad correspondiente al departamento
        cursor.execute('SELECT localidad_id FROM localidades WHERE localidad_nombre = %s AND departamento_id = %s',
                       (localidad_nombre, departamento_id))
        localidad = cursor.fetchone()

        if not localidad:
            return jsonify({'error': f'La localidad "{localidad_nombre}" no pertenece al departamento "{departamento_nombre}".'}), 400

        localidad_id = localidad['localidad_id']

        # Insertar el cliente en la base de datos
        cursor.execute(
            'INSERT INTO cliente (rut_ci, nombre, alias, telefono, whatsapp, mail, departamento_id, localidad_id, direccion) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (rut_ci, nombre, alias, telefono, whatsapp, mail, departamento_id, localidad_id, direccion)
        )
        conn.commit()

        return jsonify({'message': 'Cliente creado exitosamente!'}), 201

    except psycopg2.Error as db_error:
        conn.rollback()
        return jsonify({'error': 'Error en la base de datos', 'details': str(db_error)}), 500

    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Error inesperado', 'details': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#listado clientes
@app.route('/clientes', methods=['GET'])
def get_clientes():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute('SELECT rut_ci, nombre FROM cliente')
    clientes = cursor.fetchall()

    conn.close()
    return jsonify(clientes)  # Devuelve una lista de objetos con 'rut_ci' y 'nombre'


print(">>> Cargando función localidades()")
@app.route('/localidades', methods=['GET'])
def obtener_localidades():
    departamento_nombre = request.args.get('departamento')
    if not departamento_nombre:
        return jsonify({'error': 'El nombre del departamento es requerido.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
        # Conectar con el cursor de tipo diccionario
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

    cursor.execute('SELECT l.localidad_nombre FROM localidades l JOIN departamentos d ON l.departamento_id = d.departamento_id WHERE d.departamento_nombre = %s', (departamento_nombre,))
    localidades = [row['localidad_nombre'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return jsonify({'localidades': localidades})

print(">>> Cargando función departamentos()")
@app.route('/departamentos', methods=['GET'])
def obtener_departamentos():
    try:
        # Conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        # Conectar con el cursor de tipo diccionario
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

        # Consulta para obtener los nombres de los departamentos
        cursor.execute('SELECT departamento_nombre FROM departamentos')
        departamentos = [row['departamento_nombre'] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({'departamentos': departamentos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#crear proveedor
print(">>> Cargando función proveedor()")
@app.route('/proveedor', methods=['POST'])
def create_proveedor():
    try:
        # Obtener los datos del request
        data = request.get_json()
        rut_ci = data['rut_ci']
        nombre = data['nombre']
        alias = data['alias']
        telefono = data['telefono']
        whatsapp = data['whatsapp']
        mail = data['mail']
        departamento_nombre = data['departamento']  # Recibe el nombre del departamento
        localidad_nombre = data['localidad']       # Recibe el nombre de la localidad
        direccion = data['direccion']
        rubro_nombre = data['rubro']               # Recibe el nombre del rubro
        comentarios = data['comentarios']
        calificacion = data['calificacion']

        # Conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        # Conectar con el cursor de tipo diccionario
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

        # Obtener el ID del departamento a partir de su nombre
        cursor.execute('SELECT departamento_id FROM departamentos WHERE departamento_nombre = %s', (departamento_nombre,))
        departamento_row = cursor.fetchone()
        if not departamento_row:
            return jsonify({'error': f'El departamento "{departamento_nombre}" no existe'}), 400
        departamento_id = departamento_row['departamento_id']

        # Obtener el ID de la localidad a partir de su nombre
        cursor.execute('SELECT localidad_id FROM localidades WHERE localidad_nombre = %s', (localidad_nombre,))
        localidad_row = cursor.fetchone()
        if not localidad_row:
            return jsonify({'error': f'La localidad "{localidad_nombre}" no existe'}), 400
        localidad_id = localidad_row['localidad_id']

        # Obtener el ID del rubro a partir de su nombre
        cursor.execute('SELECT rubro_id FROM rubro WHERE rubro_nombre = %s', (rubro_nombre,))
        rubro_row = cursor.fetchone()
        if not rubro_row:
            return jsonify({'error': f'El rubro "{rubro_nombre}" no existe'}), 400
        rubro_id = rubro_row['rubro_id']

        # Insertar el nuevo proveedor con los IDs obtenidos
        query = '''
        INSERT INTO proveedor (
            rut_ci, nombre, alias, telefono, whatsapp, mail, 
            departamento_id, localidad_id, direccion, rubro_id, 
            calificación, comentarios
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (
            rut_ci, nombre, alias, telefono, whatsapp, mail,
            departamento_id, localidad_id, direccion, rubro_id,
            calificacion, comentarios
        ))

        # Confirmar los cambios y cerrar la conexión
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Proveedor creado exitosamente!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

print(">>> Cargando función obtener lista de proveedores()")
@app.route('/proveedores', methods=['GET'])
def get_proveedores():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT nombre, rut_ci FROM proveedor')
    proveedores = cursor.fetchall()
    conn.close()
    return jsonify(proveedores)


print(">>> Cargando función runros()")
@app.route('/rubros', methods=['GET'])
def obtener_rubros():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Conectar con el cursor de tipo diccionario
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

        cursor.execute('SELECT rubro_id, rubro_nombre FROM rubro')
        rubros = [{'id': row['rubro_id'], 'nombre': row['rubro_nombre']} for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'rubros': rubros}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Crear nuevo rubro
@app.route('/rubroscrear', methods=['POST'])
def crear_rubro():
    try:
        data = request.get_json()

        if not data or 'rubro_nombre' not in data:
            return jsonify({'mensaje': 'Nombre del rubro es requerido.'}), 400

        rubro_nombre = data['rubro_nombre']

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el rubro ya existe
        cursor.execute("SELECT rubro_id FROM rubro WHERE rubro_nombre = %s", (rubro_nombre,))
        rubro_existente = cursor.fetchone()
        
        if rubro_existente:
            return jsonify({'mensaje': 'El rubro ya existe.'}), 400

        # Insertar nuevo rubro
        cursor.execute("INSERT INTO rubro (rubro_nombre) VALUES (%s) RETURNING rubro_id", (rubro_nombre,))
        nuevo_rubro_id = cursor.fetchone()[0]

        # Confirmar los cambios y cerrar la conexión
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Rubro creado exitosamente.', 'rubro_id': nuevo_rubro_id, 'rubro_nombre': rubro_nombre}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Crear un nuevo empleado
@app.route('/empleado', methods=['POST'])
def create_empleado():
    try:
        data = request.get_json()

        # Extraer datos del JSON
        cedula = data.get('cedula')
        nombre = data.get('nombre')
        celular = data.get('celular')
        factor = data.get('factor')
        direccion = data.get('direccion')
        remuneracion = data.get('remuneracion')
        fecha_vencimiento_carnet = data.get('fecha_vencimiento_carnet')

        # Validación simple (puedes agregar más según sea necesario)
        if not all([cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet]):
            return jsonify({'message': 'Todos los campos son obligatorios.'}), 400

        # Conectar con la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Insertar los datos del empleado en la tabla
        cursor.execute(
            'INSERT INTO empleado (cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Empleado creado exitosamente!'}), 201

    except Exception as e:
        print(f"Error al crear el empleado: {str(e)}")
        return jsonify({'message': 'Error al crear el empleado.', 'error': str(e)}), 500
#listado de empleados
print(">>> Cargando función get_empleados_listado()")
@app.route('/obtener_empleados', methods=['GET'])  
def get_empleados_listado():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT cedula, nombre FROM empleado')
        empleados = cursor.fetchall()
        return jsonify([{'cedula': e[0], 'nombre': e[1]} for e in empleados]), 200

    finally:
        cursor.close()
        conn.close()

#Crear intervencion
@app.route('/intervenciones', methods=['POST'])
@jwt_required()  # Autenticación con JWT
def create_intervencion():
    data = request.get_json()
    print("Datos recibidos:", data)

    identidad = get_jwt_identity()
    print("Usuario autenticado:", identidad)  # Log para verificar la autenticación
    print("Headers recibidos:", request.headers)

    if not identidad:
        return jsonify({"error": "No autorizado"}), 401

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtener información del usuario actual
        cursor.execute('SELECT rol, cedula FROM usuario WHERE usuario = %s', (identidad,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        rol, cedula = usuario

        # Determinar el empleado asociado a la intervención
        if rol == 'operario':
            if not cedula:
                return jsonify({'error': 'El operario no está asociado a ningún empleado.'}), 400
            empleado_id = cedula
        elif rol in ['administrador', 'propietario']:
            empleado_nombre = data.get('empleado')
            if not empleado_nombre:
                return jsonify({'error': 'Debe seleccionar un empleado.'}), 400

            cursor.execute('SELECT cedula FROM empleado WHERE nombre = %s', (empleado_nombre,))
            result = cursor.fetchone()

            if not result:
                return jsonify({'error': f'Empleado "{empleado_nombre}" no encontrado.'}), 400

            empleado_id = result[0]
        else:
            return jsonify({'error': 'Rol no reconocido.'}), 403

        # Obtener IDs de división, tipo y descripción
        division_nombre = data.get('division')
        tipo_nombre = data.get('tipo')
        descripcion_nombre = data.get('descripcion')
        fecha = data.get('fecha')
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')

        cursor.execute('SELECT id FROM division_opciones WHERE nombre = %s', (division_nombre,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': f'División "{division_nombre}" no encontrada.'}), 400
        id_division = result[0]

        cursor.execute('SELECT id FROM tipo_opciones WHERE nombre = %s', (tipo_nombre,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': f'Tipo "{tipo_nombre}" no encontrado.'}), 400
        id_tipo = result[0]

        cursor.execute('''
            SELECT id_descripcion 
            FROM descripcion_opciones 
            WHERE nombre_descripcion = %s AND id_tipo = %s
        ''', (descripcion_nombre, id_tipo))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': f'Descripción "{descripcion_nombre}" no encontrada para el tipo seleccionado.'}), 400
        id_descripcion = result[0]

        # Obtener ID de orden
        cursor.execute('''
            SELECT numero_orden 
            FROM ordenes 
            WHERE division_id = %s AND tipo_id = %s AND descripcion_id = %s
        ''', (id_division, id_tipo, id_descripcion))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'No se encontró un número de orden para la intervención.'}), 400

        numero_orden = result[0]

        # Insertar intervención en la base de datos
        cursor.execute('''
            INSERT INTO intervenciones (empleado_cedula, numero_orden, fecha, hora_inicio, hora_fin) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (empleado_id, numero_orden, fecha, hora_inicio, hora_fin))

        conn.commit()

        return jsonify({'message': 'Intervención creada exitosamente.'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()



print(">>> Cargando función ordenes()")
@app.route('/ordenes', methods=['POST'])
def create_orden():
    try:
        data = request.get_json()
        print("Datos recibidos en /ordenes:", data)  # Depuración

        nombre_division = data["division"]  # Nombre de la división
        nombre_tipo = data["tipo"]  # Nombre del tipo
        cliente_rut = data["cliente"]  # Cliente (rut_ci)
        descripcion_nombre = data["descripcion"]
        fecha_inicio = data["fecha_inicio"]
        fecha_fin = data["fecha_fin"]

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 🔍 Buscar el ID de la división
        cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (nombre_division,))
        division_row = cursor.fetchone()

        if division_row is None:
            return jsonify({"error": f"División no encontrada: {nombre_division}"}), 404

        id_division = division_row["id"]

        # 🔍 Buscar el ID del tipo basado en el nombre
        cursor.execute("SELECT id FROM tipo_opciones WHERE nombre = %s", (nombre_tipo,))
        tipo_row = cursor.fetchone()

        if tipo_row is None:
            return jsonify({"error": f"Tipo no encontrado: {nombre_tipo}"}), 404

        id_tipo = tipo_row["id"]  # Ahora tenemos el ID real

        # 🔍 Verificar si la descripción ya existe
        cursor.execute(
            "SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion = %s AND id_tipo = %s",
            (descripcion_nombre, id_tipo),
        )
        descripcion = cursor.fetchone()

        if descripcion is None:
            cursor.execute(
                "INSERT INTO descripcion_opciones (nombre_descripcion, id_tipo) VALUES (%s, %s) RETURNING id_descripcion",
                (descripcion_nombre, id_tipo),
            )
            descripcion_id = cursor.fetchone()["id_descripcion"]
        else:
            descripcion_id = list(descripcion.values())[0]

        # 🔍 Obtener el ID del cliente (rut_ci)
        cursor.execute("SELECT rut_ci FROM cliente WHERE rut_ci = %s", (cliente_rut,))
        cliente_row = cursor.fetchone()

        if cliente_row is None:
            return jsonify({"error": f"Cliente no encontrado: {cliente_rut}"}), 404

        rut_ci = cliente_row["rut_ci"]

        # ✅ Insertar la orden con los IDs correctos
        cursor.execute(
            "INSERT INTO ordenes (division_id, tipo_id, descripcion_id, rut_ci, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)",
            (id_division, id_tipo, descripcion_id, rut_ci, fecha_inicio, fecha_fin),
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Orden creada exitosamente!"}), 201

    except Exception as e:
        print("Error en /ordenes:", str(e))  # Mostrar el error exacto en la terminal
        return jsonify({"error": "Error interno del servidor"}), 500





#obtener listado de divisiones
print(">>> Cargando función divisiones_listado()")
@app.route('/divisiones', methods=['GET'])
def get_divisiones():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener todos los nombres de la tabla division
    cursor.execute('SELECT nombre FROM division_opciones')
    divisiones = cursor.fetchall()
    
    conn.close()
    return jsonify([div[0] for div in divisiones])

#tipo segun la division seleccionada
print(">>> Cargando función tiposegundivisionlistado()")
@app.route('/tipos_por_division/<string:nombre_division>', methods=['GET'])
def get_tipos_por_division(nombre_division):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar el ID de la división a partir del nombre
    cursor.execute('SELECT id FROM division_opciones WHERE nombre = %s', (nombre_division,))
    division = cursor.fetchone()

    if not division:
        return jsonify({"error": "División no encontrada"}), 404

    # Obtener los tipos basados en el ID de la división encontrada
    cursor.execute('SELECT nombre FROM tipo_opciones WHERE id_division = %s', (division[0],))
    tipos = cursor.fetchall()

    conn.close()
    return jsonify([tipo[0] for tipo in tipos])


#descripcion segun el tipo seleccionado
@app.route('/descripcion_por_tipo/<string:nombre_tipo>', methods=['GET'])
def get_descripcion_por_tipo(nombre_tipo):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Buscar el ID del tipo a partir del nombre
        cursor.execute('SELECT id FROM tipo_opciones WHERE nombre = %s', (nombre_tipo,))
        tipo = cursor.fetchone()

        if not tipo:
            return jsonify({"error": "Tipo no encontrado"}), 404

        # Obtener las descripciones basadas en el ID del tipo encontrado
        cursor.execute('SELECT nombre_descripcion FROM descripcion_opciones WHERE id_tipo = %s', (tipo[0],))
        descripciones = cursor.fetchall()

        conn.close()
        return jsonify([descripcion[0] for descripcion in descripciones])

#agregar nueva division
@app.route('/agregar_division', methods=['POST'])
def agregar_division():
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({'error': 'Falta el campo nombre'}), 400
    
    nombre = data['nombre'].strip()
    if not nombre:
        return jsonify({'error': 'El nombre no puede estar vacío'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (nombre,))
            if cursor.fetchone():
                return jsonify({'error': 'La división ya existe'}), 409
            
            cursor.execute("INSERT INTO division_opciones (nombre) VALUES (%s) RETURNING id", (nombre,))
            new_id = cursor.fetchone()[0]
            conn.commit()
        
        return jsonify({'message': 'División agregada exitosamente', 'id': new_id}), 201
    except Exception as e:
        conn.rollback()
        print("Error al agregar división:", e)
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        conn.close()

#agregar nuevo tipo
# Configuración del logger
logging.basicConfig(level=logging.DEBUG)  # Puedes cambiar el nivel según necesites
logger = logging.getLogger(__name__)

@app.route('/agregar_tipo', methods=['POST'])
def agregar_tipo():
    data = request.get_json()  # Obtener los datos enviados por el cliente (nombre del tipo y nombre de la división)
    
    nombre_tipo = data.get('nombre')  # Nombre del nuevo tipo
    nombre_division = data.get('division')  # Nombre de la división asociada
    
    if not nombre_tipo or not nombre_division:
        logger.error('Faltan parámetros: nombre del tipo o división')
        return jsonify({'error': 'Faltan parámetros, asegúrese de enviar el nombre del tipo y la división'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Log de los datos recibidos
        logger.info(f"Recibiendo solicitud para agregar tipo: {nombre_tipo} a la división: {nombre_division}")
        logger.info(f"Valor de nombre_division: '{nombre_division}'")

        # Obtener el id de la división a partir de su nombre
        cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (nombre_division,))
        division_id = cursor.fetchone()
        
        # Log de la consulta de la división
        logger.info(f"División encontrada: {division_id}")
        
        if not division_id:
            logger.warning(f"La división '{nombre_division}' no existe en la base de datos.")
            return jsonify({'error': 'La división no existe'}), 404

        # Insertar el nuevo tipo en la tabla tipo_opciones
        cursor.execute('INSERT INTO tipo_opciones (nombre, id_division) VALUES (%s, %s)', 
                       (nombre_tipo, division_id[0]))
        conn.commit()
        conn.close()

        logger.info(f"Nuevo tipo '{nombre_tipo}' agregado exitosamente a la división '{nombre_division}'")
        return jsonify({'mensaje': 'Tipo guardado exitosamente'}), 200

    except Exception as e:
        conn.rollback()  # En caso de error, revertir la transacción
        conn.close()
        logger.error(f"Error al guardar el tipo: {e}")
        return jsonify({'error': str(e)}), 500

#crear compra
print(">>> Cargando función cerra compra()")
@app.route('/compras', methods=['POST'])
def create_compra():
    data = request.get_json()
    proveedor_rut_ci = data['proveedor_rut_ci']
    numero_factura = data['numero_factura']
    fecha = data['fecha']
    moneda = data['moneda']
    importe = data['importe']
    tipo_iva = data['tipo_iva']
    tipo_cambio = data['tipo_cambio']
    importe_pesos = data['importe_pesos']
    
    materiales = data.get('materiales', [])  # Lista de materiales a insertar

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el proveedor existe en la base de datos
        cursor.execute("SELECT COUNT(*) FROM proveedor WHERE rut_ci = %s", (proveedor_rut_ci,))
        proveedor_existe = cursor.fetchone()[0]

        if not proveedor_existe:
            return jsonify({'error': 'El proveedor ingresado no existe en la base de datos'}), 400

        # Iniciar transacción
        cursor.execute("BEGIN;")

        # Insertar la compra
        cursor.execute(
            '''INSERT INTO compras 
            (proveedor_rut_ci, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (proveedor_rut_ci, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos)
        )

        # Insertar cada material asociado a la compra
        for material in materiales:
            nombre_material = material['nombre']
            division_nombre = material['division']
            tipo_nombre = material['tipo']
            descripcion_nombre = material['descripcion']
            precio = material['precio']

            # Obtener IDs correspondientes
            cursor.execute('SELECT id FROM division_opciones WHERE nombre = %s', (division_nombre,))
            division_data = cursor.fetchone()
            if not division_data:
                raise Exception('División no encontrada')

            cursor.execute('SELECT id FROM tipo_opciones WHERE nombre = %s', (tipo_nombre,))
            tipo_data = cursor.fetchone()
            if not tipo_data:
                raise Exception('Tipo no encontrado')

            cursor.execute('SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion = %s', (descripcion_nombre,))
            descripcion_data = cursor.fetchone()
            if not descripcion_data:
                raise Exception('Descripción no encontrada')

            # Obtener el ID de orden
            cursor.execute(
                '''SELECT numero_orden FROM ordenes WHERE division_id = %s AND tipo_id = %s AND descripcion_id = %s''',
                (division_data[0], tipo_data[0], descripcion_data[0])
            )
            orden_data = cursor.fetchone()
            if not orden_data:
                raise Exception('Orden no encontrada')

            # Insertar material con la misma factura
            cursor.execute(
                '''INSERT INTO materiales (nombre_material, precio, nro_factura, id_orden) 
                VALUES (%s, %s, %s, %s)''',
                (nombre_material, precio, numero_factura, orden_data[0])
            )

        # Si todo fue bien, confirmar la transacción
        conn.commit()
        return jsonify({'message': 'Compra y materiales creados exitosamente!'}), 201

    except Exception as e:
        conn.rollback()  # Revertir si hay error
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()

    
#listado nombres materiales
@app.route('/materiales-nombres', methods=['GET'])
def obtener_nombres_materiales():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT nombre_material FROM materiales')
    materiales = cursor.fetchall()

    conn.close()

    return jsonify([material[0] for material in materiales]), 200
    

#crear usuario
print(">>> Cargando función crear usuario()")
@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()

    nombre_usuario = data.get('nombre_usuario')
    contrasena = data.get('contrasena')
    rol = data.get('rol')
    nombre_empleado = data.get('nombre_empleado')  # Recibimos el nombre del empleado (no la cédula)

    # Validar que los campos básicos estén presentes
    if not nombre_usuario or not contrasena or not rol:
        return jsonify({'error': 'Faltan datos obligatorios (nombre_usuario, contrasena, rol).'}), 400

    # Si el rol es operario, se necesita seleccionar un empleado, es decir, obtener su cédula
    if rol == 'operario' and not nombre_empleado:
        return jsonify({'error': 'El nombre del empleado es obligatorio para el rol "operario".'}), 400

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Validar que el nombre del empleado exista en la tabla empleados y obtener la cédula
        if rol == 'operario':
            cursor.execute('SELECT cedula FROM empleado WHERE nombre = %s', (nombre_empleado,))
            empleado = cursor.fetchone()

            if not empleado:
                return jsonify({'error': 'El nombre proporcionado no corresponde a ningún empleado registrado.'}), 404

            cedula = empleado[0]  # La cédula del empleado (id_empleado)

        # Insertar el nuevo usuario
        cursor.execute('''
            INSERT INTO usuario (usuario, contrasena, rol, cedula)
            VALUES (%s, %s, %s, %s)
        ''', (nombre_usuario, contrasena, rol, cedula if rol == 'operario' else None))

        conn.commit()
        return jsonify({'message': 'Usuario creado exitosamente.'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400

    finally:
        cursor.close()
        conn.close()

#login
print(">>> Cargando función login()")
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')

    if not usuario or not contrasena:
        return jsonify({'error': 'Faltan datos obligatorios (usuario, contrasena).'}), 400

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 🔹 Buscar contraseña, rol y cédula del usuario
        cursor.execute('SELECT contrasena, rol, cedula FROM usuario WHERE usuario = %s', (usuario,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        if user[0] != contrasena:
            return jsonify({'error': 'Contraseña incorrecta.'}), 401

        # Extraer datos
        rol = user[1]
        cedula = user[2]  # ✅ Ahora obtenemos la cédula del usuario

        # 🔹 Crear el token JWT
        access_token = create_access_token(identity=usuario)

        return jsonify(access_token=access_token, rol=rol, cedula=cedula), 200  # ✅ Ahora se devuelve la cédula

    except Exception as e:
        return jsonify({'error': str(e)}), 400

    finally:
        cursor.close()
        conn.close()

print(">>> Cargando función costos por orden()")
@app.route('/ordenes/detalle', methods=['GET'])
def obtener_detalle_orden():
    division_nombre = request.args.get('division')
    tipo_nombre = request.args.get('tipo')
    descripcion_nombre = request.args.get('descripcion')

    if not all([division_nombre, tipo_nombre, descripcion_nombre]):
        return jsonify({"error": "division, tipo y descripcion son obligatorios"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Obtener los IDs
            cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (division_nombre,))
            division_row = cursor.fetchone()
            if not division_row:
                return jsonify({"error": f'La división "{division_nombre}" no existe'}), 404
            division_id = division_row[0]

            cursor.execute("SELECT id FROM tipo_opciones WHERE nombre = %s", (tipo_nombre,))
            tipo_row = cursor.fetchone()
            if not tipo_row:
                return jsonify({"error": f'El tipo "{tipo_nombre}" no existe'}), 404
            tipo_id = tipo_row[0]

            cursor.execute("SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion = %s", (descripcion_nombre,))
            descripcion_row = cursor.fetchone()
            if not descripcion_row:
                return jsonify({"error": f'La descripción "{descripcion_nombre}" no existe'}), 404
            descripcion_id = descripcion_row[0]

            # Consultar la orden
            cursor.execute("""
                SELECT numero_orden, rut_ci, fecha_inicio, fecha_fin
                FROM ordenes
                WHERE division_id = %s AND tipo_id = %s AND descripcion_id = %s
            """, (division_id, tipo_id, descripcion_id))
            orden = cursor.fetchone()

            if not orden:
                return jsonify({"error": "No se encontró la orden especificada"}), 404

            numero_orden, rut_ci, fecha_inicio, fecha_fin = orden

            # Obtener el nombre del cliente
            cursor.execute("SELECT nombre FROM cliente WHERE rut_ci = %s", (rut_ci,))
            cliente_row = cursor.fetchone()
            if not cliente_row:
                return jsonify({"error": f'No se encontró el cliente con rut_ci {rut_ci}'}), 404
            cliente_nombre = cliente_row["nombre"]

            # Obtener información de compras
            cursor.execute("""
                SELECT m.nombre_material, p.nombre AS proveedor, c.numero_factura, m.precio AS importe
                FROM materiales m
                JOIN compras c ON m.nro_factura = c.numero_factura
                JOIN proveedor p ON c.proveedor_rut_ci = p.rut_ci
                WHERE m.id_orden = %s
            """, (numero_orden,))
            compras = cursor.fetchall()

            compras_detalle = [
                {
                    "material": compra["nombre_material"],
                    "proveedor": compra["proveedor"],
                    "numero_factura": compra["numero_factura"],
                    "importe": "{:.2f}".format(compra["importe"])
                }
                for compra in compras
            ]

            # Calcular el importe total de las compras
            total_compras = sum(compra["importe"] for compra in compras)
            total_compras = "{:.2f}".format(total_compras)

            # Obtener configuraciones
            cursor.execute("SELECT clave, valor FROM configuraciones")
            configuraciones = {row["clave"]: float(row["valor"]) for row in cursor.fetchall()}

            factor_fijo = configuraciones.get('factor_fijo', 0)
            costo_fijo_por_hora = configuraciones.get('costo_fijo_por_hora', 0)

            # Consultar empleados y horas trabajadas
            cursor.execute("""
                SELECT e.nombre, ht.total_horas_trabajadas, 
                       (ht.total_horas_trabajadas * (e.remuneracion * %s + %s)) AS costo_total
                FROM empleado e
                JOIN horas_trabajadas ht ON e.cedula = ht.empleado_cedula
                WHERE ht.numero_orden = %s
            """, (factor_fijo, costo_fijo_por_hora, numero_orden))
            empleados = cursor.fetchall()

            total_horas = sum(emp["total_horas_trabajadas"] for emp in empleados)
            horas = int(total_horas)  # Parte entera son las horas
            minutos = int((total_horas - horas) * 60)  # Parte decimal convertida a minutos
            total_horas_formateado = f"{horas:02d}:{minutos:02d}"

            costo_total_mano_obra = sum(emp["costo_total"] for emp in empleados)
            costo_total_mano_obra = "{:.2f}".format(costo_total_mano_obra)

            empleados_detalle = [
                {
                    "nombre": emp["nombre"],
                    "total_horas_trabajadas": f"{int(emp['total_horas_trabajadas']):02d}:{int((emp['total_horas_trabajadas'] - int(emp['total_horas_trabajadas'])) * 60):02d}",
                    "costo_total": "{:.2f}".format(emp["costo_total"])
                }
                for emp in empleados
            ]

            # Calcular el costo total (compras + mano de obra)
            costo_total_orden = float(total_compras) + float(costo_total_mano_obra)
            costo_total_orden = "{:.2f}".format(costo_total_orden)

            # Recolectar la respuesta con todos los detalles
            respuesta = {
                "numero_orden": numero_orden,
                "cliente_nombre": cliente_nombre,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "costo_total_orden": costo_total_orden,
                "mano de obra": empleados_detalle,
                "total_horas": total_horas_formateado,
                "costo_total_mano_obra": costo_total_mano_obra,
                "compras": compras_detalle,
                "total_compras": total_compras,
                "configuraciones": configuraciones
            }

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500

    finally:
        conn.close()



print(">>> Cargando función configuraciones()")
@app.route('/configuraciones', methods=['GET'])
def obtener_configuraciones():
    query = "SELECT clave, valor FROM configuraciones"
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query)
            configuraciones = {row["clave"]: row["valor"] for row in cursor.fetchall()}
        return jsonify(configuraciones)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# Actualizar una configuración específica
print(">>> Cargando función actualizar config()")
@app.route('/configuraciones/<clave>', methods=['PUT'])
def actualizar_configuracion(clave):
    datos = request.json
    nuevo_valor = datos.get("valor")

    if nuevo_valor is None:
        return jsonify({"error": "Se requiere un valor para actualizar"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = """
                UPDATE configuraciones
                SET valor = %s, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE clave = %s
            """
            cursor.execute(query, (nuevo_valor, clave))
            if cursor.rowcount == 0:
                return jsonify({"error": f"No se encontró la configuración con clave {clave}"}), 404

            conn.commit()  # Confirmar la actualización en la base de datos

        return jsonify({"mensaje": f"Configuración {clave} actualizada exitosamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


# Ruta para registrar usuarios 
print(">>> Cargando función registar()")
@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    try:
        data = request.get_json()
        usuario = data.get('usuario')
        cedula = data.get('cedula')
        contrasena = data.get('contrasena')
        rol = data.get('rol')  # Asegurar que se envía el rol

        if not usuario or not cedula or not contrasena or not rol:
            return jsonify({'error': 'Faltan datos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO usuario (usuario, cedula, contrasena, rol) VALUES (%s, %s, %s, %s)",
                       (usuario, cedula, contrasena, rol))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/editar_rol', methods=['PUT'])
def editar_rol():
    data = request.get_json()
    usuario = data.get('usuario')
    nuevo_rol = data.get('nuevo_rol')

    if not usuario or not nuevo_rol:
        return jsonify({'error': 'Usuario y nuevo rol son obligatorios.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si el usuario existe
        cursor.execute('SELECT usuario FROM usuario WHERE usuario = %s', (usuario,))
        if not cursor.fetchone():
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        # Actualizar el rol del usuario
        cursor.execute('UPDATE usuario SET rol = %s WHERE usuario = %s', (nuevo_rol, usuario))
        conn.commit()

        return jsonify({'success': True, 'message': 'Rol actualizado correctamente.'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

@app.route('/obtener_todos_usuarios', methods=['GET'])
def obtener_todos_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.usuario, u.rol, e.nombre 
            FROM usuario u
            JOIN empleado e ON u.cedula = e.cedula
        """)
        usuarios = cursor.fetchall()

        resultado = []
        for usuario in usuarios:
            resultado.append({
                'usuario': usuario[0],
                'rol': usuario[1],
                'nombre_empleado': usuario[2]
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/get_intervenciones', methods=['GET'])
def get_intervenciones():
    try:
        empleado_id = request.args.get('empleado_id')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        if not empleado_id:
            return jsonify({"error": "El parámetro 'empleado_id' es obligatorio"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Obtener la remuneración del empleado
        cursor.execute("SELECT remuneracion FROM empleado WHERE cedula = %s", (empleado_id,))
        empleado = cursor.fetchone()
        if not empleado:
            return jsonify({"error": "Empleado no encontrado"}), 404
        remuneracion = float(empleado["remuneracion"])

        # Obtener factor fijo y costo fijo por hora desde la tabla configuraciones
        cursor.execute("SELECT clave, valor FROM configuraciones WHERE clave IN ('factor_fijo', 'costo_fijo_por_hora')")
        configuraciones = cursor.fetchall()

        # Convertir los valores obtenidos en un diccionario
        config_dict = {row["clave"]: float(row["valor"]) for row in configuraciones}

        if "factor_fijo" not in config_dict or "costo_fijo_por_hora" not in config_dict:
            return jsonify({"error": "No se encontraron todas las configuraciones necesarias"}), 500

        factor_fijo = config_dict["factor_fijo"]
        costo_fijo_hora = config_dict["costo_fijo_por_hora"]

        # Calcular costo por hora del empleado
        costo_hora = (remuneracion * factor_fijo) + costo_fijo_hora

        # Query para obtener las intervenciones
        query = """
            SELECT 
                i.empleado_cedula,
                i.numero_orden,
                d.nombre AS division,
                t.nombre AS tipo,
                descripcion_op.nombre_descripcion AS descripcion,
                SUM(EXTRACT(EPOCH FROM (i.hora_fin - i.hora_inicio)) / 3600) AS horas_trabajadas
            FROM intervenciones i
            JOIN ordenes o ON i.numero_orden = o.numero_orden
            JOIN division_opciones d ON o.division_id = d.id
            JOIN tipo_opciones t ON o.tipo_id = t.id
            JOIN descripcion_opciones descripcion_op ON o.descripcion_id = descripcion_op.id_descripcion
            WHERE i.empleado_cedula = %s
        """

        parametros = [empleado_id]

        if fecha_desde:
            query += " AND i.fecha >= %s"
            parametros.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND i.fecha <= %s"
            parametros.append(fecha_hasta)
        
        query += """
            GROUP BY i.empleado_cedula, i.numero_orden, d.nombre, t.nombre, descripcion_op.nombre_descripcion
            ORDER BY i.numero_orden;
        """

        cursor.execute(query, tuple(parametros))
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return jsonify({"error": "No se encontraron datos"}), 404

        total_horas = 0
        total_costo = 0
        intervenciones = []
        
        for row in resultados:
            horas = float(row["horas_trabajadas"])  # Convertir a float para cálculos
            costo_intervencion = horas * costo_hora

            horas_int = int(horas)
            minutos = int((horas - horas_int) * 60)
            horas_formateadas = f"{horas_int:02}:{minutos:02}"

            intervenciones.append({
                "empleado_cedula": row["empleado_cedula"],
                "numero_orden": row["numero_orden"],
                "division": row["division"],
                "tipo": row["tipo"],
                "descripcion": row["descripcion"],
                "horas_trabajadas": horas_formateadas,
                "costo_intervencion": round(costo_intervencion, 2)  # Redondeado a 2 decimales
            })

            # Acumular total de horas y costos
            total_horas += horas
            total_costo += costo_intervencion

        # Formatear las horas totales en horas y minutos
        total_horas_int = int(total_horas)
        total_minutos = int((total_horas - total_horas_int) * 60)
        total_horas_formateadas = f"{total_horas_int:02}:{total_minutos:02}"

        # Agregar totales a la respuesta
        return jsonify({
            "intervenciones": intervenciones,
            "total_horas": total_horas_formateadas,
            "total_costo": round(total_costo, 2)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

