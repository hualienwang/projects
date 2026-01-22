import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/run': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/stream_run': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/node_run': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/cancel': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/graph_parameter': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/health': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/v1': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
