import sqlite3
import pandas as pd
import os
from datetime import datetime
from config import CONFIG_REPORTES

print(pd.__version__)
# Si necesitas configuraciones globales:
#from config import UMBRAL_MONTO_SOSPECHOSO, CARPETA_REPORTES  

class ReportGenerator:
    def __init__(self):
        os.makedirs(CONFIG_REPORTES['ruta_salida'], exist_ok=True)
        

    def generar_reporte_anomalias(self, datos, umbral=None):
        """
        Genera reporte 
        """
        try:
            # Convertir a DataFrame manejando diferentes casos
            if isinstance(datos, dict):
                # Si los valores no son listas, los convertimos
                if all(not isinstance(v, (list, pd.Series)) for v in datos.values()):
                    df = pd.DataFrame([datos])  # Crear DF de una sola fila
                else:
                    df = pd.DataFrame(datos)
            elif isinstance(datos, pd.DataFrame):
                df = datos
            else:
                raise ValueError("Formato de datos no soportado")

            if umbral is not None:
                df = df[df['monto_total'] > umbral]

            # Generar reporte en los formatos configurados
            formatos = CONFIG_REPORTES.get('formatos', ['excel'])
            resultados = []

            for formato in formatos:
                if formato == 'pdf':
                    resultados.append(self._generar_pdf(df))
                else:
                    resultados.append(self._guardar_reporte(df, formato))
            
            # Mostrar en consola
            self._imprimir_consola(df)
            
            return self._guardar_reporte(df)

        except Exception as e:
            print(f"Error generando reporte: {str(e)}")
            return False 

    def _guardar_reporte(self, df, formato="xlsx"):
        try:
            fecha = datetime.now().strftime("%Y%m%d_%H%M")
            ruta = f"{CONFIG_REPORTES['ruta_salida']}/reporte_{fecha}.{formato}"
            
            if formato == "xlsx":
                df.to_excel(ruta, index=False, engine='openpyxl')
            elif formato == "csv":
                df.to_csv(ruta, index=False)
            
            print(f"✓ Reporte {formato} guardado: {ruta}")
            return True
        except Exception as e:
            print(f"Error al guardar {formato}: {str(e)}")
            return False
    
    def _generar_pdf(self, df):
        """Genera PDF usando ReportLab"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            
            fecha = datetime.now().strftime("%Y%m%d_%H%M")
            ruta = f"{CONFIG_REPORTES['ruta_salida']}/reporte_{fecha}.pdf"
            
            doc = SimpleDocTemplate(ruta, pagesize=letter)
            elementos = []
            
            datos = [df.columns.to_list()] + df.values.tolist()
            tabla = Table(datos)
            
            estilo = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ])
            tabla.setStyle(estilo)
            elementos.append(tabla)
            
            doc.build(elementos)
            print(f"✓ Reporte PDF guardado: {ruta}")
            return True
            
        except Exception as e:
            print(f"Error al generar PDF: {str(e)}")
            return False


    def _imprimir_consola(self, df):
        """Muestra reporte formateado en consola"""
        print("\n" + "="*50)
        print("*** REPORTE DE ANOMALÍAS ***".center(50))
        print("="*50)
        print(df.to_string(index=False))
        print("\n📊 Resumen:")
        print(f"- Total facturas sospechosas: {len(df)}")
        

# Uso rápido para pruebas
if __name__ == "__main__":
     # Datos de ejemplo
    datos_ejemplo = {
        'factura': ['F001', 'F002'],
        'monto_total': [500000, 1500000],
        'proveedor': ['Prov1', 'Prov2']
    }
    
    generador = ReportGenerator()
    generador.generar_reporte(datos_ejemplo, umbral=1000000)