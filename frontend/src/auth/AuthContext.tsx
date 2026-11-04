import { useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useMemo, type ReactNode } from "react";

import { ApiError, api, registrarSesionExpirada } from "../api/client";
import type { UsuarioActual } from "../api/types";

interface Autenticacion {
  usuario: UsuarioActual | null;
  cargando: boolean;
  iniciarSesion: (correo: string, password: string) => Promise<UsuarioActual>;
  cerrarSesion: () => Promise<void>;
}

const ClaveUsuario = ["usuario-actual"];
const ContextoAuth = createContext<Autenticacion | null>(null);

function actualizarSesion(clienteQuery: QueryClient, usuario: UsuarioActual | null): void {
  // Borra los datos del usuario anterior, pero conserva la consulta que observa AuthProvider.
  clienteQuery.removeQueries({
    predicate: (consulta) => consulta.queryKey[0] !== ClaveUsuario[0],
  });
  clienteQuery.setQueryData(ClaveUsuario, usuario);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const clienteQuery = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ClaveUsuario,
    queryFn: async (): Promise<UsuarioActual | null> => {
      try {
        return await api<UsuarioActual>("/auth/me", { ignorar401: true });
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) return null;
        throw error;
      }
    },
    retry: false,
    staleTime: Infinity,
  });

  useEffect(() => {
    registrarSesionExpirada(() => actualizarSesion(clienteQuery, null));
  }, [clienteQuery]);

  const valor = useMemo<Autenticacion>(
    () => ({
      usuario: data ?? null,
      cargando: isLoading,
      iniciarSesion: async (correo: string, password: string) => {
        const usuario = await api<UsuarioActual>("/auth/login", {
          metodo: "POST",
          cuerpo: { correo, password },
          ignorar401: true,
        });
        actualizarSesion(clienteQuery, usuario);
        return usuario;
      },
      cerrarSesion: async () => {
        await api<void>("/auth/logout", { metodo: "POST", ignorar401: true }).catch(() => undefined);
        actualizarSesion(clienteQuery, null);
      },
    }),
    [clienteQuery, data, isLoading],
  );

  return <ContextoAuth.Provider value={valor}>{children}</ContextoAuth.Provider>;
}

export function useAuth(): Autenticacion {
  const contexto = useContext(ContextoAuth);
  if (!contexto) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return contexto;
}

export function useUsuario(): UsuarioActual {
  const { usuario } = useAuth();
  if (!usuario) throw new Error("Esta pantalla requiere una sesión activa");
  return usuario;
}

export function rutaInicial(usuario: UsuarioActual): string {
  return usuario.modulos.includes("notas-credito") ? "/notas" : "/directorio";
}
