import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pymongo
import mysql.connector
import threading
import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Función para insertar texto en el widget con hilos
def insertar_en_texto(widget, texto):
    widget.after(0, lambda: widget.insert(tk.END, texto))

def limpiar_texto(widget):
    widget.after(0, lambda: widget.delete(1.0, tk.END))

def validar_tienda_mongo(tienda, system, resultado_text):
    db_connections = {
        "BK": {
            "conn_str": os.environ.get("BK_MONGO_CONN"),
            "db_name": os.environ.get("BK_MONGO_DB")
        },
        "MC": {
            "conn_str": os.environ.get("MC_MONGO_CONN"),
            "db_name": os.environ.get("MC_MONGO_DB")
        }
    }

    if system not in db_connections:
        insertar_en_texto(resultado_text, "Sistema no válido\n")
        return []

    conn_str = db_connections[system]["conn_str"]
    client = pymongo.MongoClient(conn_str)
    db = client[db_connections[system]["db_name"]]
    stores = db.tiendas
    gds = db.grupos

    tiendas = tienda.split(',')
    resultado_list = []

    for tienda in tiendas:
        store_list = []
        try:
            tienda_id = int(tienda.strip())
            for store in stores.find({'Id': tienda_id}):
                store_list.append(store)

            if store_list:
                distribution_group_id = store_list[0]['Grupo']
                group_info = gds.find_one({'_id': distribution_group_id})

                if group_info:
                    auto_expedition = group_info.get('autoEmpaquetado')
                    if auto_expedition is not None:
                        insertar_en_texto(resultado_text, f"Tienda: {tienda}\nMongoDB OK & ")
                        resultado = f'{tienda}, OK, '
                        resultado += validar_tienda_legacy(tienda, system, resultado_text)
                        resultado_list.append(resultado)
                    else:
                        insertar_en_texto(resultado_text, f"Tienda: {tienda}\nMongoDB NOT OK & ")
                        resultado = f'{tienda}, NOT OK, '
                        resultado += validar_tienda_legacy(tienda, system, resultado_text)
                        resultado_list.append(resultado)
                else:
                    insertar_en_texto(resultado_text, f"Tienda {tienda}: Grupo no encontrado\n")
            else:
                insertar_en_texto(resultado_text, f"Tienda {tienda}: No encontrada en lista de tiendas\n")
        except Exception as e:
            insertar_en_texto(resultado_text, f"Error al validar tienda {tienda}: {str(e)}\n")

    client.close()
    return resultado_list

def validar_tienda_legacy(tienda, system, resultado_text):
    db_connections = {
        "BK": {
            "host": os.environ.get("BK_DB_HOST"),
            "user": os.environ.get("BK_DB_USER"),
            "password": os.environ.get("BK_DB_PASSWORD"),
            "database": os.environ.get("BK_DB_NAME")
        },
        "MC": {
            "host": os.environ.get("MC_DB_HOST"),
            "user": os.environ.get("MC_DB_USER"),
            "password": os.environ.get("MC_DB_PASSWORD"),
            "database": os.environ.get("MC_DB_NAME")
        }
    }

    if system not in db_connections:
        insertar_en_texto(resultado_text, "Sistema no válido\n")
        return "NOT OK"

    conn_info = db_connections[system]

    query = """
    SELECT T.id AS TIENDA, G.id AS GD, C.Nombre AS VAR, C.VALOR 
    FROM Tiendas T 
    JOIN Grupos G ON G.id = T.Grupo
    LEFT JOIN Configuracion C ON C.id_grupo = G.id 
    WHERE T.id = %s 
    AND C.Nombre IN ('TIENDA_MIGRADA_MONGO')
    ORDER BY GD, TIENDA;
    """

    resultado = 'OK'
    try:
        conn = mysql.connector.connect(**conn_info)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (tienda,))
        rows = cursor.fetchall()
        aux = sum(1 for row in rows if row['VALOR'] == 1)

        if aux == 1:
            insertar_en_texto(resultado_text, "Legacy OK\n")
            resultado = 'OK'
        else:
            insertar_en_texto(resultado_text, "Legacy NOT OK\n")
            resultado = 'NOT OK'

        cursor.close()
        conn.close()
    except Exception as e:
        insertar_en_texto(resultado_text, f"Error en Legacy al validar tienda {tienda}: {str(e)}\n")
        resultado = 'NOT OK'

    return resultado

def exportar_resultado(resultado, ventana):
    resultado_separado = [cadena.split(', ') for cadena in resultado]
    storeIds, IOP, Legacy = [], [], []

    for store_data in resultado_separado:
        if len(store_data) == 3:
            storeIds.append(store_data[0])
            IOP.append(store_data[1])
            Legacy.append(store_data[2])

    df = pd.DataFrame({
        'storeId': storeIds,
        'MongoDB': IOP,
        'Legacy': Legacy
    }).set_index('storeId')

    ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")])
    if ruta:
        def exportar_excel():
            df.to_excel(ruta)
            messagebox.showinfo("Archivo guardado", "El archivo ha sido guardado correctamente.")
        threading.Thread(target=exportar_excel).start()

def consultar(resultado_text, store_entry, system_var):
    tienda = store_entry.get()
    selected_system = system_var.get()
    limpiar_texto(resultado_text)
    threading.Thread(target=validar_tienda_mongo, args=(tienda, selected_system, resultado_text)).start()

def exportar_con_hilos(store_entry, system_var, ventana, resultado_text):
    tiendas = store_entry.get()
    selected_system = system_var.get()

    def ejecutar():
        resultado = validar_tienda_mongo(tiendas, selected_system, resultado_text)
        exportar_resultado(resultado, ventana)

    threading.Thread(target=ejecutar).start()

def limpiar(resultado_text):
    limpiar_texto(resultado_text)

def main():
    ventana = tk.Toplevel()
    ventana.title("Comprobar variables de migración")
    ventana.geometry("650x400")

    marco = ttk.Frame(ventana)
    marco.pack(padx=20, pady=20)

    ttk.Label(marco, text="Tiendas (separadas por comas):").grid(row=1, column=0, padx=10, pady=10)
    store_entry = ttk.Entry(marco, width=40)
    store_entry.grid(row=1, column=1, padx=10, pady=10)

    ttk.Label(marco, text="Selecciona la conexión:").grid(row=3, column=0, padx=10, pady=10)
    system_var = tk.StringVar(value="BK")

    system_frame = ttk.Frame(marco)
    system_frame.grid(row=3, column=1, columnspan=2, padx=10, pady=5)
    ttk.Radiobutton(system_frame, text="BurguerQueen", variable=system_var, value="BK").grid(row=0, column=0, padx=5, pady=5)
    ttk.Radiobutton(system_frame, text="McAndrews", variable=system_var, value="MC").grid(row=0, column=1, padx=5, pady=5)

    resultado_text = tk.Text(marco, height=10, width=60)
    resultado_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    button_frame = ttk.Frame(marco)
    button_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    ttk.Button(button_frame, text="Consultar", command=lambda: consultar(resultado_text, store_entry, system_var)).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(button_frame, text="Limpiar", command=lambda: limpiar(resultado_text)).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(button_frame, text="Exportar", command=lambda: exportar_con_hilos(store_entry, system_var, ventana, resultado_text)).grid(row=0, column=2, padx=5, pady=5)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    main()
    root.mainloop()
