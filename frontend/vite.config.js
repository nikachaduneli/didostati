import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const django = 'http://127.0.0.1:8000'

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  // Built files are served by Django's staticfiles under /static/
  base: command === 'build' ? '/static/' : '/',
  server: {
    proxy: {
      '/api': django,
      '/media': django,
      '/admin': django,
      '/static': django,
      '/ckeditor5': django,
      '/i18n': django,
    },
  },
}))
