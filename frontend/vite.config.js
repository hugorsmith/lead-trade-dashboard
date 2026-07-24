import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Pure static build — there is no API to proxy. The dashboard loads its data
// from public/data/ (trade.tsv + meta.json) and computes everything in the
// browser, so `vite build` produces a directory any static host can serve.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
