import sqlite3

conexion = sqlite3.connect("hrms.db")
cursor = conexion.cursor()

# 1. Tu tabla original (Maestro de personal)
cursor.execute("""
CREATE TABLE IF NOT EXISTS maestro_personal (
    id_empleado TEXT PRIMARY KEY,
    dni TEXT UNIQUE,
    nombres_completos TEXT,
    cargo TEXT,
    departamento TEXT,
    fecha_ingreso TEXT,
    estado TEXT
)
""")

# 2. NUEVA TABLA: El registro diario de entradas y salidas
cursor.execute("""
CREATE TABLE IF NOT EXISTS registro_asistencia (
    id_marcaje INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado TEXT,
    fecha_hora TEXT,
    tipo_marcaje TEXT,
    latitud TEXT,
    longitud TEXT,
    foto_path TEXT
)
""")

conexion.commit()
conexion.close()

print("¡Tablas MAESTRO_PERSONAL y REGISTRO_ASISTENCIA listas y operativas!")