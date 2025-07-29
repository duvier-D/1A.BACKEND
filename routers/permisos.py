from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal
from models import PermisoSalida, Computador, Trabajador
from schemas import PermisoSalidaCreate, PermisoSalidaUpdate, PermisoSalidaOut
from typing import List, Optional

router = APIRouter(prefix="/permisos", tags=["Permisos"])

# ✅ Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Normalizar Enum
def normalize_enum(permiso: PermisoSalida):
    if hasattr(permiso.estado, "value"):
        permiso.estado = permiso.estado.value
    return permiso

# ✅ 1. Listar permisos con filtros
@router.get("/", response_model=List[PermisoSalidaOut])
def listar_permisos(
    estado: Optional[str] = None,
    nombre: Optional[str] = None,
    apellido: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PermisoSalida).options(joinedload(PermisoSalida.computador), joinedload(PermisoSalida.trabajador))

    if estado:
        query = query.filter(PermisoSalida.estado == estado)
    if nombre:
        query = query.join(PermisoSalida.trabajador).filter(Trabajador.nombre.ilike(f"%{nombre}%"))
    if apellido:
        query = query.join(PermisoSalida.trabajador).filter(Trabajador.apellidos.ilike(f"%{apellido}%"))

    permisos = query.order_by(PermisoSalida.id.desc()).all()
    return [normalize_enum(p) for p in permisos]

# ✅ 2. Crear permiso
@router.post("/", response_model=PermisoSalidaOut)
def crear_permiso(permiso: PermisoSalidaCreate, db: Session = Depends(get_db)):
    computador = db.query(Computador).filter(Computador.codigo == permiso.codigo_computador).first()
    trabajador = db.query(Trabajador).filter(Trabajador.cedula == permiso.cedula_trabajador).first()

    if not computador:
        raise HTTPException(status_code=404, detail="Computador no encontrado")
    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    nuevo = PermisoSalida(**permiso.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return normalize_enum(nuevo)

# ✅ 3. Actualizar permiso
@router.put("/{id}", response_model=PermisoSalidaOut)
def actualizar_permiso(id: int, permiso: PermisoSalidaUpdate, db: Session = Depends(get_db)):
    db_permiso = db.query(PermisoSalida).filter(PermisoSalida.id == id).first()
    if not db_permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")

    for key, value in permiso.dict().items():
        setattr(db_permiso, key, value)

    db.commit()
    db.refresh(db_permiso)
    return normalize_enum(db_permiso)

# ✅ 4. Eliminar permiso
@router.delete("/{id}")
def eliminar_permiso(id: int, db: Session = Depends(get_db)):
    permiso = db.query(PermisoSalida).filter(PermisoSalida.id == id).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")

    db.delete(permiso)
    db.commit()
    return {"mensaje": "✅ Permiso eliminado exitosamente"}
