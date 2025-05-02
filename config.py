import os
from pathlib import Path
# Configuración básica del sistema
BASE_DIR = Path(__file__).parent.absolute()

# 1. Rutas de archivos
RUTA_EXCEL = r"C:\Users\alias\OneDrive\Escritorio\AIEP\Semestre 6\Automatizacion\BOT-FACTURA\data\facturas.xlsx"
RUTA_DB = "data/facturas.db"  # Ruta de la base de datos

# 2. Parámetros de facturación
UMBRAL_ANOMALIAS = 1000000  # Monto mínimo para considerar anomalía
DIAS_VENCIMIENTO = 30  # Días para vencimiento de facturas

# 3. Configuración de reportes
CARPETA_REPORTES = "outputs/reportes"  # Donde se guardan los PDF/Excel
# config.py
CONFIG_REPORTES = {
    'ruta_salida': 'outputs/reportes',
    'formatos': ['xlsx', 'pdf'],  # Formatos a generar
    'estilo_pdf': {
        'color_encabezado': '#CCCCCC',
        'color_filas': '#FFFFFF'
    }
}
CONFIG = {
    # Rutas absolutas para evitar problemas
    'ruta_inputs': os.path.join(BASE_DIR, 'inputs'),
    'ruta_reportes': os.path.join(BASE_DIR, 'outputs', 'reportes'),
    'ruta_procesadas': os.path.join(BASE_DIR, 'outputs', 'facturas_procesadas'),
    
    # Configuración de archivos
    'formatos_soportados': ['.xlsx', '.xls'],  # Formatos de factura aceptados
    'formato_reporte': 'xlsx',  # Formato de salida para reportes
    
    # Configuración de la base de datos
    'ruta_bd': os.path.join(BASE_DIR, 'data', 'facturas.db'),
    
    # Configuración de PDF (si se usa)
    'estilo_pdf': {
        'color_encabezado': '#CCCCCC',
        'color_filas': '#FFFFFF',
        'tamanio_letra': 10
    }
}
