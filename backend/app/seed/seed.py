"""Borra y recrea los datos de demo. Uso, desde backend/: python -m app.seed.seed"""
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, SessionLocal
from app.models import (
    Cargo,
    Colaborador,
    Compania,
    Departamento,
    Funcion,
    MotivoNotaCredito,
    Nivel,
    Pais,
    Tienda,
    Usuario,
)
from app.security.passwords import hash_password
from app.seed import datos


def vaciar_tablas(session: Session) -> None:
    # Los nombres vienen de nuestros modelos, nunca de una entrada externa.
    # TRUNCATE no dispara el trigger de auditoria, que solo cubre UPDATE y DELETE por fila.
    tablas = ", ".join(tabla.name for tabla in Base.metadata.sorted_tables)
    session.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))


def cargar_catalogos(session: Session) -> dict[str, Pais]:
    paises = {codigo: Pais(codigo_iso=codigo, nombre=nombre) for codigo, nombre in datos.PAISES}
    session.add_all(paises.values())
    session.add_all(
        Tienda(nombre=nombre, pais=paises[codigo]) for nombre, codigo in datos.TIENDAS
    )
    session.add_all(Compania(nombre=nombre, rubro=rubro) for nombre, rubro in datos.COMPANIAS)
    session.add_all(
        MotivoNotaCredito(codigo=codigo, nombre=nombre) for codigo, nombre in datos.MOTIVOS
    )
    return paises


def cargar_organizacion(session: Session) -> dict[tuple[str, str], Cargo]:
    niveles = {nombre: Nivel(nombre=nombre, orden=orden) for nombre, orden in datos.NIVELES}
    session.add_all(niveles.values())

    funciones: dict[str, Funcion] = {}
    cargos: dict[tuple[str, str], Cargo] = {}
    for codigo, (nombre, descripcion, _, lista_cargos) in datos.DEPARTAMENTOS.items():
        departamento = Departamento(codigo=codigo, nombre=nombre, descripcion=descripcion)
        session.add(departamento)
        for nombre_cargo, nivel, es_jefatura, descripciones in lista_cargos:
            cargo = Cargo(
                nombre=nombre_cargo,
                departamento=departamento,
                nivel=niveles[nivel],
                es_jefatura=es_jefatura,
                funciones=[
                    funciones.setdefault(texto, Funcion(descripcion=texto))
                    for texto in descripciones
                ],
            )
            session.add(cargo)
            cargos[(codigo, nombre_cargo)] = cargo
    return cargos


def cargar_personas(
    session: Session, paises: dict[str, Pais], cargos: dict[tuple[str, str], Cargo]
) -> None:
    for persona in datos.generar_colaboradores():
        colaborador = Colaborador(
            nombres=persona.nombres,
            apellidos=persona.apellidos,
            correo=persona.correo,
            fecha_ingreso=persona.fecha_ingreso,
            estado=persona.estado,
            pais=paises[persona.pais],
            cargo=cargos[(persona.departamento, persona.cargo)],
        )
        session.add(colaborador)
        if persona.rol:
            session.add(
                Usuario(
                    colaborador=colaborador,
                    password_hash=hash_password(settings.seed_default_password),
                    rol=persona.rol,
                )
            )


def main() -> None:
    with SessionLocal() as session:
        vaciar_tablas(session)
        paises = cargar_catalogos(session)
        cargos = cargar_organizacion(session)
        cargar_personas(session, paises, cargos)
        session.commit()

        total_colaboradores = len(session.scalars(select(Colaborador.id)).all())
        total_usuarios = len(session.scalars(select(Usuario.id)).all())

    print(f"Seed completado: {total_colaboradores} colaboradores, {total_usuarios} usuarios.")


if __name__ == "__main__":
    main()
