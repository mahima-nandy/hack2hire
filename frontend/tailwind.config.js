/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1120",
        panel: "rgba(15, 23, 42, 0.72)",
        mint: "#38f8b6",
        coral: "#ff7a59"
      },
      boxShadow: {
        glass: "0 20px 80px rgba(0, 0, 0, 0.35)"
      }
    }
  },
  plugins: []
};
