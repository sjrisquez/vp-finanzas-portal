# Registro de uso de IA

Herramientas usadas: Claude

## Entrada 1 — Fase 0 — 2026-11-03

**Prompt (resumido):** Construir la Fase 0 del portal siguiendo el brief: repositorio, PostgreSQL con Docker, esqueletos de FastAPI y React, y plantillas de documentación, con comandos para Windows.

**Qué propuso la IA:** Estructura base del repositorio; PostgreSQL 16 con base de test y puerto limitado a 127.0.0.1; configuración validada con pydantic-settings; `/api/health`; React 18 y Vite con proxy de `/api`; `JWT_SECRET` vacío en `.env.example` para que la app no arranque con un valor de ejemplo; instalación gradual de dependencias por fase.

**Veredicto:** Aceptado

**Razón:** Lo probé en mi equipo: las dos bases de datos se crearon, el backend se negó a arrancar sin `JWT_SECRET` y el frontend obtuvo el estado de la API a través del proxy. Dejar el secreto vacío evita arrancar con un valor público de ejemplo.

## Entrada 2 — Fase 0 — 2026-11-03

**Prompt (resumido):** Integrar los datos de ejemplo entregados por la empresa para las notas de crédito.

**Qué propuso la IA:** Mantener la trazabilidad por usuario pese a que el README de los datos no la exigía; agregar Cuentas por Cobrar y Cuentas por Pagar; usar un umbral de 4000 por moneda; agregar `tiendas` y `companias`; y reproducir las 25 notas mediante el servicio con usuarios demo.

**Veredicto:** Aceptado

**Razón:** El enunciado exige auditar quién actúa e impedir la autoaprobación, por lo que mantuve la trazabilidad por usuario. Elegí umbrales por moneda porque ninguna nota superaba 5000 y comparar USD con VES no sería correcto sin una tasa de cambio.

## Entrada 3 — Fase 1 — 2026-11-04

**Prompt (resumido):** Implementar los modelos, la migración inicial y el seed reproducible, incorporando los datos de la empresa y las decisiones sobre departamentos, monedas y umbral.

**Qué propuso la IA:** 13 tablas con restricciones `UNIQUE`, `CHECK` y FK; migración en SQL visible; trigger para auditoría de solo inserción; umbral por moneda; `moneda` sin valor por defecto; bcrypt adelantado para crear usuarios demo; y carga de las 25 notas pospuesta a la Fase 4.

**Veredicto:** Aceptado

**Razón:** Lo validé en mi entorno: `alembic check` no detectó diferencias, el seed cargó 57 colaboradores y 15 usuarios, y PostgreSQL rechazó un rol inválido. La migración en SQL visible me permite revisar y explicar cada restricción.

## Errores o malas prácticas detectados en respuestas de la IA

### Error 1

**Qué propuso la IA:** Generar el archivo bundle del repositorio con `git bundle create archivo.bundle main`.

**Por qué estaba mal:** El bundle no incluía `HEAD`, así que `git clone` no creó la rama `main` y `git push` falló con `src refspec main does not match any`.

**Cómo se corrigió:** Se creó la rama local con `git switch -c main origin/main` y se volvió a ejecutar el push.

## Entrada 4 — Fase 2 — 2026-11-04

**Prompt (resumido):** Implementar autenticación con JWT en cookie httpOnly, login, logout y `/me`, dependencias de rol y alcance por departamento, y sus tests.

**Qué propuso la IA:** JWT HS256 con algoritmo fijado; usuario cargado de la BD en cada petición; mensaje único de login y bcrypt también para correos inexistentes; `str` en lugar de `EmailStr` por el dominio `.test`; manejador genérico de errores; tests sobre la migración real con protección de la base de test; y traslado de los tests 3 y 4 a la Fase 3.

**Veredicto:** Aceptado

**Razón:** Los 32 tests pasaron contra PostgreSQL y comprobé en `/docs` que el login fija una cookie `HttpOnly`, que `/me` responde 401 sin sesión y que una contraseña incorrecta recibe un mensaje genérico. Acepté mover los tests 3 y 4 a la Fase 3 porque requieren endpoints que aún no existen.