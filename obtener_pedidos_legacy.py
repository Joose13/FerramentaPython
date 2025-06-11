import os
import mysql.connector
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def pedidos_legacy(localizaciones_input, conexion):
    # Leer configuración desde .env en lugar de hardcodear
    if conexion == "BQ":
        conn_info = {
            "host": os.getenv("BK_DB_HOST"),
            "user": os.getenv("BK_DB_USER"),
            "password": os.getenv("BK_DB_PASSWORD"),
            "database": os.getenv("BK_DB_NAME")
        }
    elif conexion == "MA":
        conn_info = {
            "host": os.getenv("MC_DB_HOST"),
            "user": os.getenv("MC_DB_USER"),
            "password": os.getenv("MC_DB_PASSWORD"),
            "database": os.getenv("MC_DB_NAME")
        }
    else:
        raise ValueError("Conexión no válida. Usa 'BQ' o 'MA'.")

    resultado = ''
    resultado_list = []

    try:
        localizaciones = localizaciones_input.split(",")

        for localizacion in localizaciones:
            print(f'Pedidos legacy store {localizacion.strip()}:')
            resultado = f'Pedidos legacy:'

            query = """
            SELECT p.id_tienda, p.operativa, COUNT(p.id) AS pedidos, SUM(p.unidades) AS uds
            FROM Pedidos p
            JOIN Tiendas t ON t.id = p.id_tienda
            WHERE p.id_tienda = %s
            AND p.fecha_compra >= NOW() - INTERVAL 60 DAY
            GROUP BY p.id_tienda, p.operativa
            ORDER BY p.id_tienda ASC;
            """

            conn = mysql.connector.connect(**conn_info)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(query, (localizacion.strip(),))
            rows = cursor.fetchall()

            for row in rows:
                operativa = row['operativa']
                pedidos = row['pedidos']
                print(f"{operativa}, Pedidos: {pedidos}")
                resultado += '\n' + f"{operativa}, Pedidos: {pedidos}"
                resultado_list.append(resultado)

            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error en Legacy al validar tienda {localizacion}: {str(e)}\n")
        resultado = 'NOT OK'

    return resultado
