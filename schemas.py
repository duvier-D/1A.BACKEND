from pydantic import BaseModel, EmailStr
from typing import Optional, Literal,List
from datetime import date, time

class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol: Literal["admin", "normal"]

class UsuarioLogin(BaseModel):
    username: str
    password: str

class UsuarioOut(BaseModel):
    username: str
    rol: str

    model_config = {
        "from_attributes": True
    }

class DetalleBase(BaseModel):
    procesador: str
    ram: str
    almacenamiento: str
    sistema_operativo: str
    observaciones: Optional[str] = None
    serial: Optional[str] = None

class DetalleCreate(DetalleBase):
    codigo_computador: str

class DetalleOut(DetalleCreate):
    id: int

    model_config = {
        "from_attributes": True
    }

class TrabajadorBase(BaseModel):
    nombre: str
    apellidos: str
    cargo: str
    area_de_trabajo: str
    edad: int
    residencia: str
    telefono: str
    correo: EmailStr
    foto: Optional[str] = None

class TrabajadorCreate(TrabajadorBase):
    cedula: str

class TrabajadorUpdate(TrabajadorBase):
    pass

class TrabajadorOut(TrabajadorBase):
    cedula: str

    model_config = {
        "from_attributes": True
    }

class AsignarUsuarioCreate(BaseModel):
    usuario_id: str   
    trabajador_id: str  

class AsignarUsuarioOut(BaseModel):
    id: int
    usuario_id: str
    trabajador_id: str

    model_config = {
        "from_attributes": True
    }

class PerfilResponse(BaseModel):
    nombre: str
    foto: Optional[str] = None

class ComputadorBase(BaseModel):
    nombre: str
    marca: str
    trabajador_id: Optional[str] = None
    foto: Optional[str] = None

class ComputadorCreate(ComputadorBase):
    codigo: str

class ComputadorUpdate(ComputadorBase):
    pass

class ComputadorOut(ComputadorCreate):
    trabajador: Optional[TrabajadorOut] = None

    model_config = {
        "from_attributes": True
    }

class MantenimientoBase(BaseModel):
    computador_id: str
    fecha: date
    hora: time
    tipo: Literal["preventivo", "correctivo"]
    observaciones: Optional[str] = None
    estado: Literal["pendiente", "hecho"]

class MantenimientoCreate(MantenimientoBase):
    pass

class MantenimientoUpdate(MantenimientoBase):
    pass

class MantenimientoOut(MantenimientoBase):
    id: int
    computador: Optional[ComputadorOut] = None  # ✅ incluir datos del computador

    model_config = {
        "from_attributes": True
    }


class PermisoSalidaBase(BaseModel):
    codigo_computador: str
    cedula_trabajador: str
    estado: Literal["activo", "inactivo"]

class PermisoSalidaCreate(PermisoSalidaBase):
    pass

class PermisoSalidaUpdate(BaseModel):
    codigo_computador: Optional[str] = None
    cedula_trabajador: Optional[str] = None
    estado: Optional[Literal["activo", "inactivo"]] = None

class PermisoSalidaOut(PermisoSalidaBase):
    id: int
    computador: Optional[ComputadorOut] = None
    trabajador: Optional[TrabajadorOut] = None

    model_config = {
        "from_attributes": True
    }