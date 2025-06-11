import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import threading

# Importamos los módulos con las funciones originales
import copia_gds
import copia_tiendas
import gdarray
import weekendDays
import maxprep
import obtener_gds
import obtener_tiendas
import filtro_retraso
import filtro_allowblocked
import filtro_buffer
import obtener_pedidos
import pedidos_picking
import check_packing
import migra_grupos
import migra_tiendas

# Función para ejecutar tareas en segundo plano
def ejecutar_en_hilo(func):
    def wrapper():
        threading.Thread(target=func, daemon=True).start()
    return wrapper

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Utilidades Migración y Soporte")
        self.root.geometry("900x500")
        self.root.resizable(False, False)
        
        # Aplicar estilo moderno con ttkbootstrap
        self.style = tb.Style("darkly")
        
        # Crear menú superior mejorado
        self.crear_menu()
        
        # Crear contenedor de botones
        self.crear_contenido()

        # Añadir fondo ASCII
        self.crear_fondo_ascii()

    def crear_menu(self):
        menu_bar = tk.Menu(self.root)

        # Menú de Copias de Seguridad
        menu_copias = tk.Menu(menu_bar, tearoff=0)
        menu_copias.add_command(label="📁 Copia Grupos", command=ejecutar_en_hilo(copia_gds.main))
        menu_copias.add_command(label="🏪 Copia Tendas", command=ejecutar_en_hilo(copia_tiendas.main))
        menu_copias.add_separator()
        menu_bar.add_cascade(label="🔄 Copias de Seguridade", menu=menu_copias)

        # Menú de Utilidades
        menu_utilidades = tk.Menu(menu_bar, tearoff=0)
        menu_utilidades.add_command(label="📊 Gruposs a Array", command=ejecutar_en_hilo(gdarray.main))
        menu_utilidades.add_command(label="📆 Fins de Semana", command=ejecutar_en_hilo(weekendDays.main))
        menu_utilidades.add_command(label="⏳ Data máxima de preparación", command=ejecutar_en_hilo(maxprep.main))
        menu_utilidades.add_separator()
        menu_utilidades.add_command(label="📋 Obter varios Grupos", command=ejecutar_en_hilo(obtener_gds.main))
        menu_utilidades.add_command(label="🏬 Obter varias Tendas", command=ejecutar_en_hilo(obtener_tiendas.main))
        menu_bar.add_cascade(label="⚙️ Utilidades", menu=menu_utilidades)

        # Menú de Filtros
        menu_filtros = tk.Menu(menu_bar, tearoff=0)
        menu_filtros.add_command(label="⏳ Filtro Retraso", command=ejecutar_en_hilo(filtro_retraso.main))
        menu_filtros.add_command(label="🚫 Filtro Pedidos Bloqueados", command=ejecutar_en_hilo(filtro_allowblocked.main))
        menu_filtros.add_command(label="📦 Filtro Buffer", command=ejecutar_en_hilo(filtro_buffer.main))
        menu_filtros.add_separator()
        menu_bar.add_cascade(label="🛠️ Filtros", menu=menu_filtros)

        # Menú de Configuraciones
        menu_config = tk.Menu(menu_bar, tearoff=0)
        menu_config.add_command(label="📦 Comparar pedidos", command=ejecutar_en_hilo(obtener_pedidos.main))
        menu_config.add_separator()
        menu_config.add_command(label="⚡ Check Migradas", command=ejecutar_en_hilo(check_packing.main))
        menu_config.add_separator()
        menu_config.add_command(label="🚛 Últimos Pedidos Recibidos", command=ejecutar_en_hilo(pedidos_picking.main))
        menu_bar.add_cascade(label="✅ Chequeos", menu=menu_config)


        # Menú de Migraciones
        menu_migra = tk.Menu(menu_bar, tearoff=0)
        menu_migra.add_command(label="📦 Migración Grupos", command=ejecutar_en_hilo(migra_grupos.main))
        menu_migra.add_command(label="⚙️ Migra Tiendas", command=ejecutar_en_hilo(migra_tiendas.main))

        menu_migra.add_separator()
        menu_bar.add_cascade(label="⚡ Migraciones", menu=menu_migra)


        # Agregar el menú a la ventana
        self.root.config(menu=menu_bar)

    def crear_fondo_ascii(self):
        texto_ascii = """
         _   _ _____ ___ _     ___ ____    _    ____  _____ ____    ____  _____ 
        | | | |_   _|_ _| |   |_ _|  _ \  / \  |  _ \| ____/ ___|  |  _ \| ____|
        | | | | | |  | || |    | || | | |/ _ \ | | | |  _| \___ \  | | | |  _|  
        | |_| | | |  | || |___ | || |_| / ___ \| |_| | |___ ___) | | |_| | |___ 
        \___/  |_| |___|_____|___|____/_/_ _\_\____/|_____|____/  |____/|_____|
        / ___| / _ \|  _ \ / _ \|  _ \_   _| ____| \ \ / /                      
        \___ \| | | | |_) | | | | |_) || | |  _|    \ V /                       
        ___) | |_| |  __/| |_| |  _ < | | | |___    | |                        
        |____/_\___/|_|_ __\___/|_|_\_\|_|_|_____|__ |_|  _                     
        |  \/  |_ _/ ___|  _ \    / \  / ___|_ _|/_/ | \ | |                    
        | |\/| || | |  _| |_) |  / _ \| |    | |/ _ \|  \| |                    
        | |  | || | |_| |  _ <  / ___ \ |___ | | |_| | |\  |                    
        |_|  |_|___\____|_| \_\/_/   \_\____|___\___/|_| \_|                                                                                                                                        
        """
        text_widget = tk.Text(self.root, wrap="word", font=("Courier", 8), bg="black", fg="white", height=15, width=80)
        text_widget.insert(tk.END, texto_ascii)
        text_widget.config(state=tk.DISABLED)  
        text_widget.place(relx=0.6, rely=0.7, anchor="center")  

    def crear_contenido(self):
        frame = ttk.LabelFrame(self.root, text="Acciones Rápidas", padding=20)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Botones principales con iconos
        botones = [
            ("📁 Copia Grupos", copia_gds.main),
            ("🏪 Copia Tendas", copia_tiendas.main),
            ("📊 Grupos a Array", gdarray.main),
            ("📆 Fins de  Semana", weekendDays.main),
            ("⏳ Data Max Preparacion", maxprep.main),
            ("📋 Obter varios Grupos", obtener_gds.main),
            ("✅ Check Migradas", check_packing.main)
        ]
        
        for i, (texto, comando) in enumerate(botones):
            btn = tb.Button(frame, text=texto, command=ejecutar_en_hilo(comando), bootstyle="primary")
            btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
