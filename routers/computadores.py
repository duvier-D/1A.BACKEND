from fastapi import APIRouter, Depends, HTTPException,requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Computador
from schemas import ComputadorCreate, ComputadorUpdate, ComputadorOut
from fastapi import UploadFile, File
from sqlalchemy.orm import joinedload
import shutil
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/computadores/", response_model=list[ComputadorOut])
def listar_computadores(db: Session = Depends(get_db)):
    return db.query(Computador).options(joinedload(Computador.trabajador)).all()

@router.post("/computadores/", response_model=ComputadorOut)
def crear_computador(computador: ComputadorCreate, db: Session = Depends(get_db)):
    nuevo = Computador(**computador.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/computadores/{codigo}", response_model=ComputadorOut)
def actualizar_computador(codigo: str, computador: ComputadorUpdate, db: Session = Depends(get_db)):
    db_computador = db.query(Computador).filter(Computador.codigo == codigo).first()
    if not db_computador:
        raise HTTPException(status_code=404, detail="Computador no encontrado")

    for key, value in computador.dict().items():
        setattr(db_computador, key, value)

    db.commit()
    db.refresh(db_computador)
    return db_computador

@router.delete("/computadores/{codigo}")
def eliminar_computador(codigo: str, db: Session = Depends(get_db)):
    computador = db.query(Computador).filter(Computador.codigo == codigo).first()

    if not computador:
        raise HTTPException(status_code=404, detail="Computador no encontrado")

    # Si tiene una ruta de foto, intenta eliminar el archivo físico
    if computador.foto and computador.foto.startswith("http://192.168.1.233:8000/fotos/"):
        nombre_foto = computador.foto.split("/fotos/")[-1]  # solo el nombre del archivo
        ruta_foto = os.path.join(os.path.dirname(__file__), "..", "fotos", nombre_foto)

        if os.path.exists(ruta_foto):
            os.remove(ruta_foto)

    db.delete(computador)
    db.commit()
    return {"mensaje": "Computador eliminado"}

FOTOS_DIR = os.path.join(os.path.dirname(__file__), "..", "fotos")

@router.post("/upload-foto/")
def subir_foto(foto: UploadFile = File(...)):
    ruta_destino = os.path.join(FOTOS_DIR, foto.filename)

    with open(ruta_destino, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    url_foto = f"http://192.168.1.233:8000/fotos/{foto.filename}"
    return {"foto_url": url_foto}

# ✅ Obtener un computador por su código
@router.get("/computadores/{codigo}", response_model=ComputadorOut)
def obtener_computador(codigo: str, db: Session = Depends(get_db)):
    computador = db.query(Computador).filter(Computador.codigo == codigo).first()
    if not computador:
        raise HTTPException(status_code=404, detail="Computador no encontrado")
    return computador
