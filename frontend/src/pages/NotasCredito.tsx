import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import type { DepartamentoCorto, EstadoNota, NotaResumen } from "../api/types";
import { useUsuario } from "../auth/AuthContext";
import {
  Cargando,
  EtiquetaEstado,
  MensajeError,
  NOMBRE_ESTADO,
  formatearFecha,
  formatearMonto,
} from "../components/Estados";

const ESTADOS = Object.keys(NOMBRE_ESTADO) as EstadoNota[];

export function NotasCredito() {
  const usuario = useUsuario();
  const puedeFirmar = usuario.rol === "ADMIN" || usuario.rol === "APROBADOR";
  const puedeCrear = usuario.rol === "ADMIN" || usuario.rol === "JEFE_DEPARTAMENTO";

  const [soloMiFirma, setSoloMiFirma] = useState(puedeFirmar);
  const [estado, setEstado] = useState("");
  const [departamento, setDepartamento] = useState("");

  const parametros = new URLSearchParams();
  if (soloMiFirma) parametros.set("pendientes_de_mi_firma", "true");
  if (estado && !soloMiFirma) parametros.set("estado", estado);
  if (departamento) parametros.set("departamento_id", departamento);

  const notas = useQuery({
    queryKey: ["notas", parametros.toString()],
    queryFn: () => api<NotaResumen[]>(`/notas-credito?${parametros.toString()}`),
  });
  const departamentos = useQuery({
    queryKey: ["departamentos"],
    queryFn: () => api<DepartamentoCorto[]>("/departamentos"),
  });

  const filas = notas.data ?? [];

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-tinta">Notas de crédito</h1>
        {puedeCrear && (
          <Link to="/notas/nueva" className="boton-principal">
            Crear nota
          </Link>
        )}
      </div>

      {puedeFirmar && (
        <div role="tablist" aria-label="Bandeja" className="mt-5 flex gap-1 border-b border-linea">
          {[
            { valor: true, nombre: "Pendientes de mi firma" },
            { valor: false, nombre: "Todas las notas" },
          ].map((pestana) => (
            <button
              key={pestana.nombre}
              type="button"
              role="tab"
              aria-selected={soloMiFirma === pestana.valor}
              onClick={() => setSoloMiFirma(pestana.valor)}
              className={`-mb-px border-b-2 px-4 py-2 transition-colors text-sm font-semibold ${
                soloMiFirma === pestana.valor ? "border-tinta text-tinta" : "border-transparent text-tenue"
              }`}
            >
              {pestana.nombre}
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {!soloMiFirma && (
          <div>
            <label htmlFor="estado" className="text-xs text-tenue">
              Estado
            </label>
            <select id="estado" className="campo mt-1" value={estado} onChange={(e) => setEstado(e.target.value)}>
              <option value="">Todos</option>
              {ESTADOS.map((clave) => (
                <option key={clave} value={clave}>
                  {NOMBRE_ESTADO[clave]}
                </option>
              ))}
            </select>
          </div>
        )}
        {(departamentos.data?.length ?? 0) > 1 && (
          <div>
            <label htmlFor="departamento" className="text-xs text-tenue">
              Departamento
            </label>
            <select
              id="departamento"
              className="campo mt-1"
              value={departamento}
              onChange={(e) => setDepartamento(e.target.value)}
            >
              <option value="">Todos</option>
              {departamentos.data?.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.nombre}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="mt-5">
        {notas.isLoading && <Cargando />}
        {notas.isError && <MensajeError error={notas.error} />}
        {notas.isSuccess && filas.length === 0 && (
          <p className="superficie p-6 text-sm text-tenue">
            {soloMiFirma ? "No tienes notas pendientes de firma." : "No hay notas con estos filtros."}
          </p>
        )}
        {filas.length > 0 && (
          <div className="overflow-x-auto superficie">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-linea bg-papel/60 text-xs text-tenue">
                <tr>
                  <th className="px-4 py-3 font-semibold">Código</th>
                  <th className="px-4 py-3 font-semibold">Departamento</th>
                  <th className="px-4 py-3 font-semibold">Motivo</th>
                  <th className="px-4 py-3 text-right font-semibold">Monto</th>
                  <th className="px-4 py-3 font-semibold">Estado</th>
                  <th className="px-4 py-3 font-semibold">Creada</th>
                </tr>
              </thead>
              <tbody>
                {filas.map((nota) => (
                  <tr key={nota.id} className="border-b border-linea transition-colors last:border-0 hover:bg-papel/60">
                    <td className="cifras whitespace-nowrap px-4 py-3">
                      <Link className="enlace" to={`/notas/${nota.id}`}>
                        {nota.codigo}
                      </Link>
                    </td>
                    <td className="px-4 py-3">{nota.departamento.nombre}</td>
                    <td className="min-w-52 px-4 py-3">{nota.motivo.nombre}</td>
                    <td className="cifras whitespace-nowrap px-4 py-3 text-right font-medium">
                      {formatearMonto(nota.monto, nota.moneda)}
                    </td>
                    <td className="px-4 py-3">
                      <EtiquetaEstado estado={nota.estado} />
                    </td>
                    <td className="cifras whitespace-nowrap px-4 py-3">{formatearFecha(nota.creada_en)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
