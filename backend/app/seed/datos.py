"""Datos ficticios del seed. Sin base de datos, para poder revisarlos y probarlos aparte."""
import random
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta

DOMINIO_CORREO = "vpfinanzas.test"
ROL_ADMIN = "ADMIN"
ROL_JEFE = "JEFE_DEPARTAMENTO"
ROL_APROBADOR = "APROBADOR"
ROL_COLABORADOR = "COLABORADOR"

NIVELES = [("Junior", 1), ("Semi-senior", 2), ("Senior", 3), ("Gerente", 4)]

PAISES = [
    ("VE", "Venezuela"),
    ("CO", "Colombia"),
    ("PA", "Panamá"),
    ("AR", "Argentina"),
    ("ES", "España"),
]

# Tiendas, compañías y motivos provienen del dataset entregado por la empresa.
TIENDAS = [
    ("Tienda Chacao", "VE"),
    ("Tienda Las Mercedes", "VE"),
    ("Tienda Maracaibo Centro", "VE"),
    ("Tienda Palermo", "AR"),
    ("Tienda Belgrano", "AR"),
    ("Tienda Córdoba Norte", "AR"),
]

COMPANIAS = [
    ("Laboratorios Andina C.A.", "Farmacéutico"),
    ("Distribuidora Cuyaní", "Cuidado personal"),
    ("Nutrisana Import", "Nutrición y suplementos"),
    ("Grupo Farmavalle", "Farmacéutico"),
    ("Beltek Consumo Masivo", "Consumo masivo"),
    ("Salud Total Distribución", "Farmacéutico"),
]

MOTIVOS = [
    ("AJUSTE_PROMOCION", "Ajuste de precio por promoción no aplicada"),
    ("DESCUENTO_COMERCIAL", "Descuento comercial no reflejado en factura"),
    ("DEVOLUCION_VENCIDO", "Devolución de producto por vencimiento"),
    ("DIFERENCIA_CAMBIARIA", "Diferencia cambiaria en pago anticipado a proveedor"),
    ("DUPLICIDAD_DESPACHO", "Duplicidad de despacho a la misma tienda"),
    ("ERROR_FACTURACION", "Error de facturación en monto despachado"),
    ("PRODUCTO_MAL_ESTADO", "Producto recibido en mal estado"),
]

# Una función repetida aquí se guarda una sola vez y se comparte mediante cargo_funcion.
REPORTES = "Elaborar reportes de gestión del área"
SUPERVISAR = "Supervisar al equipo y asignar prioridades"
APROBAR_AREA = "Aprobar los entregables del área"
DOCUMENTOS = "Mantener el archivo de soportes del área"

