import sqlite3
import os

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

def insert_invoice(
    numero_factura: str,
    proveedor_id: int,
    fecha_emision: str,
    items: list,  # Lista de diccionarios con {producto, cantidad, precio_unitario}
    fecha_vencimiento: str = None,
    estado: str = "Pendiente",
    anomalia: int = None,
    comentarios: str = ""
) -> int:
    """
    Inserta una factura con su detalle en la base de datos.
    
    Args:
        numero: Número único de factura
        proveedor_id: ID del proveedor en la tabla proveedores
        items: Lista de ítems [{"producto": str, "cantidad": float, "precio_unitario": float}]
        fecha_emision: Fecha en formato YYYY-MM-DD
        estado: 'Pendiente', 'Aprobada' o 'Rechazada'
        anomalia: -1 (anomalía), 0 (no revisado), 1 (normal)
    
    Returns:
        int: ID de la factura insertada
    
    Raises:
        ValueError: Si los datos son inválidos
        sqlite3.Error: Si hay error en la base de datos
    """
    conn = sqlite3.connect("data/facturas.db")
    cursor = conn.cursor()
    
    try:
        # Validación básica
        if not items:
            raise ValueError("La factura debe tener al menos un ítem")
        
        if estado not in ('Pendiente', 'Aprobada', 'Rechazada'):
            raise ValueError(f"Estado inválido: {estado}. Debe ser: Pendiente, Aprobada o Rechazada")
        # Calcular totales
        neto = sum(item['cantidad'] * item['precio_unitario'] for item in items)
        iva = neto * 0.19  # Ejemplo para Chile (19% IVA)
        total = neto + iva

        # 1. Insertar encabezado de factura
        cursor.execute('''
        INSERT INTO facturas (
            numero_factura, 
            proveedor_id,
            fecha_emision,
            fecha_vencimiento,
            monto_total,
            estado,
            anomalia,
            comentarios
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            numero_factura,
            proveedor_id,
            fecha_emision,
            fecha_vencimiento,
            total,
            estado,
            anomalia,
            comentarios
        ))
        factura_id = cursor.lastrowid

        # 2. Insertar ítems de detalle
        for item in items:
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
        print(f"✅ Factura {numero_factura} insertada (ID: {factura_id})")
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