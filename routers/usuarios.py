from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario, RolEnum
from schemas import UsuarioCreate, UsuarioLogin, UsuarioOut
import hashlib

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/usuarios/registrar", response_model=UsuarioOut)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.query(Usuario).filter(Usuario.username == usuario.username).first()
    if existe:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    nuevo = Usuario(
        username=usuario.username,
        password=hash_password(usuario.password),
        rol=usuario.rol
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.post("/usuarios/login", response_model=UsuarioOut)
def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == usuario.username).first()
    if not user or user.password != hash_password(usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return user

@router.get("/usuarios/", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@router.delete("/usuarios/{username}")
def eliminar_usuario(username: str, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"mensaje": "Usuario eliminado"}
