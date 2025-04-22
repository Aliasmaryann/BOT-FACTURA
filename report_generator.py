import sqlite3
import pandas as pd
import os
from datetime import datetime

print(pd.__version__)
# Si necesitas configuraciones globales:
#from config import UMBRAL_MONTO_SOSPECHOSO, CARPETA_REPORTES  

class ReportGenerator:
    def __init__(self, db_path="data/facturas.db"):
        self.db_path = db_path
        os.makedirs("outputs/reportes", exist_ok=True)
        self.UMBRAL_DEFAULT = 1000000  # Valor por defecto

    def generar_reporte_anomalias(self, umbral=None):
        """
        Genera reporte consolidado de facturas con anomalías.
        
        Args:
            umbral (float): Monto mínimo para alerta. Si es None, usa el de config.py
        
        Returns:
            DataFrame: Pandas DataFrame con resultados
        """
        try:
            umbral = umbral if umbral is not None else self.UMBRAL_DEFAULT
            with sqlite3.connect(self.db_path) as conn:
            
                query = f"""
                SELECT 
                    numero_factura AS "N° Factura",
                    proveedor AS "Proveedor",
                    printf("%,.2f", monto) AS "Monto",
                    fecha AS "Fecha",
                    CASE 
                        WHEN anomalia = '-1' THEN '🚨 Anomalía IA'
                        WHEN monto > {umbral} THEN '⚠️ Monto Alto'
                    END AS "Alerta"
                FROM facturas 
                WHERE anomalia = '-1' OR monto > {umbral}
                ORDER BY monto DESC
                """
                
                df = pd.read_sql(query, conn)
                
                if not df.empty:
                    self._guardar_reporte(df)
                    self._imprimir_consola(df)
                
                return df
            
        except Exception as e:
            print(f"Error generando reporte: {str(e)}")
            return pd.DataFrame()
        

    def _guardar_reporte(self, df, formatos=["csv", "excel", "pdf"]):
        """Guarda reporte en archivo"""
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        resultados = []
        
        extensiones = {"excel": "xlsx", "csv": "csv", "pdf": "pdf"}

        for formato in formatos:
            try:
                ext = extensiones.get(formato, formato)  # usar extensión real
                ruta = f"outputs/reportes/reporte_{fecha}.{ext}"
                
                if formato == "excel":
                    df.to_excel(ruta, index=False, engine='openpyxl')
                elif formato == "csv":
                    df.to_csv(ruta, index=False)
                
                elif formato == "pdf":
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
                    from reportlab.lib import colors
                    
                    doc = SimpleDocTemplate(ruta, pagesize=letter)
                    elementos = []
                    
                    # Convertir DataFrame a lista (incluyendo headers)
                    datos = [df.columns.to_list()] + df.values.tolist()

                    tabla = Table(datos)
                    estilo = TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.grey),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTSIZE', (0,0), (-1,0), 12),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                        ('GRID', (0,0), (-1,-1), 1, colors.black)
                    ])
                    tabla.setStyle(estilo)
                    elementos.append(tabla)
                    
                    doc.build(elementos)
                
                print(f"\n📁 Reporte guardado en: {ruta}")
                resultados.append(True)

            except Exception as e:
                print(f"❌ Error al guardar reporte: {str(e)}")
                resultados.append(False)
        
        return all(resultados)

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
    generador = ReportGenerator()
    generador.generar_reporte_anomalias(umbral=1000000)