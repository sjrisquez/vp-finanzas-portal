# Decisiones técnicas

## 1. Stack elegido y justificación

## 2. Modelo de datos

```mermaid
erDiagram
    DEPARTAMENTOS ||--o{ CARGOS : tiene
    NIVELES ||--o{ CARGOS : clasifica
    CARGOS ||--o{ CARGO_FUNCION : asigna
    FUNCIONES ||--o{ CARGO_FUNCION : compone
    CARGOS ||--o{ COLABORADORES : ocupa
    PAISES ||--o{ COLABORADORES : reside
    COLABORADORES ||--o| USUARIOS : accede
    PAISES ||--o{ TIENDAS : ubica
    DEPARTAMENTOS ||--o{ NOTAS_CREDITO : solicita
    USUARIOS ||--o{ NOTAS_CREDITO : crea
    USUARIOS |o--o{ NOTAS_CREDITO : "primera firma"
    MOTIVOS_NOTA_CREDITO ||--o{ NOTAS_CREDITO : justifica
    TIENDAS ||--o{ NOTAS_CREDITO : recibe
    COMPANIAS ||--o{ NOTAS_CREDITO : provee
    NOTAS_CREDITO ||--o{ NOTAS_CREDITO_EVENTOS : registra
    USUARIOS ||--o{ NOTAS_CREDITO_EVENTOS : ejecuta

    DEPARTAMENTOS {
        serial id PK
        varchar codigo UK
        varchar nombre UK
        text descripcion
    }
    NIVELES {
        serial id PK
        varchar nombre UK
        smallint orden UK
    }
    CARGOS {
        serial id PK
        varchar nombre
        int departamento_id FK
        int nivel_id FK
        boolean es_jefatura
    }
    FUNCIONES {
        serial id PK
        varchar descripcion UK
    }
    CARGO_FUNCION {
        int cargo_id PK
        int funcion_id PK
    }
    PAISES {
        serial id PK
        char codigo_iso UK
        varchar nombre UK
    }
    COLABORADORES {
        serial id PK
        varchar nombres
        varchar apellidos
        varchar correo UK
        date fecha_ingreso
        varchar estado
        int pais_id FK
        int cargo_id FK
        timestamptz creado_en
    }
    USUARIOS {
        serial id PK
        int colaborador_id FK
        varchar password_hash
        varchar rol
        boolean activo
        timestamptz ultimo_login
    }
    MOTIVOS_NOTA_CREDITO {
        serial id PK
        varchar codigo UK
        varchar nombre UK
    }
    TIENDAS {
        serial id PK
        varchar nombre UK
        int pais_id FK
    }
    COMPANIAS {
        serial id PK
        varchar nombre UK
        varchar rubro
    }
    NOTAS_CREDITO {
        serial id PK
        varchar codigo UK
        int departamento_id FK
        int solicitante_id FK
        int motivo_id FK
        int tienda_id FK
        int compania_id FK
        varchar factura_referencia
        text descripcion
        numeric monto
        char moneda
        varchar estado
        boolean requiere_doble_aprobacion
        int primer_aprobador_id FK
        timestamptz creada_en
        timestamptz actualizada_en
    }
    NOTAS_CREDITO_EVENTOS {
        bigserial id PK
        int nota_id FK
        int actor_id FK
        varchar accion
        varchar estado_anterior
        varchar estado_nuevo
        text comentario
        timestamptz creado_en
    }
```

### Decisiones de modelado

- **Sin `departamento_id` en `colaboradores`:** el departamento se obtiene a través del cargo. Guardarlo dos veces permitiría inconsistencias.
- **Cargo por departamento:** `UNIQUE(nombre, departamento_id)` permite que dos departamentos tengan un cargo con el mismo nombre.
- **Funciones N:M:** una función puede pertenecer a varios cargos sin repetir su texto.
- **`usuarios` separada de `colaboradores`:** no todo colaborador tiene acceso; aísla las credenciales de los datos de RR. HH.
- **Rol con `CHECK`:** los roles están acoplados al código de autorización, y agregar uno exige cambiar el código de todos modos.
- **`NUMERIC(14,2)` para montos:** el punto flotante binario produce errores de redondeo en dinero.
- **`requiere_doble_aprobacion` guardado:** un cambio posterior del umbral no altera las notas en curso.
- **Auditoría de solo inserción:** no hay endpoints de edición, y un trigger de PostgreSQL rechaza `UPDATE` y `DELETE` en `notas_credito_eventos`.

### Datos entregados por la empresa

- **Tablas agregadas:** `tiendas` y `companias` vienen del dataset, lo que da 13 tablas. `tiendas` referencia `paises` en lugar de repetir el nombre del país.
- **Departamentos:** se agregan Cuentas por Cobrar y Cuentas por Pagar a los 4 departamentos iniciales.
- **Motivos:** el texto libre del dataset se normaliza en un catálogo de 7 motivos.
- **Monedas:** USD y VES se validan con `CHECK`, y `moneda` no tiene valor por defecto para no asumir una por omisión.
- **Umbral por moneda:** `NC_UMBRAL_USD` y `NC_UMBRAL_VES` evitan comparar monedas distintas o inventar una tasa de cambio.
- **Trazabilidad por usuario:** el README del dataset no exige registrar quién actúa, pero el enunciado pide auditar quién actuó e impedir la autoaprobación. Prevalece el enunciado.

## 3. Proceso de negocio elegido

## 4. Resolución de la ambigüedad de roles

## 5. Matriz de permisos y su aplicación

## 6. Decisiones de seguridad

## 7. Limitaciones conocidas

## 8. Qué haría con más tiempo
