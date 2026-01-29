import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // В production используем корень /
  const base = '/';

  return {
    plugins: [react()],
    base,
    build: {
      minify: 'esbuild',
      // Добавляем хеш к именам файлов для кэширования
      rollupOptions: {
        output: {
          entryFileNames: `assets/[name]-[hash].js`,
          chunkFileNames: `assets/[name]-[hash].js`,
          assetFileNames: `assets/[name]-[hash].[ext]`,
        },
      },
    },
    server: {
      port: 5173,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: 'http://72.56.79.153:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
        '/socket.io': {
          target: 'ws://72.56.79.153:8000',
          ws: true,
        },
      },
    },
  };
});
