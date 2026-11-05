import type { ReactNode } from "react";

import type { AccionNota, EstadoNota } from "../api/types";
import { ApiError } from "../api/client";

export function Cargando() {
  return (
    <p role="status" className="p-8 text-sm text-tenue">
      Cargando…
    </p>
  );
}

export function MensajeError({ mensaje, error }: { mensaje?: string; error?: unknown }) {
  const texto =
    mensaje ?? (error instanceof ApiError ? error.message : "No se pudo completar la operación.");
  return (
    <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900">
      {texto}
    </p>
  );
}

export const NOMBRE_ESTADO: Record<EstadoNota, string> = {
  PENDIENTE: "Pendiente",
  PENDIENTE_SEGUNDA_FIRMA: "Falta segunda firma",
  DEVUELTA: "Devuelta",
  APROBADA: "Aprobada",
  RECHAZADA: "Rechazada",
};

const COLOR_ESTADO: Record<EstadoNota, string> = {
  PENDIENTE: "border-amber-400 bg-amber-50 text-amber-900",
  PENDIENTE_SEGUNDA_FIRMA: "border-blue-400 bg-blue-50 text-blue-900",
  DEVUELTA: "border-violet-400 bg-violet-50 text-violet-900",
  APROBADA: "border-emerald-500 bg-emerald-50 text-emerald-900",
  RECHAZADA: "border-red-400 bg-red-50 text-red-900",
};

export function EtiquetaEstado({ estado }: { estado: EstadoNota }) {
  return (
    <span
      className={`inline-block whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-semibold ${COLOR_ESTADO[estado]}`}
    >
      {NOMBRE_ESTADO[estado]}
    </span>
  );
}

export const NOMBRE_ACCION: Record<AccionNota, string> = {
  CREAR: "Creó la nota",
  APROBAR: "Aprobó",
  RECHAZAR: "Rechazó",
  DEVOLVER: "Devolvió para corregir",
  REENVIAR: "Corrigió y reenvió",
};

export function formatearMonto(monto: string, moneda: string): string {
  const numero = Number(monto).toLocaleString("es-VE", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `${moneda} ${numero}`;
}

export function formatearFecha(iso: string): string {
  return new Date(iso).toLocaleDateString("es-VE", { dateStyle: "medium" });
}

export function formatearFechaHora(iso: string): string {
  return new Date(iso).toLocaleString("es-VE", { dateStyle: "medium", timeStyle: "short" });
}

export function Dato({ etiqueta, children }: { etiqueta: string; children: ReactNode }) {
  return (
    <div>
      <dt className="text-xs text-tenue">{etiqueta}</dt>
      <dd className="mt-0.5 text-sm font-medium">{children}</dd>
    </div>
  );
}
