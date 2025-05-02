# interfaz_grafica.py
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from main import procesar_carpeta
from config import CONFIG


class InterfazFacturas:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot de Facturas")
        self.root.geometry("400x300")
        try:
            self.root.iconbitmap('icono.ico')  # Añadir esta línea
        except:
            pass
        # Asegurar que existan las carpetas
        os.makedirs(CONFIG['ruta_reportes'], exist_ok=True)
        os.makedirs(CONFIG['ruta_inputs'], exist_ok=True)
        os.makedirs(CONFIG['ruta_procesadas'], exist_ok=True)

        # Widgets
        tk.Label(root, text="Sistema Automatizado de Facturas", font=('Arial', 14)).pack(pady=10)
        
        tk.Button(root, text="Procesar Facturas", command=self.procesar).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(root, text="Abrir Carpeta de Reportes", command=self.abrir_reportes).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(root, text="Configuración", command=self.configuracion).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(root, text="Abrir Carpeta de Facturas", command=lambda: os.startfile(CONFIG['ruta_inputs'])).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(root, text="Salir", command=root.quit).pack(pady=5, fill=tk.X, padx=50)
        
        # Área de estado
        self.estado = tk.Label(root, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.estado.pack(side=tk.BOTTOM, fill=tk.X)

    def procesar(self):
        self.estado.config(text="Procesando...")
        self.root.update()
        
        try:
            resultado = procesar_carpeta()
            if resultado:  # Verificar que haya resultados
                messagebox.showinfo("Éxito", f"Procesadas {len(resultado)} facturas")
            else:
                messagebox.showwarning("Advertencia", "No se encontraron archivos para procesar")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
        self.estado.config(text="Listo")

    def abrir_reportes(self):
        try:
            if os.path.exists(CONFIG['ruta_reportes']):
                os.startfile(CONFIG['ruta_reportes'])
            else:
                messagebox.showwarning("Advertencia", "La carpeta de reportes no existe")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {str(e)}")

    def configuracion(self):
        config_text = (
            f"Carpeta de entrada: {CONFIG['ruta_inputs']}\n"
            f"Carpeta de reportes: {CONFIG['ruta_reportes']}\n"
            f"Formatos soportados: {', '.join(CONFIG['formatos_soportados'])}\n"
            f"Formato de reporte: {CONFIG['formato_reporte']}"
        )
        messagebox.showinfo("Configuración", config_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazFacturas(root)
    root.mainloop()