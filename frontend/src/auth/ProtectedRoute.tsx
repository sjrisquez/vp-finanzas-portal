import { Navigate, Outlet, useLocation } from "react-router-dom";

import { Cargando } from "../components/Estados";
import { useAuth } from "./AuthContext";

export function ProtectedRoute() {
  const { usuario, cargando } = useAuth();
  const ubicacion = useLocation();

  if (cargando) return <Cargando />;
  if (!usuario) return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />;
  return <Outlet />;
}
