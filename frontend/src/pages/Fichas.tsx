import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { api } from "../api/client";
import type { CargoDetalle, ColaboradorDetalle } from "../api/types";
import { useUsuario } from "../auth/AuthContext";
import { Cargando, Dato, MensajeError, formatearFecha } from "../components/Estados";

function FichaColaboradorContenido({ id }: { id: number }) {
  const colaborador = useQuery({
    queryKey: ["colaborador", id],
    queryFn: () => api<ColaboradorDetalle>(`/colaboradores/${id}`),
  });

  if (colaborador.isLoading) return <Cargando />;
  if (colaborador.isError) return <MensajeError error={colaborador.error} />;
  const datos = colaborador.data;
  if (!datos) return null;

  return (
    <>
      <h1 className="text-2xl font-bold text-tinta">
        {datos.nombres} {datos.apellidos}
      </h1>
      <p className="mt-1 text-sm text-tenue">{datos.correo}</p>

      <dl className="mt-6 grid gap-5 rounded border border-linea bg-white p-6 sm:grid-cols-3">
        <Dato etiqueta="Cargo">
          <Link className="enlace" to={`/cargos/${datos.cargo.id}`}>
            {datos.cargo.nombre}
          </Link>
        </Dato>
        <Dato etiqueta="Departamento">{datos.cargo.departamento.nombre}</Dato>
        <Dato etiqueta="Nivel">{datos.cargo.nivel.nombre}</Dato>
        <Dato etiqueta="País">{datos.pais.nombre}</Dato>
        <Dato etiqueta="Fecha de ingreso">{formatearFecha(datos.fecha_ingreso)}</Dato>
        <Dato etiqueta="Estado">{datos.estado === "activo" ? "Activo" : "Inactivo"}</Dato>
      </dl>
    </>
  );
}

function FichaCargoContenido({ id }: { id: number }) {
  const cargo = useQuery({
    queryKey: ["cargo", id],
    queryFn: () => api<CargoDetalle>(`/cargos/${id}`),
  });

  if (cargo.isLoading) return <Cargando />;
  if (cargo.isError) return <MensajeError error={cargo.error} />;
  const datos = cargo.data;
  if (!datos) return null;

  return (
    <>
      <h2 className="text-xl font-bold text-tinta">{datos.nombre}</h2>
      <dl className="mt-4 grid gap-5 rounded border border-linea bg-white p-6 sm:grid-cols-3">
        <Dato etiqueta="Departamento">{datos.departamento.nombre}</Dato>
        <Dato etiqueta="Nivel">{datos.nivel.nombre}</Dato>
        <Dato etiqueta="Jefatura">{datos.es_jefatura ? "Sí" : "No"}</Dato>
      </dl>
      <h3 className="mt-6 text-sm font-semibold">Funciones del cargo</h3>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
        {datos.funciones.map((funcion) => (
          <li key={funcion.id}>{funcion.descripcion}</li>
        ))}
      </ul>
    </>
  );
}

export function FichaColaborador() {
  const { id } = useParams();
  return <FichaColaboradorContenido id={Number(id)} />;
}

export function FichaCargo() {
  const { id } = useParams();
  return <FichaCargoContenido id={Number(id)} />;
}

export function MiPerfil() {
  const usuario = useUsuario();
  return (
    <>
      <FichaColaboradorContenido id={usuario.colaborador_id} />
      <div className="mt-8">
        <FichaCargoContenido id={usuario.cargo_id} />
      </div>
    </>
  );
}
