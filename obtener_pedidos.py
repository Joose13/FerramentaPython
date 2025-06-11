import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import obtener_pedidos_legacy
import obtener_pedidos_IOP

# Función para ejecutar los scripts y guardar los resultados en un archivo .txt
def ejecutar_scripts(store_ids_entry, conexion):
    # Obtener los storeId ingresados en la interfaz
    store_ids = store_ids_entry.get()
    store_ids_list = store_ids.split(",")

    # Ejecutar los scripts y obtener los resultados
    resultados_por_tienda = {}

    for store_id in store_ids_list:
        resultado_legacy = obtener_pedidos_legacy.pedidos_legacy(store_id.strip(), conexion)
        resultado_IOP = obtener_pedidos_IOP.pedidos_IOP(store_id.strip(), conexion)
        resultados_por_tienda[store_id] = {
            'Legacy': resultado_legacy,
            'MongoDB': resultado_IOP
        }

    # Ordenar los resultados por storeId
    resultados_ordenados = sorted(resultados_por_tienda.items(), key=lambda x: x[0])

    # Guardar los resultados en un archivo .txt
    archivo_resultados = filedialog.asksaveasfile(defaultextension=".txt")
    if archivo_resultados is not None:
        archivo_resultados.write("Resultados por tienda:\n\n")
        archivo_resultados.write("----------------------------------------------------\n\n")
        for store_id, resultados in resultados_ordenados:
            archivo_resultados.write(f"Id de tienda: {store_id}\n\n")
            archivo_resultados.write(resultados['Legacy'] + "\n\n")
            archivo_resultados.write(resultados['MongoDB'] + "\n\n")
            archivo_resultados.write("----------------------------------------------------\n\n")

        archivo_resultados.close()
        print("Los resultados se han guardado exitosamente.")


# Crear la interfaz con tkinter
def main():
    window = tk.Toplevel()
    window.title("Obtener Pedidos")
    window.geometry("300x200")

    # Etiqueta y campo de entrada para los storeId
    store_ids_label = tk.Label(window, text="Ingresa las tiendas separadas por comas:")
    store_ids_label.pack(padx=10, pady=(10, 0))

    store_ids_entry = tk.Entry(window, width=40)
    store_ids_entry.pack(padx=10, pady=(0, 10))

    conexion_var = tk.StringVar()
    conexion_label = ttk.Label(window, text="Selecciona la conexión:")
    conexion_label.pack(pady=10)
    conexion_combobox = ttk.Combobox(window, textvariable=conexion_var, values=["BQ", "MA"])
    conexion_combobox.pack()

    # Botón para ejecutar los scripts y guardar los resultados
    ejecutar_button = tk.Button(window, text="Guardar Resultados", command=lambda: ejecutar_scripts(store_ids_entry, conexion_var.get()))
    ejecutar_button.pack(padx=10, pady=(0, 10))


if __name__ == '__main__':
    main()