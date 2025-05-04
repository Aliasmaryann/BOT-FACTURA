from database import create_database, insert_invoice_from_excel, obtener_historico_proveedor, verificar_tablas
from invoice_processor import procesar_factura_excel, validar_factura, clasificar_factura
from ia_anomaly_detection import detectar_anomalias
import os
import pandas as pd
from config import CONFIG
from report_generator import ReportGenerator
import shutil
#bot_env\Scripts\activate
db_path = CONFIG['ruta_bd']

def crear_estructura():
    """Crea las carpetas necesarias si no existen"""
    os.makedirs(CONFIG['ruta_inputs'], exist_ok=True)
    os.makedirs(CONFIG['ruta_reportes'], exist_ok=True)
    os.makedirs(CONFIG['ruta_procesadas'], exist_ok=True)

def procesar_carpeta():
    reporte_consolidado = []
    
    for archivo in os.listdir(CONFIG['ruta_inputs']):
        if any(archivo.endswith(ext) for ext in CONFIG['formatos_soportados']):
            ruta_completa = os.path.join(CONFIG['ruta_inputs'], archivo)
            try:
                print(f"\n🔹 Procesando: {archivo}")
                
                # Procesamiento de la factura
                datos_factura = procesar_factura_excel(ruta_completa)
                
                # Agregar datos para reporte consolidado
                reporte_consolidado.append({
                    'archivo': archivo,
                    'numero_factura': datos_factura['encabezado']['numero_factura'],
                    'monto_total': datos_factura['totales']['monto_total'],
                    'estado': 'Procesado'
                })

                # Mover archivo procesado
                shutil.move(
                    ruta_completa,
                    os.path.join(CONFIG['ruta_procesadas'], archivo)
                )
            except Exception as e:
                print(f"❌ Error procesando {archivo}: {str(e)}")
    
    # Generar reporte consolidado
    if reporte_consolidado:
        generador = ReportGenerator()
        generador.generar_reporte(pd.DataFrame(reporte_consolidado))

def main():

    print("🔹 Script iniciado...")
    crear_estructura()
    # Valores por defecto
    estado = "Rechazada"
    motivo = "No procesado"
    errores = []
    
    db_path = CONFIG['ruta_bd']
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
        verificar_tablas()
    except Exception as e:
        errores.append(f"Error al crear BD: {str(e)}")
  

    reporte_consolidado = []
    for archivo in os.listdir(CONFIG['ruta_inputs']):
        if any(archivo.endswith(ext) for ext in CONFIG['formatos_soportados']):
            ruta_completa = os.path.join(CONFIG['ruta_inputs'], archivo)
            try:
                print(f"\n🔹 Procesando: {archivo}")
                
                # Procesar factura
                datos_factura = procesar_factura_excel(ruta_completa)
                errores = validar_factura(datos_factura)
                
                if errores:
                    print(f"❌ Errores en {archivo}: {', '.join(errores)}")
                    continue
                
                # Detección de anomalías
                montos = [item['precio_unitario'] * item['cantidad'] for item in datos_factura["items"]]
                anomalias = detectar_anomalias(montos)
                
                # Clasificación
                historico = obtener_historico_proveedor(datos_factura["encabezado"]["proveedor_id"])
                estado, motivo = clasificar_factura(datos_factura, historico)
                
                # Insertar en BD
                factura_id = insert_invoice_from_excel(
                    ruta_excel=ruta_completa,
                    estado=estado,
                    anomalia="Anomalía" if any(a == -1 for a in anomalias) else None
                )
                
                # Agregar para reporte consolidado
                reporte_consolidado.append({
                    'archivo': archivo,
                    'numero_factura': datos_factura['encabezado']['numero_factura'],
                    'proveedor': datos_factura['encabezado']['proveedor_id'],
                    'monto_total': datos_factura['totales']['monto_total'],
                    'estado': estado,
                    'motivo': motivo
                })
                
                # Mover archivo procesado
                shutil.move(ruta_completa, os.path.join(CONFIG['ruta_procesadas'], archivo))
                
                print(f"✅ Factura procesada: {datos_factura['encabezado']['numero_factura']}")
                
            except Exception as e:
                print(f"❌ Error procesando {archivo}: {str(e)}")

    # 3. Generación de reporte final
    if reporte_consolidado:
        print("\n📊 Resumen de procesamiento:")
        df_reporte = pd.DataFrame(reporte_consolidado)
        print(df_reporte.to_string(index=False))
        
        generador = ReportGenerator()
        generador.generar_reporte_anomalias(df_reporte)
    
    print("🔹 Script finalizado.")
        

if __name__ == "__main__":
    main()