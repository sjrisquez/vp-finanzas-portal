# Portal VP de Finanzas

Portal interno con datos ficticios para consultar la estructura de la VP de Finanzas y gestionar notas de crédito.

> Estado: Fase 2. Incluye base de datos, datos de demo, inicio de sesión y permisos. Los módulos llegan en las fases siguientes.

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
alembic upgrade head
python -m app.seed.seed
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

El seed borra y recrea los datos de demo cada vez que se ejecuta.

## Tests

Requieren la base de datos levantada. Desde `backend/`, con el entorno virtual activo:

```powershell
pytest
```

Usan `vpfinanzas_test` y vacían sus tablas; nunca tocan los datos de desarrollo.

## Usuarios de demo

Todos usan la contraseña definida en `SEED_DEFAULT_PASSWORD`. El dominio de los correos es `@vpfinanzas.test`.

| Rol | Departamento | Correo |
|---|---|---|
| ADMIN | Planificación Financiera | `alma.quintanar` |
| JEFE_DEPARTAMENTO | Planificación Financiera | `bruno.salcedo` |
| JEFE_DEPARTAMENTO | Tesorería | `celia.arvelo` |
| JEFE_DEPARTAMENTO | Contraloría | `dario.ugarte` |
| JEFE_DEPARTAMENTO | Contabilidad | `elena.pacheco` |
| JEFE_DEPARTAMENTO | Cuentas por Cobrar | `fabian.lozada` |
| JEFE_DEPARTAMENTO | Cuentas por Pagar | `gloria.bermudez` |
| APROBADOR | Contraloría | `hector.zambrano` |
| APROBADOR | Contraloría | `irene.cordero` |
| COLABORADOR | Planificación Financiera | `joaquin.rivas` |
| COLABORADOR | Tesorería | `karla.mendoza` |
| COLABORADOR | Contraloría | `luis.ferrer` |
| COLABORADOR | Contabilidad | `marta.ibarra` |
| COLABORADOR | Cuentas por Cobrar | `nestor.paredes` |
| COLABORADOR | Cuentas por Pagar | `olga.tovar` |

## Documentación

- [Decisiones técnicas](docs/DECISIONES.md)
- [Registro de uso de IA](docs/AI_LOG.md)