# codigo: (nombre, descripción, cantidad de colaboradores, cargos)
# cargo: (nombre, nivel, es_jefatura, funciones)
DEPARTAMENTOS = {
    "PLF": ("Planificación Financiera", "Presupuesto y proyecciones de la VP.", 10, [
        ("Gerente de Planificación Financiera", "Gerente", True,
         [SUPERVISAR, APROBAR_AREA, "Presentar el presupuesto anual a la VP"]),
        ("Analista Senior de Planificación", "Senior", False,
         ["Construir modelos de proyección financiera", "Analizar desviaciones presupuestarias", REPORTES]),
        ("Analista de Presupuesto", "Semi-senior", False,
         ["Consolidar el presupuesto por departamento", REPORTES]),
        ("Asistente de Planificación", "Junior", False,
         ["Actualizar indicadores de gestión", DOCUMENTOS]),
    ]),
    "TES": ("Tesorería", "Gestión de liquidez y pagos.", 9, [
        ("Gerente de Tesorería", "Gerente", True,
         [SUPERVISAR, APROBAR_AREA, "Definir la política de liquidez"]),
        ("Analista Senior de Tesorería", "Senior", False,
         ["Gestionar el flujo de caja", "Programar pagos a proveedores", REPORTES]),
        ("Analista de Tesorería", "Semi-senior", False,
         ["Conciliar cuentas bancarias", "Registrar movimientos bancarios"]),
        ("Asistente de Tesorería", "Junior", False,
         ["Preparar soportes de pago", DOCUMENTOS]),
    ]),
    "CTR": ("Contraloría", "Control interno y aprobación financiera.", 11, [
        ("Gerente de Contraloría", "Gerente", True,
         [SUPERVISAR, APROBAR_AREA, "Definir los controles internos"]),
        ("Subgerente de Control Interno", "Gerente", False,
         ["Aprobar notas de crédito", "Evaluar excepciones de control"]),
        ("Auditor Interno Senior", "Senior", False,
         ["Auditar procesos financieros", "Dar seguimiento a hallazgos", REPORTES]),
        ("Analista de Control", "Semi-senior", False,
         ["Verificar soportes de operaciones", DOCUMENTOS]),
    ]),
    "CON": ("Contabilidad", "Registro contable y cierres.", 8, [
        ("Gerente de Contabilidad", "Gerente", True,
         [SUPERVISAR, APROBAR_AREA, "Validar los estados financieros"]),
        ("Contador Senior", "Senior", False,
         ["Ejecutar el cierre contable mensual", "Revisar asientos contables", REPORTES]),
        ("Contador", "Semi-senior", False,
         ["Registrar asientos contables", "Conciliar cuentas contables"]),
        ("Asistente Contable", "Junior", False,
         ["Clasificar comprobantes contables", DOCUMENTOS]),
    ]),
    "CXC": ("Cuentas por Cobrar", "Gestión de cobros y notas de crédito por despachos.", 9, [
        ("Gerente de Cuentas por Cobrar", "Gerente", True,
         [SUPERVISAR, APROBAR_AREA, "Solicitar notas de crédito del área"]),
        ("Analista Senior de Cobranzas", "Senior", False,
         ["Gestionar cuentas vencidas", "Analizar la antigüedad de saldos", REPORTES]),
        ("Analista de Cuentas por Cobrar", "Semi-senior", False,
         ["Aplicar cobros a facturas", "Validar soportes de despacho"]),
        ("Asistente de Cuentas por Cobrar", "Junior", False,
         ["Registrar facturas por cobrar", DOCUMENTOS]),
    ]),
    "CXP": ("Cuentas por Pagar", "Gestión de obligaciones con proveedores.", 10, [
        ("Gerente de Cuentas por Pagar", "Gerente", True,
         [SUPERVISAR, APROBAR_AREA, "Solicitar notas de crédito a proveedores"]),
        ("Analista Senior de Proveedores", "Senior", False,
         ["Negociar condiciones de pago", "Analizar saldos de proveedores", REPORTES]),
        ("Analista de Cuentas por Pagar", "Semi-senior", False,
         ["Validar facturas de proveedores", "Preparar lotes de pago"]),
        ("Asistente de Cuentas por Pagar", "Junior", False,
         ["Registrar facturas por pagar", DOCUMENTOS]),
    ]),
}

# Usuarios de demo: nombres fijos para poder listar sus correos en el README.
# (nombres, apellidos, departamento, cargo o None para jefatura, rol)
USUARIOS_DEMO = [
    ("Alma", "Quintanar", "PLF", "Analista Senior de Planificación", ROL_ADMIN),
    ("Bruno", "Salcedo", "PLF", None, ROL_JEFE),
    ("Celia", "Arvelo", "TES", None, ROL_JEFE),
    ("Dario", "Ugarte", "CTR", None, ROL_JEFE),
    ("Elena", "Pacheco", "CON", None, ROL_JEFE),
    ("Fabian", "Lozada", "CXC", None, ROL_JEFE),
    ("Gloria", "Bermudez", "CXP", None, ROL_JEFE),
    ("Hector", "Zambrano", "CTR", "Subgerente de Control Interno", ROL_APROBADOR),
    ("Irene", "Cordero", "CTR", "Subgerente de Control Interno", ROL_APROBADOR),
    ("Joaquin", "Rivas", "PLF", "Analista de Presupuesto", ROL_COLABORADOR),
    ("Karla", "Mendoza", "TES", "Analista de Tesorería", ROL_COLABORADOR),
    ("Luis", "Ferrer", "CTR", "Analista de Control", ROL_COLABORADOR),
    ("Marta", "Ibarra", "CON", "Contador", ROL_COLABORADOR),
    ("Nestor", "Paredes", "CXC", "Analista de Cuentas por Cobrar", ROL_COLABORADOR),
    ("Olga", "Tovar", "CXP", "Analista de Cuentas por Pagar", ROL_COLABORADOR),
]

