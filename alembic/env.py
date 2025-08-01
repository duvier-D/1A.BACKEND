from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 👉 Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Importar Base y modelos
from database import Base  # Asegúrate de que database.py tenga Base = declarative_base()
from models import *       # Importa tus modelos para que Alembic los detecte

# 🔧 Configuración de Alembic
config = context.config

# ✅ Configuración de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 📌 Define el metadata que usará Alembic
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Migraciones en modo offline"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Migraciones en modo online"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Ejecutar migraciones según el modo
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
