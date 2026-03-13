import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: "#050816",
        surface: "#0b1020",
        surfaceMuted: "#111827",
        accent: "#38bdf8"
      }
    }
  },
  plugins: [],
};

export default config;

