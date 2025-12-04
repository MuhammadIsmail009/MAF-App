/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./src/app/**/*.{ts,tsx}", "./src/components/**/*.{ts,tsx}", "./src/visualizations/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#050816",
        foreground: "#f9fafb",
        card: "#0b1020",
        border: "#1f2937",
        accent: {
          DEFAULT: "#6366f1",
          soft: "#4f46e5"
        },
        danger: {
          DEFAULT: "#ef4444",
          soft: "#991b1b"
        }
      },
      boxShadow: {
        glow: "0 0 30px rgba(99, 102, 241, 0.6)",
        "glow-danger": "0 0 30px rgba(239, 68, 68, 0.7)"
      }
    }
  },
  plugins: []
};


