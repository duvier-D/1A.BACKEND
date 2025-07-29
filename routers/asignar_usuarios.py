from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario, Trabajador, AsignarUsuario
from schemas import AsignarUsuarioCreate, AsignarUsuarioOut, PerfilResponse

router = APIRouter(prefix="/asignar-usuario", tags=["Asignar Usuario"])

# ✅ 1. Crear asignación (usuario ↔ trabajador)
@router.post("/", response_model=AsignarUsuarioOut)
def asignar_usuario(asignacion: AsignarUsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.username == asignacion.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    trabajador = db.query(Trabajador).filter(Trabajador.cedula == asignacion.trabajador_id).first()
    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    nueva_asignacion = AsignarUsuario(usuario_id=usuario.username, trabajador_id=trabajador.cedula)
    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)

    return nueva_asignacion


# ✅ 2. Obtener perfil por usuario (para el header)
@router.get("/perfil/{username}", response_model=PerfilResponse)
def obtener_perfil(username: str, db: Session = Depends(get_db)):
    asignacion = db.query(AsignarUsuario).filter(AsignarUsuario.usuario_id == username).first()
    if not asignacion:
        raise HTTPException(status_code=404, detail="No hay trabajador asignado a este usuario")

    trabajador = db.query(Trabajador).filter(Trabajador.cedula == asignacion.trabajador_id).first()
    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    return PerfilResponse(nombre=trabajador.nombre, foto=trabajador.foto)

# ✅ Eliminar asignación
@router.delete("/{id}", status_code=204)
def eliminar_asignacion(id: int, db: Session = Depends(get_db)):
    asignacion = db.query(AsignarUsuario).filter(AsignarUsuario.id == id).first()
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    db.delete(asignacion)
    db.commit()
    return {"message": "Asignación eliminada correctamente"}

    
@router.get("/", response_model=list[AsignarUsuarioOut])
def listar_asignaciones(db: Session = Depends(get_db)):
    return db.query(AsignarUsuario).all()
