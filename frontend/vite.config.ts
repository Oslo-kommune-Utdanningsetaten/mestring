import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { loadEnv } from 'vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd(), '') }
  console.log('Vite environment variables:', process.env)

  const proxyConfig = process.env.VITE_API_BASE_URL
    ? {
        '/api': {
          target: process.env.VITE_API_BASE_URL,
          changeOrigin: true,
          secure: false,
          // rewrite: (path: string) => path.replace(/^\/api/, ''),
        },
        '/auth/': {
          target: process.env.VITE_API_BASE_URL,
          changeOrigin: true,
          secure: false,
          // rewrite: (path: string) => path.replace(/^\/api/, ''),
        },
      }
    : undefined

  return {
    plugins: [svelte()],
    server: {
      proxy: proxyConfig,
      host: true,
    },
  }
})
