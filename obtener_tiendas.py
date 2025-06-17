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
        value = value.strip()
        request_url = url + value

        try:
            response = requests.get(request_url, verify=False)
            if response.status_code == 200:
                responses.append(response.json())
            else:
                # Muestra error y cancela todo
                messagebox.showerror("Error", f"La tienda '{value}' no fue encontrada (código {response.status_code}). Operación cancelada.")
                return
        except requests.RequestException as e:
            # Muestra error de conexión y cancela todo
            messagebox.showerror("Error de conexión", f"No se pudo conectar con la tienda '{value}': {str(e)}. Operación cancelada.")
            return

    # Si todas las respuestas fueron válidas, solicita ruta de guardado
    ruta = filedialog.asksaveasfilename(defaultextension=".json")

    if ruta:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Archivo guardado", f"El archivo {ruta} se ha guardado correctamente.")
    else:
        messagebox.showwarning("Cancelado", "No se seleccionó ninguna ruta para guardar.")



def main():
    # Crea la ventana principal
    root = tk.Toplevel()
    root.title("Obtener varias tiendas")
    root.geometry("300x250")

    # Crea un marco para los campos de entrada
    input_frame = tk.Frame(root)
    input_frame.pack(padx=10, pady=10)

    # Crea un campo de entrada para los valores
    values_label = tk.Label(input_frame, text="Tiendas (separadas por comas):")
    values_label.pack(side=tk.LEFT)

    values_entry = tk.Entry(input_frame)
    values_entry.pack(side=tk.LEFT, padx=(10, 0))

    url_frame = tk.Frame(root)
    url_frame.pack(padx=10, pady=(0, 10))

    url_var = tk.StringVar()
    url_var.set("URL")
    url_radio1 = tk.Radiobutton(url_frame, text="BurguerQueen", variable=url_var, value="http://192.168.1.3:3000/api/tiendas/")
    url_radio1.pack(side=tk.LEFT)
    url_radio2 = tk.Radiobutton(url_frame, text="McAndrews", variable=url_var, value="http://192.168.1.3:4000/api/tiendas/")
    url_radio2.pack(side=tk.LEFT)

    # Crea un botón para "Guardar Datos"
    button = tk.Button(root, text="Obtener Tiendas", command=lambda: run_script(values_entry, url_var.get()))
    button.pack(pady=10)


if __name__ == '__main__':
    main()
