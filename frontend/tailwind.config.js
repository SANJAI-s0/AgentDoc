/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        sand: "#f7f4ee",
        ink: "#13263a",
        ocean: "#0f6ea8",
        ember: "#d18d24",
      },
      fontFamily: {
        sans: ["Aptos", "Trebuchet MS", "sans-serif"],
        serif: ["Rockwell", "Georgia", "serif"],
        mono: ["Consolas", "Courier New", "monospace"],
      },
      boxShadow: {
        card: "0 16px 36px rgba(21, 41, 65, 0.12)",
      },
    },
  },
  plugins: [],
};
