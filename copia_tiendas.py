import os
from datetime import datetime
import json
import requests
import urllib3
import tkinter as tk
from tkinter import messagebox

urllib3.disable_warnings()

all_data = {"BQ": {}, "MA": {}}

def get_data(file_path, base_url):
    try:
        response = requests.get(base_url, timeout=10, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(response.json(), file, ensure_ascii=False)
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

    # URLs para BQ y MA
    BQ_base_url = "http://192.168.1.3:3000/api/tiendas"
    MA_base_url = "http://192.168.1.3:4000/api/tiendas"

    if use_BQ:
        # Guardamos los datos para BQ solo para el tenant de BQ
        BQ_tenant = "BQ"
        BQ_file_name = f"tiendas_{BQ_tenant}.json"
        BQ_file_path = os.path.join(backup_folder_path, BQ_file_name)
        get_data(BQ_file_path, BQ_base_url)

    if use_MA:
        # Guardamos los datos para el resto de tenants en MA
            MA_tenant = "MA"
            MA_file_name = f"tiendas_{MA_tenant}.json"
            MA_file_path = os.path.join(backup_folder_path, MA_file_name)
            get_data(MA_file_path, MA_base_url)

    # Leemos los datos de BQ y MA y los almacenamos en all_data
    try:
        if use_BQ:
            with open(BQ_file_path, "r", encoding="utf-8") as BQ_file:
                BQ_data = json.load(BQ_file)
                all_data["BQ"][BQ_tenant] = BQ_data

        if use_MA:
                with open(MA_file_path, "r", encoding="utf-8") as MA_file:
                    MA_data = json.load(MA_file)
                    all_data["MA"][MA_tenant] = MA_data

    except IOError as error:
        print(f"Error: {error}")

def save_data(use_BQ, use_MA, ventana):
    save_all_data(use_BQ, use_MA)
    messagebox.showinfo("Éxito", "Copia de grupos realizada con éxito")

    ventana.destroy()

def main():

    ventana = tk.Toplevel()
    ventana.title("Copia Tiendas")
    ventana.geometry('400x200')

    BQ_var = tk.BooleanVar(value=False)
    MA_var = tk.BooleanVar(value=False)

    BQ_checkbutton = tk.Checkbutton(ventana, text="BurguerQueen", variable=BQ_var, onvalue=True, offvalue=False)
    BQ_checkbutton.pack()

    MA_checkbutton = tk.Checkbutton(ventana, text="MAAndrews", variable=MA_var, onvalue=True, offvalue=False)
    MA_checkbutton.pack()

    button = tk.Button(ventana, text="Guardar Datos", command=lambda: save_data(BQ_var.get(), MA_var.get(),ventana))
    button.pack()

if __name__ == '__main__':
    root = tk.Tk()
    app = tk.Button(root, text="Abrir Copia Tiendas", command=main)
    app.pack()
    root.mainloop()