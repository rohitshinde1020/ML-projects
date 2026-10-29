/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18332d",
        sage: "#dce9df",
        moss: "#3d705e",
        mint: "#eef6ef",
        sand: "#f7f5ef",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Georgia", "ui-serif", "serif"],
      },
    },
  },
  plugins: [],
};
