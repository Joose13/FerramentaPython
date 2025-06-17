import os
from datetime import datetime
import json
import requests
import urllib3
import tkinter as tk
from tkinter import messagebox

urllib3.disable_warnings()

all_data = {"BQ": {}, "MA": {}}

def remove_filters(json_obj):
    if isinstance(json_obj, list):
        for item in json_obj:
            remove_filters(item)
    elif isinstance(json_obj, dict):
        if "filters" in json_obj:
            del json_obj["filters"]
        for key, value in json_obj.items():
            remove_filters(value)

def get_data(file_path, base_url):
    try:
        response = requests.get(base_url, timeout=10, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            remove_filters(data)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False)
    except requests.exceptions.RequestException as error:
        print(f"Error: {error}")
    except IOError as error:
        print(f"Error: {error}")

def save_all_data(use_BQ, use_MA):
    global all_data

    # Creamos la carpeta con la fecha actual
    current_date = datetime.now().strftime("%d-%m-%Y")
    backup_folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    backup_folder_path = os.path.join(backup_folder, current_date)
    os.makedirs(backup_folder_path, exist_ok=True)

    # URLs para BK y MC
    BQ_base_url = "http://192.168.1.3:3000/api/grupos/"
    MA_base_url = "http://192.168.1.3:4000/api/grupos"

    if use_BQ:
        # Guardamos los datos para BK solo para el tenant de BK
        BK_file_name = f"gds_BQ.json"
        BK_file_path = os.path.join(backup_folder_path, BK_file_name)
        get_data(BK_file_path, BQ_base_url)

    if use_MA:
        # Guardamos los datos para el resto de tenants en MC
        MC_file_name = f"gds_MA.json"
        MC_file_path = os.path.join(backup_folder_path, MC_file_name)
        get_data(MC_file_path, MA_base_url)

    # Leemos los datos de BK y MC y los almacenamos en all_data
    try:
        if use_BQ:
            with open(BK_file_path, "r", encoding="utf-8") as BQ_file:
                BQ_data = json.load(BQ_file)
                all_data["BQ"] = BQ_data

        if use_MA:
                with open(MC_file_path, "r", encoding="utf-8") as MA_file:
                    MA_data = json.load(MA_file)
                    all_data["MA"] = MA_data

    except IOError as error:
        print(f"Error: {error}")

def save_data(use_BQ, use_MA):
    save_all_data(use_BQ, use_MA)
    messagebox.showinfo("Copia realizada exitosamente.")

# Función principal para la ejecución de la interfaz gráfica
def main():
    root = tk.Toplevel()
    root.title("Eliminar filtros")
    root.geometry('400x200')

    BQ_var = tk.BooleanVar()
    MA_var = tk.BooleanVar()

    BK_checkbutton = tk.Checkbutton(root, text="BQ", variable=BQ_var)
    BK_checkbutton.pack()

    MC_checkbutton = tk.Checkbutton(root, text="MA", variable=MA_var)
    MC_checkbutton.pack()

    button = tk.Button(root, text="Guardar Datos", command=lambda: save_data(BQ_var.get(), MA_var.get()))
    button.pack()


if __name__ == '__main__':
    main()
