import pandas as pd
from typing import List, Dict, Optional, Tuple

def leer_facturas_excel(ruta: str) -> List[Dict]:

    try:
        df = pd.read_excel(ruta, sheet_name="Hoja1")
        # Normaliza nombres de columnas (opcional)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        return df.to_dict('records')
    except Exception as e:
        raise ValueError(f"Error al leer el archivo Excel: {str(e)}") # Convertir a lista de diccionarios

def validar_factura(factura: Dict) -> List[str]:
    errores = []
    if not factura.get("numero_factura"):
        errores.append("Número de factura vacío")
    if not isinstance(factura.get("monto"), (int, float)) or factura["monto"] <= 0:
        errores.append("Monto inválido o faltante")
    if not factura.get("proveedor_id"):
        errores.append("ID de proveedor faltante")
    return errores

def clasificar_factura(
    factura: Dict, 
    historico_proveedor: Optional[Dict]
) -> Tuple[str, Optional[str]]:
    

    errores = validar_factura(factura)
    if errores:  # Corregido: estaba if not validar_factura()
        return "Rechazada", "; ".join(errores)
    
    if not historico_proveedor:
        return "Pendiente", "Proveedor no registrado"
    
    monto_historico = historico_proveedor.get("monto_promedio", 0)
    
    if abs(factura["monto"] - monto_historico) > monto_historico * 0.2:
        return "Pendiente", "Monto difiere del histórico en más del 20%"
    
    return "Aprobada", None