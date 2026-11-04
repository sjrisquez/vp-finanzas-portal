"""Esquema inicial: 13 tablas y auditoria de solo insercion.

Revision ID: 0001
Revises:
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

UPGRADE_SQL = """
CREATE TABLE departamentos (
    id SERIAL,
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    CONSTRAINT pk_departamentos PRIMARY KEY (id),
    CONSTRAINT uq_departamentos_codigo UNIQUE (codigo),
    CONSTRAINT uq_departamentos_nombre UNIQUE (nombre)
);

CREATE TABLE niveles (
    id SERIAL,
    nombre VARCHAR(50) NOT NULL,
    orden SMALLINT NOT NULL,
    CONSTRAINT pk_niveles PRIMARY KEY (id),
    CONSTRAINT uq_niveles_nombre UNIQUE (nombre),
    CONSTRAINT uq_niveles_orden UNIQUE (orden)
);

CREATE TABLE cargos (
    id SERIAL,
    nombre VARCHAR(100) NOT NULL,
    departamento_id INTEGER NOT NULL,
    nivel_id INTEGER NOT NULL,
    es_jefatura BOOLEAN NOT NULL DEFAULT false,
    CONSTRAINT pk_cargos PRIMARY KEY (id),
    CONSTRAINT uq_cargos_nombre_departamento_id UNIQUE (nombre, departamento_id),
    CONSTRAINT fk_cargos_departamento_id_departamentos
        FOREIGN KEY (departamento_id) REFERENCES departamentos (id),
    CONSTRAINT fk_cargos_nivel_id_niveles FOREIGN KEY (nivel_id) REFERENCES niveles (id)
);

CREATE INDEX ix_cargos_departamento_id ON cargos (departamento_id);

CREATE INDEX ix_cargos_nivel_id ON cargos (nivel_id);

CREATE TABLE funciones (
    id SERIAL,
    descripcion VARCHAR(255) NOT NULL,
    CONSTRAINT pk_funciones PRIMARY KEY (id),
    CONSTRAINT uq_funciones_descripcion UNIQUE (descripcion)
);

CREATE TABLE cargo_funcion (
    cargo_id INTEGER NOT NULL,
    funcion_id INTEGER NOT NULL,
    CONSTRAINT pk_cargo_funcion PRIMARY KEY (cargo_id, funcion_id),
    CONSTRAINT fk_cargo_funcion_cargo_id_cargos
        FOREIGN KEY (cargo_id) REFERENCES cargos (id) ON DELETE CASCADE,
    CONSTRAINT fk_cargo_funcion_funcion_id_funciones
        FOREIGN KEY (funcion_id) REFERENCES funciones (id) ON DELETE CASCADE
);

CREATE TABLE paises (
    id SERIAL,
    codigo_iso CHAR(2) NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    CONSTRAINT pk_paises PRIMARY KEY (id),
    CONSTRAINT uq_paises_codigo_iso UNIQUE (codigo_iso),
    CONSTRAINT uq_paises_nombre UNIQUE (nombre)
);

CREATE TABLE colaboradores (
    id SERIAL,
    nombres VARCHAR(80) NOT NULL,
    apellidos VARCHAR(80) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    estado VARCHAR(10) NOT NULL,
    pais_id INTEGER NOT NULL,
    cargo_id INTEGER NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT pk_colaboradores PRIMARY KEY (id),
    CONSTRAINT uq_colaboradores_correo UNIQUE (correo),
    CONSTRAINT ck_colaboradores_estado_valido CHECK (estado IN ('activo', 'inactivo')),
    CONSTRAINT fk_colaboradores_pais_id_paises FOREIGN KEY (pais_id) REFERENCES paises (id),
    CONSTRAINT fk_colaboradores_cargo_id_cargos FOREIGN KEY (cargo_id) REFERENCES cargos (id)
);

CREATE INDEX ix_colaboradores_pais_id ON colaboradores (pais_id);

CREATE INDEX ix_colaboradores_cargo_id ON colaboradores (cargo_id);

CREATE TABLE usuarios (
    id SERIAL,
    colaborador_id INTEGER NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT true,
    ultimo_login TIMESTAMPTZ,
    CONSTRAINT pk_usuarios PRIMARY KEY (id),
    CONSTRAINT uq_usuarios_colaborador_id UNIQUE (colaborador_id),
    CONSTRAINT ck_usuarios_rol_valido
        CHECK (rol IN ('ADMIN', 'JEFE_DEPARTAMENTO', 'APROBADOR', 'COLABORADOR')),
    CONSTRAINT fk_usuarios_colaborador_id_colaboradores
        FOREIGN KEY (colaborador_id) REFERENCES colaboradores (id)
);

CREATE TABLE motivos_nota_credito (
    id SERIAL,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT pk_motivos_nota_credito PRIMARY KEY (id),
    CONSTRAINT uq_motivos_nota_credito_codigo UNIQUE (codigo),
    CONSTRAINT uq_motivos_nota_credito_nombre UNIQUE (nombre)
);

CREATE TABLE tiendas (
    id SERIAL,
    nombre VARCHAR(100) NOT NULL,
    pais_id INTEGER NOT NULL,
    CONSTRAINT pk_tiendas PRIMARY KEY (id),
    CONSTRAINT uq_tiendas_nombre UNIQUE (nombre),
    CONSTRAINT fk_tiendas_pais_id_paises FOREIGN KEY (pais_id) REFERENCES paises (id)
);

