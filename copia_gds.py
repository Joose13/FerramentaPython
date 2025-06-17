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
        print("RESPONSE:",response.json())
        if response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(response.json(), file, ensure_ascii=False)
    except requests.exceptions.RequestException as error:
        print(f"Error: {error}")
    except IOError as error:
        print(f"Error: {error}")

def save_all_data(use_BK=True, use_MC=True):

    global all_data

    # Creamos la carpeta con la fecha actual
    current_date = datetime.now().strftime("%d-%m-%Y")
    backup_folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    backup_folder_path = os.path.join(backup_folder, current_date)
    os.makedirs(backup_folder_path, exist_ok=True)

    # URLs para BQ y MA
    BQ_base_url = "http://192.168.1.3:3000/api/grupos"
    MA_base_url = "http://192.168.1.3:4000/api/grupos"

    if use_BK:
        BK_file_name = f"grupos_BQ.json"
        BK_file_path = os.path.join(backup_folder_path, BK_file_name)
        get_data(BK_file_path, BQ_base_url)

    if use_MC:
            MC_file_name = f"grupos_MA.json"
            MC_file_path = os.path.join(backup_folder_path, MC_file_name)
            get_data(MC_file_path, MA_base_url)

    # Leemos los datos de BQ y MA y los almacenamos en all_data
    try:
        if use_BK:
            with open(BK_file_path, "r", encoding="utf-8") as BK_file:
                BK_data = json.load(BK_file)
                all_data["BQ"]["BQ"] = BK_data

        if use_MC:
                with open(MC_file_path, "r", encoding="utf-8") as MC_file:
                    MC_data = json.load(MC_file)
                    all_data["MA"]["MA"] = MC_data

    except IOError as error:
        print(f"Error: {error}")

def save_data(use_BK, use_MC,ventana):
    save_all_data(use_BK, use_MC)
    messagebox.showinfo("Éxito", "Copia de grupos realizada con éxito")

    ventana.destroy()

# Función principal para la ejecución de la interfaz gráfica
def main():
    
    ventana = tk.Toplevel()
    ventana.title("Copia Grupos")
    ventana.geometry('400x200')

    BK_var = tk.BooleanVar(value=False)
    MC_var = tk.BooleanVar(value=False)

    BK_checkbutton = tk.Checkbutton(ventana, text="BurguerQueen", variable=BK_var, onvalue=True, offvalue=False)
    BK_checkbutton.pack()

    MC_checkbutton = tk.Checkbutton(ventana, text="McAndrews", variable=MC_var, onvalue=True, offvalue=False)
    MC_checkbutton.pack()

    button = tk.Button(ventana, text="Guardar Datos", command=lambda: save_data(BK_var.get(), MC_var.get(),ventana))
    button.pack()


if __name__ == '__main__':
    root = tk.Tk()
    app = tk.Button(root, text="Abrir Copia Grupos", command=main)
    app.pack()
    root.mainloop()
