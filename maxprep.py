import json
import requests
import re
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Define la función que inserta los datos
def insert_data(gd_list_entry_var, entry_list, option, utc_entry_var):
    
    print(option.get())
    gd_list = gd_list_entry_var.get().split(",")
    if not any(gd_list):
        messagebox.showinfo(message="Debes proporcionar al menos un GDS")
        return

    # Define la expresión regular para verificar el formato
    datetime_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$|^null$"

    new_record_list = []
    for entry in entry_list:
        # Pide los valores para los campos
        init_date_time = entry[0].get()
        end_date_time = entry[1].get()
        day_offset = entry[2].get()

        if not re.match(datetime_regex, init_date_time):
            messagebox.showinfo(message="fechaInicio debe tener el formato '2023-01-30T00:00:00Z' o 'null'")
            return
        if not re.match(datetime_regex, end_date_time):
            messagebox.showinfo(message="fechaFin debe tener el formato '2023-01-30T00:00:00Z' o 'null'")
            return

        if init_date_time == "null":
            init_date_time = None

        if end_date_time == "null":
            end_date_time = None

        # Convierte las fechas según la zona horaria
        if init_date_time and end_date_time:
            # Extraer el componente de fecha y hora sin 'Z'
            init_date_str = init_date_time[:-1]
            end_date_str = end_date_time[:-1]

            # Convertir las fechas en objetos datetime
            init_date = datetime.strptime(init_date_str, "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S")

            # Sumar o restar el valor de utc_entry_var a las fechas
            updated_init_date = init_date + timedelta(hours=float(utc_entry_var.get()))
            updated_end_date = end_date + timedelta(hours=float(utc_entry_var.get()))

            # Formatear las fechas actualizadas en el mismo formato original
            updated_init_date_str = updated_init_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            updated_end_date_str = updated_end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            updated_init_date_str = init_date_time
            updated_end_date_str = end_date_time

        # Crea el diccionario con los datos a agregar
        new_record = {
            "fechaInicio": updated_init_date_str,
            "fechaFin": updated_end_date_str,
            "horaLimitePreparacion": "23:59:59",
            "habilitado": True,
            "horasPreparacion": day_offset
        }
        new_record_list.append(new_record)

    results = []
    if option.get() < 1:
        for gd in gd_list:
            url = f"http://192.168.1.3:3000/api/grupos/{gd}"
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                data = response.json()
                if "fechaMaxPreparacion" in data and "fechasPreparacionDefecto" in data["fechaMaxPreparacion"]["1"]:
                    for index, record in enumerate(new_record_list):
                        data["fechaMaxPreparacion"]["1"]["fechasPreparacionDefecto"].insert(index, record)
                    results.append(data)
                else:
                    messagebox.showinfo(message=f"No se encontró 'fechasPreparacionDefecto' en el GDS {gd}")
            else:
                messagebox.showinfo(message=f"Error al obtener el GDS {gd}: {response.status_code}")
    elif option.get() == 1:
        for gd in gd_list:
            url = f"http://192.168.1.3:3000/api/grupos/{gd}"
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                data = response.json()
                if "fechaMaxPreparacion" in data and "fechasPreparacionDefecto" in data["fechaMaxPreparacion"]["1"]:
                    for index, record in enumerate(new_record_list):
                        data["fechaMaxPreparacion"]["1"]["fechasPreparacionDefecto"].insert(index, record)
                        data["fechaMaxPreparacion"]["2"]["fechasPreparacionDefecto"].insert(index, record)
                    results.append(data)
                else:
                    messagebox.showinfo(message=f"No se encontró 'fechasPreparacionDefecto' en el grupo indicado {gd}")
            else:
                messagebox.showinfo(message=f"Error al obtener el grupo {gd}: {response.status_code}")

    if results:
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Archivo JSON", "*.json")])
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            messagebox.showinfo(message=f"Resultados guardados en {file_path}")
    else:
        messagebox.showinfo(message="No se encontraron Grupos válidos para procesar")


