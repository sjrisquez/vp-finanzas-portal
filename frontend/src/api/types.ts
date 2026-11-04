export type Rol = "ADMIN" | "JEFE_DEPARTAMENTO" | "APROBADOR" | "COLABORADOR";
export type EstadoNota =
  | "PENDIENTE"
  | "PENDIENTE_SEGUNDA_FIRMA"
  | "DEVUELTA"
  | "APROBADA"
  | "RECHAZADA";
export type AccionNota = "CREAR" | "APROBAR" | "RECHAZAR" | "DEVOLVER" | "REENVIAR";
export type Moneda = "USD" | "VES";

export interface DepartamentoCorto {
  id: number;
  codigo: string;
  nombre: string;
}

export interface UsuarioActual {
  id: number;
  colaborador_id: number;
  cargo_id: number;
  nombres: string;
  apellidos: string;
  correo: string;
  rol: Rol;
  departamento: DepartamentoCorto;
  modulos: string[];
}

export interface Nivel {
  id: number;
  nombre: string;
  orden: number;
}

export interface Pais {
  id: number;
  codigo_iso: string;
  nombre: string;
}

export interface ColaboradorPublico {
  id: number;
  nombres: string;
  apellidos: string;
  correo: string;
  cargo: string;
}

export interface ColaboradorDetalle {
  id: number;
  nombres: string;
  apellidos: string;
  correo: string;
  fecha_ingreso: string;
  estado: string;
  pais: Pais;
  cargo: {
    id: number;
    nombre: string;
    es_jefatura: boolean;
    departamento: DepartamentoCorto;
    nivel: Nivel;
  };
}

export type ColaboradorFila = ColaboradorPublico | ColaboradorDetalle;

export interface CargoDetalle {
  id: number;
  nombre: string;
  es_jefatura: boolean;
  departamento: DepartamentoCorto;
  nivel: Nivel;
  funciones: { id: number; descripcion: string }[];
}

export interface Catalogo {
  id: number;
  nombre: string;
}

export interface Motivo extends Catalogo {
  codigo: string;
}

export interface Compania extends Catalogo {
  rubro: string;
}

export interface NotaResumen {
  id: number;
  codigo: string;
  departamento: DepartamentoCorto;
  solicitante: string;
  motivo: Motivo;
  tienda: Catalogo;
  compania: Compania;
  factura_referencia: string;
  monto: string;
  moneda: Moneda;
  estado: EstadoNota;
  requiere_doble_aprobacion: boolean;
  creada_en: string;
  actualizada_en: string;
}

export interface EventoNota {
  id: number;
  accion: AccionNota;
  estado_anterior: EstadoNota | null;
  estado_nuevo: EstadoNota;
  comentario: string | null;
  actor: string;
  creado_en: string;
}

export interface NotaDetalle extends NotaResumen {
  descripcion: string;
  primer_aprobador: string | null;
  acciones_disponibles: AccionNota[];
  eventos: EventoNota[];
}

export interface Umbrales {
  USD: string;
  VES: string;
}
