from pydantic import BaseModel, Field


class LoginEntrada(BaseModel):
    # str y no EmailStr: el validador de correo rechaza el dominio reservado .test.
    correo: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=1, max_length=128)


class DepartamentoResumen(BaseModel):
    id: int
    codigo: str
    nombre: str


class UsuarioActual(BaseModel):
    id: int
    colaborador_id: int
    cargo_id: int
    nombres: str
    apellidos: str
    correo: str
    rol: str
    departamento: DepartamentoResumen
    modulos: list[str]
