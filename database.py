import sqlite3
import os

def create_database():
    try:

        os.makedirs("data", exist_ok=True)
        conn = sqlite3.connect("data/facturas.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facturas'")

        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE facturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_factura TEXT UNIQUE,
                    proveedor TEXT,
                    monto REAL,
                    fecha TEXT,
                    estado TEXT DEFAULT 'Pendiente',
                    anomalia TEXT DEFAULT NULL
                )
            ''')
            conn.commit()
            print("✅ Tabla 'facturas' creada exitosamente")
        else:
            print("ℹ️ La tabla 'facturas' ya existe")
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
    finally:
        if conn:
            conn.close()

def insert_invoice(numero, proveedor, monto, fecha, anomalia=None):
    conn = sqlite3.connect("data/facturas.db")
    cursor = conn.cursor()
    try:
        if hasattr(fecha, 'strftime'):  # Si es datetime, Timestamp, etc.
            fecha = fecha.strftime('%Y-%m-%d')

        cursor.execute('''
            INSERT INTO facturas 
            (numero_factura, proveedor, monto, fecha, estado, anomalia)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            numero,
            proveedor,
            monto,
            fecha,
            'Procesado',
            str(anomalia) if anomalia is not None else None
            
        ))
        conn.commit()
        print(f"✅ Factura {numero} insertada correctamente")
    except sqlite3.Error as e:
        print(f"Error al insertar factura {numero}: {e}")
    finally:
        conn.close()