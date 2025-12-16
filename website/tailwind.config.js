const docsPreset = require('@usecross/docs/tailwind.preset')

/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [docsPreset],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 10%, white)',
          100: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 20%, white)',
          200: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 30%, white)',
          300: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 50%, white)',
          400: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 70%, white)',
          500: 'var(--color-primary-500, #22c55e)',
          600: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 90%, black)',
          700: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 70%, black)',
          800: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 50%, black)',
          900: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 30%, black)',
          950: 'color-mix(in srgb, var(--color-primary-500, #22c55e) 15%, black)',
        },
      },
    },
  },
}
