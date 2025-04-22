from database import create_database, insert_invoice
from invoice_processor import leer_facturas_excel, validar_factura
from ia_anomaly_detection import detectar_anomalias
import os
import sqlite3
import pandas as pd

from report_generator import ReportGenerator
#bot_env\Scripts\activate

def main():

    # --- RESET DE BASE DE DATOS (opcional, solo para desarrollo) ---
    if os.path.exists("data/facturas.db"):
        os.remove("data/facturas.db")  # Elimina la base de datos existente
        print("🗑️ Base de datos anterior eliminada")

    create_database()  # Crea una nueva estructura limpia

    conn = sqlite3.connect("data/facturas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tablas existentes:", cursor.fetchall())
    cursor.execute("PRAGMA table_info(facturas)")
    print("Columnas de 'facturas':", cursor.fetchall())
    conn.close()    

    facturas = leer_facturas_excel(r"C:\Users\alias\OneDrive\Escritorio\AIEP\Semestre 6\Automatizacion\factura_bot\data\facturas.xlsx")
    
    #deteccion de anomalias
    montos = [f["monto"] for f in facturas]
    anomalias = detectar_anomalias(montos)
    
    for i, factura in enumerate(facturas):
        errores = validar_factura(factura)
        if not errores:
            if factura["monto"] > 1000000:  # Umbral ajustable
                print(f"⚠️ Alerta: Monto sospechoso en factura {factura['numero_factura']} (${factura['monto']})")
            if anomalias[i] == -1:
                print(f"🚨 Alerta IA: Anomalía detectada en {factura['numero_factura']}")
            
            insert_invoice(
                numero=factura["numero_factura"],
                proveedor=factura["proveedor"],
                monto=factura["monto"],
                fecha=factura["fecha"],
                anomalia=anomalias[i]
            )

    

    print("\n🚨 Resumen de anomalías:")
    conn = sqlite3.connect("data/facturas.db")
    df_anomalias = pd.read_sql("SELECT numero_factura, proveedor, monto FROM facturas WHERE anomalia = '-1'", conn)
    print(df_anomalias)
    conn.close()        
    
    print("Proceso completado. Anomalías detectadas:", anomalias)
    
    conn = sqlite3.connect("data/facturas.db")
    df = pd.read_sql("SELECT * FROM facturas", conn)
    print("\n📊 Contenido de la base de datos:")
    print(df)
    conn.close()

    # Generar reportes
    generador = ReportGenerator()
    reporte = generador.generar_reporte_anomalias()
    
    # Guardar en otro formato
    if not reporte.empty:
        generador._guardar_reporte(reporte)

if __name__ == "__main__":
    print("🔹 Script iniciado...")  # Mensaje de prueba
    main()
    print("🔹 Script finalizado.")  # Confirmación de ejecución