"""Borra y recrea los datos de demo. Uso, desde backend/: python -m app.seed.seed"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select, text
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
    NotaCredito,
    NotaCreditoEvento,
    Pais,
    Tienda,
    Usuario,
)
from app.schemas.notas_credito import NotaCreditoCrear, NotaCreditoReenviar
from app.security.deps import consulta_usuario
from app.security.passwords import hash_password
from app.seed import datos, notas_dataset
from app.services import notas_credito as servicio

# El dataset trae fechas sin zona horaria; se interpretan en hora de Caracas.
ZONA_DEMO = timezone(timedelta(hours=-4))


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


def fecha(texto: str) -> datetime:
    return datetime.fromisoformat(texto).replace(tzinfo=ZONA_DEMO)


class CargadorNotas:
    """Crea las notas con la capa de servicios para que su auditoria sea consistente."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.jefes = {
            "CXC": self._usuario("fabian.lozada"),
            "CXP": self._usuario("gloria.bermudez"),
        }
        self.primer_firmante = self._usuario("hector.zambrano")
        self.segundo_firmante = self._usuario("irene.cordero")
        self.motivos = {m.nombre: m.id for m in session.scalars(select(MotivoNotaCredito))}
        self.tiendas = {t.nombre: t.id for t in session.scalars(select(Tienda))}
        self.companias = {c.nombre: c.id for c in session.scalars(select(Compania))}
        self.departamentos = {d.codigo: d.id for d in session.scalars(select(Departamento))}
        self.facturas = 0

    def _usuario(self, nombre_correo: str) -> Usuario:
        correo = f"{nombre_correo}@{datos.DOMINIO_CORREO}"
        return self.session.scalars(
            consulta_usuario().join(Usuario.colaborador).where(Colaborador.correo == correo)
        ).one()

    def crear(self, nota: notas_dataset.NotaDataset, descripcion: str) -> NotaCredito:
        self.facturas += 1
        entrada = NotaCreditoCrear(
            departamento_id=self.departamentos[nota.departamento],
            motivo_id=self.motivos[nota.motivo],
            tienda_id=self.tiendas[nota.tienda],
            compania_id=self.companias[nota.compania],
            factura_referencia=f"FAC-2026-{self.facturas:05d}",
            descripcion=descripcion,
            monto=Decimal(nota.monto),
            moneda=nota.moneda,
        )
        return servicio.crear_nota(
            self.session,
            self.jefes[nota.departamento],
            entrada,
            momento=fecha(nota.creada),
            comentario=notas_dataset.COMENTARIO_CREACION,
        )

    def resolver(self, nota: NotaCredito, dato: notas_dataset.NotaDataset) -> None:
        if dato.estado == "rechazada":
            servicio.rechazar_nota(
                self.session,
                self.primer_firmante,
                nota.id,
                notas_dataset.COMENTARIO_RECHAZADA,
                momento=fecha(dato.resuelta),
            )
        elif dato.estado == "aprobada":
            comentario = notas_dataset.COMENTARIO_APROBADA
            momento = fecha(dato.resuelta)
            servicio.aprobar_nota(
                self.session, self.primer_firmante, nota.id, comentario, momento=momento
            )
            if nota.requiere_doble_aprobacion:
                # Las notas sobre el umbral necesitan una segunda firma que el dataset no trae.
                servicio.aprobar_nota(
                    self.session,
                    self.segundo_firmante,
                    nota.id,
                    comentario,
                    momento=momento + timedelta(hours=2),
                )

    def cargar_dataset(self) -> None:
        for dato in notas_dataset.NOTAS:
            descripcion = f"{dato.motivo}. Despacho a {dato.tienda}."
            self.resolver(self.crear(dato, descripcion), dato)

    def cargar_adicionales(self) -> None:
        # Muestran los estados y acciones que el dataset no incluye.
        def adicional(monto: str, moneda: str, motivo: str, departamento: str, dia: str) -> NotaCredito:
            dato = notas_dataset.NotaDataset(
                monto, moneda, motivo, "Tienda Chacao", "Grupo Farmavalle",
                departamento, "pendiente", dia, None,
            )
            return self.crear(dato, f"Nota adicional de demo. {motivo}.")

        segunda_firma = adicional(
            "4500.00", "USD", "Producto recibido en mal estado", "CXC", "2026-08-03"
        )
        servicio.aprobar_nota(
            self.session,
            self.primer_firmante,
            segunda_firma.id,
            "Primera firma registrada",
            momento=fecha("2026-08-04"),
        )

        devuelta = adicional(
            "1500.00", "VES", "Error de facturación en monto despachado", "CXP", "2026-08-05"
        )
        servicio.devolver_nota(
            self.session,
            self.primer_firmante,
            devuelta.id,
            "Falta el soporte de despacho; adjuntar y corregir el monto",
            momento=fecha("2026-08-06"),
        )

        reenviada = adicional(
            "1200.00", "USD", "Duplicidad de despacho a la misma tienda", "CXC", "2026-08-07"
        )
        servicio.devolver_nota(
            self.session,
            self.primer_firmante,
            reenviada.id,
            "Corregir el monto según la factura",
            momento=fecha("2026-08-08"),
        )
        servicio.reenviar_nota(
            self.session,
            self.jefes["CXC"],
            reenviada.id,
            NotaCreditoReenviar(
                motivo_id=reenviada.motivo_id,
                descripcion="Nota adicional de demo. Monto corregido según la factura.",
                monto=Decimal("1150.00"),
                comentario="Monto corregido",
            ),
            momento=fecha("2026-08-09"),
        )
        servicio.aprobar_nota(
            self.session,
            self.segundo_firmante,
            reenviada.id,
            notas_dataset.COMENTARIO_APROBADA,
            momento=fecha("2026-08-10"),
        )


def main() -> None:
    with SessionLocal() as session:
        vaciar_tablas(session)
        paises = cargar_catalogos(session)
        cargos = cargar_organizacion(session)
        cargar_personas(session, paises, cargos)
        session.commit()

        cargador = CargadorNotas(session)
        cargador.cargar_dataset()
        cargador.cargar_adicionales()

        totales = {
            modelo.__name__: session.scalar(select(func.count()).select_from(modelo))
            for modelo in (Colaborador, Usuario, NotaCredito, NotaCreditoEvento)
        }

    print(
        f"Seed completado: {totales['Colaborador']} colaboradores, {totales['Usuario']} usuarios, "
        f"{totales['NotaCredito']} notas, {totales['NotaCreditoEvento']} eventos."
    )


if __name__ == "__main__":
    main()
