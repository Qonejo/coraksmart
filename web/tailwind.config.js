/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",          // ✅ busca en el index de /web
    "./src/**/*.{js,ts,jsx,tsx}" // ✅ busca en todos tus componentes
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
