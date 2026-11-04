# Portal VP de Finanzas

Portal interno con datos ficticios para consultar la estructura de la VP de Finanzas y gestionar notas de crédito.

> Estado: Fase 0. Solo incluye la infraestructura base, sin lógica de negocio.

## Requisitos

- Docker Desktop
- Python 3.12
- Node 20 o superior
- Git

## Configuración (Windows, PowerShell)

Ejecuta los comandos desde la raíz del repositorio.

```powershell
Copy-Item .env.example .env
```

Abre `.env`, cambia `cambia_esto` en todas sus apariciones y completa `JWT_SECRET` con el valor generado en el paso del backend.

## Base de datos

```powershell
docker compose up -d
docker compose ps
```

## Backend

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import secrets; print(secrets.token_urlsafe(48))"
uvicorn app.main:app --reload
```

API: <http://127.0.0.1:8000/api/health>. Documentación: <http://127.0.0.1:8000/docs>.

## Frontend

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

App: <http://localhost:5173>.

## Documentación

- [Decisiones técnicas](docs/DECISIONES.md)
- [Registro de uso de IA](docs/AI_LOG.md)
