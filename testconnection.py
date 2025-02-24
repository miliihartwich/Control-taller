import psycopg2
from psycopg2 import OperationalError

def test_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="base_de_datos_taller",  
            user="postgres",    
            password="miliMili0801",  
            host="localhost",   
            port="5432",
            client_encoding="utf8"  # Asegura la codificación correcta
        )
        print("Conexión exitosa a la base de datos local")
        conn.close()
    except OperationalError as e:
        print(f"Error al conectar a la base de datos: {e}")

test_db_connection()
