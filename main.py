from fastapi import FastAPI
from database import engine, SessionLocal
from models import Base, Usuario, RolEnum
from routers import computadores, usuarios, detalles, trabajador,asignar_usuarios,mantenimiento,permisos
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import hashlib

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear carpeta 'fotos' si no existe
ruta_fotos = os.path.join(os.path.dirname(__file__), "fotos")
os.makedirs(ruta_fotos, exist_ok=True)
app.mount("/fotos", StaticFiles(directory=ruta_fotos), name="fotos")

# Registrar routers
app.include_router(computadores.router)
app.include_router(usuarios.router)
app.include_router(detalles.router)
app.include_router(trabajador.router)
app.include_router(asignar_usuarios.router)
app.include_router(mantenimiento.router)
app.include_router(permisos.router)




@app.get("/")
def root():
    return {"mensaje": "Servidor FastAPI activo"}

# ======== USUARIO PREDETERMINADO ========

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def crear_usuario_admin():
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.username == "admin").first()
        if not existe:
            admin = Usuario(
                username="admin",
                password=hash_password("admin"),  # 👈 Contraseña por defecto
                rol=RolEnum.admin  # Mejor usar el Enum directamente
            )
            db.add(admin)
            db.commit()
            print("✅ Usuario 'admin' creado por defecto")
        else:
            print("ℹ️ Usuario 'admin' ya existe")
    finally:
        db.close()

# 👇 Ejecutar solo al iniciar el servidor
@app.on_event("startup")
def on_startup():
    crear_usuario_admin()