def max_prep(num_fechas_entry_var):
    # Crea la ventana principal
    root = tk.Tk()
    root.title("Max Prep Dates de BurguerQueen")
    root.geometry("800x300")

    # Crea el frame para la entrada de GDS
    gd_list_frame = tk.Frame(root)
    gd_list_label = tk.Label(gd_list_frame, text="Lista de grupos separados por comas:", anchor=tk.W, width=30)
    gd_list_entry_var = tk.StringVar(root)  # variable para guardar el valor de la entrada
    gd_list_entry = tk.Entry(gd_list_frame, textvariable=gd_list_entry_var, width=60)
    gd_list_label.grid(row=0, column=0, sticky=tk.W)
    gd_list_entry.grid(row=0, column=1, sticky=tk.W)
    gd_list_frame.pack(padx=10, pady=10, fill=tk.X)

    # Crea el frame para la zona horaria
    utc_frame = tk.Frame(root)
    utc_label = tk.Label(utc_frame, text="Zona horaria (introducir +-horas) :", anchor=tk.W, width=30)
    utc_entry_var = tk.StringVar(root)  # variable para guardar el valor de la entrada
    utc_entry = tk.Entry(utc_frame, textvariable=utc_entry_var, width=60)
    utc_label.grid(row=0, column=0, sticky=tk.W)
    utc_entry.grid(row=0, column=1, sticky=tk.W)
    utc_frame.pack(padx=10, pady=10, fill=tk.X)

    # Crear radiobutton para introducir config para PS
    PS_radiobutton_frame = tk.Frame(root)
    PS_radiobutton_label = tk.Label(PS_radiobutton_frame, text="Introducir configuracion para pedido Auto (campo 2 fechasPreparacionDefecto)", anchor=tk.W, width=60)
    PS_option = tk.IntVar(root)
    PS_option.set(-1)
    PS_option1 = tk.Radiobutton(PS_radiobutton_frame, text="Sí", variable=PS_option, value=1)
    PS_option2 = tk.Radiobutton(PS_radiobutton_frame, text="No", variable=PS_option, value=-1)
    PS_radiobutton_label.grid(row=0, column=0, sticky=tk.W)
    PS_option1.grid(row=1, column=0, sticky=tk.W)
    PS_option2.grid(row=1, column=1, sticky=tk.W)
    PS_radiobutton_frame.pack(padx=10, pady=10, fill=tk.X)

    # Crea el canvas para el área deslizable
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Crea el scrollbar para el canvas
    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Crea el frame dentro del canvas para contener las entradas
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

    def on_canvas_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", on_canvas_configure)

    entry_list = []
    for i in range(num_fechas_entry_var.get()):
        # Crea el frame para la entrada de initDateTime
        init_date_time_frame = tk.Frame(inner_frame)
        init_date_time_label = tk.Label(init_date_time_frame, text=f"Valor {i+1} para initDateTime:", anchor=tk.W, width=30)
        init_date_time_var = tk.StringVar(inner_frame)
        init_date_time_entry = tk.Entry(init_date_time_frame, textvariable=init_date_time_var, width=60)
        init_date_time_label.grid(row=0, column=0, sticky=tk.W)
        init_date_time_entry.grid(row=0, column=1, sticky=tk.W)

        # Agrega una etiqueta de texto para indicar el formato esperado
        init_date_time_format_label = tk.Label(init_date_time_frame, text="Formato esperado: 2023-01-01T00:00:00Z o null", fg="gray", anchor=tk.W, width=60)
        init_date_time_format_label.grid(row=1, column=1, sticky=tk.W)
        init_date_time_frame.pack(padx=10, pady=10, fill=tk.X)

        # Crea el frame para la entrada de endDateTime
        end_date_time_frame = tk.Frame(inner_frame)
        end_date_time_label = tk.Label(end_date_time_frame, text=f"Valor {i+1} para endDateTime:", anchor=tk.W, width=30)
        end_date_time_var = tk.StringVar(inner_frame)
        end_date_time_entry = tk.Entry(end_date_time_frame, textvariable=end_date_time_var, width=60)
        end_date_time_label.grid(row=0, column=0, sticky=tk.W)
        end_date_time_entry.grid(row=0, column=1, sticky=tk.W)

        # Agrega una etiqueta de texto para indicar el formato esperado
        end_date_time_format_label = tk.Label(end_date_time_frame, text="Formato esperado: 2023-01-01T00:00:00Z o null", fg="gray", anchor=tk.W, width=60)
        end_date_time_format_label.grid(row=1, column=1, sticky=tk.W)
        end_date_time_frame.pack(padx=10, pady=10, fill=tk.X)

        # Crea el frame para la entrada de dayOffset
        day_offset_frame = tk.Frame(inner_frame)
        day_offset_label = tk.Label(day_offset_frame, text=f"Valor {i+1} para dayOffset:", anchor=tk.W, width=30)
        day_offset_var = tk.IntVar(inner_frame)
        day_offset_entry = tk.Entry(day_offset_frame, textvariable=day_offset_var, width=60)
        day_offset_label.grid(row=0, column=0, sticky=tk.W)
        day_offset_entry.grid(row=0, column=1, sticky=tk.W)
        day_offset_frame.pack(padx=10, pady=10, fill=tk.X)

        entry_list.append([init_date_time_var, end_date_time_var, day_offset_var])

    # Crea el botón para insertar los datos
    insert_button = tk.Button(root, text="Modificar Datos", command=lambda: insert_data(gd_list_entry_var, entry_list, PS_option, utc_entry_var), width=20)
    insert_button.pack(pady=10, padx=(0, 20))

    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Inicia el loop de la ventana
    root.mainloop()

def main():
    root = tk.Toplevel()
    root.title("Max Prep Fechas")
    root.geometry("300x200")

    num_fechas_frame = tk.Frame(root)
    num_fechas_label = tk.Label(num_fechas_frame, text="Número de bloques de fechas a insertar:", anchor=tk.W, width=30)
    num_fechas_entry_var = tk.IntVar(root)  # variable para guardar el valor de la entrada
    num_fechas_entry = tk.Entry(num_fechas_frame, textvariable=num_fechas_entry_var, width=60)
    num_fechas_label.grid(row=0, column=0, sticky=tk.W)
    num_fechas_entry.grid(row=1, column=0, sticky=tk.W)
    num_fechas_frame.pack(padx=10, pady=10, fill=tk.X)

    run_button = tk.Button(root, text="Aceptar", command=lambda: max_prep(num_fechas_entry_var), width=20)
    run_button.pack(pady=10)

if __name__ == '__main__':
    main()