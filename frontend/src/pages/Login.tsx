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
    <div className="flex min-h-screen items-center justify-center bg-tinta p-4">
      <form onSubmit={enviar} className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-xl">
        <h1 className="text-2xl font-bold text-tinta">Portal VP de Finanzas</h1>
        <p className="mt-1 text-sm text-tenue">Entra con tu correo interno.</p>

        <label className="mt-6 block text-sm font-medium" htmlFor="correo">
          Correo
        </label>
        <input
          id="correo"
          className="campo mt-1"
          type="email"
          autoComplete="username"
          required
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
        />

        <label className="mt-4 block text-sm font-medium" htmlFor="password">
          Contraseña
        </label>
        <input
          id="password"
          className="campo mt-1"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error !== null && (
          <div className="mt-4">
            <MensajeError error={error} />
          </div>
        )}

        <button type="submit" disabled={enviando} className="boton-principal mt-6 w-full">
          {enviando ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </div>
  );
}
