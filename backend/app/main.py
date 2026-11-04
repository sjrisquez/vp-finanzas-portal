import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, cargos, catalogos, colaboradores, departamentos, notas_credito
from app.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="Portal VP de Finanzas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(Exception)
def error_inesperado(request: Request, exc: Exception) -> JSONResponse:
    # El detalle queda en el log del servidor; el cliente nunca ve trazas ni datos de la BD.
    logger.error("Error inesperado en %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


app.include_router(auth.router)
app.include_router(departamentos.router)
app.include_router(colaboradores.router)
app.include_router(cargos.router)
app.include_router(catalogos.router)
app.include_router(notas_credito.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
