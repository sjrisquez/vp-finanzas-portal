from datetime import date

from pydantic import BaseModel, ConfigDict


class Resumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DepartamentoSalida(Resumen):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None


class NivelSalida(Resumen):
    id: int
    nombre: str
    orden: int


class CargoResumen(Resumen):
    id: int
    nombre: str
    es_jefatura: bool
    nivel: NivelSalida


class DepartamentoDetalle(DepartamentoSalida):
    cargos: list[CargoResumen]


class DepartamentoCorto(Resumen):
    id: int
    codigo: str
    nombre: str


class FuncionSalida(Resumen):
    id: int
    descripcion: str


class CargoDetalle(Resumen):
    id: int
    nombre: str
    es_jefatura: bool
    departamento: DepartamentoCorto
    nivel: NivelSalida
    funciones: list[FuncionSalida]


class PaisSalida(Resumen):
    id: int
    codigo_iso: str
    nombre: str


class CargoDeColaborador(Resumen):
    id: int
    nombre: str
    es_jefatura: bool
    departamento: DepartamentoCorto
    nivel: NivelSalida


class ColaboradorPublico(BaseModel):
    """Vista limitada: sin fecha de ingreso, pais ni estado."""

    id: int
    nombres: str
    apellidos: str
    correo: str
    cargo: str


class ColaboradorDetalle(Resumen):
    id: int
    nombres: str
    apellidos: str
    correo: str
    fecha_ingreso: date
    estado: str
    pais: PaisSalida
    cargo: CargoDeColaborador
