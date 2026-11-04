import { useEffect, useState } from "react";

type Estado = "cargando" | "conectado" | "sin conexion";

export default function App() {
  const [estado, setEstado] = useState<Estado>("cargando");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<{ status: string }>;
      })
      .then((data) => setEstado(data.status === "ok" ? "conectado" : "sin conexion"))
      .catch(() => setEstado("sin conexion"));
  }, []);

  return (
    <main>
      <h1>Portal VP de Finanzas</h1>
      <p>Estado de la API: {estado}</p>
    </main>
  );
}
