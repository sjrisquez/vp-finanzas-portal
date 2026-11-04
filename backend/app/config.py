from decimal import Decimal
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> raiz del repositorio
ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # POSTGRES_* es para Docker, no para la app
        hide_input_in_errors=True,  # Un error no debe imprimir secretos
    )

    database_url: str = Field(repr=False)
    test_database_url: str = Field(repr=False)

    jwt_secret: str = Field(min_length=32, repr=False)
    jwt_expire_minutes: int = Field(default=60, gt=0)
    cookie_secure: bool = False

    cors_origins: str
    nc_umbral_usd: Decimal = Field(gt=0)
    nc_umbral_ves: Decimal = Field(gt=0)

    seed_default_password: str = Field(repr=False)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Se crea al importar: si la configuracion es invalida, la app no arranca.
settings = Settings()
