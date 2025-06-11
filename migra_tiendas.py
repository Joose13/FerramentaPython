import mysql.connector
import requests
import tkinter as tk
from tkinter import messagebox
import json
from dotenv import load_dotenv
import os

# Carga de variables de entorno
load_dotenv()

class MigraTiendas:
    def __init__(self, mysql_config, api_config):
        self.mysql_config = mysql_config
        self.api_config = api_config

    def conectar_mysql(self):
        self.mysql_conn = mysql.connector.connect(**self.mysql_config)
        self.mysql_cursor = self.mysql_conn.cursor(dictionary=True)

    def obtener_datos_mysql(self, ids_tiendas):
        placeholders = ",".join(["%s"] * len(ids_tiendas))
        query = f"SELECT id, Grupo, Pais FROM Tiendas WHERE id IN ({placeholders}) AND Activo = 1"
        self.mysql_cursor.execute(query, ids_tiendas)
        return self.mysql_cursor.fetchall()

    def obtener_grupo_desde_api(self, id_grupo):
        request_url = f"{self.api_config['url_get_grupo']}/{id_grupo}"
        response = requests.get(request_url, verify=False)

        if response.status_code == 200:
            data = response.json()
            return data.get('_id')  # Ajusta este campo si el JSON cambia
        else:
            raise Exception(f"Error al obtener grupo {id_grupo}: {response.status_code} - {response.text}")

    def transformar_datos(self, datos_mysql):
        datos_transformados = []
        for row in datos_mysql:
            grupo_api = self.obtener_grupo_desde_api(row['Grupo'])
            documento = {
                "Id": row['id'],
                "Grupo": grupo_api,
                "Pais": row['Pais']
            }
            datos_transformados.append(documento)
        return datos_transformados

    def migrar_datos(self, ids_tiendas):
        self.conectar_mysql()
        datos_mysql = self.obtener_datos_mysql(ids_tiendas)
        documentos = self.transformar_datos(datos_mysql)

        if not documentos:
            print("No se encontraron datos.")
            self.cerrar_conexion()
            return

        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            self.api_config['url_post_tienda'],
            data=json.dumps(documentos),
            headers=headers
        )

        if response.status_code == 200:
            print("Migración completada correctamente.")
        else:
            raise Exception(f"Error al enviar datos a la API: {response.status_code} - {response.text}")

        self.cerrar_conexion()

    def cerrar_conexion(self):
        self.mysql_cursor.close()
        self.mysql_conn.close()


def ejecutar_migracion(ids_entry, conexion_var):
    try:
        ids_tiendas = list(map(int, ids_entry.get().split(",")))

        if conexion_var.get() == "BK":
            mysql_config = {
                "host": os.getenv("BK_DB_HOST"),
                "user": os.getenv("BK_DB_USER"),
                "password": os.getenv("BK_DB_PASSWORD"),
                "database": os.getenv("BK_DB_NAME")
            }
            api_config = {
                "url_get_grupo": os.getenv("BK_API_GRUPOS"),
                "url_post_tienda": os.getenv("BK_API_TIENDAS")
            }
        else:
            mysql_config = {
                "host": os.getenv("MC_DB_HOST"),
                "user": os.getenv("MC_DB_USER"),
                "password": os.getenv("MC_DB_PASSWORD"),
                "database": os.getenv("MC_DB_NAME")
            }
            api_config = {
                "url_get_grupo": os.getenv("MC_API_GRUPOS"),
                "url_post_tienda": os.getenv("MC_API_TIENDAS")
            }

        migrador = MigraTiendas(mysql_config, api_config)
        migrador.migrar_datos(ids_tiendas)

        messagebox.showinfo("Éxito", "La migración se completó correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")


def main():
    root = tk.Toplevel()
    root.title("Migrar Tiendas a través de API")

    frame_input = tk.Frame(root)
    frame_input.pack(padx=10, pady=10)

    tk.Label(frame_input, text="IDs de tiendas (separados por coma):").pack(side=tk.LEFT)
    ids_entry = tk.Entry(frame_input)
    ids_entry.pack(side=tk.LEFT, padx=5)

    frame_conexion = tk.Frame(root)
    frame_conexion.pack(pady=(0, 10))

    conexion_var = tk.StringVar(value="BK")
    tk.Radiobutton(frame_conexion, text="BurguerQueen", variable=conexion_var, value="BK").pack(side=tk.LEFT)
    tk.Radiobutton(frame_conexion, text="McAndrews", variable=conexion_var, value="MC").pack(side=tk.LEFT)

    btn = tk.Button(root, text="Ejecutar Migración", command=lambda: ejecutar_migracion(ids_entry, conexion_var))
    btn.pack(pady=10)


if __name__ == '__main__':
    main()
