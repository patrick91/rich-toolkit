import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig(({ isSsrBuild, command }) => ({
  plugins: [tailwindcss(), react()],
  root: 'frontend',
  resolve: {
    dedupe: ['react', 'react-dom', '@inertiajs/react'],
  },
  build: {
    emptyOutDir: true,
    manifest: !isSsrBuild,
    rollupOptions: {
      input: 'app.tsx',
    },
  },
  ssr: {
    // Bundle all dependencies into the SSR build so no node_modules needed at runtime
    noExternal: isSsrBuild ? true : ['shiki', '@inertiajs/react'],
  },
  server: {
    origin: 'http://localhost:5173',
    fs: {
      allow: ['..'],
    },
  },
}))
