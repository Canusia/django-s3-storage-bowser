import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Builds straight into the Django app's namespaced static directory with
// fixed file names; the page markup is the hand-written
// templates/s3_storage_browser/_app.html, so no HTML is emitted.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../s3_storage_browser/static/s3_storage_browser',
    emptyOutDir: true,
    rollupOptions: {
      input: 'src/main.tsx',
      output: {
        entryFileNames: 'index.js',
        chunkFileNames: '[name].js',
        assetFileNames: (asset) =>
          asset.names?.some((name) => name.endsWith('.css')) ? 'index.css' : '[name][extname]',
      },
    },
  },
});
