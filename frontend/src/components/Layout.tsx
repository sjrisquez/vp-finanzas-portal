import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth, useUsuario } from "../auth/AuthContext";

const MODULOS: Record<string, { ruta: string; nombre: string }> = {
  "notas-credito": { ruta: "/notas", nombre: "Notas de crédito" },
  directorio: { ruta: "/directorio", nombre: "Directorio" },
  "mi-perfil": { ruta: "/mi-perfil", nombre: "Mi perfil" },
};

const NOMBRE_ROL = {
  ADMIN: "Administrador",
  JEFE_DEPARTAMENTO: "Jefe de departamento",
  APROBADOR: "Aprobador",
  COLABORADOR: "Colaborador",
};

export function Layout() {
  const usuario = useUsuario();
  const { cerrarSesion } = useAuth();
  const navegar = useNavigate();

  const salir = async () => {
    await cerrarSesion();
    navegar("/login", { replace: true });
  };

  const modulos = Object.keys(MODULOS).filter((clave) => usuario.modulos.includes(clave));

  return (
    <div className="min-h-screen md:flex">
      <aside className="bg-tinta text-white md:sticky md:top-0 md:flex md:h-screen md:w-60 md:flex-col md:p-5">
        <div className="p-4 md:p-0">
          <p className="text-lg font-bold leading-tight">VP de Finanzas</p>
          <p className="text-xs text-blue-100">Portal interno</p>
        </div>

        {/* El menú sale de /api/auth/me; no se decide por rol en el cliente. */}
        <nav aria-label="Módulos" className="flex gap-1 overflow-x-auto px-3 pb-3 md:mt-8 md:flex-col md:px-0">
          {modulos.map((clave) => (
            <NavLink
              key={clave}
              to={MODULOS[clave].ruta}
              className={({ isActive }: { isActive: boolean }) =>
                `whitespace-nowrap rounded-lg px-3 py-2 transition-colors text-sm font-medium ${
                  isActive ? "bg-white text-tinta" : "text-white hover:bg-tintaSuave"
                }`
              }
            >
              {MODULOS[clave].nombre}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-tintaSuave p-4 text-sm md:mt-auto md:px-0 md:pb-0">
          <p className="font-semibold">
            {usuario.nombres} {usuario.apellidos}
          </p>
          <p className="text-xs text-blue-100">{NOMBRE_ROL[usuario.rol]}</p>
          <p className="text-xs text-blue-100">{usuario.departamento.nombre}</p>
          <button type="button" onClick={salir} className="mt-3 text-sm font-medium underline underline-offset-2">
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 p-4 md:p-8">
        <div className="mx-auto max-w-6xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
