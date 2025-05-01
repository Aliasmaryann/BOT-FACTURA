import sqlite3
import os
import pandas as pd

def create_database():
    try:

        os.makedirs("data", exist_ok=True)#manejo de errores
        
        conn = sqlite3.connect("data/facturas.db")
        cursor = conn.cursor()


        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='proveedores'")
        if not cursor.fetchone():
            # Nueva tabla para proveedores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT UNIQUE NOT NULL,
                    rut TEXT UNIQUE NOT NULL,
                    monto_promedio REAL,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            print("✅ Tabla 'proveedores' creada exitosamente")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facturas'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE facturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_factura TEXT UNIQUE NOT NULL,
                    proveedor_id INTEGER NOT NULL,
                    monto_total REAL CHECK(monto_total > 0),
                    fecha_emision TEXT CHECK(date(fecha_emision) IS NOT NULL),
                    estado TEXT DEFAULT 'Pendiente'
                        CHECK(estado IN ('Pendiente', 'Aprobada', 'Rechazada')),
                    anomalia TEXT DEFAULT NULL,
                    comentarios TEXT,
                    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
                )
            ''')
            print("✅ Tabla 'facturas' creada exitosamente")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detalle_factura'")
        if not cursor.fetchone():
            #TABLA DETALEE-FACTURA
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_factura (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER NOT NULL,
                producto TEXT NOT NULL,
                cantidad REAL NOT NULL CHECK(cantidad > 0),
                precio_unitario REAL NOT NULL CHECK(precio_unitario >= 0),
                subtotal REAL GENERATED ALWAYS AS (cantidad * precio_unitario) VIRTUAL,
                FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE
            )
            ''')
            print("✅ Tabla 'detalle_factura' creada exitosamente")
            conn.commit()
            
        else:
            print("ℹ️ La tabla 'facturas' ya existe")
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
    finally:
        if conn:
            conn.close()

def procesar_factura_excel(ruta: str) -> dict:
    """
    Procesa el archivo Excel con el nuevo formato y devuelve datos estructurados.
    
    Returns:
        {
            "encabezado": {
                "numero_factura": "F001",
                "proveedor_id": 1,
                "fecha_emision": "2025-04-10",
                "comentarios": "30 días de plazo"
            },
            "items": [
                {"producto": "Laptop 32\" LG", "cantidad": 2, "precio_unitario": 160000},
                ...
            ],
            "totales": {
                "iva": 60800,
                "monto_total": 380800
            }
        }
    """
    # Leer solo las celdas con datos
    df = pd.read_excel(ruta, header=None, usecols="A:D", nrows=15).dropna(how="all")
    
    # Extraer encabezado (filas 1-4)
    encabezado = {
        "numero_factura": df.iloc[0, 1],
        "proveedor_id": int(df.iloc[1, 1]),
        "fecha_emision": df.iloc[2, 1].strftime("%Y-%m-%d"),
        "comentarios": df.iloc[3, 1] if pd.notna(df.iloc[3, 1]) else None
    }
    
    # Extraer items (filas 6-11)
    items = []
    for i in range(5, 11):
        if pd.notna(df.iloc[i, 0]):
            items.append({
                "producto": df.iloc[i, 0],
                "cantidad": float(df.iloc[i, 1]),
                "precio_unitario": float(df.iloc[i, 2])
            })
    
    # Extraer totales (filas 13-14)
    totales = {
        "iva": float(df.iloc[12, 2]),
        "monto_total": float(df.iloc[13, 2])
    }
    
    return {"encabezado": encabezado, "items": items, "totales": totales}


def insert_invoice_from_excel(ruta_excel: str, estado: str = "Pendiente", anomalia: str = None) -> int:
    """
    Procesa un archivo Excel en el nuevo formato y lo inserta en la DB.
    
    Args:
        ruta_excel: Path del archivo Excel con el formato nuevo
        estado: 'Pendiente', 'Aprobada' o 'Rechazada'
        anomalia: None, 'Normal' o 'Anomalía'
        
    Returns:
        ID de la factura insertada
    """
    datos = procesar_factura_excel(ruta_excel)
    
    conn = sqlite3.connect("data/facturas.db")
    cursor = conn.cursor()
    
    try:
        # Validación básica
        if not datos["items"]:
            raise ValueError("La factura debe tener al menos un ítem")
        
        if estado not in ('Pendiente', 'Aprobada', 'Rechazada'):
            raise ValueError(f"Estado inválido: {estado}. Debe ser: Pendiente, Aprobada o Rechazada")
        # Calcular totales
        neto = sum(item['cantidad'] * item['precio_unitario'] for item in datos["items"] )
        iva = neto * 0.19  # Ejemplo para Chile (19% IVA)
        total = neto + iva

        # 1. Insertar encabezado de factura
        cursor.execute('''
        # Insertar encabezado
        
            INSERT INTO facturas (
                numero_factura, proveedor_id, fecha_emision,
                monto_total, comentarios, estado, anomalia
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos["encabezado"]["numero_factura"],
            datos["encabezado"]["proveedor_id"],
            datos["encabezado"]["fecha_emision"],
            datos["totales"]["monto_total"],
            datos["encabezado"]["comentarios"],
            estado,
            anomalia
        ))
        factura_id = cursor.lastrowid


        # 2. Insertar ítems de detalle
        for item in datos["items"]:
            cursor.execute('''
            INSERT INTO detalle_factura (
                factura_id,
                producto,
                cantidad,
                precio_unitario
            ) VALUES (?, ?, ?, ?)
            ''', (
                factura_id,
                item['producto'],
                item['cantidad'],
                item['precio_unitario']
            ))

        conn.commit()

        print(f"✅ Factura {datos['encabezado']['numero_factura']} insertada (ID: {factura_id})")
        return factura_id

    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Error de integridad: {str(e)}")
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def obtener_historico_proveedor(nombre_proveedor: str) -> dict:
    
    conn = sqlite3.connect("data/facturas.db")
    try:
        cursor = conn.cursor()
        
        # 1. Verificar si el proveedor existe en la tabla proveedores
        cursor.execute('''
            SELECT id, monto_promedio, activo 
            FROM proveedores 
            WHERE nombre = ?
        ''', (nombre_proveedor,))
        prov_data = cursor.fetchone()
        
        
        if not prov_data:
            return None 
        
        proveedor_id, monto_prom, activo = prov_data

        cursor.execute('''
            SELECT 
                COUNT(*) as cantidad,
                AVG(monto_total) as promedio,
                MAX(monto_total) as maximo
            FROM facturas 
            WHERE proveedor_id = ? AND estado = 'Aprobada'
        ''', (proveedor_id,))
        stats = cursor.fetchone()
        
        return {
            'proveedor': nombre_proveedor,
            'monto_promedio': float(monto_prom if monto_prom else (stats[1] if stats and stats[1] else 0)),
            'activo': bool(activo),
            'cantidad_aprobadas': stats[0] if stats else 0,
            'monto_maximo': float(stats[2] if stats and stats[2] else 0)
        }
        
    except sqlite3.Error as e:
        print(f"Error al consultar proveedor: {e}")
        return None
    finally:
        conn.close()