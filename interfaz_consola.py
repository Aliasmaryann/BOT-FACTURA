# interfaz_consola.py
import os
from main import procesar_carpeta
from config import CONFIG

def mostrar_menu():
    print("\n" + "="*40)
    print(" BOT PROCESADOR DE FACTURAS ".center(40))
    print("="*40)
    print("1. Procesar facturas nuevas")
    print("2. Ver reportes anteriores")
    print("3. Configuración")
    print("4. Salir")

def interfaz_consola():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            print("\nProcesando facturas...")
            archivos_procesados = procesar_carpeta()
            print(f"\n✅ Se procesaron {len(archivos_procesados)} facturas")
            
        elif opcion == "2":
            reportes = os.listdir("outputs/reportes")
            print("\nReportes disponibles:")
            for i, reporte in enumerate(reportes, 1):
                print(f"{i}. {reporte}")
            
        elif opcion == "3":
            print("\nConfiguración actual:")
            print(f"- Carpeta de entrada: {CONFIG['ruta_inputs']}")
            print(f"- Formatos soportados: {', '.join(CONFIG['formatos_soportados'])}")
            
        elif opcion == "4":
            print("\nHasta luego!")
            break
            
        else:
            print("\n❌ Opción no válida")

if __name__ == "__main__":
    interfaz_consola()