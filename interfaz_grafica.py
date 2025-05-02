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
        
        # Asegurar que existan las carpetas
        os.makedirs(CONFIG['ruta_reportes'], exist_ok=True)
        os.makedirs(CONFIG['ruta_inputs'], exist_ok=True)
        os.makedirs(CONFIG['ruta_procesadas'], exist_ok=True)

        # Widgets
        tk.Label(root, text="Sistema Automatizado de Facturas", font=('Arial', 14)).pack(pady=10)
        
        tk.Button(root, text="Procesar Facturas", command=self.procesar).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(root, text="Abrir Carpeta de Reportes", command=self.abrir_reportes).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(root, text="Configuración", command=self.configuracion).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(
            root, 
            text="Abrir Carpeta de Facturas", 
            command=lambda: self.abrir_carpeta('inputs')  # Usaremos un método nuevo
        ).pack(pady=5, fill=tk.X, padx=50)
        tk.Button(root, text="Salir", command=root.quit).pack(pady=5, fill=tk.X, padx=50)
        
        # Área de estado
        self.estado = tk.Label(root, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.estado.pack(side=tk.BOTTOM, fill=tk.X)

    def procesar(self):
        self.estado.config(text="Procesando...")
        self.root.update()
        
        try:
            resultado = procesar_carpeta()
            if resultado:
                msg = (
                    f"✅ Se procesaron {len(resultado)} facturas\n\n"
                    f"📂 Origen: {CONFIG['ruta_inputs']}\n"
                    f"📦 Destino: {CONFIG['ruta_procesadas']}\n"
                    f"📊 Reportes generados en: {CONFIG['ruta_reportes']}"
                )
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showwarning(
                    "Advertencia", 
                    f"No se encontraron archivos para procesar en:\n{CONFIG['ruta_inputs']}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
        finally:
            self.estado.config(text="Listo")

    def abrir_carpeta(self, tipo_carpeta):
        try:
            ruta = {
                'inputs': CONFIG['ruta_inputs'],
                'reportes': CONFIG['ruta_reportes'],
                'procesadas': CONFIG['ruta_procesadas']
            }.get(tipo_carpeta)
            
            if os.path.exists(ruta):
                os.startfile(ruta)
            else:
                messagebox.showerror(
                    "Error", 
                    f"No se encontró la carpeta:\n{ruta}"
                )
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"No se pudo abrir la carpeta:\n{str(e)}"
            )

    def abrir_reportes(self):
        try:
            if os.path.exists(CONFIG['ruta_reportes']):
                if os.listdir(CONFIG['ruta_reportes']):  # Verifica si hay archivos
                    os.startfile(CONFIG['ruta_reportes'])
                else:
                    messagebox.showwarning(
                        "Advertencia", 
                        f"La carpeta de reportes está vacía:\n{CONFIG['ruta_reportes']}"
                    )
            else:
                messagebox.showerror(
                    "Error", 
                    f"No se encontró la carpeta:\n{CONFIG['ruta_reportes']}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")
    def configuracion(self):
        config_text = (
            "Configuración Actual:\n\n"
            f"📁 Carpeta de entrada: {CONFIG['ruta_inputs']}\n"
            f"📊 Carpeta de reportes: {CONFIG['ruta_reportes']}\n"
            f"🗄️ Carpeta procesadas: {CONFIG['ruta_procesadas']}\n"
            f"🔄 Formatos soportados: {', '.join(CONFIG['formatos_soportados'])}\n"
            f"📄 Formato de reporte: {CONFIG['formato_reporte'].upper()}"
        )
        messagebox.showinfo("Configuración del Sistema", config_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazFacturas(root)
    root.mainloop()