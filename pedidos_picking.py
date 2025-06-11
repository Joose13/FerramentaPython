import os
import tkinter as tk
from tkinter import ttk
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

def connect_to_db(conexion):
    if conexion == "BQ":
        connection_info = {
            "host": os.getenv("BK_DB_HOST"),
            "user": os.getenv("BK_DB_USER"),
            "password": os.getenv("BK_DB_PASSWORD"),
            "database": os.getenv("BK_DB_NAME")
        }
    elif conexion == "MA":
        connection_info = {
            "host": os.getenv("MC_DB_HOST"),
            "user": os.getenv("MC_DB_USER"),
            "password": os.getenv("MC_DB_PASSWORD"),
            "database": os.getenv("MC_DB_NAME")
        }
    else:
        raise ValueError("Conexión no válida. Usa 'BQ' o 'MA'.")

    try:
        conn = mysql.connector.connect(
            host=connection_info["host"],
            user=connection_info["user"],
            password=connection_info["password"],
            database=connection_info["database"]
        )
        return conn, connection_info["database"]
    except mysql.connector.Error as err:
        raise ConnectionError(f"Error de conexión a la base de datos: {err}")

def calcular_fecha_limite(dias):
    if dias == "7 días":
        return "7 DAY"
    elif dias == "1 mes":
        return "1 MONTH"
    elif dias == "2 meses":
        return "2 MONTH"
    else:
        return "7 DAY"

def fecha_ultimo_pedido(tienda, conn, schema):
    cursor = conn.cursor()
    query = '''
        SELECT P.fecha_alta
        FROM Pedidos P 
        WHERE P.id_tienda = %s AND P.estado = "RECIBIDO"
        ORDER BY P.fecha_compra DESC
        LIMIT 1
    '''
    cursor.execute(query, (tienda,))
    row = cursor.fetchone()
    return row[0] if row else -1

def verificar_pedidos(tiendas_entry, resultado_label, conexion_var, dias_var):
    localizaciones_input = tiendas_entry
    conexion = conexion_var
    dias = dias_var

    if not localizaciones_input or not conexion or not dias:
        resultado_label.config(text="Todos los campos deben estar completos.")
        return

    conn = None

    try:
        conn, schema = connect_to_db(conexion)

        localizaciones = [loc.strip() for loc in localizaciones_input.split(",")]
        if len(localizaciones) > 5:
            resultado_label.config(text="Máximo 5 tiendas permitidas")
            return

        resultado = ""
        for localizacion in localizaciones:
            fecha_limite = calcular_fecha_limite(dias)
            num_pedidos, fecha_mas_reciente = obtener_info_pedidos(conn, schema, localizacion, fecha_limite)
            resultado += f"Tienda {localizacion}: {num_pedidos} pedidos"
            if fecha_mas_reciente:
                if isinstance(fecha_mas_reciente, datetime):
                    fecha_formateada = fecha_mas_reciente.strftime("%Y-%m-%d")
                else:
                    fecha_formateada = str(fecha_mas_reciente)
                resultado += f", Pedido más reciente: {fecha_formateada}"
            resultado += "\n"

        resultado_label.config(text=resultado)

    except ConnectionError as e:
        resultado_label.config(text=str(e))
    finally:
        if conn:
            conn.close()

def obtener_fecha_mas_reciente(conn, schema, localizacion):
    cursor = conn.cursor()
    query = '''
        SELECT MAX(P.fecha_compra) AS FECHA
        FROM Pedidos P 
        WHERE P.id_tienda = %s AND P.estado = "RECIBIDO"
    '''
    cursor.execute(query, (localizacion,))
    row = cursor.fetchone()
    return row[0] if row else None

def obtener_info_pedidos(conn, schema, localizacion, fecha_limite):
    cursor = conn.cursor()
    query = f"""
        SELECT COUNT(*) AS NUM_PEDIDOS  
        FROM Pedidos P 
        WHERE P.id_tienda = %s 
        AND P.fecha_compra >= NOW() - INTERVAL {fecha_limite}
    """
    try:
        cursor.execute(query, (localizacion,))
        row = cursor.fetchone()
        if row:
            num_pedidos = int(row[0])
            fecha = obtener_fecha_mas_reciente(conn, schema, localizacion)
            return num_pedidos, fecha
        else:
            return 0, None
    except mysql.connector.Error as db_error:
        print(db_error)
        return -1, None

def main():
    root = tk.Toplevel()
    dias_var = tk.StringVar()
    conexion_var = tk.StringVar()

    root.title("Consulta pedidos")
    root.geometry("400x350")

    tiendas_label = ttk.Label(root, text="Tiendas (separadas por comas, máximo 5):")
    tiendas_label.pack(pady=10)
    tiendas_entry = ttk.Entry(root, width=40)
    tiendas_entry.pack()

    conexion_label = ttk.Label(root, text="Selecciona la conexión:")
    conexion_label.pack(pady=10)
    conexion_combobox = ttk.Combobox(root, textvariable=conexion_var, values=["BQ", "MA"], state="readonly")
    conexion_combobox.pack()
    conexion_combobox.current(0)

    dias_label = ttk.Label(root, text="Selecciona el número de días:")
    dias_label.pack(pady=10)
    dias_combobox = ttk.Combobox(root, textvariable=dias_var, values=["7 días", "1 mes", "2 meses"], state="readonly")
    dias_combobox.pack()
    dias_combobox.current(0)

    resultado_label = ttk.Label(root, text="", wraplength=400)
    resultado_label.pack()

    verificar_button = ttk.Button(root, text="Verificar Pedidos",
        command=lambda: verificar_pedidos(tiendas_entry.get(), resultado_label, conexion_var.get(), dias_var.get())
    )
    verificar_button.pack(pady=20)

if __name__ == '__main__':
    root = tk.Tk()
    main()
