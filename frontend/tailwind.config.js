/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#1e40af', // 700
          light: '#3b82f6',   // 500
          dark: '#1e3a8a',    // 900
        },
        secondary: '#64748b',
        accent: '#f59e0b',
      }
    },
  },
  plugins: [],
}
