"""Las 25 notas del dataset entregado por la empresa, con sus valores originales."""
from typing import NamedTuple

COMENTARIO_CREACION = "Nota de crédito generada por despacho a tienda"
COMENTARIO_APROBADA = "Aprobada tras validación de soporte de despacho"
COMENTARIO_RECHAZADA = "Rechazada: soporte de despacho insuficiente"


class NotaDataset(NamedTuple):
    monto: str
    moneda: str
    motivo: str
    tienda: str
    compania: str
    departamento: str
    estado: str
    creada: str
    resuelta: str | None


NOTAS = [
    NotaDataset(
        '1262.21', 'USD',
        'Error de facturación en monto despachado',
        'Tienda Córdoba Norte', 'Laboratorios Andina C.A.',
        'CXC', 'aprobada', '2026-05-18', '2026-05-22',
    ),
    NotaDataset(
        '1132.26', 'USD',
        'Producto recibido en mal estado',
        'Tienda Belgrano', 'Grupo Farmavalle',
        'CXC', 'pendiente', '2026-07-04', None,
    ),
    NotaDataset(
        '2966.87', 'USD',
        'Diferencia cambiaria en pago anticipado a proveedor',
        'Tienda Córdoba Norte', 'Salud Total Distribución',
        'CXP', 'pendiente', '2026-05-01', None,
    ),
    NotaDataset(
        '3829.30', 'USD',
        'Diferencia cambiaria en pago anticipado a proveedor',
        'Tienda Maracaibo Centro', 'Nutrisana Import',
        'CXC', 'pendiente', '2026-05-14', None,
    ),
    NotaDataset(
        '4045.28', 'USD',
        'Diferencia cambiaria en pago anticipado a proveedor',
        'Tienda Chacao', 'Nutrisana Import',
        'CXP', 'aprobada', '2026-06-28', '2026-07-02',
    ),
    NotaDataset(
        '3111.67', 'USD',
        'Error de facturación en monto despachado',
        'Tienda Chacao', 'Beltek Consumo Masivo',
        'CXP', 'rechazada', '2026-06-16', '2026-06-18',
    ),
    NotaDataset(
        '4926.85', 'USD',
        'Diferencia cambiaria en pago anticipado a proveedor',
        'Tienda Chacao', 'Salud Total Distribución',
        'CXC', 'aprobada', '2026-05-30', '2026-05-31',
    ),
    NotaDataset(
        '1808.59', 'VES',
        'Error de facturación en monto despachado',
        'Tienda Maracaibo Centro', 'Grupo Farmavalle',
        'CXP', 'pendiente', '2026-07-25', None,
    ),
    NotaDataset(
        '1261.81', 'VES',
        'Duplicidad de despacho a la misma tienda',
        'Tienda Belgrano', 'Salud Total Distribución',
        'CXC', 'aprobada', '2026-06-29', '2026-06-30',
    ),
    NotaDataset(
        '4222.12', 'USD',
        'Devolución de producto por vencimiento',
        'Tienda Córdoba Norte', 'Salud Total Distribución',
        'CXC', 'aprobada', '2026-05-08', '2026-05-12',
    ),
    NotaDataset(
        '4570.02', 'VES',
        'Producto recibido en mal estado',
        'Tienda Maracaibo Centro', 'Grupo Farmavalle',
        'CXP', 'pendiente', '2026-07-12', None,
    ),
    NotaDataset(
        '3232.12', 'VES',
        'Ajuste de precio por promoción no aplicada',
        'Tienda Córdoba Norte', 'Grupo Farmavalle',
        'CXP', 'rechazada', '2026-05-19', '2026-05-22',
    ),
    NotaDataset(
        '2170.75', 'VES',
        'Descuento comercial no reflejado en factura',
        'Tienda Las Mercedes', 'Salud Total Distribución',
        'CXP', 'aprobada', '2026-07-14', '2026-07-18',
    ),
    NotaDataset(
        '283.23', 'USD',
        'Ajuste de precio por promoción no aplicada',
        'Tienda Las Mercedes', 'Distribuidora Cuyaní',
        'CXP', 'pendiente', '2026-05-15', None,
    ),
    NotaDataset(
        '2999.65', 'VES',
        'Devolución de producto por vencimiento',
        'Tienda Córdoba Norte', 'Grupo Farmavalle',
        'CXC', 'aprobada', '2026-06-29', '2026-07-03',
    ),
    NotaDataset(
        '2708.00', 'VES',
        'Error de facturación en monto despachado',
        'Tienda Córdoba Norte', 'Salud Total Distribución',
        'CXC', 'aprobada', '2026-06-04', '2026-06-08',
    ),
    NotaDataset(
        '4771.39', 'USD',
        'Error de facturación en monto despachado',
        'Tienda Maracaibo Centro', 'Grupo Farmavalle',
        'CXC', 'aprobada', '2026-06-03', '2026-06-04',
    ),
    NotaDataset(
        '3824.43', 'USD',
        'Descuento comercial no reflejado en factura',
        'Tienda Córdoba Norte', 'Nutrisana Import',
        'CXC', 'pendiente', '2026-07-09', None,
    ),
    NotaDataset(
        '4399.67', 'USD',
        'Devolución de producto por vencimiento',
        'Tienda Palermo', 'Laboratorios Andina C.A.',
        'CXC', 'rechazada', '2026-06-09', '2026-06-10',
    ),
    NotaDataset(
        '2455.65', 'USD',
        'Ajuste de precio por promoción no aplicada',
        'Tienda Las Mercedes', 'Beltek Consumo Masivo',
        'CXC', 'pendiente', '2026-05-09', None,
    ),
    NotaDataset(
        '4368.54', 'USD',
        'Producto recibido en mal estado',
        'Tienda Córdoba Norte', 'Grupo Farmavalle',
        'CXC', 'pendiente', '2026-06-24', None,
    ),
    NotaDataset(
        '3266.90', 'VES',
        'Error de facturación en monto despachado',
        'Tienda Córdoba Norte', 'Nutrisana Import',
        'CXP', 'rechazada', '2026-06-26', '2026-06-27',
    ),
    NotaDataset(
        '2962.13', 'USD',
        'Devolución de producto por vencimiento',
        'Tienda Las Mercedes', 'Distribuidora Cuyaní',
        'CXC', 'pendiente', '2026-05-30', None,
    ),
    NotaDataset(
        '4531.83', 'USD',
        'Producto recibido en mal estado',
        'Tienda Chacao', 'Salud Total Distribución',
        'CXC', 'pendiente', '2026-06-12', None,
    ),
    NotaDataset(
        '704.94', 'VES',
        'Producto recibido en mal estado',
        'Tienda Maracaibo Centro', 'Salud Total Distribución',
        'CXP', 'pendiente', '2026-07-13', None,
    ),
]
