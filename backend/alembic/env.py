from logging.config import fileConfig

from alembic import context

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.config import settings
from app.db import Base, engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def ejecutar(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
elif (conexion_externa := config.attributes.get("connection")) is not None:
    # Los tests entregan su conexion para migrar la BD de test, no la de desarrollo.
    ejecutar(conexion_externa)
else:
    with engine.connect() as connection:
        ejecutar(connection)
