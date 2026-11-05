import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../api/client";
import type { AccionNota, NotaDetalle as Nota } from "../api/types";
import {
  Cargando,
  Dato,
  EtiquetaEstado,
  MensajeError,
  NOMBRE_ACCION,
  NOMBRE_ESTADO,
  formatearFechaHora,
  formatearMonto,
} from "../components/Estados";

type AccionFirma = "APROBAR" | "RECHAZAR" | "DEVOLVER";

const CONFIG: Record<AccionFirma, { ruta: string; boton: string; clase: string; pide: boolean }> = {
  APROBAR: { ruta: "aprobar", boton: "Aprobar", clase: "boton-principal", pide: false },
  DEVOLVER: { ruta: "devolver", boton: "Devolver para corregir", clase: "boton-secundario", pide: true },
  RECHAZAR: { ruta: "rechazar", boton: "Rechazar", clase: "boton-peligro", pide: true },
};

function esFirma(accion: AccionNota): accion is AccionFirma {
  return accion in CONFIG;
}

export function NotaDetalle() {
  const { id } = useParams();
  const clienteQuery = useQueryClient();
  const [comentario, setComentario] = useState("");
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  const nota = useQuery({
    queryKey: ["nota", id],
    queryFn: () => api<Nota>(`/notas-credito/${id}`),
  });

  const ejecutar = useMutation({
    mutationFn: (accion: AccionFirma) =>
      api<Nota>(`/notas-credito/${id}/${CONFIG[accion].ruta}`, {
        metodo: "POST",
        cuerpo: { comentario: comentario.trim() || null },
      }),
    onSuccess: (actualizada) => {
      setComentario("");
      clienteQuery.setQueryData(["nota", id], actualizada);
      clienteQuery.invalidateQueries({ queryKey: ["notas"] });
    },
    onError: () => {
      // El estado pudo cambiar por otra persona: se vuelve a leer lo vigente.
      clienteQuery.invalidateQueries({ queryKey: ["nota", id] });
    },
  });

  if (nota.isLoading) return <Cargando />;
  if (nota.isError) return <MensajeError error={nota.error} />;
  const datos = nota.data;
  if (!datos) return null;

  const firmas = datos.acciones_disponibles.filter(esFirma);
  const puedeReenviar = datos.acciones_disponibles.includes("REENVIAR");

  const actuar = (accion: AccionFirma) => {
    if (CONFIG[accion].pide && !comentario.trim()) {
      setErrorLocal("Escribe un comentario para explicar esta decisión.");
      return;
    }
    setErrorLocal(null);
    ejecutar.mutate(accion);
  };

  return (
    <>
      <p className="text-sm">
        <Link className="enlace" to="/notas">
          Volver a la bandeja
        </Link>
      </p>

      <div className="mt-2 flex flex-wrap items-center gap-3">
        <h1 className="cifras text-2xl font-bold text-tinta">{datos.codigo}</h1>
        <EtiquetaEstado estado={datos.estado} />
      </div>
      <p className="cifras mt-2 text-3xl font-semibold">{formatearMonto(datos.monto, datos.moneda)}</p>

      <div className="mt-6 grid gap-6 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-3">
          <dl className="grid gap-5 superficie p-6 sm:grid-cols-2">
            <Dato etiqueta="Motivo">{datos.motivo.nombre}</Dato>
            <Dato etiqueta="Departamento">{datos.departamento.nombre}</Dato>
            <Dato etiqueta="Solicitante">{datos.solicitante}</Dato>
            <Dato etiqueta="Factura">{datos.factura_referencia}</Dato>
            <Dato etiqueta="Tienda">{datos.tienda.nombre}</Dato>
            <Dato etiqueta="Compañía">{datos.compania.nombre}</Dato>
            <Dato etiqueta="Firmas requeridas">{datos.requiere_doble_aprobacion ? "Dos" : "Una"}</Dato>
            {datos.primer_aprobador && <Dato etiqueta="Primera firma">{datos.primer_aprobador}</Dato>}
            <div className="sm:col-span-2">
              <Dato etiqueta="Descripción">{datos.descripcion}</Dato>
            </div>
          </dl>

          {firmas.length > 0 && (
            <section aria-labelledby="titulo-decision" className="superficie p-6">
              <h2 id="titulo-decision" className="font-semibold text-tinta">
                Tu decisión
              </h2>
              <label htmlFor="comentario" className="mt-3 block text-sm font-medium">
                Comentario (obligatorio para rechazar o devolver)
              </label>
              <textarea
                id="comentario"
                className="campo mt-1"
                rows={3}
                maxLength={1000}
                value={comentario}
                onChange={(e) => setComentario(e.target.value)}
              />
              {errorLocal && (
                <div className="mt-3">
                  <MensajeError mensaje={errorLocal} />
                </div>
              )}
              {ejecutar.isError && (
                <div className="mt-3">
                  <MensajeError error={ejecutar.error} />
                </div>
              )}
              <div className="mt-4 flex flex-wrap gap-2">
                {firmas.map((accion) => (
                  <button
                    key={accion}
                    type="button"
                    className={CONFIG[accion].clase}
                    disabled={ejecutar.isPending}
                    onClick={() => actuar(accion)}
                  >
                    {CONFIG[accion].boton}
                  </button>
                ))}
              </div>
            </section>
          )}

          {puedeReenviar && (
            <Link to={`/notas/${datos.id}/reenviar`} className="boton-principal">
              Corregir y reenviar
            </Link>
          )}
        </div>

        <section aria-labelledby="titulo-historial" className="lg:col-span-2">
          <h2 id="titulo-historial" className="font-semibold text-tinta">
            Historial de auditoría
          </h2>
          <ol className="mt-3 border-l-2 border-tinta pl-5">
            {datos.eventos.map((evento) => (
              <li key={evento.id} className="relative pb-6 last:pb-0">
                <span
                  aria-hidden="true"
                  className="absolute -left-[27px] top-1.5 h-3 w-3 rounded-full border-2 border-tinta bg-papel"
                />
                <p className="text-sm font-semibold">
                  {evento.actor}: {NOMBRE_ACCION[evento.accion].toLowerCase()}
                </p>
                <p className="cifras text-xs text-tenue">{formatearFechaHora(evento.creado_en)}</p>
                <p className="mt-1 text-xs">
                  {evento.estado_anterior ? `${NOMBRE_ESTADO[evento.estado_anterior]} a ` : "Inició en "}
                  {NOMBRE_ESTADO[evento.estado_nuevo]}
                </p>
                {evento.comentario && <p className="mt-1 text-sm">{evento.comentario}</p>}
              </li>
            ))}
          </ol>
        </section>
      </div>
    </>
  );
}
