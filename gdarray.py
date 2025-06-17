import json
import tkinter as tk
from tkinter import filedialog, messagebox

campo_archivo = None
archivo_elegido = None 

#Funcion para seleccionar archivo a modificar
def seleccionar_archivo():
    global campo_archivo, archivo_elegido

    archivo = filedialog.askopenfilename(
        initialdir="/", title="Seleccionar archivo", filetypes=[("JSON", "*.json")]
    )

    if archivo:
        campo_archivo.config(state="normal")
        archivo_elegido.set(archivo)
    else:
        campo_archivo.config(state="disabled")

#Funcion para realizar modificaciones sobre el archivo seleccionado
def procesar_archivo():
    archivo_entrada = archivo_elegido.get()
    archivo_salida = filedialog.asksaveasfilename(
        initialdir="/", title="Guardar archivo como", filetypes=[("JSON", "*.json")]
    )

    if not archivo_salida.endswith('.json'):
        archivo_salida += '.json'

    lineas_con_error = []

    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        contenido = f.readlines()

        for i, linea in enumerate(contenido):
            try:
                json.loads(linea.strip())
            except (ValueError, json.JSONDecodeError):
                lineas_con_error.append(i + 1)

    if lineas_con_error:
        mensaje_error = f"No se puede decodificar la(s) línea(s) {', '.join(map(str, lineas_con_error))}"
        messagebox.showerror("Error", mensaje_error)
        return

    contenido_compacto = json.dumps([json.loads(linea.strip()) for linea in contenido], separators=(',', ':'), indent=None)
    contenido_reemplazado = contenido_compacto.replace('{"_id":', ']},{"distributionGroups":[{"_id":')
    contenido_final = contenido_reemplazado.replace(']},', '', 1) + '}]'
    contenido_inicio = contenido_final.replace('[[', '[').replace(']]',']')

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(contenido_inicio)

    messagebox.showinfo("Archivo guardado", "El archivo ha sido procesado correctamente.")


def main():
    global campo_archivo, archivo_elegido

    ventana = tk.Tk()
    ventana.title("Grupos a array")
    ventana.geometry("400x200")

    archivo_elegido = tk.StringVar()

    etiqueta_archivo = tk.Label(ventana, text="Archivo:")
    etiqueta_archivo.pack(pady=5)

    campo_archivo = tk.Entry(ventana, textvariable=archivo_elegido, state="disabled", width=50)
    campo_archivo.pack(padx=5)

    boton_seleccionar_archivo = tk.Button(ventana, text="Seleccionar JSON", command=seleccionar_archivo)
    boton_seleccionar_archivo.pack(pady=5)

    boton_procesar_archivo = tk.Button(ventana, text="Procesar JSON", command=procesar_archivo)
    boton_procesar_archivo.pack(pady=5)

    ventana.mainloop()


if __name__ == '__main__':
    main()
