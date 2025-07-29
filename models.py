from sqlalchemy import Column, String, Enum, Integer, ForeignKey,Date,Time,Text # ✅ Agrega Enum aquí
from sqlalchemy.orm import relationship
from database import Base
import enum

# Enum de roles
class RolEnum(enum.Enum):
    admin = "admin"
    normal = "normal"

# Modelo de usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    username = Column(String(50), primary_key=True, index=True)
    password = Column(String(100), nullable=False)
    rol = Column(Enum(RolEnum), nullable=False)  # ✅ Usa Enum de SQLAlchemy


class Trabajador(Base):
    __tablename__ = "trabajadores"

    cedula = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    area_de_trabajo = Column(String(100), nullable=False)
    edad = Column(Integer, nullable=False)
    residencia = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=False)
    correo = Column(String(150), nullable=False)
    foto = Column(String(255), nullable=True)

# Modelo de computador
class Computador(Base):
    __tablename__ = "computadores"

    codigo = Column(String(50), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    marca = Column(String(50), nullable=False)
    trabajador_id = Column(String(20), ForeignKey("trabajadores.cedula", ondelete="SET NULL"), nullable=True)
    foto = Column(String(255), nullable=True)  # Ruta o URL de la imagen
    trabajador = relationship("Trabajador", backref="computadores")

# Modelo detalles
class Detalle(Base):
    __tablename__ = "detalle"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_computador = Column(String(50), ForeignKey("computadores.codigo", ondelete="CASCADE"), nullable=False)
    procesador = Column(String(100), nullable=False)
    ram = Column(String(50), nullable=False)
    almacenamiento = Column(String(100), nullable=False)
    sistema_operativo = Column(String(100), nullable=False)
    observaciones = Column(String(255), nullable=True)
    serial = Column(String(100), nullable=True)  # en la clase Detalle



Computador.detalles = relationship(
    "Detalle",
    backref="computador",
    cascade="all, delete",
    passive_deletes=True
)




# TABLA ASIGNAR USUARIO
class AsignarUsuario(Base):
    __tablename__ = "asignar_usuario"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(String(50), ForeignKey("usuarios.username", ondelete="CASCADE"))
    trabajador_id = Column(String(20), ForeignKey("trabajadores.cedula", ondelete="CASCADE"))

# RELACIONES ENTRE MODELOS
Usuario.asignaciones = relationship("AsignarUsuario", back_populates="usuario")
Trabajador.asignaciones = relationship("AsignarUsuario", back_populates="trabajador")
AsignarUsuario.usuario = relationship("Usuario", back_populates="asignaciones")
AsignarUsuario.trabajador = relationship("Trabajador", back_populates="asignaciones")



class TipoMantenimientoEnum(enum.Enum):
    preventivo = "preventivo"
    correctivo = "correctivo"

class EstadoMantenimientoEnum(enum.Enum):
    pendiente = "pendiente"
    hecho = "hecho"

class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    computador_id = Column(String(50), ForeignKey("computadores.codigo", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    tipo = Column(Enum(TipoMantenimientoEnum), nullable=False)
    observaciones = Column(Text, nullable=True)
    estado = Column(Enum(EstadoMantenimientoEnum), nullable=False)

    computador = relationship("Computador", backref="mantenimientos", lazy="joined")


class EstadoPermisoEnum(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class PermisoSalida(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_computador = Column(String(50), ForeignKey("computadores.codigo", ondelete="CASCADE"), nullable=False)
    cedula_trabajador = Column(String(20), ForeignKey("trabajadores.cedula", ondelete="CASCADE"), nullable=False)
    estado = Column(Enum(EstadoPermisoEnum), nullable=False)

    # Relaciones
    computador = relationship("Computador", backref="permisos", lazy="joined")
    trabajador = relationship("Trabajador", backref="permisos", lazy="joined")
