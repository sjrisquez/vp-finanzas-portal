import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { MensajeError } from "../components/Estados";
import { rutaInicial, useAuth } from "../auth/AuthContext";

export function Login() {
  const { usuario, iniciarSesion } = useAuth();
  const navegar = useNavigate();
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  if (usuario) return <Navigate to={rutaInicial(usuario)} replace />;

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      const actual = await iniciarSesion(correo, password);
      navegar(rutaInicial(actual), { replace: true });
    } catch (fallo) {
      setError(fallo);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="login-fondo flex min-h-screen items-center justify-center p-4">
      <form onSubmit={enviar} className="login-tarjeta w-full max-w-md rounded-3xl p-6 sm:p-10">
        <h1 className="text-3xl font-bold tracking-tight text-tinta">Portal VP de Finanzas</h1>
        <p className="mt-1 text-sm text-texto">Entra con tu correo interno.</p>

        <label className="mt-7 block text-sm font-medium" htmlFor="correo">
          Correo
        </label>
        <div className="relative mt-1">
          <svg className="login-icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
            <rect x="3" y="5" width="18" height="14" rx="2" />
            <path d="m3 7 9 6 9-6" />
          </svg>
          <input
            id="correo"
            className="login-campo"
            type="email"
            autoComplete="username"
            required
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
          />
        </div>

        <label className="mt-4 block text-sm font-medium" htmlFor="password">
          Contraseña
        </label>
        <div className="relative mt-1">
          <svg className="login-icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
            <rect x="5" y="11" width="14" height="10" rx="2" />
            <path d="M8 11V7a4 4 0 0 1 8 0v4" />
          </svg>
          <input
            id="password"
            className="login-campo"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {error !== null && (
          <div className="mt-4">
            <MensajeError error={error} />
          </div>
        )}

        <button type="submit" disabled={enviando} className="login-boton mt-7">
          {enviando ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </div>
  );
}
