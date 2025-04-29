from database import create_database, insert_invoice_from_excel, obtener_historico_proveedor
from invoice_processor import procesar_factura_excel, validar_factura, clasificar_factura
from ia_anomaly_detection import detectar_anomalias
import os
import sqlite3
import pandas as pd

from report_generator import ReportGenerator
#bot_env\Scripts\activate

def main():

    # Creacion de BD
    if not os.path.exists("data/facturas.db"):
        create_database()  # Elimina la base de datos existente
        print("🗑️ Base de datos creada")



    conn = sqlite3.connect("data/facturas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tablas existentes:", cursor.fetchall())
    conn.close()    

    ruta_excel = r"C:\Users\alias\OneDrive\Escritorio\AIEP\Semestre 6\Automatizacion\factura_bot\data\facturas.xlsx"
    datos_factura = procesar_factura_excel(ruta_excel)
    
    
    #deteccion de anomalias
    montos = [item['precio_unitario'] * item['cantidad'] for item in datos_factura["items"]]
    anomalias = detectar_anomalias(montos)
    
    # Validación y clasificación
    errores = validar_factura(datos_factura)
    

        
    if not errores:
        # Obtener histórico del proveedor
        historico = obtener_historico_proveedor(datos_factura["encabezado"]["proveedor_id"]) 

        # Clasificar la factura
        estado, motivo = clasificar_factura(datos_factura, historico)

        if estado == "Pendiente":
            print(f"⚡ [PENDIENTE] Factura {datos_factura['encabezado']['numero_factura']} - {motivo}")
        elif estado == "Rechazada":
            print(f"❌ [RECHAZADA] Factura {datos_factura['encabezado']['numero_factura']} - {motivo}")

        # Verificación de montos sospechosos (usando monto_total de los datos procesados)
        if datos_factura["totales"]["monto_total"] > 1000000:  # Umbral ajustable
            print(f"⚠️ Alerta: Monto sospechoso en factura {datos_factura['encabezado']['numero_factura']} (${datos_factura['totales']['monto_total']:,})")

        

        # Alertas
        if any(a == -1 for a in anomalias):
            print(f"🚨 Alerta IA: Anomalía detectada en factura {datos_factura['encabezado']['numero_factura']}")
            print(f"""\n
            ⚡ Factura {datos_factura['encabezado']['numero_factura']} - {estado}
            -----------------------------------------
            Proveedor ID: {datos_factura['encabezado']['proveedor_id']}
            Monto Total: ${datos_factura['totales']['monto_total']:,}
            Motivo: {motivo}
            """)
         # Insertar en base de datos
        factura_id = insert_invoice_from_excel(
            ruta_excel=ruta_excel,
            estado=estado,
            anomalia="Anomalía" if any(a == -1 for a in anomalias) else None
        )
        # Generación de reportes
        print("\n🚨 Resumen de anomalías:")
        conn = sqlite3.connect("data/facturas.db")
        df_anomalias = pd.read_sql("""
            SELECT f.numero_factura, p.nombre as proveedor, f.monto_total 
            FROM facturas f
            JOIN proveedores p ON f.proveedor_id = p.id
            WHERE f.anomalia = 'Anomalía'
        """, conn)
        print(df_anomalias)

            
        print("\n📊 Contenido completo de la base de datos:")
        df_facturas = pd.read_sql("""
            SELECT f.id, f.numero_factura, p.nombre as proveedor, 
                f.monto_total, f.estado, f.anomalia
            FROM facturas f
            JOIN proveedores p ON f.proveedor_id = p.id
        """, conn)
        print(df_facturas)
        conn.close()

        # Generar y guardar reportes
        generador = ReportGenerator()
        if not df_anomalias.empty:
            generador.guardar_reporte(df_anomalias, "reporte_anomalias")
        if not df_facturas.empty:
            generador.guardar_reporte(df_facturas, "reporte_general")

if __name__ == "__main__":
    print("🔹 Script iniciado...")  # Mensaje de prueba
    main()
    print("🔹 Script finalizado.")  # Confirmación de ejecución