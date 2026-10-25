import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages serves the app from /<repository-name>/.
// Set VITE_BASE_PATH for a custom deployment path; root hosting defaults to '/'.
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE_PATH || '/',
})
