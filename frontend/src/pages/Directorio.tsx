import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import type { ColaboradorDetalle, ColaboradorFila, DepartamentoCorto } from "../api/types";
import { useUsuario } from "../auth/AuthContext";
import { Cargando, MensajeError, formatearFecha } from "../components/Estados";

function esDetalle(fila: ColaboradorFila): fila is ColaboradorDetalle {
  return "fecha_ingreso" in fila;
}

export function Directorio() {
  const usuario = useUsuario();
  const [departamento, setDepartamento] = useState("");
  const [estado, setEstado] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const parametros = new URLSearchParams();
  if (departamento) parametros.set("departamento_id", departamento);
  if (estado) parametros.set("estado", estado);
  if (busqueda.trim()) parametros.set("q", busqueda.trim());

  const departamentos = useQuery({
    queryKey: ["departamentos"],
    queryFn: () => api<DepartamentoCorto[]>("/departamentos"),
  });
  const colaboradores = useQuery({
    queryKey: ["colaboradores", parametros.toString()],
    queryFn: () => api<ColaboradorFila[]>(`/colaboradores?${parametros.toString()}`),
  });

  const filas = colaboradores.data ?? [];
  // Las columnas dependen de lo que devolvió la API, no de ocultar datos aquí.
  const vistaCompleta = filas.some(esDetalle);
  const limitada = usuario.rol === "COLABORADOR";

  return (
    <>
      <h1 className="text-2xl font-bold text-tinta">Directorio</h1>
      <p className="mt-1 text-sm text-tenue">
        {limitada ? `Compañeros activos de ${usuario.departamento.nombre}.` : "Colaboradores dentro de tu alcance."}
      </p>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <div>
          <label htmlFor="busqueda" className="text-xs text-tenue">
            Buscar por nombre o correo
          </label>
          <input
            id="busqueda"
            className="campo mt-1"
            maxLength={100}
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>
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
        {!limitada && (
          <div>
            <label htmlFor="estado" className="text-xs text-tenue">
              Estado
            </label>
            <select id="estado" className="campo mt-1" value={estado} onChange={(e) => setEstado(e.target.value)}>
              <option value="">Todos</option>
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
            </select>
          </div>
        )}
      </div>

      <div className="mt-5">
        {colaboradores.isLoading && <Cargando />}
        {colaboradores.isError && <MensajeError error={colaboradores.error} />}
        {colaboradores.isSuccess && filas.length === 0 && (
          <p className="superficie p-6 text-sm text-tenue">
            Nadie coincide con estos filtros. Prueba con una búsqueda más amplia.
          </p>
        )}
        {filas.length > 0 && (
          <div className="overflow-x-auto superficie">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-linea bg-papel/60 text-xs text-tenue">
                <tr>
                  <th className="px-4 py-3 font-semibold">Nombre</th>
                  <th className="px-4 py-3 font-semibold">Cargo</th>
                  <th className="px-4 py-3 font-semibold">Correo</th>
                  {vistaCompleta && (
                    <>
                      <th className="px-4 py-3 font-semibold">Departamento</th>
                      <th className="px-4 py-3 font-semibold">País</th>
                      <th className="px-4 py-3 font-semibold">Ingreso</th>
                      <th className="px-4 py-3 font-semibold">Estado</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {filas.map((fila) => {
                  const nombre = `${fila.apellidos}, ${fila.nombres}`;
                  const puedeAbrir = esDetalle(fila) || fila.id === usuario.colaborador_id;
                  return (
                    <tr key={fila.id} className="border-b border-linea transition-colors last:border-0 hover:bg-papel/60">
                      <td className="whitespace-nowrap px-4 py-3 font-medium">
                        {puedeAbrir ? (
                          <Link className="enlace" to={`/colaboradores/${fila.id}`}>
                            {nombre}
                          </Link>
                        ) : (
                          nombre
                        )}
                      </td>
                      <td className="px-4 py-3">{esDetalle(fila) ? fila.cargo.nombre : fila.cargo}</td>
                      <td className="px-4 py-3">{fila.correo}</td>
                      {esDetalle(fila) && (
                        <>
                          <td className="px-4 py-3">{fila.cargo.departamento.nombre}</td>
                          <td className="px-4 py-3">{fila.pais.nombre}</td>
                          <td className="cifras whitespace-nowrap px-4 py-3">{formatearFecha(fila.fecha_ingreso)}</td>
                          <td className="px-4 py-3">{fila.estado === "activo" ? "Activo" : "Inactivo"}</td>
                        </>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
