from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Trabajador
from schemas import TrabajadorCreate, TrabajadorUpdate, TrabajadorOut
import os
import shutil

router = APIRouter()

# Carpeta para fotos
FOTOS_DIR = os.path.join(os.path.dirname(__file__), "..", "fotos")
os.makedirs(FOTOS_DIR, exist_ok=True)

# Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Listar trabajadores
@router.get("/trabajadores/", response_model=list[TrabajadorOut])
def listar_trabajadores(db: Session = Depends(get_db)):
    return db.query(Trabajador).all()

# ✅ Crear trabajador
@router.post("/trabajadores/", response_model=TrabajadorOut)
def crear_trabajador(trabajador: TrabajadorCreate, db: Session = Depends(get_db)):
    nuevo = Trabajador(**trabajador.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ✅ Actualizar trabajador
@router.put("/trabajadores/{cedula}", response_model=TrabajadorOut)
def actualizar_trabajador(cedula: str, trabajador: TrabajadorUpdate, db: Session = Depends(get_db)):
    db_trabajador = db.query(Trabajador).filter(Trabajador.cedula == cedula).first()
    if not db_trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    for key, value in trabajador.dict().items():
        setattr(db_trabajador, key, value)

    db.commit()
    db.refresh(db_trabajador)
    return db_trabajador

# ✅ Eliminar trabajador
@router.delete("/trabajadores/{cedula}")
def eliminar_trabajador(cedula: str, db: Session = Depends(get_db)):
    trabajador = db.query(Trabajador).filter(Trabajador.cedula == cedula).first()
    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    # Eliminar foto física si existe
    if trabajador.foto and trabajador.foto.startswith("http://192.168.1.233:8000/fotos/"):
        nombre_foto = trabajador.foto.split("/fotos/")[-1]
        ruta_foto = os.path.join(FOTOS_DIR, nombre_foto)
        if os.path.exists(ruta_foto):
            os.remove(ruta_foto)

    db.delete(trabajador)
    db.commit()
    return {"mensaje": "Trabajador eliminado"}

# ✅ Subir foto
@router.post("/trabajadores/upload-foto/")
def subir_foto(foto: UploadFile = File(...)):
    ruta_destino = os.path.join(FOTOS_DIR, foto.filename)
    with open(ruta_destino, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    url_foto = f"http://192.168.1.233:8000/fotos/{foto.filename}"
    return {"foto_url": url_foto}


# ✅ Obtener un trabajador por su cédula
@router.get("/trabajadores/{cedula}", response_model=TrabajadorOut)
def obtener_trabajador(cedula: str, db: Session = Depends(get_db)):
    trabajador = db.query(Trabajador).filter(Trabajador.cedula == cedula).first()
    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    return trabajador
