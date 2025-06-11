import json
import requests
import urllib3
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

urllib3.disable_warnings()

def get_weekend_days(cadena_var, mercados_entry, tipo_var):
    cadena = cadena_var.get()
    cadenas = ['BQ','MA']
    while cadena not in cadenas:
        messagebox.showerror(title="Error", message="La cadena indicada no es válida.\nSelecciona una cadena entre las siguientes: " + str(cadenas))
        return

    URL_BK = f'http://192.168.1.3:3000/api/grupos'
    URL_MC = f'http://192.168.1.3:4000/api/grupos'

    mercados = mercados_entry.get().upper().split(",")
    tipos = ['Viernes, Sábado', 'Domingo', 'Sin definir', 'Fin de semana']
    tipo = tipo_var.get()

    weekendays = None

    while tipo not in tipos:
        messagebox.showerror(title="Error", message="Opción no válida.\nIntroduce un tipo de weekendDays válido (Solo el número):\n 1 - Viernes, Sábado\n 2 - Domingo\n 3 - Sin definir\n 4 - Fin de semana\n")
        return

    if tipo == "Viernes, Sábado":
        weekendays = ["FRIDAY", "SATURDAY"]
    elif tipo == "Domingo":
        weekendays = ["SUNDAY"]
    elif tipo == "Sin definir":
        weekendays = []
    elif tipo == "Fin de semana":
        weekendays = ["SATURDAY", "SUNDAY"]

    path_save = filedialog.asksaveasfilename(defaultextension=".json", filetypes=(("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")))

    try:
        if cadena == "BQ":
            resp = requests.get(URL_BK, verify=False)
        else:
            resp = requests.get(URL_MC, verify=False)
        response = resp.text

        # convertimos el json en objetos python
        new_json_object = []
        json_object = json.loads(response)
        for i in range(len(json_object)):
            if json_object[i]["Pais"] in mercados:
                for j in range(1, 7):
                    json_object[i]["FinesDeSemana"] = weekendays
                new_json_object.append(json_object[i])

        with open(path_save, "w") as f:
            # Guardamos el json en un fichero con la función json.dump
            json_string = json.dumps(new_json_object, ensure_ascii=False, indent=4)
            f.write(json_string)

        messagebox.showinfo(title="Éxito", message="Proceso finalizado correctamente.")

    except Exception as e:
        messagebox.showerror(title="Error", message=f"Error: {e}")

def main():
    # Creamos la ventana principal
    root = tk.Toplevel()
    root.title("Configurar Fines de Semana")
    root.geometry("400x300")

    # Variables
    cadena_var = tk.StringVar()
    cadena_var.set("BQ")  # Valor predeterminado
    tipo_var = tk.StringVar()
    tipo_var.set("Fin de semana")  # Valor predeterminado

    # Creamos los widgets
    cadena_label = tk.Label(root, text="Selecciona la cadena deseada:")
    cadena_optionmenu = tk.OptionMenu(root, cadena_var, "BQ", "MA")
    labelmargen1 = tk.Label(root, text="") 
    mercados_label = tk.Label(root, text="Introduce el ISO de los Países separados por comas:")
    mercados_entry = tk.Entry(root)
    labelmargen2 = tk.Label(root, text="") 
    tipo_label = tk.Label(root, text="Selecciona el tipo de weekendDays:")
    tipo_optionmenu = tk.OptionMenu(root, tipo_var, "Viernes, Sábado", "Domingo", "Sin definir", "Fin de semana")
    labelmargen3 = tk.Label(root, text="") 
    run_button = tk.Button(root, text="Guardar archivo", command=lambda: get_weekend_days(cadena_var, mercados_entry, tipo_var))

    # Colocamos los widgets en la ventana
    cadena_label.pack()
    cadena_optionmenu.pack()
    labelmargen1.pack()  
    mercados_label.pack()
    mercados_entry.pack()
    labelmargen2.pack() 
    tipo_label.pack()
    tipo_optionmenu.pack()
    labelmargen3.pack()
    run_button.pack()



if __name__ == '__main__':
    main()
