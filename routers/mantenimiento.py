from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal
from models import Mantenimiento, Computador
from schemas import MantenimientoCreate, MantenimientoUpdate, MantenimientoOut
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/mantenimientos", tags=["Mantenimientos"])

# ✅ Dependencia para DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_enum(mantenimiento: Mantenimiento):
    if hasattr(mantenimiento.tipo, "value"):
        mantenimiento.tipo = mantenimiento.tipo.value
    if hasattr(mantenimiento.estado, "value"):
        mantenimiento.estado = mantenimiento.estado.value
    return mantenimiento


# ✅ 1. Listar mantenimientos con rango de fechas
@router.get("/", response_model=List[MantenimientoOut])
def listar_mantenimientos(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    estado: Optional[str] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Mantenimiento).options(joinedload(Mantenimiento.computador))

    if fecha_inicio and fecha_fin:
        query = query.filter(Mantenimiento.fecha.between(fecha_inicio, fecha_fin))
    elif fecha_inicio:
        query = query.filter(Mantenimiento.fecha >= fecha_inicio)
    elif fecha_fin:
        query = query.filter(Mantenimiento.fecha <= fecha_fin)

    if tipo:
        query = query.filter(Mantenimiento.tipo == tipo)
    if estado:
        query = query.filter(Mantenimiento.estado == estado)

    mantenimientos = query.order_by(Mantenimiento.fecha.desc()).all()
    return [normalize_enum(m) for m in mantenimientos]


# ✅ 2. Crear mantenimiento
@router.post("/", response_model=MantenimientoOut)
def crear_mantenimiento(mantenimiento: MantenimientoCreate, db: Session = Depends(get_db)):
    computador = db.query(Computador).filter(Computador.codigo == mantenimiento.computador_id).first()
    if not computador:
        raise HTTPException(status_code=404, detail="Computador no encontrado")

    nuevo = Mantenimiento(**mantenimiento.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return normalize_enum(nuevo)


# ✅ 3. Actualizar mantenimiento
@router.put("/{id}", response_model=MantenimientoOut)
def actualizar_mantenimiento(id: int, mantenimiento: MantenimientoUpdate, db: Session = Depends(get_db)):
    db_mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == id).first()
    if not db_mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    for key, value in mantenimiento.dict().items():
        setattr(db_mantenimiento, key, value)

    db.commit()
    db.refresh(db_mantenimiento)
    return normalize_enum(db_mantenimiento)


# ✅ 4. Eliminar mantenimiento
@router.delete("/{id}")
def eliminar_mantenimiento(id: int, db: Session = Depends(get_db)):
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == id).first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    db.delete(mantenimiento)
    db.commit()
    return {"mensaje": "✅ Mantenimiento eliminado exitosamente"}


# ✅ 5. Listar computadores
@router.get("/computadores", response_model=List[dict])
def listar_computadores(db: Session = Depends(get_db)):
    computadores = db.query(Computador).all()
    return [{"codigo": c.codigo, "nombre": c.nombre} for c in computadores]
