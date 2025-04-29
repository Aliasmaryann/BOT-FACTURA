import pandas as pd
from typing import List, Dict, Optional, Tuple

def procesar_factura_excel(ruta: str) -> Dict:
    
    try:
        df = pd.read_excel(ruta, header=None, usecols="A:D")

        # Extraer encabezado
        encabezado = {
            "numero_factura": df.iloc[1, 1],
            "proveedor_id": int(df.iloc[2, 1]),
            "fecha_emision": pd.to_datetime(df.iloc[3, 1]).strftime("%d-%m-%Y") if pd.notna(df.iloc[3, 1]) else None,
            "comentarios": df.iloc[4, 1] if pd.notna(df.iloc[4, 1]) else None
        }
        
        # Extraer items
        items = []
        row = 6  
        while row < len(df):
            # Condiciones para detectar el final de los ítems:
            # - Si la columna B está vacía Y (la columna C o D contiene "IVA" o "TOTAL")
            if isinstance(df.iloc[row, 2], str) and any(
                x in df.iloc[row, 2].lower() for x in ["iva", "total"]
            ):
                break  # Termina el bucle
            
            # Si la fila tiene datos de producto (columna B no vacía)
            if pd.notna(df.iloc[row, 1]):
                try:
                    items.append({
                        "producto": df.iloc[row, 1],  # B
                        "cantidad": float(df.iloc[row, 2]),  # C
                        "precio_unitario": float(df.iloc[row, 3])  # D
                    })
                except ValueError as e:
                    print(f"⚠️ Fila {row+1} ignorada (datos inválidos): {str(e)}")
            row += 1
        
        # --- 3. Extraer totales (busca "IVA" y "TOTAL" en columna C) ---
        totales = {"iva": 0.0, "monto_total": 0.0}
        
        for row_total in range(row, len(df)):
            celda_c = str(df.iloc[row_total, 2]).lower()  # Columna C (ej: "IVA", "TOTAL")
            
            if "iva" in celda_c and pd.notna(df.iloc[row_total, 3]):
                totales["iva"] = float(df.iloc[row_total, 3])  # D
            elif "total" in celda_c and pd.notna(df.iloc[row_total, 3]):
                totales["monto_total"] = float(df.iloc[row_total, 3])  # D

        return {
            "encabezado": encabezado,
            "items": items,
            "totales": totales
        }

    except Exception as e:
        raise ValueError(f"Error al procesar Excel: {str(e)}")

def validar_factura(datos_factura: Dict) -> List[str]:
    errores = []
    encabezado = datos_factura["encabezado"]
    items = datos_factura["items"]

    if not encabezado.get("numero_factura"):
        errores.append("Número de factura vacío")
    
    if not items:
        errores.append("La factura no contiene items")
    
    for i, item in enumerate(items, 1):
        if not item.get("producto"):
            errores.append(f"Item {i}: Producto no especificado")
        if not isinstance(item.get("cantidad"), (int, float)) or item["cantidad"] <= 0:
            errores.append(f"Item {i}: Cantidad inválida")
        if not isinstance(item.get("precio_unitario"), (int, float)) or item["precio_unitario"] <= 0:
            errores.append(f"Item {i}: Precio unitario inválido")
    
    return errores

def clasificar_factura(
    datos_factura: Dict, 
    historico_proveedor: Optional[Dict]
) -> Tuple[str, Optional[str]]:
    

    errores = validar_factura(datos_factura)
    if errores:
        return "Rechazada", "; ".join(errores)
    
    if not historico_proveedor:
        return "Pendiente", "Proveedor no registrado"
    
    monto_actual = datos_factura["totales"]["monto_total"]
    monto_historico = historico_proveedor.get("monto_promedio", 0)
    
    if abs(monto_actual - monto_historico) > monto_historico * 0.2:
        return "Pendiente", "Monto difiere del histórico en más del 20%"
    
    return "Aprobada", None