CREATE INDEX ix_tiendas_pais_id ON tiendas (pais_id);

CREATE TABLE companias (
    id SERIAL,
    nombre VARCHAR(100) NOT NULL,
    rubro VARCHAR(50) NOT NULL,
    CONSTRAINT pk_companias PRIMARY KEY (id),
    CONSTRAINT uq_companias_nombre UNIQUE (nombre)
);

CREATE TABLE notas_credito (
    id SERIAL,
    codigo VARCHAR(20) NOT NULL,
    departamento_id INTEGER NOT NULL,
    solicitante_id INTEGER NOT NULL,
    motivo_id INTEGER NOT NULL,
    tienda_id INTEGER NOT NULL,
    compania_id INTEGER NOT NULL,
    factura_referencia VARCHAR(30) NOT NULL,
    descripcion TEXT NOT NULL,
    monto NUMERIC(14, 2) NOT NULL,
    moneda CHAR(3) NOT NULL,
    estado VARCHAR(30) NOT NULL,
    requiere_doble_aprobacion BOOLEAN NOT NULL,
    primer_aprobador_id INTEGER,
    creada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT pk_notas_credito PRIMARY KEY (id),
    CONSTRAINT uq_notas_credito_codigo UNIQUE (codigo),
    CONSTRAINT ck_notas_credito_monto_positivo CHECK (monto > 0),
    CONSTRAINT ck_notas_credito_moneda_valida CHECK (moneda IN ('USD', 'VES')),
    CONSTRAINT ck_notas_credito_estado_valido CHECK (
        estado IN ('PENDIENTE', 'PENDIENTE_SEGUNDA_FIRMA', 'DEVUELTA', 'APROBADA', 'RECHAZADA')
    ),
    CONSTRAINT fk_notas_credito_departamento_id_departamentos
        FOREIGN KEY (departamento_id) REFERENCES departamentos (id),
    CONSTRAINT fk_notas_credito_solicitante_id_usuarios
        FOREIGN KEY (solicitante_id) REFERENCES usuarios (id),
    CONSTRAINT fk_notas_credito_motivo_id_motivos_nota_credito
        FOREIGN KEY (motivo_id) REFERENCES motivos_nota_credito (id),
    CONSTRAINT fk_notas_credito_tienda_id_tiendas FOREIGN KEY (tienda_id) REFERENCES tiendas (id),
    CONSTRAINT fk_notas_credito_compania_id_companias
        FOREIGN KEY (compania_id) REFERENCES companias (id),
    CONSTRAINT fk_notas_credito_primer_aprobador_id_usuarios
        FOREIGN KEY (primer_aprobador_id) REFERENCES usuarios (id)
);

CREATE INDEX ix_notas_credito_departamento_id ON notas_credito (departamento_id);

CREATE INDEX ix_notas_credito_solicitante_id ON notas_credito (solicitante_id);

CREATE INDEX ix_notas_credito_motivo_id ON notas_credito (motivo_id);

CREATE INDEX ix_notas_credito_tienda_id ON notas_credito (tienda_id);

CREATE INDEX ix_notas_credito_compania_id ON notas_credito (compania_id);

CREATE INDEX ix_notas_credito_estado ON notas_credito (estado);

CREATE TABLE notas_credito_eventos (
    id BIGSERIAL,
    nota_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    accion VARCHAR(20) NOT NULL,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    comentario TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT pk_notas_credito_eventos PRIMARY KEY (id),
    CONSTRAINT ck_notas_credito_eventos_accion_valida
        CHECK (accion IN ('CREAR', 'APROBAR', 'RECHAZAR', 'DEVOLVER', 'REENVIAR')),
    CONSTRAINT fk_notas_credito_eventos_nota_id_notas_credito
        FOREIGN KEY (nota_id) REFERENCES notas_credito (id),
    CONSTRAINT fk_notas_credito_eventos_actor_id_usuarios
        FOREIGN KEY (actor_id) REFERENCES usuarios (id)
);

CREATE INDEX ix_notas_credito_eventos_nota_id ON notas_credito_eventos (nota_id);

CREATE INDEX ix_notas_credito_eventos_actor_id ON notas_credito_eventos (actor_id);

CREATE FUNCTION bloquear_cambios_auditoria() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'La auditoria de notas de credito es de solo insercion';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_eventos_solo_insercion
    BEFORE UPDATE OR DELETE ON notas_credito_eventos
    FOR EACH ROW EXECUTE FUNCTION bloquear_cambios_auditoria();
"""

DOWNGRADE_SQL = """
DROP TABLE notas_credito_eventos;

DROP FUNCTION bloquear_cambios_auditoria();

DROP TABLE notas_credito;

DROP TABLE companias;

DROP TABLE tiendas;

DROP TABLE motivos_nota_credito;

DROP TABLE usuarios;

DROP TABLE colaboradores;

DROP TABLE paises;

DROP TABLE cargo_funcion;

DROP TABLE funciones;

DROP TABLE cargos;

DROP TABLE niveles;

DROP TABLE departamentos;
"""


def ejecutar(script: str) -> None:
    # Una sentencia a la vez; los scripts las separan con una linea en blanco.
    for sentencia in script.split(";\n\n"):
        if sentencia.strip():
            op.execute(sentencia)


def upgrade() -> None:
    ejecutar(UPGRADE_SQL)


def downgrade() -> None:
    ejecutar(DOWNGRADE_SQL)
