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
        grupo = response.json()

        # Verifica si el campo "pedidosBloqueados" ya existe en la sección filtros de cada Grupo
        filtros = grupo.get("filtros", [])
        blocked_key_exists = any(filter.get("clave") == "pedidosBloqueados" for filter in filtros)

        # Si el campo no existe, agregarlo a la lista de filtros
        if not blocked_key_exists:
            filtros.append({
                "clave": "pedidosBloqueados",
                "descripcion": "Incluir pds. bloqueados por espera de pago",
                "habilitado": True,
                "modo": "SINGLE",
                "opciones": [
                    {
                        "clave": "TRUE",
                        "descripcion": "Todas las unidades",
                        "activo": False
                    },
                    {
                        "clave": "FALSE",
                        "descripcion": "Unidades no bloqueadas",
                        "activo": True
                    }
                ]
            })

        # Actualiza la sección filtros en el GDS
        grupo["filtros"] = filtros

        # Agrega el Grupo modificado a la lista de respuestas
        responses.append(grupo)

    # Muestra un cuadro de diálogo para seleccionar la ruta de salida
    ruta = filedialog.asksaveasfilename(defaultextension=".json")

    # Escribe las respuestas en un archivo JSON con codificación UTF-8
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=4)

    # Muestra un mensaje emergente para indicar que el archivo se ha guardado correctamente
    messagebox.showinfo("Archivo guardado", f"El archivo {ruta} se ha guardado correctamente.")


def main():
    # Crea la ventana secundaria
    root = tk.Toplevel()
    root.title("Añadir filtro pedidosBloqueados")

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
    url_radio1 = tk.Radiobutton(url_frame, text="BurguerQueen", variable=url_var, value="http://192.168.1.3:3000/api/grupos/")
    url_radio1.pack(side=tk.LEFT)
    url_radio2 = tk.Radiobutton(url_frame, text="McAndrews", variable=url_var, value="http://192.168.1.3:4000/api/grupos/")
    url_radio2.pack(side=tk.LEFT)

    # Crea un botón para ejecutar el script
    button = tk.Button(root, text="Executar", command=lambda: run_script(values_entry, url_var.get()))
    button.pack(pady=10)


if __name__ == '__main__':
    main()