import { Navigate, Route, Routes } from "react-router-dom";

import { rutaInicial, useAuth } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { RoleGate } from "./auth/RoleGate";
import { Cargando, MensajeError } from "./components/Estados";
import { Layout } from "./components/Layout";
import { Directorio } from "./pages/Directorio";
import { FichaCargo, FichaColaborador, MiPerfil } from "./pages/Fichas";
import { Login } from "./pages/Login";
import { NotaDetalle } from "./pages/NotaDetalle";
import { NotaFormulario } from "./pages/NotaFormulario";
import { NotasCredito } from "./pages/NotasCredito";

function Inicio() {
  const { usuario, cargando } = useAuth();
  if (cargando) return <Cargando />;
  return <Navigate to={usuario ? rutaInicial(usuario) : "/login"} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Inicio />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/directorio" element={<Directorio />} />
          <Route path="/colaboradores/:id" element={<FichaColaborador />} />
          <Route path="/cargos/:id" element={<FichaCargo />} />
          <Route path="/mi-perfil" element={<MiPerfil />} />
          <Route element={<RoleGate roles={["ADMIN", "JEFE_DEPARTAMENTO", "APROBADOR"]} />}>
            <Route path="/notas" element={<NotasCredito />} />
            <Route path="/notas/:id" element={<NotaDetalle />} />
          </Route>
          <Route element={<RoleGate roles={["ADMIN", "JEFE_DEPARTAMENTO"]} />}>
            <Route path="/notas/nueva" element={<NotaFormulario />} />
            <Route path="/notas/:id/reenviar" element={<NotaFormulario />} />
          </Route>
          <Route path="*" element={<MensajeError mensaje="Esta página no existe. Usa el menú para continuar." />} />
        </Route>
      </Route>
    </Routes>
  );
}
