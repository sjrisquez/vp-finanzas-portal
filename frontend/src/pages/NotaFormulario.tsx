import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api/client";
import type {
  Catalogo,
  Compania,
  DepartamentoCorto,
  Moneda,
  Motivo,
  NotaDetalle,
  Umbrales,
} from "../api/types";
import { useUsuario } from "../auth/AuthContext";
import { Cargando, MensajeError, formatearMonto } from "../components/Estados";

const FORMATO_MONTO = /^\d{1,9}(\.\d{1,2})?$/;

export function NotaFormulario() {
  const { id } = useParams();
  const reenvio = id !== undefined;
  const usuario = useUsuario();
  const navegar = useNavigate();
  const clienteQuery = useQueryClient();

  const [departamento, setDepartamento] = useState(String(usuario.departamento.id));
  const [motivo, setMotivo] = useState("");
  const [tienda, setTienda] = useState("");
  const [compania, setCompania] = useState("");
  const [factura, setFactura] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [monto, setMonto] = useState("");
  const [moneda, setMoneda] = useState<Moneda>("USD");
  const [comentario, setComentario] = useState("");
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  const nota = useQuery({
    queryKey: ["nota", id],
    queryFn: () => api<NotaDetalle>(`/notas-credito/${id}`),
    enabled: reenvio,
  });
  const motivos = useQuery({ queryKey: ["motivos"], queryFn: () => api<Motivo[]>("/catalogos/motivos") });
  const tiendas = useQuery({
    queryKey: ["tiendas"],
    queryFn: () => api<Catalogo[]>("/catalogos/tiendas"),
    enabled: !reenvio,
  });
  const companias = useQuery({
    queryKey: ["companias"],
    queryFn: () => api<Compania[]>("/catalogos/companias"),
    enabled: !reenvio,
  });
  const departamentos = useQuery({
    queryKey: ["departamentos"],
    queryFn: () => api<DepartamentoCorto[]>("/departamentos"),
    enabled: !reenvio && usuario.rol === "ADMIN",
  });
  const umbrales = useQuery({ queryKey: ["umbrales"], queryFn: () => api<Umbrales>("/catalogos/umbrales") });

  useEffect(() => {
    if (nota.data) {
      setMotivo(String(nota.data.motivo.id));
      setDescripcion(nota.data.descripcion);
      setMonto(nota.data.monto);
      setMoneda(nota.data.moneda);
    }
  }, [nota.data]);

  const guardar = useMutation({
    mutationFn: () =>
      reenvio
        ? api<NotaDetalle>(`/notas-credito/${id}/reenviar`, {
            metodo: "PUT",
            cuerpo: {
              motivo_id: Number(motivo),
              descripcion,
              monto,
              comentario: comentario.trim() || null,
            },
          })
        : api<NotaDetalle>("/notas-credito", {
            metodo: "POST",
            cuerpo: {
              departamento_id: Number(departamento),
              motivo_id: Number(motivo),
              tienda_id: Number(tienda),
              compania_id: Number(compania),
              factura_referencia: factura,
              descripcion,
              monto,
              moneda,
            },
          }),
    onSuccess: (guardada) => {
      clienteQuery.invalidateQueries({ queryKey: ["notas"] });
      clienteQuery.setQueryData(["nota", String(guardada.id)], guardada);
      navegar(`/notas/${guardada.id}`);
    },
  });

  if (reenvio && nota.isLoading) return <Cargando />;
  if (reenvio && nota.isError) return <MensajeError error={nota.error} />;

  const superaUmbral =
    umbrales.data !== undefined && FORMATO_MONTO.test(monto) && Number(monto) > Number(umbrales.data[moneda]);

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!FORMATO_MONTO.test(monto) || Number(monto) <= 0) {
      setErrorLocal("Escribe un monto mayor a 0, con hasta 2 decimales. Ejemplo: 1250.50");
      return;
    }
    setErrorLocal(null);
    guardar.mutate();
  };

  return (
    <>
      <p className="text-sm">
        <Link className="enlace" to={reenvio ? `/notas/${id}` : "/notas"}>
          Volver
        </Link>
      </p>
      <h1 className="mt-2 text-2xl font-bold text-tinta">
        {reenvio ? `Corregir ${nota.data?.codigo ?? ""}` : "Crear nota de crédito"}
      </h1>

      <form onSubmit={enviar} className="mt-5 grid max-w-3xl gap-4 superficie p-6 sm:grid-cols-2">
        {!reenvio && usuario.rol === "ADMIN" && (
          <div className="sm:col-span-2">
            <label htmlFor="departamento" className="text-sm font-medium">
              Departamento solicitante
            </label>
            <select
              id="departamento"
              className="campo mt-1"
              required
              value={departamento}
              onChange={(e) => setDepartamento(e.target.value)}
            >
              {departamentos.data?.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.nombre}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="sm:col-span-2">
          <label htmlFor="motivo" className="text-sm font-medium">
            Motivo
          </label>
          <select id="motivo" className="campo mt-1" required value={motivo} onChange={(e) => setMotivo(e.target.value)}>
            <option value="">Selecciona un motivo</option>
            {motivos.data?.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nombre}
              </option>
            ))}
          </select>
        </div>

        {!reenvio && (
          <>
            <div>
              <label htmlFor="tienda" className="text-sm font-medium">
                Tienda
              </label>
              <select id="tienda" className="campo mt-1" required value={tienda} onChange={(e) => setTienda(e.target.value)}>
                <option value="">Selecciona una tienda</option>
                {tiendas.data?.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="compania" className="text-sm font-medium">
                Compañía
              </label>
              <select
                id="compania"
                className="campo mt-1"
                required
                value={compania}
                onChange={(e) => setCompania(e.target.value)}
              >
                <option value="">Selecciona una compañía</option>
                {companias.data?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="factura" className="text-sm font-medium">
                Referencia de factura
              </label>
              <input
                id="factura"
                className="campo mt-1"
                required
                maxLength={30}
                value={factura}
                onChange={(e) => setFactura(e.target.value)}
              />
            </div>
          </>
        )}

        <div>
          <label htmlFor="monto" className="text-sm font-medium">
            Monto
          </label>
          <input
            id="monto"
            className="campo cifras mt-1"
            inputMode="decimal"
            required
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="moneda" className="text-sm font-medium">
            Moneda
          </label>
          <select
            id="moneda"
            className="campo mt-1"
            disabled={reenvio}
            value={moneda}
            onChange={(e) => setMoneda(e.target.value as Moneda)}
          >
            <option value="USD">USD</option>
            <option value="VES">VES</option>
          </select>
        </div>

        {superaUmbral && umbrales.data && (
          <p className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-900 sm:col-span-2">
            Supera {formatearMonto(umbrales.data[moneda], moneda)}: necesitará la firma de dos aprobadores distintos.
          </p>
        )}

        <div className="sm:col-span-2">
          <label htmlFor="descripcion" className="text-sm font-medium">
            Descripción
          </label>
          <textarea
            id="descripcion"
            className="campo mt-1"
            rows={3}
            required
            maxLength={2000}
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
          />
        </div>

        {reenvio && (
          <div className="sm:col-span-2">
            <label htmlFor="comentario" className="text-sm font-medium">
              Comentario sobre la corrección (opcional)
            </label>
            <textarea
              id="comentario"
              className="campo mt-1"
              rows={2}
              maxLength={1000}
              value={comentario}
              onChange={(e) => setComentario(e.target.value)}
            />
          </div>
        )}

        {errorLocal && (
          <div className="sm:col-span-2">
            <MensajeError mensaje={errorLocal} />
          </div>
        )}
        {guardar.isError && (
          <div className="sm:col-span-2">
            <MensajeError error={guardar.error} />
          </div>
        )}

        <div className="sm:col-span-2">
          <button type="submit" className="boton-principal" disabled={guardar.isPending}>
            {guardar.isPending ? "Guardando…" : reenvio ? "Reenviar nota" : "Crear nota"}
          </button>
        </div>
      </form>
    </>
  );
}
