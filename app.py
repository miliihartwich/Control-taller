from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
from flask_jwt_extended import jwt_required,get_jwt_identity,create_access_token
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from sqlalchemy import text
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={r"/*": {"origins": [
    "https://control-taller.bubbleapps.io/version-test",
    "https://control-taller.bubbleapps.io/version-test?debug_mode=true"
]}})

# Configuración secreta para JWT
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "default_secret")
jwt = JWTManager(app)

# URL de conexión a la base de datos desde las variables de entorno
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://base_de_datos_taller_user:s0CBwhZkqiu1WfxnG8KhlSHezzN8WwD3@dpg-ctmrs9i3esus739s5ua0-a.oregon-postgres.render.com/base_de_datos_taller"
)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        raise RuntimeError(f"Error al conectar a la base de datos: {e}")

@app.route('/')
def index():
    return '¡Hola desde Flask!'

#obtener todo de empleado
@app.route('/get_empleado', methods=['GET'])
def get_empleados():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM empleado')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

#obtener todo de proveedor
@app.route('/get_proveedor', methods=['GET'])
def get_proveedor():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM proveedor')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

#obtener todo de cliente
@app.route('/get_cliente', methods=['GET'])
def get_cliente():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cliente')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

#obtener todo de ordenes
@app.route('/get_orden', methods=['GET'])
def get_orden():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordenes')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# Crear un nuevo cliente
@app.route('/cliente', methods=['POST'])
def create_cliente():
    data = request.get_json()

    # Datos del cliente desde el frontend
    rut_ci = data['RUT/CI']
    tipo = data['tipo']
    nombre = data['nombre']
    alias = data['alias']
    telefono = data['telefono']
    whatsapp = data['whatsapp']
    mail = data['mail']
    departamento_nombre = data['departamento']  # Nombre del departamento
    localidad_nombre = data['localidad']       # Nombre de la localidad
    direccion = data['dirección']

    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Conectar con el cursor de tipo diccionario
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario


    try:
        # Obtener el ID del departamento
        cursor.execute('SELECT departamento_id FROM departamentos WHERE departamento_nombre = %s', (departamento_nombre,))
        departamento = cursor.fetchone()

        if not departamento:
            return jsonify({'error': f'El departamento "{departamento_nombre}" no existe.'}), 400

        departamento_id = departamento['departamento_id']  # Acceder al campo 'id' por nombre (como un diccionario)

        # Obtener el ID de la localidad correspondiente al departamento
        cursor.execute('SELECT localidad_id FROM localidades WHERE localidad_nombre = %s AND departamento_id = %s', (localidad_nombre, departamento_id))
        localidad = cursor.fetchone()

        if not localidad:
            return jsonify({'error': f'La localidad "{localidad_nombre}" no pertenece al departamento "{departamento_nombre}".'}), 400

        localidad_id = localidad['localidad_id']  # Acceder al campo 'id' por nombre (como un diccionario)

        # Insertar el cliente en la base de datos
        cursor.execute(
            'INSERT INTO cliente (rut_ci, tipo, nombre, alias, telefono, whatsapp, mail, departamento_id, localidad_id, direccion) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (rut_ci, tipo, nombre, alias, telefono, whatsapp, mail, departamento_id, localidad_id, direccion)
        )
        conn.commit()

        return jsonify({'message': 'Cliente creado exitosamente!'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

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
@app.route('/proveedor', methods=['POST'])
def create_proveedor():
    try:
        # Obtener los datos del request
        data = request.get_json()
        rut_ci = data['RUT/CI']
        nombre = data['nombre']
        alias = data['alias']
        telefono = data['telefono']
        whatsapp = data['whatsapp']
        mail = data['mail']
        departamento_nombre = data['departamento']  # Recibe el nombre del departamento
        localidad_nombre = data['localidad']       # Recibe el nombre de la localidad
        direccion = data['dirección']
        rubro_nombre = data['rubro']               # Recibe el nombre del rubro
        comentarios = data['comentarios']
        calificacion = data['calificación']

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

# Crear un nuevo empleado
@app.route('/empleado', methods=['POST'])
def create_empleado():
    data = request.get_json()
    cedula = data['cedula']
    nombre = data['nombre']
    celular = data['celular']
    factor = data['factor']
    direccion = data['dirección']
    remuneracion = data['remuneración']
    fecha_vencimiento_carnet = data['fecha_vencimiento_carnet']
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Conectar con el cursor de tipo diccionario
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

    cursor.execute(
    'INSERT INTO empleado (cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet) VALUES (%s, %s, %s, %s, %s, %s, %s)',
    (cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet)
)

    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Empleado creado exitosamente!'}), 201

#listado empleados
@app.route('/obtener_empleados', methods=['GET']) #chequearrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
@jwt_required()
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

#crear intervencion
@app.route('/intervencion', methods=['POST'])
@jwt_required()  # Autenticación con JWT
def create_intervencion():
    data = request.get_json()
    usuario_actual = get_jwt_identity()  # Obtiene el ID del usuario logueado
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtener información del usuario actual
        cursor.execute('SELECT rol, cedula FROM usuario WHERE usuario = %s', (usuario_actual,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.'}), 404
        
        rol, cedula = usuario

        if rol == 'operario':
            # Si es operario, el empleado asociado al usuario actual
            if not cedula:
                return jsonify({'error': 'El operario no está asociado a ningún empleado.'}), 400

            empleado = cedula
        elif rol in ['administrador', 'propietario']:
            # Si es administrador o propietario, se espera que el frontend envíe el ID del empleado seleccionado
            empleado = data.get('empleado')
            if not empleado:
                return jsonify({'error': 'Debe seleccionar un empleado.'}), 400
        else:
            return jsonify({'error': 'Rol no reconocido.'}), 403

        # Obtener el ID de la orden asociada
        division_nombre = data['división']
        tipo_nombre = data['tipo']
        descripcion_nombre = data['descripción']
        fecha = data['fecha']
        hora_inicio = data['hora_inicio']
        hora_fin = data['hora_fin']

        # Obtener IDs de division, tipo y descripción
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
        numero_orden = cursor.fetchone()[0]

        # Insertar intervención
        cursor.execute('''
            INSERT INTO intervenciones (empleado_cedula, numero_orden, fecha, hora_inicio, hora_fin) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (empleado, numero_orden, fecha, hora_inicio, hora_fin))

        conn.commit()
        return jsonify({'message': 'Intervención creada exitosamente.'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400

    finally:
        cursor.close()
        conn.close()

@app.route('/ordenes', methods=['POST'])
def create_orden():
    data = request.get_json()

    # Datos ingresados por el usuario
    division_nombre = data['division']
    tipo_nombre = data['tipo']
    cliente_nombre = data['cliente']
    descripcion_nombre = data['descripcion']
    fecha_inicio = data['fecha_inicio']
    fecha_fin = data['fecha_fin']

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Obtener el ID de la división según el nombre
    cursor.execute('SELECT id FROM division_opciones WHERE nombre = %s', (division_nombre,))
    division_row = cursor.fetchone()
    if division_row is None:
        return jsonify({'error': f'División no encontrada: {division_nombre}'}), 404
    id_division = list(division_row.values())[0]  # Obtén el valor dinámicamente

    # Obtener el ID del tipo según el nombre
    cursor.execute('SELECT id FROM tipo_opciones WHERE nombre = %s', (tipo_nombre,))
    tipo_row = cursor.fetchone()
    if tipo_row is None:
        return jsonify({'error': f'Tipo no encontrado: {tipo_nombre}'}), 404
    id_tipo = list(tipo_row.values())[0]  # Obtén el valor dinámicamente

    # Verificar si la descripción ya existe o si se debe crear una nueva
    cursor.execute('''
        SELECT id_descripcion 
        FROM descripcion_opciones 
        WHERE nombre_descripcion = %s AND id_tipo = %s 
    ''', (descripcion_nombre, id_tipo))
    descripcion = cursor.fetchone()

    if descripcion is None:  # Si la descripción no existe, crear una nueva 
        cursor.execute('''
            INSERT INTO descripcion_opciones (nombre_descripcion, id_tipo) 
            VALUES (%s, %s) RETURNING id_descripcion
        ''', (descripcion_nombre, id_tipo))
        descripcion_id = cursor.fetchone()['id_descripcion']
    else:
        descripcion_id = list(descripcion.values())[0]  # Obtén el valor dinámicamente

    # Obtener el ID del cliente según el nombre
    cursor.execute('SELECT rut_ci FROM cliente WHERE nombre = %s', (cliente_nombre,))
    cliente_row = cursor.fetchone()
    if cliente_row is None:
        return jsonify({'error': f'Cliente no encontrado: {cliente_nombre}'}), 404
    rut_ci = list(cliente_row.values())[0]  # Obtén el valor dinámicamente

    # Insertar la nueva orden con los IDs obtenidos
    cursor.execute(''' 
        INSERT INTO ordenes (division_id, tipo_id, descripcion_id, rut_ci, fecha_inicio, fecha_fin) 
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (id_division, id_tipo, descripcion_id, rut_ci, fecha_inicio, fecha_fin))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Orden creada exitosamente!'}), 201


#obtener listado de divisiones
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
@app.route('/tipos_por_division/<int:id_division>', methods=['GET'])
def get_tipos_por_division(id_division):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todos los tipos que pertenecen a la división seleccionada
    cursor.execute('SELECT nombre FROM tipo_opciones WHERE id_division = %s', (id_division,))
    tipos = cursor.fetchall()

    conn.close()
    return jsonify([tipo[0] for tipo in tipos])

#descripcion segun el tipo seleccionado
@app.route('/descripcion_por_tipo/<int:id_tipo>', methods=['GET'])
def get_descripcion_por_tipo(id_tipo):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todos las descripciones que pertenecen al tipo seleccionado
    cursor.execute('SELECT nombre_descripcion FROM descripcion_opciones WHERE id_tipo = %s', (id_tipo,))
    descripciones = cursor.fetchall()

    conn.close()
    return jsonify([descripcion[0] for descripcion in descripciones])

#crear compra
@app.route('/compras', methods=['POST'])
def create_compra():
    data = request.get_json()
    proveedor_nombre = data['proveedor']  # Nombre del proveedor recibido del cliente
    numero_factura = data['numero de factura']
    fecha = data['fecha']
    moneda = data['moneda']
    importe = data['importe']
    tipo_iva = data['tipo de iva']
    tipo_cambio = data['tipo de cambio']
    importe_pesos = data['importe pesos']

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Obtener el RUT/CI del proveedor a partir de su nombre
        cursor.execute('SELECT rut_ci FROM proveedor WHERE nombre = %s', (proveedor_nombre,))
        proveedor_data = cursor.fetchone()

        if not proveedor_data:
            conn.close()
            return jsonify({'error': 'Proveedor no encontrado'}), 404

        proveedor_rut_ci = proveedor_data['rut_ci']

        # Insertar la compra con el RUT/CI del proveedor
        cursor.execute(
            '''INSERT INTO compras 
            (proveedor_rut_ci, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (proveedor_rut_ci, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos)
        )
        conn.commit()
        return jsonify({'message': 'Compra creada exitosamente!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


#crear material
@app.route('/materiales', methods=['POST'])
def create_material():
    data = request.get_json()
    nombre_material = data['material']
    precio = data['importe']
    numero_factura = data['numero de factura']
    division_nombre = data['división']
    tipo_nombre = data['tipo']
    descripcion_nombre = data['descripción']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener ID de division
    cursor.execute(
        'SELECT id FROM division_opciones WHERE nombre = %s', 
        (division_nombre,)
    )
    division_data = cursor.fetchone()

    if not division_data:
        conn.close()
        return jsonify({'error': 'División no encontrada'}), 404

    division_id = division_data[0]

    # Obtener ID de tipo
    cursor.execute(
        'SELECT id FROM tipo_opciones WHERE nombre = %s', 
        (tipo_nombre,)
    )
    tipo_data = cursor.fetchone()

    if not tipo_data:
        conn.close()
        return jsonify({'error': 'Tipo no encontrado'}), 404

    tipo_id = tipo_data[0]

    # Obtener ID de descripcion
    cursor.execute(
        'SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion = %s', 
        (descripcion_nombre,)
    )
    descripcion_data = cursor.fetchone()

    if not descripcion_data:
        conn.close()
        return jsonify({'error': 'Descripción no encontrada'}), 404

    descripcion_id = descripcion_data[0]

    # Obtener id_orden en base a los IDs obtenidos
    cursor.execute(
        '''
        SELECT numero_orden 
        FROM ordenes 
        WHERE division_id = %s AND tipo_id = %s AND descripcion_id = %s
        ''', 
        (division_id, tipo_id, descripcion_id)
    )
    orden_data = cursor.fetchone()

    if not orden_data:
        conn.close()
        return jsonify({'error': 'Orden no encontrada'}), 404

    id_orden = orden_data[0]

    # Verificar si el número de factura existe en la tabla compras
    cursor.execute(
        'SELECT numero_factura FROM compras WHERE numero_factura = %s', 
        (numero_factura,)
    )
    factura_data = cursor.fetchone()

    if not factura_data:
        conn.close()
        return jsonify({'error': 'Factura no encontrada'}), 404

    # Insertar el material en la tabla materiales
    cursor.execute(
        '''
        INSERT INTO materiales (nombre_material, precio, nro_factura, id_orden) 
        VALUES (%s, %s, %s, %s)
        ''',
        (nombre_material, precio, numero_factura, id_orden)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Material creado exitosamente!'}), 201

#crear usuario
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
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    contrasena = data.get('contrasena')

    if not nombre_usuario or not contrasena:
        return jsonify({'error': 'Faltan datos obligatorios (nombre_usuario, contrasena).'}), 400

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el usuario existe y la contraseña es correcta
        cursor.execute('SELECT contrasena FROM usuario WHERE usuario = %s', (nombre_usuario,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        if user[0] != contrasena:
            return jsonify({'error': 'Contraseña incorrecta.'}), 401

        # Crear el token JWT
        access_token = create_access_token(identity=nombre_usuario)
        return jsonify(access_token=access_token), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

    finally:
        cursor.close()
        conn.close()

#consultar costos por orden
@app.route('/ordenes/detalle', methods=['GET'])
def obtener_detalle_orden():
    division_nombre = request.args.get('division')
    tipo_nombre = request.args.get('tipo')
    descripcion_nombre = request.args.get('descripcion')

    if not all([division_nombre, tipo_nombre, descripcion_nombre]):
        return jsonify({"error": "division, tipo y descripcion son obligatorios"}), 400

    try:
        with engine.connect() as conn:
            # Obtener el ID de la división
            query_division = text("SELECT id FROM division_opciones WHERE nombre = :nombre")
            division_row = conn.execute(query_division, {"nombre": division_nombre}).fetchone()
            if not division_row:
                return jsonify({"error": f'La división "{division_nombre}" no existe'}), 404
            division_id = division_row[0]

            # Obtener el ID del tipo
            query_tipo = text("SELECT id FROM tipo_opciones WHERE nombre = :nombre")
            tipo_row = conn.execute(query_tipo, {"nombre": tipo_nombre}).fetchone()
            if not tipo_row:
                return jsonify({"error": f'El tipo "{tipo_nombre}" no existe'}), 404
            tipo_id = tipo_row[0]

            # Obtener el ID de la descripción
            query_descripcion = text("SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion = :nombre")
            descripcion_row = conn.execute(query_descripcion, {"nombre": descripcion_nombre}).fetchone()
            if not descripcion_row:
                return jsonify({"error": f'La descripción "{descripcion_nombre}" no existe'}), 404
            descripcion_id = descripcion_row[0]

            # Consultar el número de orden basado en los IDs
            query_orden = text("""
                SELECT numero_orden, rut_ci, fecha_inicio, fecha_fin
                FROM ordenes
                WHERE division_id = :division_id AND tipo_id = :tipo_id AND descripcion_id = :descripcion_id
            """)
            orden = conn.execute(query_orden, {
                "division_id": division_id,
                "tipo_id": tipo_id,
                "descripcion_id": descripcion_id
            }).fetchone()

            if not orden:
                return jsonify({"error": "No se encontró la orden especificada"}), 404

            numero_orden = orden[0]
            rut_ci = orden[1]

            # Obtener el nombre del cliente usando el rut_ci
            query_cliente = text("SELECT nombre FROM cliente WHERE rut_ci = :rut_ci")
            cliente_row = conn.execute(query_cliente, {"rut_ci": rut_ci}).fetchone()

            if not cliente_row:
                return jsonify({"error": f'No se encontró el cliente con rut_ci {rut_ci}'}), 404
            cliente_nombre = cliente_row[0]

            # Obtener información de compras (materiales, proveedor, número de factura, y monto)
            query_compras = text("""
                SELECT m.nombre_material, p.nombre AS proveedor, c.numero_factura, m.precio AS importe
                FROM materiales m
                JOIN compras c ON m.nro_factura = c.numero_factura
                JOIN proveedor p ON c.proveedor_rut_ci = p.rut_ci
                WHERE m.id_orden = :numero_orden
            """)
            compras = conn.execute(query_compras, {"numero_orden": numero_orden}).fetchall()

            compras_detalle = [
                {
                    "material": compra[0],
                    "proveedor": compra[1],
                    "numero_factura": compra[2],
                    "importe": compra[3]
                }
                for compra in compras
            ]

            # Calcular el importe total de las compras
            total_compras = sum(compra[3] for compra in compras)  # Sumar los importes

            # Obtener configuraciones
            query_config = text("SELECT clave, valor FROM configuraciones")
            configuraciones = {row[0]: float(row[1]) for row in conn.execute(query_config)}

            factor_fijo = configuraciones.get('factor_fijo', 0)
            costo_fijo_por_hora = configuraciones.get('costo_fijo_por_hora', 0)

            # Consultar empleados y horas trabajadas
            query_horas = text("""
                SELECT e.nombre, ht.total_horas_trabajadas, 
                       (ht.total_horas_trabajadas * (e.remuneracion * :factor_fijo + :costo_fijo_por_hora)) AS costo_total
                FROM empleado e
                JOIN horas_trabajadas ht ON e.cedula = ht.empleado_cedula
                WHERE ht.numero_orden = :numero_orden
            """)
            empleados = conn.execute(query_horas, {
                "numero_orden": numero_orden,
                "factor_fijo": factor_fijo,
                "costo_fijo_por_hora": costo_fijo_por_hora
            }).fetchall()

            total_horas = sum(emp[1] for emp in empleados)
            costo_total_mano_obra = sum(emp[2] for emp in empleados)
            empleados_detalle = [
                {
                    "nombre": emp[0],
                    "total_horas_trabajadas": emp[1],
                    "costo_total": emp[2]
                }
                for emp in empleados
            ]

            # Calcular el costo total (compras + mano de obra)
            costo_total_orden = total_compras + costo_total_mano_obra

            # Recolectar la respuesta con todos los detalles
            respuesta = {
                "numero_orden": numero_orden,
                "cliente_nombre": cliente_nombre,
                "fecha_inicio": orden[2],
                "fecha_fin": orden[3],
                "costo_total_orden": costo_total_orden,  # Costo total de compras + mano de obra
                "mano de obra":empleados_detalle,
                "total_horas": total_horas,
                "costo_total_mano_obra": costo_total_mano_obra,
                "compras": compras_detalle,
                "total_compras": total_compras
            }

            # Añadir configuraciones a la respuesta
            respuesta["configuraciones"] = configuraciones

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500

@app.route('/configuraciones', methods=['GET'])
def obtener_configuraciones():
    query = "SELECT * FROM configuraciones"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        configuraciones = [dict(zip(result.keys(), row)) for row in result.fetchall()]
    return jsonify(configuraciones)

# Actualizar una configuración específica
@app.route('/configuraciones/<clave>', methods=['PUT'])
def actualizar_configuracion(clave):
    datos = request.json
    nuevo_valor = datos.get("valor")
    if nuevo_valor is None:
        return jsonify({"error": "Se requiere un valor para actualizar"}), 400

    query = text("""
        UPDATE configuraciones
        SET valor = :valor, fecha_modificacion = CURRENT_TIMESTAMP
        WHERE clave = :clave
    """)
    with engine.connect() as conn:
        resultado = conn.execute(query, {"valor": nuevo_valor, "clave": clave})
        if resultado.rowcount == 0:
            return jsonify({"error": f"No se encontró la configuración con clave {clave}"}), 404

    return jsonify({"mensaje": f"Configuración {clave} actualizada exitosamente"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

