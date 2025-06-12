import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd(), '') }

  if (!process.env.VITE_API_BASE_URL) {
    throw new Error(
      'VITE_API_BASE_URL is not set. All is lost! Unless you set it in your .env file, that is.'
    )
  }

  const proxyConfig = {
    '/api': {
      target: process.env.VITE_API_BASE_URL,
      changeOrigin: true,
      secure: false,
    },
    '/auth/': {
      target: process.env.VITE_API_BASE_URL,
      changeOrigin: true,
      secure: false,
    },
  }

  return {
    plugins: [svelte()],
    server: {
      proxy: proxyConfig,
      host: true,
    },
  }
})
