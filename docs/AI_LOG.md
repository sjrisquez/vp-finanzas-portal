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

## Entrada 4 — Fase 2 — 2026-11-04

**Prompt (resumido):** Implementar autenticación con JWT en cookie httpOnly, login, logout y `/me`, dependencias de rol y alcance por departamento, y sus tests.

**Qué propuso la IA:** JWT HS256 con algoritmo fijado; usuario cargado de la BD en cada petición; mensaje único de login y bcrypt también para correos inexistentes; `str` en lugar de `EmailStr` por el dominio `.test`; manejador genérico de errores; tests sobre la migración real con protección de la base de test; y traslado de los tests 3 y 4 a la Fase 3.

**Veredicto:** Aceptado

**Razón:** Los 32 tests pasaron contra PostgreSQL y comprobé en `/docs` que el login fija una cookie `HttpOnly`, que `/me` responde 401 sin sesión y que una contraseña incorrecta recibe un mensaje genérico. Acepté mover los tests 3 y 4 a la Fase 3 porque requieren endpoints que aún no existían.

## Entrada 5 — Fase 3 — 2026-11-04

**Prompt (resumido):** Implementar los endpoints de departamentos, colaboradores y cargos según la matriz de permisos, con dos schemas de colaborador y tests de alcance.

**Qué propuso la IA:** Alcance por departamento en SQL; 404 fuera de alcance; `ColaboradorPublico` y `ColaboradorDetalle`; ocultar inactivos e ignorar el filtro de estado para el Colaborador; ficha y cargo solo propios para ese rol; búsqueda con comodines escapados; y agregar `colaborador_id` y `cargo_id` a `/me` para Mi perfil.

**Veredicto:** Aceptado

**Razón:** Los 63 tests pasaron y comprobé en `/docs` que ADMIN ve todos los departamentos, el Jefe solo el suyo y el Colaborador recibe la vista limitada, con 404 en fichas ajenas. Acepté ocultarle los compañeros inactivos porque, si no, podría deducir un estado que su vista excluye.

## Entrada 6 — Fase 4 — 2026-11-04

**Prompt (resumido):** Implementar el flujo de notas de crédito: máquina de estados, separación de funciones, doble aprobación, bloqueo de concurrencia, auditoría, endpoints, seed mediante el servicio y tests 5 a 14.

**Qué propuso la IA:** Tabla de transiciones como diccionario; `SELECT ... FOR UPDATE` y auditoría en la misma transacción; umbral estricto por moneda; código generado con la secuencia de PostgreSQL; `acciones_disponibles` para el frontend; carga del dataset por el servicio con parámetros solo para el seed; 3 notas adicionales; catálogos de tiendas y compañías; y un test de concurrencia con dos hilos.

**Veredicto:** Aceptado

**Razón:** Los 113 tests pasaron y el seed cargó 28 notas y 50 eventos. En el navegador comprobé que el flujo funciona con distintos usuarios. El bloqueo de fila y la auditoría en una sola transacción protegen la trazabilidad si dos personas actúan a la vez.

## Entrada 7 — Fase 5 — 2026-11-04

**Prompt (resumido):** Completar de una vez el frontend para poder visualizar el sistema, por la proximidad de la entrega, y recomendar si usar BLACKBOX.

**Qué propuso la IA:** Pantallas de login, directorio, fichas, Mi perfil, bandeja, formulario y detalle con historial; menú basado en `/api/auth/me`; botones según `acciones_disponibles`; columnas según los datos que devuelve la API; un endpoint de umbrales para no copiar la regla en el cliente; y usar BLACKBOX solo para corregir errores locales, no para rehacer el proyecto.

**Veredicto:** Aceptado

**Razón:** Recorrí el sistema en el navegador con distintos usuarios y funcionó. Mantener la autorización en el backend evita depender de lo que muestre la interfaz.

## Entrada 8 — Fase 5 — 2026-11-04

**Prompt (resumido):** Hacer la interfaz más moderna sin cambiar la paleta, y dar al login un fondo de oficina con tarjeta translúcida a partir de una imagen de referencia.

**Qué propuso la IA:** Superficies y botones más redondeados, etiquetas tipo pastilla, fondo ilustrado original y tarjeta de vidrio. Omitió los enlaces `¿Olvidó su contraseña?` y `Solicitar acceso`, y el aviso de monitoreo de la referencia, porque esas funciones no existen.

**Veredicto:** Aceptado

**Razón:** Mejora la presentación sin tocar la lógica. Preferí no mostrar opciones ni avisos que el sistema no cumple.

## Entrada 9 — Fase 5 — 2026-11-04

**Prompt (resumido):** Hacer que el logo de Farmatodo se sobreentendiera en el fondo del login.

**Qué propuso la IA:** No redibujar el logo y agregar una capa opcional de marca de agua para usar un archivo propio, advirtiendo sobre los datos ficticios y la falta de autorización.

**Veredicto:** Rechazado

**Razón:** Descarté la capa y no usé el logo. La prueba pide datos ficticios y no tengo autorización para usar la marca, así que mantuve una identidad visual neutra.

## Errores o malas prácticas detectados en respuestas de la IA

### Error 1

**Qué propuso la IA:** Generar el archivo bundle del repositorio con `git bundle create archivo.bundle main`.

**Por qué estaba mal:** El bundle no incluía `HEAD`, así que `git clone` no creó la rama `main` y `git push` falló con `src refspec main does not match any`.

**Cómo se corrigió:** Se creó la rama local con `git switch -c main origin/main` y se volvió a ejecutar el push.

---

Nota: los veredictos se redactaron con apoyo de la IA a partir de mis decisiones y pruebas, y los revisé antes de subirlos.

## Entrada 10 — Planificación — 2026-11-03

**Prompt (resumido):** Analizar el enunciado y preparar un brief con arquitectura, modelo de datos, permisos, endpoints y plan por fases, para usarlo como guía de implementación.

**Qué propuso la IA:** Portal con FastAPI, PostgreSQL y React; flujo de notas de crédito como proceso de negocio; rol APROBADOR; doble aprobación por umbral; y un plan de 8 fases.

**Veredicto:** Modificado

**Razón:** Lo usé como base, pero lo ajusté durante el desarrollo: al recibir los datos de la empresa agregué dos departamentos y dos tablas, y cambié el umbral único de 5000 por uno de 4000 por moneda.

## Entrada 11 — Verificación — 2026-11-04

**Prompt (resumido):** Ejecutar las pruebas indicadas en cada fase y comprobar si el programa devolvía las respuestas esperadas, como doble verificación del proceso.

**Qué propuso la IA:** Ejecutó las pruebas solicitadas e informó que los resultados coincidían con lo esperado y que el flujo funcionaba correctamente. No reportó errores.

**Veredicto:** Aceptado

**Razón:** Usé BLACKBOX como segunda verificación, sin pedirle que cambiara el código. Aun así, los resultados dependen de lo que reportó la herramienta, por lo que también revisé las salidas de los comandos y el recorrido en el navegador.