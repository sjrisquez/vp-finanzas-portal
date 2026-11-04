export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

let alExpirarSesion: () => void = () => undefined;

export function registrarSesionExpirada(accion: () => void): void {
  alExpirarSesion = accion;
}

const MENSAJES: Record<number, string> = {
  403: "No tienes permiso para realizar esta acción.",
  404: "No encontramos este registro, o no está dentro de tu alcance.",
  409: "Esta acción ya no es válida para el estado actual. Actualiza la página.",
  422: "Revisa los datos ingresados.",
};

function mensajeDeError(status: number, cuerpo: unknown): string {
  const detalle = (cuerpo as { detail?: unknown } | null)?.detail;
  if (typeof detalle === "string") return detalle;
  if (Array.isArray(detalle) && typeof detalle[0]?.msg === "string") {
    return `${MENSAJES[422]} ${detalle[0].msg}`;
  }
  return MENSAJES[status] ?? "No se pudo completar la operación. Intenta de nuevo.";
}

interface Opciones {
  metodo?: "GET" | "POST" | "PUT";
  cuerpo?: unknown;
  /** En el login, un 401 significa credenciales erróneas, no sesión vencida. */
  ignorar401?: boolean;
}

export async function api<T>(ruta: string, opciones: Opciones = {}): Promise<T> {
  const { metodo = "GET", cuerpo, ignorar401 = false } = opciones;
  let respuesta: Response;
  try {
    respuesta = await fetch(`/api${ruta}`, {
      method: metodo,
      // Envía la cookie httpOnly; JavaScript nunca lee el token.
      credentials: "include",
      headers: cuerpo === undefined ? undefined : { "Content-Type": "application/json" },
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    });
  } catch {
    throw new ApiError(0, "No hay conexión con el servidor. Comprueba que el backend esté activo.");
  }

  if (respuesta.status === 204) return undefined as T;

  const datos: unknown = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    if (respuesta.status === 401 && !ignorar401) alExpirarSesion();
    throw new ApiError(respuesta.status, mensajeDeError(respuesta.status, datos));
  }
  return datos as T;
}
