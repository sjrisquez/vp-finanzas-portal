/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        tinta: "#17324D",
        tintaSuave: "#2B4C6F",
        papel: "#F2F5F7",
        linea: "#D5DDE4",
        texto: "#1E2A35",
        tenue: "#5A6B7A",
      },
      fontFamily: {
        sans: ['"Libre Franklin"', "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
