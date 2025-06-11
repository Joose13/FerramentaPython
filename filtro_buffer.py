import requests
import json
import tkinter as tk
from tkinter import filedialog, messagebox


def run_script(values_entry, url):
    # Obtiene los valores separados por comas del campo de entrada
    values = values_entry.get().split(",")

    # Lista vacía para almacenar las respuestas
    responses = []

    # Itera sobre los valores y realiza la solicitud GET para cada uno
    for value in values:
        # Construye la URL con el valor actual
        request_url = url + value

        # Realiza la solicitud GET y almacena la respuesta
        response = requests.get(request_url, verify=False)
        gds = response.json()

        # Verifica si el campo "stock" ya existe en la sección filtros de cada Grupo
        filters_schema = gds.get("filtros", [])
        stock_key_exists = any(filter.get("clave") == "stock" for filter in filters_schema)

        # Si el campo no existe, agregarlo a la lista de filtersSchema
        if not stock_key_exists:
            filters_schema.append({
                "clave": "stock",
                "descripcion": "zonas de stock",
                "habilitado": True,
                "modo": "MULTIPLE",
                "scopes": ["TIENDA", "DELIVERY"],
                "opciones": [
                    {
                        "clave": "TIENDA",
                        "descripcion": "filter.stock.virtual",
                        "activo": False
                    },
                    {
                        "clave": "AUTO",
                        "descripcion": "filter.stock.internal",
                        "activo": False
                    },
                    {
                        "clave": "ALMACEN",
                        "descripcion": "filter.stock.buffer",
                        "activo": False
                    }
                ]
            })
        else:
            # Verifica si la clave "ALMACEN" ya existe en el filtro stock
            stock_filter = next((filter for filter in filters_schema if filter["key"] == "stock"), None)
            buffer_key_exists = any(option.get("clave") == "ALMACEN" for option in stock_filter.get("options", []))

            # Si la clave no existe, agregarla al filtro stock
            if not buffer_key_exists:
                stock_filter["opciones"].append({
                    "key": "ALMACEN",
                    "descripcion": "filter.stock.buffer",
                    "activo": False
                })

        # Actualiza la sección filtersSchema en el GDS
        gds["filtros"] = filters_schema

        # Agrega el GDS modificado a la lista de respuestas
        responses.append(gds)

    # Muestra un cuadro de diálogo para seleccionar la ruta de salida
    ruta = filedialog.asksaveasfilename(defaultextension=".json")

    # Escribe las respuestas en un archivo JSON con codificación UTF-8
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=4)

    # Muestra un mensaje emergente para indicar que el archivo se ha guardado correctamente
    messagebox.showinfo("Archivo guardado", f"El archivo {ruta} se ha guardado correctamente.")


def main():
    # Crea la ventana principal
    root = tk.Toplevel()
    root.title("Engadir stock almacen")

    # Crea un marco para los campos de entrada
    input_frame = tk.Frame(root)
    input_frame.pack(padx=10, pady=10)

    # Crea un campo de entrada para los valores
    values_label = tk.Label(input_frame, text="Grupos (separados por comas):")
    values_label.pack(side=tk.LEFT)

    values_entry = tk.Entry(input_frame)
    values_entry.pack(side=tk.LEFT, padx=(10, 0))

    # Crea un marco para las opciones de URL
    url_frame = tk.Frame(root)
    url_frame.pack(padx=10, pady=(0, 10))

    url_var = tk.StringVar()
    url_var.set("URL")
    url_radio1 = tk.Radiobutton(url_frame, text="BuerguerQueen", variable=url_var, value="http://192.168.1.3:3000/api/grupos/")
    url_radio1.pack(side=tk.LEFT)
    url_radio2 = tk.Radiobutton(url_frame, text="McAndrews", variable=url_var, value="http://192.168.1.3:4000/api/grupos/")
    url_radio2.pack(side=tk.LEFT)

    # Crea un botón para ejecutar el script
    button = tk.Button(root, text="Ejecutar", command=lambda: run_script(values_entry, url_var.get()))
    button.pack(pady=10)

if __name__ == '__main__':
    main()
