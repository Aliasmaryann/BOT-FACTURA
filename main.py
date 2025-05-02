from database import create_database, insert_invoice_from_excel, obtener_historico_proveedor, verificar_tablas
from invoice_processor import procesar_factura_excel, validar_factura, clasificar_factura
from ia_anomaly_detection import detectar_anomalias
import os
import sqlite3
import pandas as pd
from config import RUTA_EXCEL
from report_generator import ReportGenerator
#bot_env\Scripts\activate

def main():
    # Valores por defecto
    estado = "Rechazada"
    motivo = "No procesado"
    errores = []
    
    db_path = "data/facturas.db"
    # Eliminar BD si existe
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️ Base de datos anterior eliminada")
        except Exception as e:
            errores.append(f"No se pudo eliminar la BD: {str(e)}")

    try:
        create_database()
        print("✅ Base de datos creada")
        
        # Verificación rápida
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print("Tablas existentes:", cursor.fetchall())
        conn.close()
    except Exception as e:
        errores.append(f"Error al crear BD: {str(e)}")
  

    ruta_excel = RUTA_EXCEL
    if not os.path.exists(ruta_excel):
        errores.append(f"Archivo Excel no encontrado en {ruta_excel}")
    else:
        try:
            datos_factura = procesar_factura_excel(ruta_excel)
            errores = validar_factura(datos_factura)
            
            try:
                fecha_raw = datos_factura['encabezado'].get('fecha_emision', 'NO_EXISTE')
                print("\n=== DEBUG ===")
                print("Valor fecha:", repr(fecha_raw))
                print("Tipo fecha:", type(fecha_raw))
                print("Estructura completa disponible:", 'fecha_emision' in datos_factura['encabezado'])
            except Exception as debug_error:
                print("\n⚠️ Error en debug:", str(debug_error))

            if not errores:
                # Detección de anomalías
                montos = [item['precio_unitario'] * item['cantidad'] for item in datos_factura["items"]]
                anomalias = detectar_anomalias(montos)
                
                # Clasificación
                historico = obtener_historico_proveedor(datos_factura["encabezado"]["proveedor_id"])
                estado, motivo = clasificar_factura(datos_factura, historico)


                # Insertar en base de datos
                factura_id = insert_invoice_from_excel(
                    ruta_excel=ruta_excel,
                    estado=estado,
                    anomalia="Anomalía" if any(a == -1 for a in anomalias) else None
                )

        except Exception as e:
            errores.append(f"Error procesando factura: {str(e)}")

    # Mostrar resultados (siempre seguro)
    print(f"""\n
    📄 Factura {datos_factura['encabezado']['numero_factura'] if 'datos_factura' in locals() else 'N/A'}
    -----------------------------------------
    Proveedor ID: {datos_factura['encabezado']['proveedor_id'] if 'datos_factura' in locals() else 'N/A'}
    Monto Total: ${datos_factura['totales']['monto_total'] if 'datos_factura' in locals() else 0:,}
    Estado: {estado}
    Motivo: {motivo if not errores else ', '.join(errores)}
    """)
    

    # Generación de reportes (solo si no hay errores)
    if not errores and 'datos_factura' in locals():
        if not errores and 'datos_factura' in locals():
            reporte = ReportGenerator()
            datos_reporte = {
                'numero_factura': [datos_factura['encabezado']['numero_factura']],
                'proveedor_id': [datos_factura['encabezado']['proveedor_id']],
                'monto_total': [datos_factura['totales']['monto_total']],
                'estado': [estado],
                'motivo': [motivo]
            }
            reporte.generar_reporte_anomalias(datos_reporte)
        

if __name__ == "__main__":
    print("🔹 Script iniciado...")  # Mensaje de prueba
    main()
    print("🔹 Script finalizado.")  # Confirmación de ejecución