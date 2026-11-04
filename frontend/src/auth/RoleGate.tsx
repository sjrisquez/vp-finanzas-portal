import { Outlet } from "react-router-dom";

import type { Rol } from "../api/types";
import { MensajeError } from "../components/Estados";
import { useUsuario } from "./AuthContext";

/** Solo mejora la experiencia: quien decide de verdad es el backend. */
export function RoleGate({ roles }: { roles: Rol[] }) {
  const usuario = useUsuario();
  if (!roles.includes(usuario.rol)) {
    return <MensajeError mensaje="Tu rol no tiene acceso a este módulo." />;
  }
  return <Outlet />;
}