NOMBRES = [
    "Adriana", "Andrés", "Beatriz", "Camilo", "Daniela", "Eduardo", "Fernanda", "Gabriel",
    "Helena", "Ignacio", "Julieta", "Kevin", "Lucía", "Manuel", "Natalia", "Oscar",
    "Paola", "Ramiro", "Sofía", "Tomás", "Valeria", "Wilmer", "Ximena", "Yolanda",
]
APELLIDOS = [
    "Aponte", "Barrios", "Cedeño", "Duarte", "Escalona", "Figueroa", "Guevara", "Herrera",
    "Inojosa", "Jiménez", "Lugo", "Marcano", "Núñez", "Ochoa", "Peña", "Quevedo",
    "Rangel", "Sequera", "Trujillo", "Urdaneta", "Vargas", "Yánez", "Zerpa", "Villegas",
]

FECHA_INGRESO_MIN = date(2015, 1, 1)
FECHA_INGRESO_MAX = date(2026, 10, 31)


@dataclass(frozen=True)
class ColaboradorSeed:
    nombres: str
    apellidos: str
    correo: str
    departamento: str
    cargo: str
    pais: str
    fecha_ingreso: date
    estado: str
    rol: str | None


def crear_correo(nombres: str, apellidos: str) -> str:
    texto = unicodedata.normalize("NFKD", f"{nombres}.{apellidos}".lower())
    sin_acentos = "".join(c for c in texto if not unicodedata.combining(c))
    return f"{sin_acentos}@{DOMINIO_CORREO}"


def cargo_jefatura(codigo_departamento: str) -> str:
    cargos = DEPARTAMENTOS[codigo_departamento][3]
    return next(cargo[0] for cargo in cargos if cargo[2])


def generar_colaboradores(semilla: int = 42) -> list[ColaboradorSeed]:
    # Misma semilla, mismos datos: el resultado es reproducible.
    rng = random.Random(semilla)
    dias_rango = (FECHA_INGRESO_MAX - FECHA_INGRESO_MIN).days
    codigos_pais = [codigo for codigo, _ in PAISES]

    def fecha() -> date:
        return FECHA_INGRESO_MIN + timedelta(days=rng.randint(0, dias_rango))

    resultado: list[ColaboradorSeed] = []
    correos: set[str] = set()

    for nombres, apellidos, departamento, cargo, rol in USUARIOS_DEMO:
        correo = crear_correo(nombres, apellidos)
        correos.add(correo)
        resultado.append(ColaboradorSeed(
            nombres, apellidos, correo, departamento,
            cargo or cargo_jefatura(departamento),
            rng.choice(codigos_pais), fecha(), "activo", rol,
        ))

    for codigo, (_, _, cantidad, cargos) in DEPARTAMENTOS.items():
        existentes = sum(1 for c in resultado if c.departamento == codigo)
        # Cada departamento tiene un solo jefe y los subgerentes son los aprobadores.
        disponibles = [c[0] for c in cargos if not c[2] and not c[0].startswith("Subgerente")]
        faltantes = cantidad - existentes
        inactivos = rng.randint(1, 2)

        for indice in range(faltantes):
            while True:
                nombres, apellidos = rng.choice(NOMBRES), rng.choice(APELLIDOS)
                correo = crear_correo(nombres, apellidos)
                if correo not in correos:
                    correos.add(correo)
                    break
            resultado.append(ColaboradorSeed(
                nombres, apellidos, correo, codigo,
                disponibles[indice % len(disponibles)],
                rng.choice(codigos_pais), fecha(),
                "inactivo" if indice < inactivos else "activo",
                None,
            ))

    return resultado
