// tailwind.config.ts
import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy:  "#0d1b2a",
        teal: {
          400: "#22c98a",
          500: "#1db97a",
          600: "#1a936f",
        },
        cream: "#faf8f2",
      },
      fontFamily: {
        sans:    ["var(--font-dm-sans)", "sans-serif"],
        display: ["var(--font-playfair)", "serif"],
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        "2xl": "0 8px 48px rgba(13,27,42,0.12), 0 2px 8px rgba(13,27,42,0.06)",
      },
    },
  },
  plugins: [],
}

export default config