import sqlite3
import os
import pandas as pd
from invoice_processor import procesar_factura_excel

def create_database():
    try:
        os.makedirs("data", exist_ok=True)#manejo de errores
        conn = sqlite3.connect("data/facturas.db")
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY,
                nombre TEXT UNIQUE NOT NULL,
                rut TEXT UNIQUE NOT NULL,
                monto_promedio REAL,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        print("✅ Tabla 'proveedores' verificada/creada")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT UNIQUE NOT NULL,
                proveedor_id INTEGER NOT NULL,
                monto_total REAL CHECK(monto_total > 0),
                fecha_emision TEXT CHECK(fecha_emision IS NOT NULL),
                estado TEXT DEFAULT 'Pendiente'
                    CHECK(estado IN ('Pendiente', 'Aprobada', 'Rechazada')),
                anomalia TEXT DEFAULT NULL,
                comentarios TEXT,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
            )
        ''')
        print("✅ Tabla 'facturas' verificada/creada")
        
        # Crear tabla detalle_factura
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
        print("✅ Tabla 'detalle_factura' verificada/creada")
        conn.commit()
            
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()



def insert_invoice_from_excel(ruta_excel: str, estado: str = "Pendiente", anomalia: str = None) -> int:
    
    datos = procesar_factura_excel(ruta_excel)
    
    conn = sqlite3.connect("data/facturas.db")
    cursor = conn.cursor()
    
    try:
        # Validación básica
        if not datos["items"]:
            raise ValueError("La factura debe tener al menos un ítem")
        
        if estado not in ('Pendiente', 'Aprobada', 'Rechazada'):
            raise ValueError(f"Estado inválido: {estado}. Debe ser: Pendiente, Aprobada o Rechazada")

        # 1. Insertar encabezado de factura
        cursor.execute('''
            INSERT INTO facturas (
                numero_factura, 
                proveedor_id, 
                fecha_emision,
                monto_total, 
                comentarios, 
                estado, 
                anomalia
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

def verificar_tablas():
    conn = sqlite3.connect("data/facturas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = cursor.fetchall()
    print("Tablas existentes:", tablas)
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
                p.id,
                p.monto_promedio,
                p.activo,
                COUNT(f.id) as cantidad,
                AVG(f.monto_total) as promedio,
                MAX(f.monto_total) as maximo
            FROM proveedores p
            LEFT JOIN facturas f ON p.id = f.proveedor_id AND f.estado = 'Aprobada'
            WHERE p.nombre = ?
            GROUP BY p.id
        ''', (nombre_proveedor,))
        
    except sqlite3.Error as e:
        print(f"Error al consultar proveedor: {e}")
        return None
    finally:
        conn.close()