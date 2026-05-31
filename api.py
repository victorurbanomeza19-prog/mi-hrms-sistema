from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime

# Creamos a nuestro "recepcionista"
app = FastAPI(title="API de Asistencia HRMS")

# ==========================================
# NUEVO: REGLAS DE SEGURIDAD (CORS)
# ==========================================
# Le decimos a la API que acepte conexiones desde cualquier celular o navegador web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # El asterisco significa "Aceptar de todos lados"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Le enseñamos qué formato de datos va a recibir
class Marcaje(BaseModel):
    id_empleado: str
    tipo_marcaje: str
    latitud: str
    longitud: str
    foto: str

# Creamos la "puerta" por donde entrarán los datos
@app.post("/registrar_asistencia")
def registrar_asistencia(datos: Marcaje):
    conexion = sqlite3.connect("hrms.db")
    cursor = conexion.cursor()
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
        INSERT INTO registro_asistencia 
        (id_empleado, fecha_hora, tipo_marcaje, latitud, longitud, foto_path) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (datos.id_empleado, fecha_hora_actual, datos.tipo_marcaje, datos.latitud, datos.longitud, datos.foto))
        
        conexion.commit()
        respuesta = {"estado": "éxito", "mensaje": "Asistencia registrada correctamente"}
        
    except Exception as e:
        respuesta = {"estado": "error", "mensaje": str(e)}
        
    finally:
        conexion.close()
        
    return respuesta