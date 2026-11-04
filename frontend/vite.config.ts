import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      // 127.0.0.1 evita que "localhost" se resuelva a IPv6 y falle la conexion.
      "/api": "http://127.0.0.1:8000",
    },
  },
});
