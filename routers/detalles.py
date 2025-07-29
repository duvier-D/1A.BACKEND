from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Detalle, Computador
from schemas import DetalleCreate, DetalleOut

router = APIRouter()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔍 Obtener los detalles de un computador por su código
@router.get("/computadores/{codigo}/detalles", response_model=DetalleOut)
def obtener_detalle(codigo: str, db: Session = Depends(get_db)):
    detalle = db.query(Detalle).filter(Detalle.codigo_computador == codigo).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return detalle

# ✅ Crear detalle para un computador
@router.post("/detalles/", response_model=DetalleOut)
def crear_detalle(detalle: DetalleCreate, db: Session = Depends(get_db)):
    # Verificar que el computador exista
    computador = db.query(Computador).filter(Computador.codigo == detalle.codigo_computador).first()
    if not computador:
        raise HTTPException(status_code=404, detail="Computador no encontrado")

    nuevo = Detalle(**detalle.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ♻️ Actualizar detalle de un computador
@router.put("/computadores/{codigo}/detalles", response_model=DetalleOut)
def actualizar_detalle(codigo: str, detalle_data: DetalleCreate, db: Session = Depends(get_db)):
    detalle = db.query(Detalle).filter(Detalle.codigo_computador == codigo).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    for key, value in detalle_data.dict().items():
        setattr(detalle, key, value)

    db.commit()
    db.refresh(detalle)
    return detalle

# ❌ Eliminar detalle de un computador
@router.delete("/computadores/{codigo}/detalles")
def eliminar_detalle(codigo: str, db: Session = Depends(get_db)):
    detalle = db.query(Detalle).filter(Detalle.codigo_computador == codigo).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    db.delete(detalle)
    db.commit()
    return {"mensaje": "Detalle eliminado correctamente"}


@router.get("/detalles/{codigo_computador}", response_model=DetalleOut)
def obtener_detalle_por_computador(codigo_computador: str, db: Session = Depends(get_db)):
    detalle = db.query(Detalle).filter(Detalle.codigo_computador == codigo_computador).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return detalle