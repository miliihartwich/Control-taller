from sqlalchemy import create_engine

# URL de conexión a la base de datos
DATABASE_URL = "postgresql://base_de_datos_taller_user:s0CBwhZkqiu1WfxnG8KhlSHezzN8WwD3@dpg-ctmrs9i3esus739s5ua0-a.oregon-postgres.render.com/base_de_datos_taller"

# Probar la conexión a la base de datos
try:
    print("Intentando conectar a la base de datos...")
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Conexión exitosa a la base de datos.")
    connection.close()
except Exception as e:
    print("Error al conectar a la base de datos:", e)
