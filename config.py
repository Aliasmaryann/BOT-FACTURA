# Configuración básica del sistema

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
    'ruta_inputs': 'inputs',
    'ruta_reportes': 'outputs/reportes',
    'ruta_procesadas': 'outputs/facturas_procesadas',
    'formatos_soportados': ['.xlsx', '.xls'],
    'formato_reporte': 'xlsx'  # 'xlsx' o 'pdf'
}