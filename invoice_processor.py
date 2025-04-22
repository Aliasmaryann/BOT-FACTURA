import pandas as pd

def leer_facturas_excel(ruta):
    df = pd.read_excel(ruta, sheet_name="Hoja1")
    return df.to_dict('records')  # Convertir a lista de diccionarios

def validar_factura(factura):
    errores = []
    if not factura.get("numero_factura"):
        errores.append("Número de factura vacío")
    if factura.get("monto") <= 0:
        errores.append("Monto inválido")
    return errores